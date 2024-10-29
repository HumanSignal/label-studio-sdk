import json
import pytest
from lxml.etree import Element

from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk.label_interface.control_tags import ControlTag, ChoicesTag, LabelsTag, RectangleLabelsTag

from . import configs as c


def test_parse():
    tag = Element(
        "tag",
        {"name": "my_name", "toName": "name1,name2", "apiUrl": "http://myapi.com"},
    )
    control_tag = ControlTag.parse_node(tag)

    assert isinstance(control_tag, ControlTag)
    assert control_tag.tag == "tag"
    assert control_tag.name == "my_name"
    assert control_tag.to_name == ["name1", "name2"]
    assert control_tag.dynamic_value == True


def test_validate():
    tag = Element("tag", {"name": "my_name", "toName": "name1,name2"})
    is_control_tag1 = ControlTag.validate_node(tag)

    assert is_control_tag1 == True

    tag2 = Element("not_control_tag", {"name": "my_name"})
    is_control_tag2 = ControlTag.validate_node(tag2)

    assert is_control_tag2 == False


def test_textarea_label():
    conf = LabelInterface(c.TEXTAREA_CONF)

    region = conf.get_control(c.FROM_NAME).label(label=["Hello", "World"])


def test_label_with_choices():
    conf = LabelInterface(c.SIMPLE_CONF)
    region = conf.get_control().label(label=c.LABEL1)

    rjs = region.to_json()
    assert isinstance(rjs, str)

    rpy = json.loads(rjs)
    assert rpy["from_name"] == c.FROM_NAME
    assert rpy["to_name"] == c.TO_NAME
    assert "value" in rpy

    assert "choices" in rpy.get("value")
    assert c.LABEL1 in rpy["value"]["choices"]
    
    
@pytest.mark.parametrize("tag, regions, expected", [
    # Test case 1: ChoicesTag with single choice
    (
        ChoicesTag(name="choices", to_name=["text"], tag="Choices"),
        [{"from_name": "choices", "value": {"choices": ["positive"]}}],
        "positive"
    ),
    
    # Test case 2: ChoicesTag with multiple choices
    (
        ChoicesTag(name="choices", to_name=["text"], tag="Choices"),
        [{"from_name": "choices", "value": {"choices": ["positive", "negative"]}}],
        ["positive", "negative"]
    ),
    
    # Test case 3: Multiple regions with labels
    (
        LabelsTag(name="label", to_name=["text"], tag="Labels"),
        [
            {"from_name": "label", "to_name": "text", "value": {"labels": ["positive"], "start": 0, "end": 1}},
            {"from_name": "label", "to_name": "text", "value": {"labels": ["negative"], "start": 2, "end": 3}}
        ],
        [{"start": 0, "end": 1, "labels": ["positive"]}, {"start": 2, "end": 3, "labels": ["negative"]}]
    ),
    
    # Test case 4: Empty regions
    (
        ChoicesTag(name="choices", to_name=["text"], tag="Choices"),
        [],
        []
    ),
    
    # Test case 5: Regions with different from_name
    (
        ChoicesTag(name="choices", to_name=["text"], tag="Choices"),
        [{"from_name": "other_tag", "value": {"choices": ["positive"]}}],
        []
    ),
    
    # Test case 6: Tag without label_attr_name
    (
        ControlTag(name="base", to_name=["text"], tag="BaseTag"),
        [{"from_name": "base", "value": {"some_value": 42}}],
        [{"some_value": 42}]
    ),
])
def test_control_tag_get_labels(tag, regions, expected):
    assert tag.get_labels(regions) == expected
