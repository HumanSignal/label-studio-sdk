import json
from lxml.etree import Element

from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk.label_interface.control_tags import ControlTag

import tests.test_interface.configs as c


def test_parse():
    tag = Element('tag', {'name': 'my_name', 'toName': 'name1,name2', 'apiUrl': 'http://myapi.com'})
    control_tag = ControlTag.parse_node(tag)
    
    assert isinstance(control_tag, ControlTag)
    assert control_tag.tag == 'tag'
    assert control_tag.name == 'my_name'
    assert control_tag.to_name == ['name1', 'name2']
    assert control_tag.dynamic_value == True

def test_validate():
    tag = Element('tag', {'name': 'my_name', 'toName': 'name1,name2'})
    is_control_tag1 = ControlTag.validate_node(tag)
    
    assert is_control_tag1 == True

    tag2 = Element('not_control_tag', {'name': 'my_name'})
    is_control_tag2 = ControlTag.validate_node(tag2)

    assert is_control_tag2 == False
    

def test_textarea_label():
    conf = LabelInterface(c.TEXTAREA_CONF)

    region = conf.get_control(c.FROM_NAME).label(text=["Hello", "World"])


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
