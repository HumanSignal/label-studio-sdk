
from pydantic import BaseModel
from typing import Dict, Optional, List, Tuple, Any, Callable


class LabelStudioTag(BaseModel):
    """
    Base class for a LabelStudio Tag
    """
    attr: Optional[Dict]
    tag: Optional[str]
        
    def match(self,
              tag_type: str,
              name: Optional[str] = None,
              name_filter_fn: Optional[Callable] = None,
              to_name: Optional[str] = None,
              to_name_filter_fn: Optional[Callable] = None) -> bool:
        """
        """
        if isinstance(tag_type, str):
            tag_type = tag_type.lower()
        elif isinstance(tag_type, tuple):
            tag_type = tuple(t.lower() for t in tag_type)

        if name:
            name = name.lower()

        if to_name:
            to_name = to_name.lower()

        if (isinstance(tag_type, str) and self.tag.lower() != tag_type) or \
           (isinstance(tag_type, tuple) and self.tag.lower() not in tag_type):
            return False

        if name and self.name.lower() != name:
            return False

        if name_filter_fn and not name_filter_fn(self.name.lower()):
            return False

        if to_name and self.to_name.lower() != to_name:
            return False

        if to_name_filter_fn and not to_name_filter_fn(self.name.lower()):
            return False

        return True
