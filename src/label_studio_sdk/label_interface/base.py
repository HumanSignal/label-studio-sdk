from pydantic import BaseModel
from typing import Dict, Optional, List, Tuple, Any, Callable


def get_tag_class(name, default_mapping, re_mapping=None):
    """ """
    lc_name = name.lower()
    if re_mapping and lc_name in re_mapping:
        return re_mapping.get(lc_name)
    else:
        class_name = default_mapping.get(name.lower())
        return class_name


class LabelStudioTag(BaseModel):
    """
    Base class for a LabelStudio Tag

    Attributes:
    -----------
    attr: Optional[Dict]
        A dictionary of attributes for the tag
    tag: Optional[str]
        The tag name
    """

    attr: Optional[Dict] = {}
    tag: Optional[str] = ""

    def match(
        self,
        tag_type: str,
        name: Optional[str] = None,
        name_filter_fn: Optional[Callable] = None,
        to_name: Optional[str] = None,
        to_name_filter_fn: Optional[Callable] = None,
    ) -> bool:
        """
        This method checks if the current instance of LabelStudioTag matches the provided parameters.

        Parameters:
        -----------
        tag_type : str
            The type of the tag to match. It can be a string or a tuple of strings.
        name : Optional[str]
            The name of the tag to match. If provided, it should match the name of the current instance.
        name_filter_fn : Optional[Callable]
            A function to filter the name of the tag. If provided, the function should return True for a match.
        to_name : Optional[str]
            The 'to_name' attribute of the tag to match. If provided, it should match the 'to_name' of the current instance.
        to_name_filter_fn : Optional[Callable]
            A function to filter the 'to_name' of the tag. If provided, the function should return True for a match.

        Returns:
        --------
        bool
            True if the current instance matches the provided parameters, False otherwise.
        """
        if isinstance(tag_type, str):
            tag_type = tag_type.lower()
        elif isinstance(tag_type, tuple):
            tag_type = tuple(t.lower() for t in tag_type)

        if name:
            name = name.lower()

        if to_name:
            to_name = to_name.lower()

        if (isinstance(tag_type, str) and self.tag.lower() != tag_type) or (
            isinstance(tag_type, tuple) and self.tag.lower() not in tag_type
        ):
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
