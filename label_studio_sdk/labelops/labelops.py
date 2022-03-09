import requests
import pandas as pd

from pydantic import BaseModel, validator
from typing import Any


class LabelOpsResult(BaseModel):
    conflict: float
    coverage: float
    predictions: Any
    stats: Any

    def view_predictions(self):
        return pd.DataFrame.from_records(self.predictions)

    def view_stats(self):
        return pd.DataFrame.from_records(self.stats)


class LabelOps(BaseModel):
    base_url = 'http://localhost:8000'
    api_key: str = None

    def _handle_errors(self, response):
        try:
            response.raise_for_status()
        except Exception as exc:
            print(f'Error response: {exc}, Content: {response.content}')
            return True

    def list_patterns(self):
        response = requests.get(f'{self.base_url}/api/patterns/', headers={'API_KEY': self.api_key})
        return response.json()

    def list(self):
        response = requests.get(f'{self.base_url}/api/labelops/', headers={'API_KEY': self.api_key})
        if not self._handle_errors(response):
            return response.json()

    def create(self, labelop):
        response = requests.post(f'{self.base_url}/api/labelops/', headers={'API_KEY': self.api_key}, json=labelop)
        if not self._handle_errors(response):
            return response.json()

    def get(self, id):
        response = requests.get(f'{self.base_url}/api/labelops/{id}/', headers={'API_KEY': self.api_key})
        if not self._handle_errors(response):
            return response.json()

    def delete(self, id):
        response = requests.delete(f'{self.base_url}/api/labelops/{id}/', headers={'API_KEY': self.api_key})
        self._handle_errors(response)

    def update(self, id, new_labelop):
        response = requests.patch(f'{self.base_url}/api/labelops/{id}/', headers={'API_KEY': self.api_key}, json=new_labelop)
        if not self._handle_errors(response):
            return response.json()

    def initialize_project(self, project_id):
        response = requests.post(f'{self.base_url}/api/project', headers={'API_KEY': self.api_key}, json={'project_id': project_id})
        if not self._handle_errors(response):
            return f'Project {project_id} has been successfully initialized!'


# class LabelOps(BaseModel):
#     base_url: str = 'http://stage-21.heartex.ai:9092'
#     api_key: str
#     project_id: int = None
#
#     def _handle_errors(self, response):
#         try:
#             response.raise_for_status()
#         except Exception as exc:
#             print(f'Error response: {exc}, Content: {response.content}')
#             return True
#
#     @validator('api_key')
#     def valid_api_key(cls, v, values, **kwargs):
#         response = requests.get(f'{values["base_url"]}', headers={'API_KEY': v})
#         response.raise_for_status()
#         return v
#
#     def initialize_project(self, project_id):
#         self.project_id = project_id
#         response = requests.get(f'{self.base_url}/{self.project_id}/process', headers={'API_KEY': self.api_key})
#         if not self._handle_errors(response):
#             return f'Project {self.project_id} has been successfully initialized!'
#
#     def check_project_status(self):
#         response = requests.get(f'{self.base_url}/{self.project_id}/status', headers={'API_KEY': self.api_key})
#         return response.content
#
#     def apply(self, parameters):
#         response = requests.post(f'{self.base_url}/{self.project_id}/labelops', json=parameters, headers={'API_KEY': self.api_key})
#         if not self._handle_errors(response):
#             return LabelOpsResult.parse_obj(response.json())
#
#     def commit(self, result, model_version):
#         response = requests.post(f'{self.base_url}/{self.project_id}/commit/{model_version}', json=result.dict(), headers={'API_KEY': self.api_key})
#         if not self._handle_errors(response):
#             return response.json()
