"""
"""
from typing import Dict, Optional, List, Tuple, Any
from .base import LabelStudioTag
from .region import Region


_LABEL_TAGS = {'Label', 'Choice', 'Relation'}


def _get_parent_control_tag_name(tag, controls):
    """
    """
    # Find parental <Choices> tag for nested tags like <Choices><View><View><Choice>...
    parent = tag
    while True:
        parent = parent.getparent()
        if parent is None:
            return
        name = parent.attrib.get('name')
        if name in controls:
            return name        


class LabelTag(LabelStudioTag):
    """
    Class for Label Tag
    """
    value: Optional[str] = None
    parent_name: Optional[str] = None

    @classmethod
    def validate_node(cls, tag) -> bool:
        """Check if tag is input"""
        return tag.tag in _LABEL_TAGS

    @classmethod
    def parse_node(cls, tag, controls_context) -> 'LabelTag':
        parent_name = _get_parent_control_tag_name(tag, controls_context)
        if parent_name is not None:
            actual_value = tag.attrib.get('alias') or tag.attrib.get('value')
            if actual_value:
                return LabelTag(tag=tag.tag, attr=tag.attrib,
                                parent_name=parent_name, value=actual_value)
