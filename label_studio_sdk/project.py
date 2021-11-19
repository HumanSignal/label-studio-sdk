""" .. include::../docs/project.md
"""
import os
import time
import json

from enum import Enum
from typing import Optional, Union, List, Dict
from .client import Client
from .utils import parse_config


class LabelStudioException(Exception):
    pass


class LabelStudioAttributeError(LabelStudioException):
    pass


class ProjectSampling(Enum):
    """ Enumerate the available task sampling modes for labeling.
    """

    RANDOM = 'Uniform sampling'
    """ Uniform random sampling of tasks """
    SEQUENCE = 'Sequential sampling'
    """ Sequential sampling of tasks using task IDs """
    UNCERTAINTY = 'Uncertainty sampling'
    """ Sample tasks based on prediction scores, such as for active learning (Enterprise only)"""


class ProjectStorage(Enum):
    """ Enumerate the available types of external source and target storage for labeling projects.
    """

    GOOGLE = 'gcs'
    """ Google Cloud Storage """
    S3 = 's3'
    """ Amazon S3 Storage """
    AZURE = 'azure_blob'
    """ Microsoft Azure Blob Storage """
    LOCAL = 'localfiles'
    """ Label Studio Local File Storage """
    REDIS = 'redis'
    """ Redis Storage """
    S3_SECURED = 's3s'
    """ Amazon S3 Storage secured by IAM roles (Enterprise only)"""


