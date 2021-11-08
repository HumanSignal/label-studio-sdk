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

    @property
    def id(self):
        """ Get the project ID.

        Returns
        -------
        int
            Project ID
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
                "labels": ["Label1", "Label2", "Label3"] // taken from "alias" if it exists, else "value"
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
        """ Get all available project parameters.

        Returns
        -------
        dict
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
        """ Get all available project parameters and cache them.
        """
        self.params = self.get_params()

    def start_project(self, **kwargs):
        """ Create a labeling project in Label Studio.

        Raises LabelStudioException in case of errors.

        """
        response = self.make_request('POST', '/api/projects', json=kwargs)
        if response.status_code == 201:
            self.params = response.json()
        else:
            raise LabelStudioException('Project not created')

    @classmethod
    def get_from_id(cls, client, project_id) -> "Project":
        """ Class factory to create a project instance from project ID.

        Parameters
        ----------
        client: class Client
        project_id: int
            Project ID

        Returns
        -------
        class Project
        """
        project = cls(url=client.url, api_key=client.api_key, session=client.session)
        project.params['id'] = project_id
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
        page: int
            Page. Default is 1.
        page_size: int
            Page size. Default is -1, to retrieve all tasks in the project.
        only_ids: bool
            If true, return only task IDs

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
        """ Retrieve all tasks from the project. This call can be very slow if the project has a lot of tasks.
        """
        return self.get_tasks()

    def get_labeled_tasks(self, only_ids=False):
        """ Retrieve all tasks that have been completed, tasks where is_labeled=true.

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
        """ Retrieve all task IDs for completed tasks, tasks where is_labeled=True.

        Returns
        -------
        list
            List of task IDs
        """
        return self.get_labeled_tasks(only_ids=True)

    def get_unlabeled_tasks(self, only_ids=False):
        """ Retrieve all tasks that are <b>not</b> completed, tasks where is_labeled=False. If using Label Studio Enterprise,
        this can include tasks that have been labeled one or more times, but not the full number of times defined in the
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
        """ Retrieve all task IDs for tasks that are <b>not</b> completed, tasks where is_labeled=False. If using
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
        """ Create a prediction for a specific task.

        Parameters
        ----------
        task_id: int
            Task ID
        result: dict
            Result in the <a href="https://labelstud.io/guide/export.html#Label-Studio-JSON-format-of-annotated-tasks">
            Label Studio JSON format as for annotations</a>
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
        """ Bulk create predictions for tasks (Enterprise only).

        Parameters
        ----------
        predictions: list of dicts
            List of dicts with predictions
        """
        response = self.make_request('POST', f'/api/projects/{self.id}/import/predictions', json=predictions)
        return response.json()

    def create_annotations_from_predictions(self, model_versions=None):
        """ Create annotations from all predictions that exist for project tasks from a specific ML model version.

        Parameters
        ----------
        model_versions: string
            Convert predictions with this model_version to annotations.

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

    def get_predictions_coverage(self):
        """ Prediction coverage stats for all model versions for the project.

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
            Optional, provide a file with your Google application credentials.
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
        dict containing the same fields as in the request and:

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
            Optional, provide a file with your Google application credentials.
        title: string
            Optional, specify a title for your GCS export storage that appears in Label Studio.
        description: string
            Optional, specify a description for your GCS export storage.
        can_delete_objects: bool
            False by default. Specify whether to delete tasks in the GCS bucket if they are deleted in Label Studio.

        Returns
        -------
        dict containing the same fields as in the request and:

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
        dict containing the same fields as in the request and:

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
            Specify the name of the S3 bucket
        prefix: string
            Optional, specify the prefix or folder within the S3 bucket to export your data to
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
        can_delete_objects: bool
            False by default. Specify whether to delete tasks in the S3 bucket if they are deleted in Label Studio.

        Returns
        -------
        dict containing the same fields as in the request and:

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
