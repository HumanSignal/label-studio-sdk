from typing import Optional

from pydantic import BaseModel

from .client import Client
from .users import User


class Workspace(BaseModel):
    id: int
    title: str
    description: Optional[str] = ''
    color: str
    is_personal: bool
    created_by: int
    client: Client

    class Config:
        arbitrary_types_allowed = True

    def add_user(self, user: User):
        """Add user to workspace

        Parameters
        ----------
        user: label_studio_sdk.users.User
            User
        """
        response = self.client.make_request(
            "POST",
            f"/api/workspaces/{self.id}/memberships",
            json={"workspace": self.id, "user": user.id},
        )
        return response.json()

    def remove_user(self, user: User):
        """Remove user from workspace

        Parameters
        ----------
        user: label_studio_sdk.users.User
            User
        """
        response = self.client.make_request(
            "DELETE",
            f"/api/workspaces/{self.id}/memberships",
            json={"workspace": self.id, "user": user.id},
        )
        if response.status_code != 204:
            raise ValueError(str(response.content))

    def get_projects(self):
        """Get projects in current workspace

        Returns
        -------
        projects: list of label_studio_sdk.project.Project
            Project
        """
        from .project import Project

        final_results = []
        response = self.client.make_request(
            "GET", f"/api/workspaces/{self.id}/projects"
        )
        projects = response.json()
        for project_data in projects:
            project_id = project_data["id"]
            final_results.append(
                Project.get_from_id(
                    client=self.client,
                    project_id=project_id,
                )
            )
        return final_results
