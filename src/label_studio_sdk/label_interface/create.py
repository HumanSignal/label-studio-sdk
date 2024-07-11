"""
"""
from typing import Dict, Optional, List, Tuple, Any, Callable, Union
import xml.etree.ElementTree as ET
from xml.dom import minidom

from label_studio_sdk.label_interface.base import LabelStudioTag

import label_studio_sdk.label_interface.object_tags as OT
import label_studio_sdk.label_interface.control_tags as CT

## syntatic sugar helper functions

def labels(labels, tag_type="Labels", **kwargs):
    """
    Converts labels to a tuple structure.
    
    Args:
        labels: The labels to be converted.
        tag_type: Tag type to assign to each label.
        
    Returns:
        A tuple containing labels as per the tag type.
    """
    return (tag_type, kwargs, _convert_to_tuple(labels, tag_type="Label"))
    
    
def taxonomy(labels, **kwargs):
    """
    Constructs a taxonomy.
    
    Args:
        labels: The labels to construct the taxonomy.
        
    Returns:
        A tuple containing the taxonomy.
    """
    result = []
    
    for arg in labels:
        if isinstance(arg, tuple):
            parent, *children = _convert_to_tuple(arg)
            parent_children = (parent[0], parent[1], tuple(children))
            result.append(parent_children)            
        else:
            result.append(("Choice", {"value": arg}, {}))
    
    return ("Taxonomy", kwargs, tuple(result))    

def choices(labels, **kwargs):
    """
    Constructs a choices tuple.
    
    Args:
        labels: The labels to be converted.
        
    Returns:
        A tuple containing the choices.
    """ 
    return ("Choices", kwargs, _convert_to_tuple(labels))


def _prettify(element):
    """
    Returns a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def _convert_to_tuple(args, tag_type="Choice"):
    """
    Converts arguments to a tuple structure of choices.

    Args:
        args: The labels to be converted.
        tag_type: Tag type to assign to each label.

    Returns:
        A tuple containing all labels in specified format.
    """
    if not args:
        return None
    
    return tuple(((tag_type, {"value": arg}, {})) for arg in args)


def _create_nested_elements(parent: ET.Element, elements: List[Union[str, Dict[str, str], List]]) -> None:
    """
    Adds nested elements to the parent element in the Element Tree.

    Args:
        parent: The parent ET.Element object.
        elements: A list containing element definitions.
    """    
    for element in elements:        
        if isinstance(element, str):
            ET.SubElement(parent, element)
        elif isinstance(element, dict):
            for k, v in element.items():
                parent.set(k, v)
        elif isinstance(element, list) or isinstance(element, tuple):
            create_element(element, parent=parent)

            
def _convert(name: str, tag: Union[str, list, tuple, LabelStudioTag]) -> tuple:
    """
    Converts tags from str, list, tuple, or class instance to a tuple format.

    Args:
        name: Name of the tag.
        tag: Tag in str, list, tuple or class instance format.

    Returns:
        A tuple version of the input tag.
    
    Raises:
        TypeError: If input tag is not a str, list, tuple, or LabelStudioTag.
    """
    
    if isinstance(tag, LabelStudioTag):
        tag.name = tag.name or name
        child_tag_type = "Choice" if tag.tag in ["Choices", "Taxonomy"] else "Label"
        el = tag.tag, tag.collect_attrs(), _convert_to_tuple(getattr(tag, "labels", None), tag_type=child_tag_type)
    elif isinstance(tag, (list, tuple)):
        el = (*tag, ()) if len(tag) < 3 else tag
    elif isinstance(tag, str):        
        el = tag, {}, ()
    else:
        raise TypeError("Input tag must be one of str, list, tuple, LabelStudioTag")

    el[1].setdefault("name", name)
    
    if el[0].lower() in OT._TAG_TO_CLASS and not el[1].get("value"):
        el[1]["value"] = "$" + name
            
    return el


def _find_first_object_tag(tags):
    """
    Finds the first object tag in the input tags dictionary.

    Args:
        tags: A dictionary of tags.

    Returns:
        The first object tag found, or None.
    """
    for name, tag in tags.items():
        tag_tuple = _convert(name, tag)
        tag_name = tag_tuple[0]
                
        if tag_name.lower() in OT._TAG_TO_CLASS:
            return tag_tuple

            
def create_element(element: List[Union[str, Dict[str, str], List]], parent=None) -> ET.Element:
    """
    Creates an XML element.
    
    Args:
        element: List of tag, attributes and children to feed into the element.
        parent: Parent element to append the new element to (Optional).
        
    Returns:
        An ElementTree element.
    """
    tag, attrs, children = element
    el = ET.SubElement(parent, tag) if parent is not None else ET.Element(tag)
    
    for k, v in attrs.items():
        el.set(k, v)

    if children:
        _create_nested_elements(el, children) 
        
    return el

        
def tree_from_tuples(*elements):
    """
    Creates an ElementTree from the input element definitions, and return a string for it.

    Args:
        elements: Variable length argument list of elements to add to the ElementTree.

    Returns:
        XML configuration
    """
    view = ET.Element('View')
    for element in elements:
        el = create_element(element)
        view.append(el)

    return view


def tree_to_string(tree, pretty=True):
    """
    """    
    if pretty:
        pp = _prettify(tree)
        return pp.replace('<?xml version="1.0" ?>\n', '')
    else:
        return ET.tostring(tree, encoding='unicode')
    

def convert_tags_description(tags: Dict[str, Any],
                             mapping: Optional[Dict[str, str]]=None) -> List[Union[str, Dict[str, str], List]]:
    """
    Convert tags into a structured format.

    Args:
        tags: A dictionary of tags.
        mapping: Optional mapping of tag name transformations.

    Returns:
        A list of the structured tags.
    """
    elements = []
    first_object_tag = _find_first_object_tag(tags)
        
    for name, tag in tags.items():
        el = _convert(name, tag)

        # Set `toName` property of the tag if tag name is in
        # CT._TAG_TO_CLASS and `toName` key is not in tag attributes
        # The value of `toName` key is set based on whether `name` of
        # tag is in the mapping dictionary or the `name` of the first
        # object tag if it's not in mapping
        if el[0].lower() in CT._TAG_TO_CLASS and ("toName" not in el[1] or el[1]["toName"] is None):
            if mapping and el[1].get("name") in mapping:
                el[1]["toName"] = mapping.get(el[1]["name"])                
            else:
                el[1]["toName"] = first_object_tag[1]["name"]
        
        elements.append(el)
    
    return elements
