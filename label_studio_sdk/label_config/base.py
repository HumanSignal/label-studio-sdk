
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
        if (isinstance(tag_type, str) and self.tag != tag_type) or \
           (isinstance(tag_type, tuple) and self.tag not in tag_type):
            return False

        if name and self.name != name:
            return False

        if name_filter_fn and not name_filter_fn(self.name):
            return False

        if to_name and self.to_name != to_name:
            return False

        if to_name_filter_fn and not to_name_filter_fn(self.to_name):
            return False

        return True