class Project(Client):

    def __init__(self, *args, **kwargs):
        """ Initialize project class.

        Parameters
        ----------

        """
        super(Project, self).__init__(*args, **kwargs)
        self.params = {}

    def __getattr__(self, item):
        return self._get_param(item)

    @property
    def parsed_label_config(self):
        """ Get the parsed labeling configuration for the project. You can use this to more easily construct
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

    def _get_param(self, param_name):
        if param_name not in self.params:
            self.update_params()
            if param_name not in self.params:
                raise LabelStudioAttributeError(f'Project "{param_name}" field is not set')
        return self.params[param_name]

    def get_params(self):
        """ Get all available project parameters.

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
        response = self.make_request('GET', f'/api/projects/{self.id}')
        return response.json()

    def get_model_versions(self):
        """ Get the list of available ML model versions from pre-annotations or connected ML backends.

        Returns
        -------
        list of strings
             Model versions

        """
        response = self.make_request('GET', f'/api/projects/{self.id}/model-versions')
        return response.json()

    def update_params(self):
        """ Get [all available project parameters](#label_studio_sdk.project.Project.get_params) and cache them.
        """
        self.params = self.get_params()

    def start_project(self, **kwargs):
        """ Create a new labeling project in Label Studio.

        Raises LabelStudioException in case of errors.

        """
        response = self.make_request('POST', '/api/projects', json=kwargs)
        if response.status_code == 201:
            self.params = response.json()
        else:
            raise LabelStudioException('Project not created')

    @classmethod
    def _create_from_id(cls, client, project_id, params=None):
        project = cls(url=client.url, api_key=client.api_key, session=client.session)
        if params and isinstance(params, dict):
            # TODO: validate project parameters
            project.params = params
        project.params['id'] = project_id
        return project

    @classmethod
    def get_from_id(cls, client, project_id) -> "Project":
        """ Class factory to create a project instance from an existing project ID.

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
        """ Import JSON-formatted labeling tasks. Tasks can be unlabeled or contain predictions.

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
        params = {'return_task_ids': '1'}
        if preannotated_from_fields:
            params['preannotated_from_fields'] = ','.join(preannotated_from_fields)
        if isinstance(tasks, (list, dict)):
            response = self.make_request(
                method='POST',
                url=f'/api/projects/{self.id}/import',
                json=tasks,
                params=params
            )
        elif isinstance(tasks, str):
            # try import from file
            if not os.path.isfile(tasks):
                raise LabelStudioException(f'Not found import tasks file {tasks}')
            with open(tasks, mode='rb') as f:
                response = self.make_request(
                    method='POST',
                    url=f'/api/projects/{self.id}/import',
                    files={'file': f},
                    params=params
                )
        return response.json()['task_ids']

    def export_tasks(self, export_type='JSON'):
        """ Export annotated tasks.

        Parameters
        ----------
        export_type: string
            Default export_type is JSON.
            Specify another format type as referenced in <a href="https://github.com/heartexlabs/label-studio-converter/blob/master/label_studio_converter/converter.py#L32">
            the Label Studio converter code</a>.

        Returns
        -------
        list of dicts
            Tasks with annotations

        """
        response = self.make_request(
            method='POST',
            url=f'/api/projects/{self.id}/export?exportType={export_type}'
        )
        return response.json()

    def set_params(self, **kwargs):
        """ Low level function to set project parameters.
        """
        response = self.make_request('PATCH', f'/api/projects/{self.id}', json=kwargs)
        assert response.status_code == 200

    def set_sampling(self, sampling: ProjectSampling):
        """ Set the project sampling method for the labeling stream.
        """
        self.set_params(sampling=sampling.value)

    def set_published(self, is_published: bool):
        """ Set the project publication state. (Enterprise only)

        Parameters
        ----------
        is_published: bool
            Project publication state for reviewers and annotators

        """
        self.set_params(is_published=is_published)

    def set_model_version(self, model_version: str):
        """ Set the current model version to use for displaying predictions to annotators, perform uncertainty sampling
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
        """ Retrieve a subset of tasks from the Data Manager based on a filter, ordering mechanism, or a
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
            ```[Column.total_annotations]```
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
        data = self.get_paginated_tasks(
            filters=filters,
            ordering=ordering,
            view_id=view_id,
            selected_ids=selected_ids,
            only_ids=only_ids,
            page=1,
            page_size=-1
        )
        return data['tasks']

    def get_paginated_tasks(
        self,
        filters=None,
        ordering=None,
        view_id=None,
        selected_ids=None,
        page: int = 1,
        page_size: int = -1,
        only_ids: bool = False,
    ):
        """ Retrieve a subset of tasks from the Data Manager based on a filter, ordering mechanism, or a
        predefined view ID.

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
            ```[Column.total_annotations]```
        view_id: int
            View ID, visible as a Data Manager tab, for which to retrieve filters, ordering, and selected items
        selected_ids: list of ints
            Task IDs
        page: int
            Page. Default is 1.
        page_size: int
            Page size. Default is -1, to retrieve all tasks in the project.
        only_ids: bool
            If true, return only task IDs

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
            'filters': filters,
            'ordering': ordering or [],
            'selectedItems': {'all': False, 'included': selected_ids} if selected_ids else {'all': True, "excluded": []}
        }
        params={
            'project': self.id,
            'page': page,
            'page_size': page_size,
            'view': view_id,
            'query': json.dumps(query),
            'fields': 'all'
        }
        if only_ids:
            params['include'] = 'id'

        response = self.make_request(
            'GET', '/api/dm/tasks', params)

        data = response.json()
        tasks = data['tasks']
        if only_ids:
            data['tasks'] = [task['id'] for task in tasks]

        return data

    def get_tasks_ids(self, *args, **kwargs):
        """Same as `label_studio_sdk.project.Project.get_tasks()` but returns only task IDs.
        """
        kwargs['only_ids'] = True
        return self.get_tasks(*args, **kwargs)

    def get_paginated_tasks_ids(self, *args, **kwargs):
        """Same as `label_studio_sdk.project.Project.get_paginated_tasks()` but returns
           only task IDs.
        """
        kwargs['only_ids'] = True
        return self.get_paginated_tasks(*args, **kwargs)

    @property
    def tasks(self):
        """ Retrieve all tasks from the project. This call can be very slow if the project has a lot of tasks.
        """
        return self.get_tasks()

    @property
    def tasks_ids(self):
        """ IDs for all tasks for a project. This call can be very slow if the project has lots of tasks.
        """
        return self.get_tasks_ids()

    def get_labeled_tasks(self, only_ids=False):
        """ Retrieve all tasks that have been completed, i.e. where requested number of annotations have been created

        Parameters
        ----------
        only_ids: bool
            Return only task IDs.

        Returns
        -------
        list
            List of task dicts, the same as in `get_tasks`.

        """
        return self.get_tasks(filters={
            'conjunction': 'and',
            'items': [{
                'filter': 'filter:tasks:completed_at',
                'operator': 'empty',
                'value': False,
                'type': 'Datetime'
            }]
        }, only_ids=only_ids)

    def get_labeled_tasks_ids(self):
        """ Retrieve all task IDs for completed tasks, i.e. where requested number of annotations have been created

        Returns
        -------
        list
            List of task IDs
        """
        return self.get_labeled_tasks(only_ids=True)

    def get_unlabeled_tasks(self, only_ids=False):
        """ Retrieve all tasks that are <b>not</b> completed.
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
        return self.get_tasks(filters={
            'conjunction': 'and',
            'items': [{
                'filter': 'filter:tasks:completed_at',
                'operator': 'empty',
                'value': True,
                'type': 'Datetime'
            }]
        }, only_ids=only_ids)

    def get_unlabeled_tasks_ids(self):
        """ Retrieve all task IDs for tasks that are <b>not</b> completed. If using
        Label Studio Enterprise, this can include tasks that have been labeled one or more times, but not the full
        number of times defined in the project labeling settings.

        Returns
        -------
        list
            List of task IDs
        """
        return self.get_unlabeled_tasks(only_ids=True)

    def get_task(self, task_id):
        """ Get specific task by ID.

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
        response = self.make_request('GET', f'/api/tasks/{task_id}')
        return response.json()

    def create_prediction(
        self,
        task_id: int,
        result: Optional[Union[List[Dict], Dict, str]] = None,
        score: Optional[float] = 0,
        model_version: Optional[str] = None
    ):
        """ Create a prediction for a specific task.

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
        response = self.make_request('POST', '/api/predictions', json={
            'task': task_id, 'result': result, 'score': score, 'model_version': model_version
        })
        return response.json()

    def create_predictions(self, predictions):
        """ Bulk create predictions for tasks. See <a href="https://labelstud.io/guide/predictions.html">more
        details about pre-annotated tasks</a>.

        Parameters
        ----------
        predictions: list of dicts
            List of dicts with predictions in the <a href="https://labelstud.io/guide/export.html#Label-Studio-JSON-format-of-annotated-tasks">
            Label Studio JSON format as for annotations</a>.
        """
        response = self.make_request('POST', f'/api/projects/{self.id}/import/predictions', json=predictions)
        return response.json()

    def create_annotations_from_predictions(self, model_versions=None):
        """ Create annotations from all predictions that exist for project tasks from specific ML model versions.

        Parameters
        ----------
        model_versions: list or None
            Convert predictions with these model versions to annotations. If `None`, all existed model versions are used

        Returns
        -------
        dict
            Dict with counter of created predictions

        """
        payload = {
            'filters': {'conjunction': 'and', 'items': []},
            'model_version': model_versions,
            'ordering': [],
            'project': self.id,
            'selectedItems': {'all': True, 'excluded': []}
        }
        response = self.make_request('POST', '/api/dm/actions', params={
            'id': 'predictions_to_annotations',
            'project': self.id
        }, json=payload)
        return response.json()

    def update_annotation(self, annotation_id, **kwargs):
        """ Update specific annotation with new annotation parameters, e.g.
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
        response = self.make_request('PATCH', f'/api/annotations/{annotation_id}', json=kwargs)
        response.raise_for_status()
        return response.json()

    def get_predictions_coverage(self):
        """ Prediction coverage stats for all model versions for the project.

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
        tasks_number = params['task_number']
        coverage = {model_version: count / tasks_number for model_version, count in model_versions.items()}
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
            title: Optional[str] = '',
            description: Optional[str] = ''
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
        if os.path.isfile(google_application_credentials):
            with open(google_application_credentials) as f:
                google_application_credentials = f.read()

        payload = {
            'bucket': bucket,
            'project': self.id,
            'prefix': prefix,
            'regex_filter': regex_filter,
            'use_blob_urls': use_blob_urls,
            'google_application_credentials': google_application_credentials,
            'presign': presign,
            'presign_ttl': presign_ttl,
            'title': title,
            'description': description
        }
        response = self.make_request('POST', '/api/storages/gcs', json=payload)
        return response.json()

    def connect_google_export_storage(
            self,
            bucket: str,
            prefix: Optional[str] = None,
            google_application_credentials: Optional[str] = None,
            title: Optional[str] = '',
            description: Optional[str] = '',
            can_delete_objects: bool = False
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
            'bucket': bucket,
            'prefix': prefix,
            'google_application_credentials': google_application_credentials,
            'title': title,
            'description': description,
            'can_delete_objects': can_delete_objects
        }
        response = self.make_request('POST', '/api/storages/gcs/export', json=payload)
        return response.json()

    def connect_s3_import_storage(
            self,
            bucket: str,
            prefix: Optional[str] = None,
            regex_filter: Optional[str] = None,
            use_blob_urls: Optional[bool] = True,
            presign: Optional[bool] = True,
            presign_ttl: Optional[int] = 1,
            title: Optional[str] = '',
            description: Optional[str] = '',
            aws_access_key_id: Optional[str] = None,
            aws_secret_access_key: Optional[str] = None,
            aws_session_token: Optional[str] = None,
            region_name: Optional[str] = None,
            s3_endpoint: Optional[str] = None
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
            'bucket': bucket,
            'prefix': prefix,
            'regex_filter': regex_filter,
            'use_blob_urls': use_blob_urls,
            'aws_access_key_id': aws_access_key_id,
            'aws_secret_access_key': aws_secret_access_key,
            'aws_session_token': aws_session_token,
            'region_name': region_name,
            's3_endpoint': s3_endpoint,
            'presign': presign,
            'presign_ttl': presign_ttl,
            'title': title,
            'description': description
        }
        response = self.make_request('POST', '/api/storages/s3', json=payload)
        return response.json()

    def connect_s3_export_storage(
            self,
            bucket: str,
            prefix: Optional[str] = None,
            title: Optional[str] = '',
            description: Optional[str] = '',
            aws_access_key_id: Optional[str] = None,
            aws_secret_access_key: Optional[str] = None,
            aws_session_token: Optional[str] = None,
            region_name: Optional[str] = None,
            s3_endpoint: Optional[str] = None,
            can_delete_objects: bool = False
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
            'bucket': bucket,
            'prefix': prefix,
            'aws_access_key_id': aws_access_key_id,
            'aws_secret_access_key': aws_secret_access_key,
            'aws_session_token': aws_session_token,
            'region_name': region_name,
            's3_endpoint': s3_endpoint,
            'title': title,
            'description': description,
            'can_delete_objects': can_delete_objects
        }
        response = self.make_request('POST', '/api/storages/s3/export', json=payload)
        return response.json()

    def connect_azure_import_storage(
            self,
            container: str,
            prefix: Optional[str] = None,
            regex_filter: Optional[str] = None,
            use_blob_urls: Optional[bool] = True,
            presign: Optional[bool] = True,
            presign_ttl: Optional[int] = 1,
            title: Optional[str] = '',
            description: Optional[str] = '',
            account_name: Optional[str] = None,
            account_key: Optional[str] = None
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
            'container': container,
            'prefix': prefix,
            'regex_filter': regex_filter,
            'use_blob_urls': use_blob_urls,
            'account_name': account_name,
            'account_key': account_key,
            'presign': presign,
            'presign_ttl': presign_ttl,
            'title': title,
            'description': description
        }
        response = self.make_request('POST', '/api/storages/azure', json=payload)
        return response.json()

    def connect_azure_export_storage(
            self,
            container: str,
            prefix: Optional[str] = None,
            title: Optional[str] = '',
            description: Optional[str] = '',
            account_name: Optional[str] = None,
            account_key: Optional[str] = None,
            can_delete_objects: bool = False
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
            'container': container,
            'prefix': prefix,
            'account_name': account_name,
            'account_key': account_key,
            'title': title,
            'description': description,
            'can_delete_objects': can_delete_objects
        }
        response = self.make_request('POST', '/api/storages/azure/export', json=payload)
        return response.json()
