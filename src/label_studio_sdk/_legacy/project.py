""" .. include::../docs/project.md
"""

import json
import logging
import os
import pathlib
import time
from enum import Enum, auto
from pathlib import Path
from random import sample, shuffle
from typing import Optional, Union, List, Dict, Callable

from label_studio_sdk._extensions.label_studio_tools.core.label_config import parse_config
from label_studio_sdk._extensions.label_studio_tools.core.utils.io import get_local_path
from requests import Response
from requests.exceptions import HTTPError, InvalidSchema, MissingSchema

from .client import Client
from .utils import parse_config, chunk

logger = logging.getLogger(__name__)


class LabelStudioException(Exception):
    pass


class LabelStudioAttributeError(LabelStudioException):
    pass


class ProjectSampling(Enum):
    """Enumerate the available task sampling modes for labeling."""

    RANDOM = "Uniform sampling"
    """ Uniform random sampling of tasks """
    SEQUENCE = "Sequential sampling"
    """ Sequential sampling of tasks using task IDs """
    UNCERTAINTY = "Uncertainty sampling"
    """ Sample tasks based on prediction scores, such as for active learning (Enterprise only)"""


class ProjectStorage(Enum):
    """Enumerate the available types of external source and target storage for labeling projects."""

    GOOGLE = "gcs"
    """ Google Cloud Storage """
    S3 = "s3"
    """ Amazon S3 Storage """
    AZURE = "azure_blob"
    """ Microsoft Azure Blob Storage """
    LOCAL = "localfiles"
    """ Label Studio Local File Storage """
    REDIS = "redis"
    """ Redis Storage """
    S3_SECURED = "s3s"
    """ Amazon S3 Storage secured by IAM roles (Enterprise only) """


class AssignmentSamplingMethod(Enum):
    RANDOM = auto()  # produces uniform splits across annotators


class ExportSnapshotStatus:
    CREATED = "created"
    """ Export snapshot is created """
    IN_PROGRESS = "in_progress"
    """ Export snapshot is in progress  """
    FAILED = "failed"
    """ Export snapshot failed with errors """
    COMPLETED = "completed"
    """ Export snapshot was created and can be downloaded """

    def __init__(self, response):
        self.response = response

    def is_created(self):
        """Export snapshot is created"""
        assert (
            "status" in self.response
        ), '"status" field not found in export snapshot status response'
        return self.response["status"] == self.CREATED

    def is_in_progress(self):
        """Export snapshot is in progress"""
        assert (
            "status" in self.response
        ), '"status" field not found in export_snapshot_status response'
        return self.response["status"] == self.IN_PROGRESS

    def is_failed(self):
        """Export snapshot failed with errors"""
        assert (
            "status" in self.response
        ), '"status" field not found in export_snapshot_status response'
        return self.response["status"] == self.FAILED

    def is_completed(self):
        """Export snapshot was created and can be downloaded"""
        assert (
            "status" in self.response
        ), '"status" field not found in export_snapshot_status response'
        return self.response["status"] == self.COMPLETED


