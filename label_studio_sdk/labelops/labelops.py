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
    base_url: str = 'http://stage-21.heartex.ai:9092'
    api_key: str
    project_id: int = None

    @validator('api_key')
    def valid_api_key(cls, v, values, **kwargs):
        response = requests.get(f'{values["base_url"]}', headers={'API_KEY': v})
        response.raise_for_status()
        return v

    def initialize_project(self, project_id):
        self.project_id = project_id
        response = requests.get(f'{self.base_url}/{self.project_id}/process', headers={'API_KEY': self.api_key})
        return f'Project {self.project_id} has been successfully initialized!'

    def check_project_status(self):
        response = requests.get(f'{self.base_url}/{self.project_id}/status', headers={'API_KEY': self.api_key})
        return response.content

    def apply(self, parameters):
        response = requests.post(f'{self.base_url}/{self.project_id}/labelops', json=parameters, headers={'API_KEY': self.api_key})
        return LabelOpsResult.parse_obj(response.json())

    def commit(self, result, model_version):
        response = requests.post(f'{self.base_url}/{self.project_id}/commit/{model_version}', json=result.dict(), headers={'API_KEY': self.api_key})
        return response.json()
