import datetime

from pydantic import BaseModel
from typing import Optional
from .client import Client
from .errors import LabelStudioValidationError


class Label(BaseModel):
    id: int
    created_by: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    value: dict
    label_config_tags: Optional[list]
    title: str
    description: Optional[str]
    indexed_tags: Optional[list]
    approved: Optional[bool]
    approved_by: Optional[int]
    client: Optional[Client]

    class Config:
        arbitrary_types_allowed = True

    def update(self, *args, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise LabelStudioValidationError(f'{k} attribute not found in label {self}')
        self.client.make_request('PATCH', f'/api/labels/{self.id}', json=kwargs)

    def delete(self):
        self.client.make_request('DELETE', f'/api/labels/{self.id}')


class LabelLink(BaseModel):
    id: int
    label: Label
    from_name: str
    project: int
    client: Client

    class Config:
        arbitrary_types_allowed = True
