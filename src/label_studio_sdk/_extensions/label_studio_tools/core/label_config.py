import logging
import re

from collections import defaultdict
from lxml import etree

from label_studio_sdk._extensions.label_studio_tools.core.utils.exceptions import (
    LabelStudioXMLSyntaxErrorSentryIgnored,
)

logger = logging.getLogger(__name__)

_LABEL_TAGS = {"Label", "Choice", "Relation"}
_NOT_CONTROL_TAGS = {
    "Filter",
}
_DIR_APP_NAME = "label-studio"
_VIDEO_TRACKING_TAGS = {"videorectangle"}


def parse_config(config_string):
    """Parse a given Label Studio labeling configuration and return a structured version of the configuration.
    Useful for formatting results for predicted annotations and determining the type(s) of ML models that might
    be relevant to the labeling project.

    :param config_string: Label config string
    :return: structured config of the form:
    {
        "<ControlTag>.name": {
            "type": "ControlTag",
            "to_name": ["<ObjectTag1>.name", "<ObjectTag2>.name"],
            "inputs: [
                {"type": "ObjectTag1", "value": "<ObjectTag1>.value"},
                {"type": "ObjectTag2", "value": "<ObjectTag2>.value"}
            ],
            "labels": ["Label1", "Label2", "Label3"] // taken from "alias" if it exists, else "value"
    }
    """
    if not config_string:
        return {}

    try:
        xml_tree = etree.fromstring(config_string)
    except etree.XMLSyntaxError as e:
        raise LabelStudioXMLSyntaxErrorSentryIgnored(str(e))
    inputs, outputs, labels = {}, {}, defaultdict(dict)
    # Add variables to config (e.g. {{idx}} for index in Repeater
    variables = []
    for tag in xml_tree.iter():
        if tag.attrib and "indexFlag" in tag.attrib:
            variables.append(tag.attrib["indexFlag"])
        if _is_output_tag(tag):
            tag_info = {"type": tag.tag, "to_name": tag.attrib["toName"].split(",")}
            if variables:
                # Find variables in tag_name and regex if find it
                for v in variables:
                    for tag_name in tag_info["to_name"]:
                        if v in tag_name:
                            if "regex" not in tag_info:
                                tag_info["regex"] = {}
                            tag_info["regex"][v] = ".*"
            # Grab conditionals if any
            conditionals = {}
            if tag.attrib.get("perRegion") == "true":
                if tag.attrib.get("whenTagName"):
                    conditionals = {"type": "tag", "name": tag.attrib["whenTagName"]}
                elif tag.attrib.get("whenLabelValue"):
                    conditionals = {
                        "type": "label",
                        "name": tag.attrib["whenLabelValue"],
                    }
                elif tag.attrib.get("whenChoiceValue"):
                    conditionals = {
                        "type": "choice",
                        "name": tag.attrib["whenChoiceValue"],
                    }
            if conditionals:
                tag_info["conditionals"] = conditionals
            if has_variable(tag.attrib.get("value", "")) or tag.attrib.get("apiUrl"):
                tag_info["dynamic_labels"] = True
            outputs[tag.attrib["name"]] = tag_info
        elif _is_input_tag(tag):
            inputs[tag.attrib["name"]] = {
                "type": tag.tag,
                "valueType": tag.attrib.get("valueType"),
            }
            if 'value' in tag.attrib:
                inputs[tag.attrib["name"]]["value"] = tag.attrib["value"].lstrip("$")
            elif 'valueList' in tag.attrib:
                inputs[tag.attrib["name"]]["valueList"] = tag.attrib["valueList"].lstrip("$")
            else:
                raise ValueError(
                    'Inspecting tag {tag_name}... found no "value" or "valueList" attributes.'.format(
                        tag_name=etree.tostring(tag, encoding="unicode").strip()[:50]
                    )
                )
        if tag.tag not in _LABEL_TAGS:
            continue
        parent_name = _get_parent_output_tag_name(tag, outputs)
        if parent_name is not None:
            actual_value = tag.attrib.get("alias") or tag.attrib.get("value") or tag.attrib.get("valueList")
            if not actual_value:
                logger.debug(
                    'Inspecting tag {tag_name}... found no "value", "valueList", or "alias" attributes.'.format(
                        tag_name=etree.tostring(tag, encoding="unicode").strip()[:50]
                    )
                )
            else:
                labels[parent_name][actual_value] = dict(tag.attrib)
    for output_tag, tag_info in outputs.items():
        tag_info["inputs"] = []
        for input_tag_name in tag_info["to_name"]:
            if input_tag_name not in inputs:
                logger.info(
                    f"to_name={input_tag_name} is specified for output tag name={output_tag}, "
                    "but we can't find it among input tags"
                )
                continue
            tag_info["inputs"].append(inputs[input_tag_name])
        tag_info["labels"] = list(labels[output_tag])
        tag_info["labels_attrs"] = labels[output_tag]
    return outputs


def is_video_object_tracking(parsed_config):
    for component in parsed_config:
        if parsed_config[component]["type"].lower() in _VIDEO_TRACKING_TAGS:
            return True


def has_variable(actual_value):
    """
    Check if value has variable
    :param actual_value: value to check
    :return: True if value has variable
    """
    expression = r"^\$[A-Za-z_]+$"
    pattern = re.compile(expression)
    full_match = pattern.fullmatch(actual_value)
    if full_match:
        return True
    return False


def _is_input_tag(tag):
    """
    Check if tag is input
    """
    return tag.attrib.get("name") and (tag.attrib.get("value") or tag.attrib.get("valueList"))


def _is_output_tag(tag):
    """
    Check if tag is output
    """
    return (
        tag.attrib.get("name")
        and tag.attrib.get("toName")
        and tag.tag not in _NOT_CONTROL_TAGS
    )


def _get_parent_output_tag_name(tag, outputs):
    # Find parental <Choices> tag for nested tags like <Choices><View><View><Choice>...
    parent = tag
    while True:
        parent = parent.getparent()
        if parent is None:
            return
        name = parent.attrib.get("name")
        if name in outputs:
            return name
