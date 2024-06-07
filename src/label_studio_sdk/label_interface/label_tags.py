"""
"""

import xml.etree.ElementTree
from typing import Dict, Optional, List, Tuple, Any
from .base import LabelStudioTag
from .region import Region


_LABEL_TAGS = {"Label", "Choice", "Relation"}


def _get_parent_control_tag_name(tag, controls):
    """ """
    # Find parental <Choices> tag for nested tags like <Choices><View><View><Choice>...
    parent = tag
    while True:
        parent = parent.getparent()
        if parent is None:
            return
        name = parent.attrib.get("name")
        if name in controls:
            return name


class LabelTag(LabelStudioTag):
    """
    Class for Label Tag
    """

    value: Optional[str] = None
    parent_name: Optional[str] = None

    @classmethod
    def validate_node(cls, tag: xml.etree.ElementTree.Element) -> bool:
        """Check if tag is input"""
        return tag.tag in _LABEL_TAGS

    @classmethod
    def parse_node(
        cls,
        tag: xml.etree.ElementTree.Element,
        controls_context: Dict[str, "ControlTag"],
    ) -> "LabelTag":
        """
        This class method parses a node and returns a LabelTag object if the node has a parent control tag and a value.
        It first gets the name of the parent control tag.
        If a parent control tag is found, it gets the value of the node from its 'alias' or 'value' attribute.
        If a value is found, it returns a new LabelTag object with the tag name, attributes, parent control tag name, and value.

        Parameters:
        -----------
        tag : xml.etree.ElementTree.Element
            The node to be parsed.
        controls_context : Dict[str, 'ControlTag']
            The context of control tags.

        Returns:
        --------
        LabelTag
            A new LabelTag object with the tag name, attributes, parent control tag name, and value.
        """
        parent_name = _get_parent_control_tag_name(tag, controls_context)
        if parent_name is not None:
            actual_value = tag.attrib.get("alias") or tag.attrib.get("value")
            if actual_value is not None:
                return LabelTag(
                    tag=tag.tag,
                    attr=dict(tag.attrib),
                    parent_name=parent_name,
                    value=actual_value,
                )
