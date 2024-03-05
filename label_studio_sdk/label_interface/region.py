"""
"""
import json
from uuid import uuid4

from typing import Any
from pydantic import BaseModel, Field


class Region(BaseModel):
    """
    Class for Region Tag

    Attributes:
    -----------
    id: str
        The unique identifier of the region
    x: int
        The x coordinate of the region
    y: int

    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    from_tag: Any
    to_tag: Any
    value: Any

    def _dict(self):
        """
        """
        return {
            "id": self.id,
            "from_name": self.from_tag.name,
            "to_name": self.to_tag.name,
            "type": self.from_tag.tag.lower(),
            # TODO This needs to be improved
            "value": self.value.dict()
        }