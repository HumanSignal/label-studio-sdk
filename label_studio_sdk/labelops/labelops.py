import requests

from pydantic import BaseModel


class LabelOps(BaseModel):
    project_id: int
    base_url: str = 'http://stage-21.heartex.ai:9092'
    api_key: str = None

    def initialize_project(self):
        response = requests.get(f'{self.base_url}/{self.project_id}/process')
        return response.json()

    def check_project_status(self):
        response = requests.get(f'{self.base_url}/{self.project_id}/status')
        return response.content

    def apply(self, parameters):
        response = requests.post(f'{self.base_url}/{self.project_id}/labelops', json=parameters)
        return response.json()

    def commit(self, result, model_version):
        response = requests.post(f'{self.base_url}/{self.project_id}/commit/{model_version}', json=result)
        return response.json()
