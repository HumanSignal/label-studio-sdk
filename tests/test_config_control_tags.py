
from label_studio_sdk.label_config.control_tags import ControlTag
from lxml.etree import Element


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
    
