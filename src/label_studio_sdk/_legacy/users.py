from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from .client import Client


class UserRole(Enum):
    ANNOTATOR = "AN"
    REVIEWER = "RE"
    MANAGER = "MA"
    ADMINISTRATOR = "AD"
    OWNER = "OW"
    NOT_ACTIVATED = "NO"
    DISABLED = "DI"


class OrgMembership(BaseModel):
    role: UserRole
    active: bool
    organization_id: int


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: str
    last_activity: datetime
    initials: str
    phone: str
    active_organization: Optional[int] = None
    org_membership: Optional[List[OrgMembership]] = Field(default_factory=list)
    client: Client

    class Config:
        arbitrary_types_allowed = True

    def set_role(self, role: UserRole):
        """Set user role in current active organization

        Parameters
        ----------
        role: label_studio_sdk.users.UserRole
            User role
        """
        response = self.client.make_request(
            "PATCH",
            f"/api/organizations/{self.active_organization}/memberships",
            json={"user_id": self.id, "role": role.value},
        )
        for membership in self.org_membership:
            if membership.organization_id == self.active_organization:
                membership.role = UserRole
        return response
