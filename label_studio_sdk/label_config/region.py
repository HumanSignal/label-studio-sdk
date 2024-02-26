"""
"""
import json
from uuid import uuid4

from typing import Dict, Optional, List, Tuple, Any
from pydantic import BaseModel


class Region(BaseModel):
    """
    """
    id: str = str(uuid4())
    from_tag: Any
    to_tag: Any
    value: Any

    def _dict(self):
        """
        """
        value = self.value
        
        return {
            "id": self.id,
            "from_name": self.from_tag.name,
            "to_name": self.to_tag.name,
            "type": self.from_tag.tag.lower(),
            # TODO This needs to be improved
            "value": value.dict()
        }
    
    def as_json(self):
        """
        """
        return json.dumps(self._dict())