class Project(Client):
    def __init__(self, *args, **kwargs):
        """Initialize project class.

        Parameters
        ----------

        """
        super(Project, self).__init__(*args, **kwargs)
        self.params = {}

    def __getattr__(self, item):
        return self._get_param(item)

    @property
    def parsed_label_config(self):
        """Get the parsed labeling configuration for the project. You can use this to more easily construct
        annotation or prediction results based on your labeling configuration.

        Returns
        -------
        dict
            Object and control tags from the project labeling configuration.
            Example with structured configuration of the form:
        ```
        {
            "<ControlTag>.name": {
                "type": "ControlTag",
                "to_name": ["<ObjectTag1>.name", "<ObjectTag2>.name"],
                "inputs: [
                    {"type": "ObjectTag1", "value": "<ObjectTag1>.value"},
                    {"type": "ObjectTag2", "value": "<ObjectTag2>.value"}
                ],
                "labels": ["Label1", "Label2", "Label3"]
        }
        ```
        `"labels"` are taken from "alias" attribute if it exists, else "value"
        """
        return parse_config(self.label_config)

    def get_members(self):
        """Get members from this project.

        Parameters
        ----------

        Returns
        -------
        list of `label_studio_sdk.users.User`

        """
        from .users import User

        assert self.is_enterprise, (
            "Project members are available in the Enterprise edition of Label Studio only. "
            "Use get_users() instead."
        )

        response = self.make_request("GET", f"/api/projects/{self.id}/members")
        users = []
        for user_data in response.json():
            user_data["client"] = self
            users.append(User(**user_data))
        return users

    def add_member(self, user):
        """Add a user to a project.

        Parameters
        ----------
        user: User

        Returns
        -------
        dict
            Dict with created member

        """
        payload = {"user": user.id}
        response = self.make_request(
            "POST", f"/api/projects/{self.id}/members", json=payload
        )
        return response.json()

    def assign_annotators(self, users, tasks_ids):
        """Assign annotators to tasks

        Parameters
        ----------
        users: list of user's objects
        tasks_ids: list of integer task IDs to assign users to

        Returns
        -------
        dict
            Dict with counter of created assignments

        """
        final_response = {"assignments": 0}
        users_ids = [user.id for user in users]
        # Assign tasks to users with batches
        for c in chunk(tasks_ids, 1000):
            logger.debug(f"Starting assignment for: {users_ids}")
            payload = {
                "users": users_ids,
                "selectedItems": {"all": False, "included": c},
                "type": "AN",
            }
            response = self.make_request(
                "POST", f"/api/projects/{self.id}/tasks/assignees", json=payload
            )
            final_response["assignments"] += response.json()["assignments"]
        return final_response

    def delete_annotators_assignment(self, tasks_ids):
        """Remove all assigned annotators for tasks

        Parameters
        ----------
        tasks_ids: list of int

        Returns
        -------
        dict
            Dict with counter of deleted annotator assignments

        """
        payload = {"selectedItems": {"all": False, "included": tasks_ids}}
        response = self.make_request(
            "POST",
            f"/api/dm/actions?id=delete_annotators&project={self.id}",
            json=payload,
        )
        return response.json()

    def delete_reviewers_assignment(self, tasks_ids):
        """Clear all assigned reviewers for tasks

        Parameters
        ----------
        tasks_ids: list of int

        Returns
        -------
        dict
            Dict with counter of deleted reviewer assignments

        """
        payload = {"selectedItems": {"all": False, "included": tasks_ids}}
        response = self.make_request(
            "POST",
            f"/api/dm/actions?id=delete_reviewers&project={self.id}",
            json=payload,
        )
        return response.json()

    def assign_reviewers(self, users, tasks_ids):
        """Assign reviewers to tasks

        Parameters
        ----------
        users: list of user's objects
        tasks_ids: list of integer task IDs to assign reviewers to

        Returns
        -------
        dict
            Dict with counter of created assignments

        """
        payload = {
            "users": [user.id for user in users],
            "selectedItems": {"all": False, "included": tasks_ids},
            "type": "RE",
        }
        response = self.make_request(
            "POST", f"/api/projects/{self.id}/tasks/assignees", json=payload
        )
        return response.json()

    def _get_param(self, param_name):
        if param_name not in self.params:
            self.update_params()
            if param_name not in self.params:
                raise LabelStudioAttributeError(
                    f'Project "{param_name}" field is not set'
                )
        return self.params[param_name]

    def get_params(self):
        """Get all available project parameters.

        Returns
        --------
        dict
            containing all following params:

        title: str
            Project name.
        description: str
            Project description
        label_config: str
            Label config in XML format.
        expert_instruction: str
            Labeling instructions in HTML format
        show_instruction: bool
            Whether to display instructions to annotators before they start
        show_skip_button: bool
            Whether to show a skip button in the Label Studio UI and let annotators skip the task
        enable_empty_annotation: bool
            Allow annotators to submit empty annotations
        show_annotation_history: bool
            Show annotation history to annotator
        organization: int
            Organization ID
        color: str
            Color to decorate the project card in the Label Studio UI
        maximum_annotations: int
            Maximum number of annotations for one task. If the number of annotations per task is equal or greater
            to this value, the task is finished and is_labeled=True is set. (Enterprise only)
        is_published: bool
            Whether or not the project is published to annotators (Enterprise only)
        model_version: str
            Machine learning model version for predictions or pre-annotations
        is_draft: bool
            Whether or not the project is in the middle of being created (Enterprise only)
        created_by: object
            Details about the user that created the project
        min_annotations_to_start_training: int
            Minimum number of completed tasks after which model training is started
        show_collab_predictions: bool
            Whether to show model predictions to the annotator, allowing them to collaborate with the ML model
        sampling: str
            Type of sampling to use for task labeling. Uncertainty sampling is Enterprise only.
            Enum: "Sequential sampling" "Uniform sampling" "Uncertainty sampling"
        show_ground_truth_first: bool
            Whether to show tasks with ground truth annotations first (Enterprise only)
        show_overlap_first: bool
            Whether to show tasks with overlap first (Enterprise only)
        overlap_cohort_percentage: int
            Percentage of tasks that must be annotated multiple times. (Enterprise only)
        task_data_login: str
            User credentials for accessing task data. (Enterprise only)
        task_data_password: str
            Password credentials for accessing task data. (Enterprise only)
        control_weights: object
            Weights for control tags used when calculating agreement metrics. (Enterprise only)
        evaluate_predictions_automatically: bool
            Retrieve and display predictions when loading a task

        """
        response = self.make_request("GET", f"/api/projects/{self.id}")
        return response.json()

    def get_model_versions(self):
        """Get the list of available ML model versions from pre-annotations or connected ML backends.

        Returns
        -------
        list of strings
             Model versions

        """
        response = self.make_request("GET", f"/api/projects/{self.id}/model-versions")
        return response.json()

    def update_params(self):
        """Get [all available project parameters](#label_studio_sdk.project.Project.get_params) and cache them."""
        self.params = self.get_params()

    def start_project(self, **kwargs):
        """Create a new labeling project in Label Studio.

        Parameters
        ----------
        title: str
            Project name.
        description: str
            Project description
        label_config: str
            Label config in XML format.
        expert_instruction: str
            Labeling instructions in HTML format
        show_instruction: bool
            Whether to display instructions to annotators before they start
        show_skip_button: bool
            Whether to show a skip button in the Label Studio UI and let annotators skip the task
        enable_empty_annotation: bool
            Allow annotators to submit empty annotations
        show_annotation_history: bool
            Show annotation history to annotator
        organization: int
            Organization ID
        color: str
            Color to decorate the project card in the Label Studio UI
        maximum_annotations: int
            Maximum number of annotations for one task. If the number of annotations per task is equal or greater
            to this value, the task is finished and is_labeled=True is set. (Enterprise only)
        is_published: bool
            Whether or not the project is published to annotators (Enterprise only)
        model_version: str
            Machine learning model version for predictions or pre-annotations
        is_draft: bool
            Whether or not the project is in the middle of being created (Enterprise only)
        created_by: object
            Details about the user that created the project
        min_annotations_to_start_training: int
            Minimum number of completed tasks after which model training is started
        show_collab_predictions: bool
            Whether to show model predictions to the annotator, allowing them to collaborate with the ML model
        sampling: str
            Type of sampling to use for task labeling. Uncertainty sampling is Enterprise only.
            Enum: "Sequential sampling" "Uniform sampling" "Uncertainty sampling"
        show_ground_truth_first: bool
            Whether to show tasks with ground truth annotations first (Enterprise only)
        show_overlap_first: bool
            Whether to show tasks with overlap first (Enterprise only)
        overlap_cohort_percentage: int
            Percentage of tasks that must be annotated multiple times. (Enterprise only)
        task_data_login: str
            User credentials for accessing task data. (Enterprise only)
        task_data_password: str
            Password credentials for accessing task data. (Enterprise only)
        control_weights: object
            Weights for control tags used when calculating agreement metrics. (Enterprise only)
        evaluate_predictions_automatically: bool
            Retrieve and display predictions when loading a task

        Raises LabelStudioException in case of errors.

        """
        response = self.make_request("POST", "/api/projects", json=kwargs)
        if response.status_code == 201:
            self.params = response.json()
        else:
            raise LabelStudioException("Project not created")

    @classmethod
    def _create_from_id(cls, client, project_id, params=None):
        project = cls(
            url=client.url,
            api_key=client.api_key,
            session=client.session,
            extra_headers=client.headers,
            versions=client.versions,
            make_request_raise=client.make_request_raise,
        )
        if params and isinstance(params, dict):
            # TODO: validate project parameters
            project.params = params
        project.params["id"] = project_id
        return project

    @classmethod
    def get_from_id(cls, client, project_id) -> "Project":
        """Class factory to create a project instance from an existing project ID.

        Parameters
        ----------
        client: class Client
        project_id: int
            Project ID

        Returns
        -------
        `Project`
        """
        project = cls._create_from_id(client, project_id)
        project.update_params()
        return project

    def import_tasks(self, tasks, preannotated_from_fields: List = None):
        """Import JSON-formatted labeling tasks. Tasks can be unlabeled or contain predictions.

        Parameters
        ----------
        tasks: list of dicts | dict | path to file
            Tasks in <a href="https://labelstud.io/guide/tasks.html#Basic-Label-Studio-JSON-format">
            Label Studio JSON format</a>

        preannotated_from_fields: list of strings
            Turns flat task JSON formatted like: `{"column1": value, "column2": value}` into Label Studio prediction
            data format: `{"data": {"column1"..}, "predictions": [{..."column2"}]`
            Useful when all your data is stored in tabular format with one column dedicated to model predictions.

        Returns
        -------
        list of int
            Imported task IDs

        """
        params = {"return_task_ids": "1"}
        if preannotated_from_fields:
            params["preannotated_from_fields"] = ",".join(preannotated_from_fields)
        if isinstance(tasks, (list, dict)):
            response = self.make_request(
                method="POST",
                url=f"/api/projects/{self.id}/import",
                json=tasks,
                params=params,
                timeout=(10, 600),
            )
        elif isinstance(tasks, (str, Path)):
            # try import from file
            if not os.path.isfile(tasks):
                raise LabelStudioException(f"Not found import tasks file {tasks}")
            with open(tasks, mode="rb") as f:
                response = self.make_request(
                    method="POST",
                    url=f"/api/projects/{self.id}/import",
                    files={"file": f},
                    params=params,
                    timeout=(10, 600),
                )
        else:
            raise TypeError(
                f'Not supported type provided as "tasks" argument: {type(tasks)}'
            )
        response = response.json()

        if "import" in response:
            # check import status
            timeout = 300
            fibonacci_backoff = [1, 1]

            start_time = time.time()

            while True:
                import_status = self.make_request(
                    method="GET",
                    url=f'/api/projects/{self.id}/imports/{response["import"]}',
                ).json()

                if import_status["status"] == "completed":
                    return import_status["task_ids"]

                if import_status["status"] == "failed":
                    raise LabelStudioException(import_status["error"])

                if time.time() - start_time >= timeout:
                    raise LabelStudioException("Import timeout")

                time.sleep(fibonacci_backoff[0])
                fibonacci_backoff = [
                    fibonacci_backoff[1],
                    fibonacci_backoff[0] + fibonacci_backoff[1],
                ]

        return response["task_ids"]

    def export_tasks(
        self,
        export_type: str = "JSON",
        download_all_tasks: bool = False,
        download_resources: bool = False,
        ids: Optional[List[int]] = None,
        export_location: Optional[str] = None,
    ) -> Union[list, pathlib.Path]:
        """Export annotated tasks.

        Parameters
        ----------
        export_type: string
            Default export_type is JSON.
            Specify another format type as referenced in <a href="https://github.com/heartexlabs/label-studio-converter/blob/master/label_studio_converter/converter.py#L32">
            the Label Studio converter code</a>.

        download_all_tasks: bool
            Default download_all_tasks is False.
            If true, download all tasks regardless of status. If false, download only annotated tasks.

        download_resources: bool
            Default download_resources is False.
            If true, download all resource files such as images, audio, and others relevant to the tasks.

        ids: list of ints
            Optional, specify a list of task IDs to retrieve only the details for those tasks.
        export_location: str or path
            Optional, specify a location to save the export to, this is mandatory for the YOLO export.
            A pathlib.Path object will be returned instead of the deserialized json.
        Returns
        -------
        list of dicts if export_location is None
            Tasks with annotations
        pathlib.Path if export_location is not None
            Path to the export

        """
        params = {
            "exportType": export_type,
            "download_all_tasks": download_all_tasks,
            "download_resources": download_resources,
        }
        if ids:
            params["ids"] = ids
        response = self.make_request(
            method="GET", url=f"/api/projects/{self.id}/export", params=params
        )
        if export_location is None:
            if "JSON" not in export_type.upper():
                raise ValueError(
                    f"{export_type} export type requires an export location to be specified"
                )
            return response.json()

        export_path = pathlib.Path(export_location)

        # ensure that parent location exists even if it is in some subdirectory
        export_path.parent.mkdir(parents=True, exist_ok=True)

        with open(export_path, "wb") as out_file:
            for chunk in response.iter_content(
                chunk_size=1024
            ):  # 1 kib seems reasonable
                out_file.write(chunk)

        return export_path

    def set_params(self, **kwargs):
        """Low level function to set project parameters."""
        response = self.make_request("PATCH", f"/api/projects/{self.id}", json=kwargs)
        assert response.status_code == 200

    def set_sampling(self, sampling: ProjectSampling):
        """Set the project sampling method for the labeling stream."""
        self.set_params(sampling=sampling.value)

    def set_published(self, is_published: bool):
        """Set the project publication state. (Enterprise only)

        Parameters
        ----------
        is_published: bool
            Project publication state for reviewers and annotators

        """
        self.set_params(is_published=is_published)

    def set_model_version(self, model_version: str):
        """Set the current model version to use for displaying predictions to annotators, perform uncertainty sampling
        and annotation evaluations in Label Studio Enterprise, and other operations.

        Parameters
        ----------
        model_version: string
            It can be any string you want

        """
        self.set_params(model_version=model_version)

    def get_tasks(
        self,
        filters=None,
        ordering=None,
        view_id=None,
        selected_ids=None,
        only_ids: bool = False,
    ):
        """Retrieve a subset of tasks from the Data Manager based on a filter, ordering mechanism, or a
        predefined view ID.

        Parameters
        ----------
        filters: label_studio_sdk.data_manager.Filters.create()
            JSON objects representing Data Manager filters. Use `label_studio_sdk.data_manager.Filters.create()`
            helper to create it.
            Example:
        ```json
        {
          "conjunction": "and",
          "items": [
            {
              "filter": "filter:tasks:id",
              "operator": "equal",
              "type": "Number",
              "value": 1
            }
          ]
        }
        ```
        ordering: list of label_studio_sdk.data_manager.Column
            List with <b>one</b> string representing Data Manager ordering.
            Use `label_studio_sdk.data_manager.Column` helper class.
            Example:
            ```[Column.total_annotations]```, ```['-' + Column.total_annotations]``` - inverted order
        view_id: int
            View ID, visible as a Data Manager tab, for which to retrieve filters, ordering, and selected items
        selected_ids: list of ints
            Task IDs
        only_ids: bool
            If true, return only task IDs

        Returns
        -------
        list
            Task list with task data, annotations, predictions and other fields from the Data Manager

        """

        page = 1
        result = []
        data = {}
        while not data.get("end_pagination"):
            try:
                data = self.get_paginated_tasks(
                    filters=filters,
                    ordering=ordering,
                    view_id=view_id,
                    selected_ids=selected_ids,
                    only_ids=only_ids,
                    page=page,
                    page_size=100,
                )
                result += data["tasks"]
                page += 1
            except LabelStudioException as e:
                logger.debug(f"Error during pagination: {e}")
                break
        return result

    def get_paginated_tasks(
        self,
        filters=None,
        ordering=None,
        view_id=None,
        selected_ids=None,
        page: int = 1,
        page_size: int = 100,
        only_ids: bool = False,
        resolve_uri: bool = True,
    ):
        """Retrieve a subset of tasks from the Data Manager based on a filter, ordering mechanism, or a
        predefined view ID. For non-existent pages it returns 404 error.

        Parameters
        ----------
        filters: label_studio_sdk.data_manager.Filters.create()
            JSON objects representing Data Manager filters. Use `label_studio_sdk.data_manager.Filters.create()`
            helper to create it.
            Example:

                {
                  "conjunction": "and",
                  "items": [
                    {
                      "filter": "filter:tasks:id",
                      "operator": "equal",
                      "type": "Number",
                      "value": 1
                    }
                  ]
                }

        ordering: list of label_studio_sdk.data_manager.Column
            List with <b>one</b> string representing Data Manager ordering.
            Use `label_studio_sdk.data_manager.Column` helper class.
            Example:
            ```[Column.total_annotations]```, ```['-' + Column.total_annotations]``` - inverted order
        view_id: int
            View ID, visible as a Data Manager tab, for which to retrieve filters, ordering, and selected items
        selected_ids: list of ints
            Task IDs
        page: int
            Page. Default is 1.
        page_size: int
            Page size. Default is 100, to retrieve all tasks in the project you can use get_tasks().
        only_ids: bool
            If true, return only task IDs
        resolve_uri: bool
            Resolve pre-sign urls to https links

        Returns
        -------

        dict
            Example:

                {
                    "tasks": [{...}],
                    "total_annotations": 50,
                    "total_predictions": 100,
                    "total": 100
                }

        tasks: list of dicts
            Tasks with task data, annotations, predictions and other fields from the Data Manager
        total: int
            Total number of tasks in filtered result
        total_annotations: int
            Total number of annotations in filtered tasks
        total_predictions: int
            Total number of predictions in filtered tasks

        """
        query = {
            "filters": filters,
            "ordering": ordering or [],
            "selectedItems": (
                {"all": False, "included": selected_ids}
                if selected_ids
                else {"all": True, "excluded": []}
            ),
        }
        params = {
            "project": self.id,
            "page": page,
            "page_size": page_size,
            "view": view_id,
            "query": json.dumps(query),
            "fields": "all",
            "resolve_uri": resolve_uri,
        }
        if only_ids:
            params["include"] = "id"

        response = self.make_request(
            "GET", "/api/tasks", params, raise_exceptions=False
        )
        # we'll get 404 from API on empty page
        if response.status_code == 404:
            return {"tasks": [], "end_pagination": True}
        elif response.status_code != 200:
            self.log_response_error(response)
            try:
                response.raise_for_status()
            except HTTPError as e:
                raise LabelStudioException(f"Error loading tasks: {e}")

        data = response.json()
        tasks = data["tasks"]
        if only_ids:
            data["tasks"] = [task["id"] for task in tasks]

        return data

    def get_tasks_ids(self, *args, **kwargs):
        """Same as `label_studio_sdk.project.Project.get_tasks()` but returns only task IDs."""
        kwargs["only_ids"] = True
        return self.get_tasks(*args, **kwargs)

    def get_paginated_tasks_ids(self, *args, **kwargs):
        """Same as `label_studio_sdk.project.Project.get_paginated_tasks()` but returns
        only task IDs.
        """
        kwargs["only_ids"] = True
        return self.get_paginated_tasks(*args, **kwargs)

    def get_views(self):
        """Get all views related to the project

        Returns
        -------
        list
            List of view dicts

        The each dict contains the following fields:
        id: int
            View ID
        project: int
            Project ID
        user: int
            User ID who created this tab
        data: dict
            Filters, orderings and other visual settings
        """
        response = self.make_request("GET", f"/api/dm/views?project={self.id}")
        return response.json()

    def create_view(self, filters, ordering=None, title="Tasks"):
        """Create view

        Parameters
        ----------
        filters: dict
            Specify the filters(`label_studio_sdk.data_manager.Filters`) of the view
        ordering: list of label_studio_sdk.data_manager.Column
            List with <b>one</b> string representing Data Manager ordering.
            Use `label_studio_sdk.data_manager.Column` helper class.
            Example:
            ```[Column.total_annotations]```, ```['-' + Column.total_annotations]``` - inverted order
        title: str
            Tab name
        Returns
        -------
        dict:
            dict with created view

        """
        data = {
            "project": self.id,
            "data": {"title": title, "ordering": ordering, "filters": filters},
        }
        response = self.make_request("POST", "/api/dm/views", json=data)
        return response.json()

    def delete_view(self, view_id):
        """Delete view

        Parameters
        ----------
        view_id: int
            View ID

        Returns
        -------
        dict:
            dict with deleted view

        """
        response = self.make_request("DELETE", f"/api/dm/views/{view_id}")
        return

    @property
    def tasks(self):
        """Retrieve all tasks from the project. This call can be very slow if the project has a lot of tasks."""
        return self.get_tasks()

    @property
    def tasks_ids(self):
        """IDs for all tasks for a project. This call can be very slow if the project has lots of tasks."""
        return self.get_tasks_ids()

    def get_labeled_tasks(self, only_ids=False):
        """Retrieve all tasks that have been completed, i.e. where requested number of annotations have been created

        Parameters
        ----------
        only_ids: bool
            Return only task IDs.

        Returns
        -------
        list
            List of task dicts, the same as in `get_tasks`.

        """
        return self.get_tasks(
            filters={
                "conjunction": "and",
                "items": [
                    {
                        "filter": "filter:tasks:completed_at",
                        "operator": "empty",
                        "value": False,
                        "type": "Datetime",
                    }
                ],
            },
            only_ids=only_ids,
        )

    def get_labeled_tasks_ids(self):
        """Retrieve all task IDs for completed tasks, i.e. where requested number of annotations have been created

        Returns
        -------
        list
            List of task IDs
        """
        return self.get_labeled_tasks(only_ids=True)

    def get_unlabeled_tasks(self, only_ids=False):
        """Retrieve all tasks that are <b>not</b> completed.
         If using Label Studio Enterprise, this can include tasks that have been labeled one or more times, but not the full number of times defined in the
        project labeling settings.

        Parameters
        ----------
        only_ids: bool
            Return only task IDs

        Returns
        -------
        list
            List of task dicts, the same as in `get_tasks`.

        """
        return self.get_tasks(
            filters={
                "conjunction": "and",
                "items": [
                    {
                        "filter": "filter:tasks:completed_at",
                        "operator": "empty",
                        "value": True,
                        "type": "Datetime",
                    }
                ],
            },
            only_ids=only_ids,
        )

    def get_unlabeled_tasks_ids(self):
        """Retrieve all task IDs for tasks that are <b>not</b> completed. If using
        Label Studio Enterprise, this can include tasks that have been labeled one or more times, but not the full
        number of times defined in the project labeling settings.

        Returns
        -------
        list
            List of task IDs
        """
        return self.get_unlabeled_tasks(only_ids=True)

    def get_task(self, task_id):
        """Get specific task by ID.

        Parameters
        ----------
        task_id: int
            Task ID you want to retrieve

        Returns
        -------
        dict:
            dict of task data containing all initial data and annotation results in [Label Studio JSON format](https://labelstud.io/guide/tasks.html#Basic-Label-Studio-JSON-format)

        ```
        id: int
            Task ID
        predictions: dict
            Predictions object
        annotations: dict
            Annotations object
        drafts: dict
            Drafts object
        data: object
            User imported or uploaded data for a task. Data is formatted according to the project label config.
        meta: object
            Meta is user imported (uploaded) data and can be useful as input for an ML Backend for embeddings, advanced vectors, and other info. It is passed to ML during training/predicting steps.
            (Deprecated)
        created_at: str
            Date time string representing the time a task was created.
        updated_at: str
            Date time string representing the last time a task was updated.
        is_labeled: bool
            True if the number of annotations for this task is greater than or equal to the number of maximum_completions for the project.
        overlap: int
            Number of distinct annotators that processed the current task.
        project: int
            Project ID for this task
        file_upload: str
            Uploaded file used as data source for this task
        ```
        """
        response = self.make_request("GET", f"/api/tasks/{task_id}")
        return response.json()

    def update_task(self, task_id, **kwargs):
        """Update specific task by ID.

        Parameters
        ----------
        task_id: int
            Task ID you want to update
        kwargs: kwargs parameters
            List of parameters to update. Check all available parameters [here](https://labelstud.io/api#operation/api_tasks_partial_update)

        Returns
        -------
        dict:
            Dict with updated task

        """
        response = self.make_request("PATCH", f"/api/tasks/{task_id}", json=kwargs)
        response.raise_for_status()
        return response.json()

    def create_prediction(
        self,
        task_id: int,
        result: Optional[Union[List[Dict], Dict, str]] = None,
        score: Optional[float] = 0,
        model_version: Optional[str] = None,
    ):
        """Create a prediction for a specific task.

        Parameters
        ----------
        task_id: int
            Task ID
        result: list or dict or str
            Result in the <a href="https://labelstud.io/guide/export.html#Label-Studio-JSON-format-of-annotated-tasks">
            Label Studio JSON format as for annotations</a>.
            For the labeling config:

                <View>
                <Image name="image" value="$value"/>
                <Choices name="class_name" toName="image">
                    <Choice value="Class A"/>
                    <Choice value="Class B"/>
                </Choices>
                </View>

            The following inputs are equivalent, result could be either full `"predictions"`:

                [{
                    "from_name": "class_name",
                    "to_name": "image",
                    "type": "choices",
                    "value": {
                        "choices": ["Class A"]
                    }
                }]

            or just `"value"` payload

                {"choices": ["Class A"]}

            or just the class name:

                "Class A"

        score: float
            Model prediction score
        model_version: str
            Any string identifying your model
        """
        data = {"task": task_id, "result": result, "score": score}
        if model_version is not None:
            data["model_version"] = model_version
        response = self.make_request("POST", "/api/predictions", json=data)
        json = response.json()
        logger.debug(f"Response: {json}")
        return json

    def create_predictions(self, predictions):
        """Bulk create predictions for tasks. See <a href="https://labelstud.io/guide/predictions.html">more
        details about pre-annotated tasks</a>.

        Parameters
        ----------
        predictions: list of dicts
            List of dicts with predictions in the <a href="https://labelstud.io/guide/export.html#Label-Studio-JSON-format-of-annotated-tasks">
            Label Studio JSON format as for annotations</a>.
        """
        response = self.make_request(
            "POST", f"/api/projects/{self.id}/import/predictions", json=predictions
        )
        return response.json()

    def create_annotations_from_predictions(self, model_versions=None):
        """Create annotations from all predictions that exist for project tasks from specific ML model versions.

        Parameters
        ----------
        model_versions: list or None
            Convert predictions with these model versions to annotations. If `None`, all existing model versions are used

        Returns
        -------
        dict
            Dict with counter of created predictions

        """
        payload = {
            "filters": {"conjunction": "and", "items": []},
            "model_version": model_versions,
            "ordering": [],
            "project": self.id,
            "selectedItems": {"all": True, "excluded": []},
        }
        response = self.make_request(
            "POST",
            "/api/dm/actions",
            params={"id": "predictions_to_annotations", "project": self.id},
            json=payload,
        )
        return response.json()

    def list_annotations(self, task_id: int) -> List:
        """List all annotations for a task.

        Parameters
        ----------
        task_id: int
            Task ID

        Returns
        -------
        list of dict:
            List of annotations objects
        """
        response = self.make_request("GET", f"/api/tasks/{task_id}/annotations")
        response.raise_for_status()
        return response.json()

    def create_annotation(self, task_id: int, **kwargs) -> Dict:
        """Add annotations to a task like an annotator does.

        Parameters
        ----------
        task_id: int
            Task ID you want to update
        kwargs: kwargs parameters
            List of parameters to create. Check all available parameters [here](https://labelstud.io/api#operation/api_tasks_annotations_create).
            Labeling is stored in the `result` field as a list of dicionaries, [{...}, {...}, ...]

        Returns
        -------
        dict:
            Dict with created annotation

        """
        response = self.make_request(
            "POST", f"/api/tasks/{task_id}/annotations/", json=kwargs
        )
        response.raise_for_status()
        return response.json()

    def get_annotation(self, annotation_id: int) -> dict:
        """Retrieve a specific annotation for a task using the annotation ID.

        Parameters
        ----------
        annotation_id: int
            A unique integer value identifying this annotation.

        Returns
        ----------
        dict
            Retreived annotation object
        """
        response = self.make_request("GET", f"/api/annotations/{annotation_id}")
        response.raise_for_status()
        return response.json()

    def update_annotation(self, annotation_id, **kwargs):
        """Update specific annotation with new annotation parameters, e.g.
            ```
            project.update_annotation(annotation_id=123, ground_truth=True)
            ```

        Parameters
        ----------
        annotation_id: int
            Existing annotation ID from current project. Could be retrieved from `project.get_tasks()` response
        kwargs: kwargs parameters
            List of annotation parameters. Check all available parameters [here](https://labelstud.io/guide/export.html#Label-Studio-JSON-format-of-annotated-tasks)

        Returns
        -------
        dict
            Dict with updated annotation

        """
        response = self.make_request(
            "PATCH", f"/api/annotations/{annotation_id}", json=kwargs
        )
        response.raise_for_status()
        return response.json()

    def delete_annotation(self, annotation_id: int) -> int:
        """Delete an annotation using the annotation ID. This action can't be undone!

        Parameters
        ----------
        annotation_id: int
            A unique integer value identifying this annotation.

        Returns
        ----------
        int
            Status code for operation

        """
        response = self.make_request("DELETE", f"/api/annotations/{annotation_id}")
        response.raise_for_status()
        return response.status_code

    def get_predictions_coverage(self):
        """Prediction coverage stats for all model versions for the project.

        Returns
        -------
        dict
            Example:

                {
                    "2021-01-01": 0.9,
                     "2021-02-01": 0.7
                }

            `0.9` means that 90% of project tasks is covered by predictions with model_version `"2021-01-01"`

        """
        model_versions = self.get_model_versions()
        params = self.get_params()
        tasks_number = params["task_number"]
        coverage = {
            model_version: count / tasks_number
            for model_version, count in model_versions.items()
        }
        return coverage

    def get_predictions_conflict(self):
        raise NotImplementedError

    def get_predictions_precision(self):
        raise NotImplementedError

    def connect_google_import_storage(
        self,
        bucket: str,
        prefix: Optional[str] = None,
        regex_filter: Optional[str] = None,
        use_blob_urls: Optional[bool] = True,
        google_application_credentials: Optional[str] = None,
        presign: Optional[bool] = True,
        presign_ttl: Optional[int] = 1,
        title: Optional[str] = "",
        description: Optional[str] = "",
    ):
        """Connect a Google Cloud Storage (GCS) bucket to Label Studio to use as source storage and import tasks.

        Parameters
        ----------
        bucket: string
            Specify the name of the GCS bucket
        prefix: string
            Optional, specify the prefix or folder within the GCS bucket with your data
        regex_filter: string
            Optional, specify a regex filter to use to match the file types of your data
        use_blob_urls: bool
            Optional, true by default. Specify whether your data is raw image or video data, or JSON tasks.
        google_application_credentials: string
            Optional, provide a file with your Google application credentials. If not specified, it will use path stored in `GOOGLE_APPLICATION_CREDENTIALS` environmental variable. Read more about [Google Cloud authentication](https://cloud.google.com/docs/authentication/getting-started)
        presign: bool
            Optional, true by default. Specify whether or not to create presigned URLs.
        presign_ttl: int
            Optional, 1 by default. Specify how long to keep presigned URLs active.
        title: string
            Optional, specify a title for your GCS import storage that appears in Label Studio.
        description: string
            Optional, specify a description for your GCS import storage.

        Returns
        -------
        dict:
            containing the same fields as in the request and:

        id: int
            Storage ID
        type: str
            Type of storage
        created_at: str
            Creation time
        last_sync: str
            Time last sync finished, can be empty.
        last_sync_count: int
            Number of tasks synced in the last sync

        """
        if google_application_credentials and os.path.isfile(
            google_application_credentials
        ):
            with open(google_application_credentials) as f:
                google_application_credentials = f.read()

        payload = {
            "bucket": bucket,
            "project": self.id,
            "prefix": prefix,
            "regex_filter": regex_filter,
            "use_blob_urls": use_blob_urls,
            "google_application_credentials": google_application_credentials,
            "presign": presign,
            "presign_ttl": presign_ttl,
            "title": title,
            "description": description,
        }
        response = self.make_request("POST", "/api/storages/gcs", json=payload)
        return response.json()

    def connect_google_export_storage(
        self,
        bucket: str,
        prefix: Optional[str] = None,
        google_application_credentials: Optional[str] = None,
        title: Optional[str] = "",
        description: Optional[str] = "",
        can_delete_objects: bool = False,
    ):
        """Connect a Google Cloud Storage (GCS) bucket to Label Studio to use as target storage and export tasks.

        Parameters
        ----------
        bucket: string
            Specify the name of the GCS bucket
        prefix: string
            Optional, specify the prefix or folder within the GCS bucket to export your data to
        google_application_credentials: string
            Optional, provide a file with your Google application credentials. If not specified, it will use path stored in `GOOGLE_APPLICATION_CREDENTIALS` environmental variable. Read more about [Google Cloud authentication](https://cloud.google.com/docs/authentication/getting-started)
        title: string
            Optional, specify a title for your GCS export storage that appears in Label Studio.
        description: string
            Optional, specify a description for your GCS export storage.
        can_delete_objects: bool
            False by default. Specify whether to delete tasks in the GCS bucket if they are deleted in Label Studio.

        Returns
        -------
        dict:
            containing the same fields as in the request and:

        id: int
            Storage ID
        type: str
            Type of storage
        created_at: str
            Creation time
        last_sync: str
            Time last sync finished, can be empty.
        last_sync_count: int
            Number of tasks synced in the last sync

        """
        if os.path.isfile(google_application_credentials):
            with open(google_application_credentials) as f:
                google_application_credentials = f.read()

        payload = {
            "bucket": bucket,
            "prefix": prefix,
            "google_application_credentials": google_application_credentials,
            "title": title,
            "description": description,
            "can_delete_objects": can_delete_objects,
            "project": self.id,
        }
        response = self.make_request("POST", "/api/storages/export/gcs", json=payload)
        return response.json()

    def connect_s3_import_storage(
        self,
        bucket: str,
        prefix: Optional[str] = None,
        regex_filter: Optional[str] = None,
        use_blob_urls: Optional[bool] = True,
        presign: Optional[bool] = True,
        presign_ttl: Optional[int] = 1,
        title: Optional[str] = "",
        description: Optional[str] = "",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        region_name: Optional[str] = None,
        s3_endpoint: Optional[str] = None,
        recursive_scan: Optional[bool] = False,
    ):
        """Connect an Amazon S3 bucket to Label Studio to use as source storage and import tasks.

        Parameters
        ----------
        bucket: string
            Specify the name of the S3 bucket.
        prefix: string
            Optional, specify the prefix within the S3 bucket to import your data from.
        regex_filter: string
            Optional, specify a regex filter to use to match the file types of your data.
        use_blob_urls: bool
            Optional, true by default. Specify whether your data is raw image or video data, or JSON tasks.
        presign: bool
            Optional, true by default. Specify whether or not to create presigned URLs.
        presign_ttl: int
            Optional, 1 by default. Specify how long to keep presigned URLs active.
        title: string
            Optional, specify a title for your S3 import storage that appears in Label Studio.
        description: string
            Optional, specify a description for your S3 import storage.
        aws_access_key_id: string
            Optional, specify the access key ID for your bucket.
        aws_secret_access_key: string
            Optional, specify the secret access key for your bucket.
        aws_session_token: string
            Optional, specify a session token to use to access your bucket.
        region_name: string
            Optional, specify the AWS region of your S3 bucket.
        s3_endpoint: string
            Optional, specify an S3 endpoint URL to use to access your bucket instead of the standard access method.
        recursive_scan: bool
            Optional, specify whether to perform recursive scan over the bucket content.

        Returns
        -------
        dict:
            containing the same fields as in the request and:

        id: int
            Storage ID
        type: str
            Type of storage
        created_at: str
            Creation time
        last_sync: str
            Time last sync finished, can be empty.
        last_sync_count: int
            Number of tasks synced in the last sync
        """
        payload = {
            "bucket": bucket,
            "prefix": prefix,
            "regex_filter": regex_filter,
            "use_blob_urls": use_blob_urls,
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "aws_session_token": aws_session_token,
            "region_name": region_name,
            "s3_endpoint": s3_endpoint,
            "presign": presign,
            "presign_ttl": presign_ttl,
            "title": title,
            "description": description,
            "project": self.id,
            "recursive_scan": recursive_scan,
        }
        response = self.make_request("POST", "/api/storages/s3", json=payload)
        return response.json()

    def connect_s3s_iam_import_storage(
        self,
        role_arn: str,
        external_id: Optional[str] = None,
        bucket: Optional[str] = None,
        prefix: Optional[str] = None,
        regex_filter: Optional[str] = None,
        use_blob_urls: Optional[bool] = True,
        presign: Optional[bool] = True,
        presign_ttl: Optional[int] = 1,
        title: Optional[str] = "",
        description: Optional[str] = "",
        region_name: Optional[str] = None,
        s3_endpoint: Optional[str] = None,
        recursive_scan: Optional[bool] = False,
        aws_sse_kms_key_id: Optional[str] = None,
    ):
        """Create S3 secured import storage with IAM role access. Enterprise only.

        Parameters
        ----------
        role_arn: string
            Required, specify the AWS Role ARN to assume.
        external_id: string or None
            Optional, specify the external ID to use to assume the role. If None, SDK will call api/organizations/<id>
            and use external_id from the response. You can find this ID on the organization page in the Label Studio UI.
        bucket: string
            Specify the name of the S3 bucket.
        prefix: string
            Optional, specify the prefix within the S3 bucket to import your data from.
        regex_filter: string
            Optional, specify a regex filter to use to match the file types of your data.
        use_blob_urls: bool
            Optional, true by default. Specify whether your data is raw image or video data, or JSON tasks.
        presign: bool
            Optional, true by default. Specify whether or not to create presigned URLs.
        presign_ttl: int
            Optional, 1 by default. Specify how long to keep presigned URLs active.
        title: string
            Optional, specify a title for your S3 import storage that appears in Label Studio.
        description: string
            Optional, specify a description for your S3 import storage.
        region_name: string
            Optional, specify the AWS region of your S3 bucket.
        s3_endpoint: string
            Optional, specify an S3 endpoint URL to use to access your bucket instead of the standard access method.
        recursive_scan: bool
            Optional, specify whether to perform recursive scan over the bucket content.
        aws_sse_kms_key_id: string
            Optional, specify an AWS SSE KMS Key ID for server-side encryption.
        synchronizable, last_sync, last_sync_count, last_sync_job, status, traceback, meta:
            Parameters for synchronization details and storage status.

        Returns
        -------
        dict:
            containing the response from the API including storage ID and type, among other details.
        """
        if external_id is None:
            organization = self.get_organization()
            external_id = organization["external_id"]

        payload = {
            "bucket": bucket,
            "prefix": prefix,
            "regex_filter": regex_filter,
            "use_blob_urls": use_blob_urls,
            "presign": presign,
            "presign_ttl": presign_ttl,
            "title": title,
            "description": description,
            "recursive_scan": recursive_scan,
            "role_arn": role_arn,
            "region_name": region_name,
            "s3_endpoint": s3_endpoint,
            "aws_sse_kms_key_id": aws_sse_kms_key_id,
            "project": self.id,
            "external_id": external_id,
        }
        response = self.make_request("POST", "/api/storages/s3s/", json=payload)
        return response.json()

    def connect_s3_export_storage(
        self,
        bucket: str,
        prefix: Optional[str] = None,
        title: Optional[str] = "",
        description: Optional[str] = "",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        region_name: Optional[str] = None,
        s3_endpoint: Optional[str] = None,
        can_delete_objects: bool = False,
    ):
        """Connect an Amazon S3 bucket to Label Studio to use as target storage and export tasks.

        Parameters
        ----------
        bucket: string
            Specify the name of the S3 bucket.
        prefix: string
            Optional, specify the prefix or folder within the S3 bucket to export your data to.
        title: string
            Optional, specify a title for your S3 export storage that appears in Label Studio.
        description: string
            Optional, specify a description for your S3 export storage.
        aws_access_key_id: string
            Optional, specify the access key ID for your bucket.
        aws_secret_access_key: string
            Optional, specify the secret access key for your bucket.
        aws_session_token: string
            Optional, specify a session token to use to access your bucket.
        region_name: string
            Optional, specify the AWS region of your S3 bucket.
        s3_endpoint: string
            Optional, specify an S3 endpoint URL to use to access your bucket instead of the standard access method.
        can_delete_objects: bool
            False by default. Specify whether to delete tasks in the S3 bucket if they are deleted in Label Studio.

        Returns
        -------
        dict:
            containing the same fields as in the request and:

        id: int
            Storage ID
        type: str
            Type of storage
        created_at: str
            Creation time
        last_sync: str
            Time last sync finished, can be empty.
        last_sync_count: int
            Number of tasks synced in the last sync
        """

        payload = {
            "bucket": bucket,
            "prefix": prefix,
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "aws_session_token": aws_session_token,
            "region_name": region_name,
            "s3_endpoint": s3_endpoint,
            "title": title,
            "description": description,
            "can_delete_objects": can_delete_objects,
            "project": self.id,
        }
        response = self.make_request("POST", "/api/storages/export/s3", json=payload)
        return response.json()

    def connect_azure_import_storage(
        self,
        container: str,
        prefix: Optional[str] = None,
        regex_filter: Optional[str] = None,
        use_blob_urls: Optional[bool] = True,
        presign: Optional[bool] = True,
        presign_ttl: Optional[int] = 1,
        title: Optional[str] = "",
        description: Optional[str] = "",
        account_name: Optional[str] = None,
        account_key: Optional[str] = None,
    ):
        """Connect a Microsoft Azure BLOB storage container to Label Studio to use as source storage and import tasks.

        Parameters
        ----------
        container: string
            Specify the name of the Azure container.
        prefix: string
            Optional, specify the prefix or folder within the Azure container with your data.
        regex_filter: string
            Optional, specify a regex filter to use to match the file types of your data.
        use_blob_urls: bool
            Optional, true by default. Specify whether your data is raw image or video data, or JSON tasks.
        presign: bool
            Optional, true by default. Specify whether or not to create presigned URLs.
        presign_ttl: int
            Optional, 1 by default. Specify how long to keep presigned URLs active.
        title: string
            Optional, specify a title for your Azure import storage that appears in Label Studio.
        description: string
            Optional, specify a description for your Azure import storage.
        account_name: string
            Optional, specify the name of the account with access to the container.
        account_key: string
            Optional, specify the key for the account with access to the container.

        Returns
        -------
        dict:
            containing the same fields as in the request and:

        id: int
            Storage ID
        type: str
            Type of storage
        created_at: str
            Creation time
        last_sync: str
            Time last sync finished, can be empty.
        last_sync_count: int
            Number of tasks synced in the last sync
        """
        payload = {
            "container": container,
            "prefix": prefix,
            "regex_filter": regex_filter,
            "use_blob_urls": use_blob_urls,
            "account_name": account_name,
            "account_key": account_key,
            "presign": presign,
            "presign_ttl": presign_ttl,
            "title": title,
            "description": description,
            "project": self.id,
        }
        response = self.make_request("POST", "/api/storages/azure", json=payload)
        return response.json()

    def connect_azure_export_storage(
        self,
        container: str,
        prefix: Optional[str] = None,
        title: Optional[str] = "",
        description: Optional[str] = "",
        account_name: Optional[str] = None,
        account_key: Optional[str] = None,
        can_delete_objects: bool = False,
    ):
        """Connect Microsoft Azure BLOB storage to Label Studio to use as target storage and export tasks.

        Parameters
        ----------
        container: string
            Specify the name of the Azure storage container.
        prefix: string
            Optional, specify the prefix or folder within the Azure container to export your data to.
        title: string
            Optional, specify a title for your Azure export storage that appears in Label Studio.
        description: string
            Optional, specify a description for your Azure export storage.
        can_delete_objects: bool
            False by default. Specify whether to delete tasks in the Azure container if they are deleted in Label Studio.
        account_name: string
            Optional, specify the name of the account with access to the container.
        account_key: string
            Optional, specify the key for the account with access to the container.

        Returns
        -------
        dict:
            containing the same fields as in the request and:

        id: int
            Storage ID
        type: str
            Type of storage
        created_at: str
            Creation time
        last_sync: str
            Time last sync finished, can be empty.
        last_sync_count: int
            Number of tasks synced in the last sync
        """
        payload = {
            "container": container,
            "prefix": prefix,
            "account_name": account_name,
            "account_key": account_key,
            "title": title,
            "description": description,
            "can_delete_objects": can_delete_objects,
            "project": self.id,
        }
        response = self.make_request("POST", "/api/storages/export/azure", json=payload)
        return response.json()

    def connect_local_import_storage(
        self,
        local_store_path: [str],
        regex_filter: Optional[str] = None,
        use_blob_urls: Optional[bool] = True,
        title: Optional[str] = "",
        description: Optional[str] = "",
    ):
        """Connect a Local storage to Label Studio to use as source storage and import tasks.
        Parameters
        ----------
        local_store_path: string
            Path to declare as local storage.
        regex_filter: string
            Optional, specify a regex filter to use to match the file types of your data
        use_blob_urls: bool
            Optional, true by default. Specify whether your data is raw image or video data, or JSON tasks.
        title: string
            Optional, specify a title for your GCS import storage that appears in Label Studio.
        description: string
            Optional, specify a description for your GCS import storage.
        Returns
        -------
        dict:
            containing the same fields as in the request and:
        id: int
            Storage ID
        type: str
            Type of storage
        created_at: str
            Creation time
        last_sync: str
            Time last sync finished, can be empty.
        last_sync_count: int
            Number of tasks synced in the last sync
        """
        if "LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT" not in os.environ:
            raise ValueError(
                "To use connect_local_import_storage() you should set "
                "LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT environment variable, "
                "read more: https://labelstud.io/guide/storage.html#Prerequisites-2"
            )
        root = os.environ["LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT"]

        if not os.path.isdir(local_store_path):
            raise ValueError(f"{local_store_path} is not a directory")
        if (Path(root) in Path(local_store_path).parents) is False:
            raise ValueError(
                f"{str(Path(root))} is not presented in local_store_path parents: "
                f"{str(Path(local_store_path).parents)}"
            )

        payload = {
            "regex_filter": regex_filter,
            "use_blob_urls": use_blob_urls,
            "path": local_store_path,
            "presign": False,
            "presign_ttl": 1,
            "title": title,
            "description": description,
            "project": self.id,
        }
        response = self.make_request(
            "POST", f"/api/storages/localfiles?project={self.id}", json=payload
        )
        return response.json()

    def sync_import_storage(self, storage_type, storage_id):
        """Synchronize Import (Source) Cloud Storage.

        Parameters
        ----------
        storage_type: string
            Specify the type of the storage container. See ProjectStorage for available types.
        storage_id: int
            Specify the storage ID of the storage container. See get_import_storages() to get ids.

        Returns
        -------
        dict:
            containing the same fields as in the original storage request and:

        id: int
            Storage ID
        type: str
            Type of storage
        created_at: str
            Creation time
        last_sync: str
            Time last sync finished, can be empty.
        last_sync_count: int
            Number of tasks synced in the last sync
        """
        # originally syn was implemented in Client class, keep it for compatibility
        response = self.make_request(
            "POST", f"/api/storages/{storage_type}/{str(storage_id)}/sync"
        )
        return response.json()

    # write func for syn export storage
    def sync_export_storage(self, storage_type, storage_id):
        """Synchronize Export (Target) Cloud Storage.

        Parameters
        ----------
        storage_type: string
            Specify the type of the storage container. See ProjectStorage for available types.
        storage_id: int
            Specify the storage ID of the storage container. See get_export_storages() to get ids.

        Returns
        -------
        dict:
            containing the same fields as in the original storage request and:

        id: int
            Storage ID
        type: str
            Type of storage
        created_at: str
            Creation time
        other fields:
            See more https://api.labelstud.io/#tag/Storage:S3/operation/api_storages_export_s3_sync_create
        """
        response = self.make_request(
            "POST", f"/api/storages/export/{storage_type}/{str(storage_id)}/sync"
        )
        return response.json()

    # write code for get_import_storages()
    def get_import_storages(self):
        """Get Import (Source) Cloud Storage.

        Returns
        -------
        list of dicts:
            List of dicts with source storages, each dict consists of these fields:

        -------
        Each dict consists of these fields:

        id : int
            A unique integer value identifying this storage.
        type : str
            The type of the storage. Default is "s3".
        synchronizable : bool
            Indicates if the storage is synchronizable. Default is True.
        presign : bool
            Indicates if the storage is presign. Default is True.
        last_sync : str or None
            The last sync finished time. Can be None.
        last_sync_count : int or None
            The count of tasks synced last time. Can be None.
        last_sync_job : str or None
            The last sync job ID. Can be None.
        status : str
            The status of the storage. Can be one of "initialized", "queued", "in_progress", "failed", "completed".
        traceback : str or None
            The traceback report for the last failed sync. Can be None.
        meta : dict or None
            Meta and debug information about storage processes. Can be None.
        title : str or None
            The title of the cloud storage. Can be None.
        description : str or None
            The description of the cloud storage. Can be None.
        created_at : str
            The creation time of the storage.
        bucket : str or None
            The S3 bucket name. Can be None.
        prefix : str or None
            The S3 bucket prefix. Can be None.
        regex_filter : str or None
            The cloud storage regex for filtering objects. Can be None.
        use_blob_urls : bool
            Indicates if objects are interpreted as BLOBs and generate URLs.
        aws_access_key_id : str or None
            The AWS_ACCESS_KEY_ID. Can be None.
        aws_secret_access_key : str or None
            The AWS_SECRET_ACCESS_KEY. Can be None.
        aws_session_token : str or None
            The AWS_SESSION_TOKEN. Can be None.
        aws_sse_kms_key_id : str or None
            The AWS SSE KMS Key ID. Can be None.
        region_name : str or None
            The AWS Region. Can be None.
        s3_endpoint : str or None
            The S3 Endpoint. Can be None.
        presign_ttl : int
            The presigned URLs TTL (in minutes).
        recursive_scan : bool
            Indicates if a recursive scan over the bucket content is performed.
        glob_pattern : str or None
            The glob pattern for syncing from bucket. Can be None.
        synced : bool
            Flag indicating if the dataset has been previously synced or not.

        """
        response = self.make_request("GET", f"/api/storages/?project={self.id}")
        return response.json()

    def get_export_storages(self):
        """Get Export (Target) Cloud Storage.

        Returns
        -------
        list of dicts:
            List of dicts with target storages

        -------
        Each dict consists of these fields:

        id : int
            A unique integer value identifying this storage.
        type : str
            The type of the storage. Default is "s3".
        synchronizable : bool
            Indicates if the storage is synchronizable. Default is True.
        last_sync : str or None
            The last sync finished time. Can be None.
        last_sync_count : int or None
            The count of tasks synced last time. Can be None.
        last_sync_job : str or None
            The last sync job ID. Can be None.
        status : str
            The status of the storage. Can be one of "initialized", "queued", "in_progress", "failed", "completed".
        traceback : str or None
            The traceback report for the last failed sync. Can be None.
        meta : dict or None
            Meta and debug information about storage processes. Can be None.
        title : str or None
            The title of the cloud storage. Can be None.
        description : str or None
            The description of the cloud storage. Can be None.
        created_at : str
            The creation time of the storage.
        can_delete_objects : bool or None
            Deletion from storage enabled. Can be None.
        bucket : str or None
            The S3 bucket name. Can be None.
        prefix : str or None
            The S3 bucket prefix. Can be None.
        regex_filter : str or None
            The cloud storage regex for filtering objects. Can be None.
        use_blob_urls : bool
            Indicates if objects are interpreted as BLOBs and generate URLs.
        aws_access_key_id : str or None
            The AWS_ACCESS_KEY_ID. Can be None.
        aws_secret_access_key : str or None
            The AWS_SECRET_ACCESS_KEY. Can be None.
        aws_session_token : str or None
            The AWS_SESSION_TOKEN. Can be None.
        aws_sse_kms_key_id : str or None
            The AWS SSE KMS Key ID. Can be None.
        region_name : str or None
            The AWS Region. Can be None.
        s3_endpoint : str or None
            The S3 Endpoint. Can be None.
        project : int
            A unique integer value identifying this project.
        """
        response = self.make_request("GET", f"/api/storages/export?project={self.id}")
        return response.json()

    def _assign_by_sampling(
        self,
        users: List[int],
        assign_function: Callable,
        view_id: int = None,
        method: AssignmentSamplingMethod = AssignmentSamplingMethod.RANDOM,
        fraction: float = 1.0,
        overlap: int = 1,
    ):
        """
        Assigning tasks to Reviewers or Annotators by assign_function with method by fraction from view_id
        Parameters
        ----------
        users: List[int]
            users' IDs list
        assign_function: Callable
            Function to assign tasks by list of user IDs
        view_id: int
            Optional, view ID to filter tasks to assign
        method: AssignmentSamplingMethod
            Optional, Assignment method
        fraction: float
            Optional, expresses the size of dataset to be assigned
        overlap: int
            Optional, expresses the count of assignments for each task
        Returns
        -------
        list[dict]
            List of dicts with counter of created assignments
        """
        assert len(users) > 0, "Users list is empty."
        assert len(users) >= overlap, "Overlap is more than number of users."
        # check if users are int and not User objects
        if isinstance(users[0], int):
            # get users from project
            project_users = self.get_members()
            # User objects list
            users = [user for user in project_users if user.id in users]
        final_results = []
        # Get tasks to assign
        tasks = self.get_tasks(view_id=view_id, only_ids=True)
        assert len(tasks) > 0, "Tasks list is empty."
        # Choice fraction of tasks
        if fraction != 1.0:
            k = int(len(tasks) * fraction)
            tasks = sample(tasks, k)
        # prepare random list of tasks for overlap > 1
        if overlap > 1:
            shuffle(tasks)
            tasks = tasks * overlap
        # Check how many tasks for each user
        n_tasks = max(int(len(tasks) // len(users)), 1)
        # Assign each user tasks
        for user in users:
            # check if last chunk of tasks is less than average chunk
            if n_tasks > len(tasks):
                n_tasks = len(tasks)
            # check if last chunk of tasks is more than average chunk + 1
            # (covers rounding issue in line 1407)
            elif n_tasks + 1 == len(tasks) and n_tasks != 1:
                n_tasks = n_tasks + 1
            if method == AssignmentSamplingMethod.RANDOM and overlap == 1:
                sample_tasks = sample(tasks, n_tasks)
            elif method == AssignmentSamplingMethod.RANDOM and overlap > 1:
                sample_tasks = tasks[:n_tasks]
            else:
                raise ValueError(f"Sampling method {method} is not allowed")
            final_results.append(assign_function([user], sample_tasks))
            if overlap > 1:
                tasks = tasks[n_tasks:]
            else:
                tasks = list(set(tasks) - set(sample_tasks))
            if len(tasks) == 0:
                break
        # check if any tasks left
        if len(tasks) > 0:
            for user in users:
                if not tasks:
                    break
                task = tasks.pop()
                final_results.append(assign_function([user], [task]))
        return final_results

    def assign_reviewers_by_sampling(
        self,
        users: List[int],
        view_id: int = None,
        method: AssignmentSamplingMethod = AssignmentSamplingMethod.RANDOM,
        fraction: float = 1.0,
        overlap: int = 1,
    ):
        """
        Behaves similarly like `assign_reviewers()` but instead of specify tasks_ids explicitely,
        it gets users' IDs list and optional view ID and uniformly splits all tasks across reviewers
        Fraction expresses the size of dataset to be assigned
        Parameters
        ----------
        users: List[int]
            users' IDs list
        view_id: int
            Optional, view ID to filter tasks to assign
        method: AssignmentSamplingMethod
            Optional, Assignment method
        fraction: float
            Optional, expresses the size of dataset to be assigned
        overlap: int
            Optional, expresses the count of assignments for each task
        Returns
        -------
        list[dict]
            List of dicts with counter of created assignments
        """
        return self._assign_by_sampling(
            users=users,
            assign_function=self.assign_reviewers,
            view_id=view_id,
            method=method,
            fraction=fraction,
            overlap=overlap,
        )

    def assign_annotators_by_sampling(
        self,
        users: List[int],
        view_id: int = None,
        method: AssignmentSamplingMethod = AssignmentSamplingMethod.RANDOM,
        fraction: float = 1.0,
        overlap: int = 1,
    ):
        """
        Behaves similarly like `assign_annotators()` but instead of specify tasks_ids explicitly,
        it gets users' IDs list and optional view ID and splits all tasks across annotators.
        Fraction expresses the size of dataset to be assigned.
        Parameters
        ----------
        users: List[int]
            users' IDs list
        view_id: int
            Optional, view ID to filter tasks to assign
        method: AssignmentSamplingMethod
            Optional, Assignment method
        fraction: float
            Optional, expresses the size of dataset to be assigned
        overlap: int
            Optional, expresses the count of assignments for each task
        Returns
        -------
        list[dict]
            List of dicts with counter of created assignments
        """
        return self._assign_by_sampling(
            users=users,
            assign_function=self.assign_annotators,
            view_id=view_id,
            method=method,
            fraction=fraction,
            overlap=overlap,
        )

    def export_snapshot_list(self) -> list:
        """
        Get list of export snapshots for the current project
        -------
        Returns
        -------
        list[dict]
            List of dict with export snapshots with status:

        id: int
            Export ID
        created_at: str
            Creation time
        status: str
            Export status
        created_by: dict
            User data
        finished_at: str
            Finished time
        """
        response = self.make_request("GET", f"/api/projects/{self.id}/exports")
        return response.json()

    def export_snapshot_create(
        self,
        title: str,
        task_filter_options: dict = None,
        serialization_options_drafts: bool = True,
        serialization_options_predictions: bool = True,
        serialization_options_annotations__completed_by: bool = True,
        annotation_filter_options_usual: bool = True,
        annotation_filter_options_ground_truth: bool = True,
        annotation_filter_options_skipped: bool = True,
        interpolate_key_frames: bool = False,
    ) -> dict:
        """
        Create new export snapshot
        ----------
        Parameters
        ----------
        title: str
            Export title
        task_filter_options: dict
            Task filter options, use {"view": tab_id} to apply filter from this tab,
            <a href="https://api.labelstud.io/#operation/api_projects_exports_create">check the API parameters for more details</a>
        serialization_options_drafts: bool
            Expand drafts (False) or include only ID (True)
        serialization_options_predictions: bool
            Expand predictions (False) or include only ID (True)
        serialization_options_annotations__completed_by: bool
            Expand user that completed_by (False) or include only ID (True)
        annotation_filter_options_usual: bool
            Include not cancelled and not ground truth annotations
        annotation_filter_options_ground_truth: bool
            Filter ground truth annotations
        annotation_filter_options_skipped: bool
            Filter skipped annotations
        interpolate_key_frames: bool
            Interpolate key frames into sequence

        Returns
        -------
        dict:
            containing the same fields as in the request and the created export fields:
        id: int
            Export ID
        created_at: str
            Creation time
        status: str
            Export status
        created_by: dict
            User data
        finished_at: str
            Finished time

        """
        if task_filter_options is None:
            task_filter_options = {}

        payload = {
            "title": title,
            "serialization_options": {
                "drafts": {"only_id": serialization_options_drafts},
                "predictions": {"only_id": serialization_options_predictions},
                "annotations__completed_by": {
                    "only_id": serialization_options_annotations__completed_by
                },
                "interpolate_key_frames": interpolate_key_frames,
            },
            "task_filter_options": task_filter_options,
            "annotation_filter_options": {
                "usual": annotation_filter_options_usual,
                "ground_truth": annotation_filter_options_ground_truth,
                "skipped": annotation_filter_options_skipped,
            },
        }
        response = self.make_request(
            "POST",
            f"/api/projects/{self.id}/exports?interpolate_key_frames={interpolate_key_frames}",
            json=payload,
        )
        return response.json()

    def export(
        self,
        filters=None,
        title="SDK Export",
        export_type="JSON",
        output_dir=".",
        **kwargs,
    ):
        """
        Export tasks from the project with optional filters,
        and save the exported data to a specified directory.

        This method:
        (1) creates a temporary view with the specified filters if they are not None,
        (2) creates a new export snapshot using the view ID,
        (3) checks the status of the snapshot creation while it's in progress,
        (4) and downloads the snapshot file in the specified export format.
        (5) After the export, it cleans up and remove the temporary view.

        Parameters
        ----------
        filters : data_manager.Filters, dict, optional
            Filters to apply when exporting tasks.
            If provided, a temporary view is created with these filters.
            The format of the filters should match the Label Studio filter options.
            Default is None, which means all tasks are exported.
            Use label_studio_sdk.data_manager.Filters.create() to create filters,
            Example of the filters JSON format:
        ```json
        {
          "conjunction": "and",
          "items": [
            {
              "filter": "filter:tasks:id",
              "operator": "equal",
              "type": "Number",
              "value": 1
            }
          ]
        }
        ```
        titile : str, optional
            The title of the export snapshot. Default is 'SDK Export'.
        export_type : str, optional
            The format of the exported data. It should be one of the formats supported by Label Studio ('JSON', 'CSV', etc.). Default is 'JSON'.
        output_dir : str, optional
            The directory where the exported file will be saved. Default is the current directory.
        kwargs : kwargs, optional
            The same parameters as in the export_snapshot_create method.

        Returns
        -------
        dict
            containing the status of the export, the filename of the exported file, and the export ID.

        filename : str
            Path to the downloaded export file
        status : int
            200 is ok
        export_id : int
            Export ID, you can retrieve more details about this export using this ID
        """

        # Create a temporary view with the specified filters
        if filters:
            view = self.create_view(title="Temp SDK export", filters=filters)
            task_filter_options = {"view": view["id"]}
        else:
            task_filter_options = None
            view = None

        # Create a new export snapshot using the view ID
        export_result = self.export_snapshot_create(
            title=title,
            task_filter_options=task_filter_options,
            **kwargs,
        )

        # Check the status of the snapshot creation
        export_id = export_result["id"]
        while self.export_snapshot_status(export_id).is_in_progress():
            time.sleep(1.0)  # Wait until the snapshot is ready

        os.makedirs(output_dir, exist_ok=True)

        # Download the snapshot file once it's ready
        status, filename = self.export_snapshot_download(
            export_id, export_type=export_type, path=output_dir
        )

        # Clean up the view
        if view:
            self.delete_view(view["id"])
        return {"status": status, "filename": filename, "export_id": export_id}

    def export_snapshot_status(self, export_id: int) -> ExportSnapshotStatus:
        """
        Get export snapshot status by Export ID
        ----------
        Parameters
        ----------
        export_id: int
            Existing Export ID from current project. Can be referred as id from self.exports()

        Returns
        -------
        `label_studio_sdk.project.ExportSnapshotStatus`

        ExportSnapshotStatus.response is dict and contains the following fields:
        id: int
            Export ID
        created_at: str
            Creation time
        status: str
            created, completed, in_progress, failed
        created_by: dict
            User data
        finished_at: str
            Finished time
        """
        response = self.make_request(
            "GET", f"/api/projects/{self.id}/exports/{export_id}"
        )
        return ExportSnapshotStatus(response.json())

    def export_snapshot_download(
        self, export_id: int, export_type: str = "JSON", path: str = "."
    ) -> (int, str):
        """
        Download file with export snapshot in provided format
        ----------
        Parameters
        ----------
        export_id: int
            Existing Export ID from current project. Can be referred as id from self.exports()
        export_type: str
            Default export_type is JSON.
            Specify another format type as referenced in <a href="https://github.com/heartexlabs/label-studio-converter/blob/master/label_studio_converter/converter.py#L32">
            the Label Studio converter code</a>.
        path: str
            Default path to store downloaded files
        Returns
        -------
        Status code for operation and downloaded filename
        """
        response = self.make_request(
            "GET",
            f"/api/projects/{self.id}/exports/{export_id}/download?exportType={export_type}",
        )
        filename = None
        if response.status_code == 200:
            content_disposition = response.headers.get("Content-Disposition")
            if content_disposition:
                filename = content_disposition.split("filename=")[-1].strip("\"'")
                filename = os.path.basename(filename)
            else:
                raise LabelStudioException("No filename in response")
            with open(os.path.join(path, filename), "wb") as f:
                for chk in response:
                    f.write(chk)
        return response.status_code, filename

    def export_snapshot_delete(self, export_id: int) -> int:
        """Delete an export file by specified export ID

        Parameters
        ----------
        export_id: int
            Existing Export ID from current project

        Returns
        ----------
        Status code for operation
        """
        response = self.make_request(
            "DELETE", f"/api/projects/{self.id}/exports/{export_id}"
        )
        return response.status_code

    def get_files_from_tasks(self, tasks: Dict, get_tasks: bool = False):
        """Copy files from tasks to cache folder

        Parameters
        ----------
        tasks: Dict
        Tasks to download to local storage
        get_tasks: bool
        Get all tasks from current project

        Returns
        -------
        list
            List of filenames
        """
        if get_tasks:
            tasks = self.get_tasks()
        filenames = []
        if tasks:
            for task in tasks:
                for key in task["data"]:
                    try:
                        filename = get_local_path(
                            task["data"][key],
                            access_token=self.api_key,
                            hostname=self.url,
                        )
                        filenames.append(filename)
                    except (FileNotFoundError, InvalidSchema, MissingSchema, IOError):
                        logger.debug(f"Couldn't copy file {task['data'][key]}.")
        return filenames

    def delete_task(self, task_id: int) -> Response:
        """Delete a task. To remove multiple tasks `use delete_tasks()`.

        Parameters
        ----------
        task_id: int
            Task id.
        """
        assert isinstance(task_id, int), "task_id should be int"
        return self.make_request("DELETE", f"/api/tasks/{task_id}")

    def delete_tasks(self, task_ids: list) -> Response:
        """Delete multiple tasks by IDs.

        Parameters
        ----------
        task_ids: list of int
            Task ids.
        """
        assert isinstance(task_ids, list), "task_ids should be list of int"
        if not task_ids:  # avoid deletion of all tasks when task_ids = []
            return Response()
        payload = {
            "selectedItems": {"all": False, "included": task_ids},
            "project": self.id,
        }
        return self.make_request(
            "POST", f"/api/dm/actions?project={self.id}&id=delete_tasks", json=payload
        )

    def delete_all_tasks(self, excluded_ids: list = None) -> Response:
        """Delete all tasks from the project.

        Parameters
        ----------
        excluded_ids: list of int
            Task ids that should be excluded from the deletion.
        """
        assert (
            isinstance(excluded_ids, list) or excluded_ids is None
        ), "excluded_ids should be list of int or None"
        if excluded_ids is None:
            excluded_ids = []
        payload = {
            "selectedItems": {"all": True, "excluded": excluded_ids},
            "project": self.id,
        }
        return self.make_request(
            "POST", f"/api/dm/actions?project={self.id}&id=delete_tasks", json=payload
        )
