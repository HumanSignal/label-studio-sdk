import requests

from pydantic import BaseModel, validator


class LabelOps(BaseModel):
    project_id: int
    base_url: str = 'http://stage-21.heartex.ai:9092'
    api_key: str = ''

    @validator('api_key')
    def valid_api_key(cls, v, values, **kwargs):
        response = requests.get(f'{values["base_url"]}', headers={'API_KEY': v})
        response.raise_for_status()
        return v

    def initialize_project(self):
        response = requests.get(f'{self.base_url}/{self.project_id}/process', headers={'API_KEY': self.api_key})
        return response.json()

    def check_project_status(self):
        response = requests.get(f'{self.base_url}/{self.project_id}/status', headers={'API_KEY': self.api_key})
        return response.content

    def apply(self, parameters):
        response = requests.post(f'{self.base_url}/{self.project_id}/labelops', json=parameters, headers={'API_KEY': self.api_key})
        return response.json()

    def commit(self, result, model_version):
        response = requests.post(f'{self.base_url}/{self.project_id}/commit/{model_version}', json=result, headers={'API_KEY': self.api_key})
        return response.json()
