from label_studio_sdk.label_interface.object_tags import ObjectTag
from lxml.etree import Element


def test_parse():
    tag = Element("tag", {"name": "my_name", "value": "my_value"})
    object_tag = ObjectTag.parse_node(tag)

    assert object_tag.name == "my_name"
    assert object_tag.value == "my_value"
    assert object_tag.value_type == None


def test_validate():
    tag = Element("tag", {"name": "my_name", "value": "$my_value"})
    validation_result = ObjectTag.validate_node(tag)

    assert validation_result == True


def test_value_type():
    tag = Element(
        "tag", {"name": "my_name", "value": "my_value", "valueType": "string"}
    )
    object_tag = ObjectTag.parse_node(tag)
    tag_value_type = object_tag.value_type

    assert tag_value_type == "string"


def test_value_is_variable():
    tag = Element("tag", {"name": "my_name", "value": "$my_var"})
    object_tag = ObjectTag.parse_node(tag)
    is_variable = object_tag.value_is_variable

    assert is_variable == True
