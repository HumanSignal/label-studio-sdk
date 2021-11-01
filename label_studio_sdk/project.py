import os
import time
import json

from enum import Enum
from typing import Optional, Union, List, Dict
from .client import Client
from .utils import parse_config


class ProjectSampling(Enum):
    RANDOM = 'Uniform sampling'
    SEQUENCE = 'Sequential sampling'
    UNCERTAINTY = 'Uncertainty sampling'


class ProjectStorage(Enum):
    GOOGLE = 'gcs'
    S3 = 's3'
    AZURE = 'azure_blob'
    LOCAL = 'localfiles'
    REDIS = 'redis'
    S3_SECURED = 's3s'


class LabelStudioException(Exception):
    pass


class Project(Client):

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        self.params = {}

    @property
    def id(self):
        return self._get_param('id')

    @property
    def label_config(self):
        return self._get_param('label_config')

    @property
    def parsed_label_config(self):
        return parse_config(self.label_config)

    def _get_param(self, param_name):
        if param_name not in self.params:
            self.update_params()
            if param_name not in self.params:
                raise LabelStudioException(f'Project "{param_name}" field is not set')
        return self.params[param_name]

    def get_params(self):
        response = self.make_request('GET', f'/api/projects/{self.id}')
        return response.json()

    def get_model_versions(self):
        response = self.make_request('GET', f'/api/projects/{self.id}/model-versions')
        return response.json()

    def update_params(self):
        self.params = self.get_params()

    def start_project(self, **kwargs):
        """
        Start new project
        :param kwargs:
        :return:
        """
        response = self.make_request('POST', '/api/projects', json=kwargs)
        if response.status_code == 201:
            self.params = response.json()
        else:
            raise LabelStudioException('Project not created')

    @classmethod
    def get_from_id(cls, client, id) -> "Project":
        """Class factory to create Project instance from project ID"""
        project = cls(url=client.url, api_key=client.api_key, session=client.session)
        project.params['id'] = id
        project.update_params()
        return project

    def import_tasks(self, tasks, preannotated_from_fields: List = None):
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

    def set_options(self, **kwargs):
        """
        Low level function to set project options
        :param kwargs:
        :return:
        """
        response = self.make_request('PATCH', f'/api/projects/{self.id}', json=kwargs)
        assert response.status_code == 200

    def set_sampling(self, sampling: ProjectSampling):
        """
        Set project sampling
        :param sampling:
        :return:
        """
        self.set_options(sampling=sampling.value)

    def set_published(self, is_published: bool):
        """
        Set project publishing state
        :param is_published:
        :return:
        """
        self.set_options(is_published=is_published)

    def set_model_version(self, model_version: str):
        """
        Set active model version
        :param model_version: any string
        :return:
        """
        self.set_options(model_version=model_version)

    def get_tasks(
        self,
        filters=None,
        ordering=None,
        view_id=None,
        selected_ids=None,
        only_ids: bool = False
    ):
        """
        Get tasks slice based on filters, orders or view id specified
        :param filters: JSON objects represents DataManager filters
        :param order: JSON objects represents DataManager orderings
        :param view_id: existed View ID
        :param selected_ids:
        :param only_ids:
        :return:
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
                'page_size': None,          # TODO: disable pagination
                'query': json.dumps(query)
            })
        tasks = response.json()['tasks']
        if only_ids:
            return [task['id'] for task in tasks]
        return tasks

    @property
    def tasks(self):
        return self.get_tasks()

    def get_tasks_ids(
        self,
        filters: Optional[List[Dict]] = None,
        order: Optional[List[Dict]] = None,
        view_id: Optional[int] = None,
    ):
        """
        Returns tasks IDs, filtered and ordered according to the specified rules
        :param filters:
        :param order:
        :param view_id:
        :return:
        """
        return self.get_tasks(filters, order, view_id, only_ids=True)

    def get_labeled_tasks(self, only_ids=False):
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
        return self.get_labeled_tasks(only_ids=True)

    def get_unlabeled_tasks(self, only_ids=False):
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
        return self.get_unlabeled_tasks(only_ids=True)

    def get_task(self, task_id):
        response = self.make_request('GET', f'/api/tasks/{task_id}')
        return response.json()

    def create_prediction(
        self,
        task_id: int,
        result: Optional[List[Dict]] = None,
        score: Optional[float] = 0,
        model_version: Optional[str] = None
    ):
        """
        Create prediction for a specific task
        :param task_id: task ID
        :param result:
        :param score:
        :param model_version:
        :return:
        """
        response = self.make_request('POST', '/api/predictions', json={
            'task': task_id, 'result': result, 'score': score, 'model_version': model_version
        })
        return response.json()

    def create_predictions(self, predictions):
        response = self.make_request('POST', f'/api/projects/{self.id}/import/predictions', json=predictions)
        return response.json()

    def create_annotations_from_predictions(self, model_versions=None):
        model_versions = model_versions or []
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
