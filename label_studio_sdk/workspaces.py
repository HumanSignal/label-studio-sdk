from pydantic import BaseModel
from typing import List, Optional
from .users import User
from .client import Client


class Workspace(BaseModel):
    id: int
    title: str
    description: Optional[str]
    color: str
    is_personal: bool
    created_by: int
    client: Client

    class Config:
        arbitrary_types_allowed = True

    def add_user(self, user: User):
        """ Add user to workspace

        Parameters
        ----------
        user: label_studio_sdk.users.User
            User
        """
        response = self.client.make_request(
            'POST', f'/api/workspaces/{self.id}/memberships',
            json={'workspace': self.id, 'user': user.id})
        return response.json()

    def remove_user(self, user: User):
        """ Remove user from workspace

        Parameters
        ----------
        user: label_studio_sdk.users.User
            User
        """
        response = self.client.make_request(
            'DELETE', f'/api/workspaces/{self.id}/memberships',
            json={'workspace': self.id, 'user': user.id})
        if response.status_code != 204:
            raise ValueError(str(response.content))
