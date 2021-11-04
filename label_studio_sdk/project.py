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
    """ .. include::../docs/project_exceptions.md
    """
    pass


class ProjectSampling(Enum):
    """ Enumerate the available task sampling modes for labeling.
    """

    RANDOM = 'Uniform sampling'
    """ Uniform random sampling of tasks """
    SEQUENCE = 'Sequential sampling'
    """ Sequential sampling of tasks using task IDs """
    UNCERTAINTY = 'Uncertainty sampling'
    """ Sample tasks based on prediction scores, such as for active learning """


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

    @property
    def id(self):
        """ Get the project ID.

        Returns
        -------
        int

        """
        return self._get_param('id')

    @property
    def label_config(self):
        """ Get the labeling configuration for the project.

        Returns
        -------
        str
            Labeling configuration in XML format

        """
        return self._get_param('label_config')

    @property
    def parsed_label_config(self):
        """ Get the parsed labeling configuration for the project. You can use this version to more easily construct
        annotation or prediction results based on your labeling configuration.

        Returns
        -------
        dict
            Object and control tags from the project labeling config.
            Example with structured config of the form:
        ```
        {
            "<ControlTag>.name": {
                "type": "ControlTag",
                "to_name": ["<ObjectTag1>.name", "<ObjectTag2>.name"],
                "inputs: [
                    {"type": "ObjectTag1", "value": "<ObjectTag1>.value"},
                    {"type": "ObjectTag2", "value": "<ObjectTag2>.value"}
                ],
                "labels": ["Label1", "Label2", "Label3"] // taken from "alias" if it exists else "value"
        }
        ```

        """
        return parse_config(self.label_config)

    def _get_param(self, param_name):
        if param_name not in self.params:
            self.update_params()
            if param_name not in self.params:
                raise LabelStudioException(f'Project "{param_name}" field is not set')
        return self.params[param_name]

    def get_params(self):
        """ Get all parameters from the project info

        Returns
        -------
        dict
        """
        response = self.make_request('GET', f'/api/projects/{self.id}')
        return response.json()

    def get_model_versions(self):
        """ Get the list of ML model versions

        Returns
        -------
        list of strings
             Model versions

        """
        response = self.make_request('GET', f'/api/projects/{self.id}/model-versions')
        return response.json()

    def update_params(self):
        """ Get all project params and cache it
        """
        self.params = self.get_params()

    def start_project(self, **kwargs):
        """ Create a new project

        Raise LabelStudioException in case of errors

        """
        response = self.make_request('POST', '/api/projects', json=kwargs)
        if response.status_code == 201:
            self.params = response.json()
        else:
            raise LabelStudioException('Project not created')

    @classmethod
    def get_from_id(cls, client, project_id) -> "Project":
        """ Class factory to create Project instance from project ID

        Parameters
        ----------
        client: class Client
        project_id: project ID

        Returns
        -------
        class Project
        """
        project = cls(url=client.url, api_key=client.api_key, session=client.session)
        project.params['id'] = project_id
        project.update_params()
        return project

    def import_tasks(self, tasks, preannotated_from_fields: List = None):
        """ Import tasks

        Parameters
        ----------
        tasks: list of dicts | dict | path to file
            Tasks in <a href="https://labelstud.io/guide/tasks.html#Basic-Label-Studio-JSON-format">
            Label Studio Format</a>

        preannotated_from_fields: list of strings
            Turn flat task JSONs `{"column1": value, "column2": value}` into `{"data": {"column1"..}, "predictions": [{..."column2"}]`

        Returns
        -------
        list of int
            Imported task ids

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
        """ Simple export for tasks with annotations

        Parameters
        ----------
        export_type: string
            Format type as  <a href="https://github.com/heartexlabs/label-studio-converter/blob/master/label_studio_converter/converter.py#L32">
            in the converter</a>

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
        """ Low level function to set project parameters
        """
        response = self.make_request('PATCH', f'/api/projects/{self.id}', json=kwargs)
        assert response.status_code == 200

    def set_sampling(self, sampling: ProjectSampling):
        """ Set the project sampling for the labeling stream
        """
        self.set_params(sampling=sampling.value)

    def set_published(self, is_published: bool):
        """ Set project publishing state

        Parameters
        ----------
        is_published: bool
            Project publish state for reviewers and annotators

        """
        self.set_params(is_published=is_published)

    def set_model_version(self, model_version: str):
        """ Set active model version

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
        page: int = 1,
        page_size: int = -1,
        only_ids: bool = False,
    ):
        """ Get tasks slice based on filters, orders or view id specified

        Parameters
        ----------
        filters: dict
            JSON objects represents DataManager filters.
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
        ordering: list
            list with one string representing DataManager orderings. Example:
            ```["tasks:total_annotations"]```
        view_id: int
            Tab ID to retrieve filters, ordering and selected items
        selected_ids: list of ints
            Task IDs
        page: int
            Page (by default 1)
        page_size: int
            Page size (by default -1, means all tasks in the project)
        only_ids: bool
            Return IDs only

        Returns
        -------
        if page_size == -1 => list
            Task list with task data, annotations, predictions and other fields from the Data Manager

        if page_size > 0 => dict
            Example: ```{"tasks":[...], "total_annotations": 0, "total_predictions": 0, "total": 0}```

        tasks: list of dicts
            Tasks with task data, annotations, predictions and other fields from the Data Manager
        total: int
            Total number of tasks in filtered result
        total_annotations: int
            Total number of annotations in filtered tasks
        total_predictions: int
            Total number of predictions in filtered tasks

        """
        # TODO: implement filter-based tasks selection
        query = {
            'filters': filters,
            'ordering': ordering or [],
            'selectedItems': {'all': False, 'included': selected_ids} if selected_ids else {'all': True, "excluded": []}
        }
        response = self.make_request(
            'GET', '/api/dm/tasks', params={
                'project': {self.id},
                'only_ids': only_ids,
                'page': page,
                'page_size': page_size,
                'query': json.dumps(query)
            })

        data = response.json()
        tasks = data['tasks']
        if only_ids:
            data['tasks'] = [task['id'] for task in tasks]

        if page_size == -1:
            return data['tasks']
        else:
            return data

    @property
    def tasks(self):
        """ All tasks from project. This call can be very slow if the project has tons of tasks
        """
        return self.get_tasks()

    def get_labeled_tasks(self, only_ids=False):
        """ All tasks with finished state (is_labeled=True)

        Parameters
        ----------
        only_ids: bool
            Return IDs only

        Returns
        -------
        list
            List of task dicts (the same as for `get_tasks`)

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
        """ All task ids with finished state (is_labeled=True)

        Returns
        -------
        list
            List of task ids
        """
        return self.get_labeled_tasks(only_ids=True)

    def get_unlabeled_tasks(self, only_ids=False):
        """ All tasks with <b>not</b> finished state (is_labeled=False)

        Parameters
        ----------
        only_ids: bool
            Return IDs only

        Returns
        -------
        list
            List of task dicts (the same as for `get_tasks`)

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
        """ All task ids with <b>not</b> finished state (is_labeled=False)

        Returns
        -------
        list
            List of task ids
        """
        return self.get_unlabeled_tasks(only_ids=True)

    def get_task(self, task_id):
        """ Get specific task by ID

        Parameters
        ----------
        task_id: int
            Task ID you want to retrieve

        Returns
        -------
        dict

        """
        response = self.make_request('GET', f'/api/tasks/{task_id}')
        return response.json()

    def create_prediction(
        self,
        task_id: int,
        result: Optional[List[Dict]] = None,
        score: Optional[float] = 0,
        model_version: Optional[str] = None
    ):
        """ Create prediction for a specific task

        Parameters
        ----------
        task_id: int
            Task ID
        result: dict
            Result in the <a href="https://labelstud.io/guide/export.html#Label-Studio-JSON-format-of-annotated-tasks">
            Label Studio JSON format as for annotations</a>
        score: float
            Model score
        model_version: str
            Any string identifying your model
        """
        response = self.make_request('POST', '/api/predictions', json={
            'task': task_id, 'result': result, 'score': score, 'model_version': model_version
        })
        return response.json()

    def create_predictions(self, predictions):
        """ Bulk create predictions

        Parameters
        ----------
        predictions: list of dicts
            List of dicts with predictions
        """
        response = self.make_request('POST', f'/api/projects/{self.id}/import/predictions', json=predictions)
        return response.json()

    def create_annotations_from_predictions(self, model_version=None):
        """ Create annotation from all existing predictions

        Parameters
        ----------
        model_version: string
            Convert predictions with this model_version to annotations

        Returns
        -------
        dict
            Dict with counter of created predictions

        """
        payload = {
            'filters': {'conjunction': 'and', 'items': []},
            'model_version': model_version,
            'ordering': [],
            'project': self.id,
            'selectedItems': {'all': True, 'excluded': []}
        }
        response = self.make_request('POST', '/api/dm/actions', params={
            'id': 'predictions_to_annotations',
            'project': self.id
        }, json=payload)
        return response.json()

    def get_predictions_coverage(self):
        """ Prediction coverage per model version for the project

        Returns
        -------
        dict
            Example: {"2021-01-01": 0.9, "2021-02-01": 0.7},
            0.9 means that 90% of project tasks is covered by predictions with model_version "2021-01-01"

        """
        model_versions = self.get_model_versions()
        params = self.get_params()
        tasks_number = params['task_number']
        coverage = {model_version: count / tasks_number for model_version, count in model_versions.items()}
        return coverage

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
        if os.path.isfile(google_application_credentials):
            with open(google_application_credentials) as f:
                google_application_credentials = f.read()

        payload = {
            'bucket': bucket,
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
