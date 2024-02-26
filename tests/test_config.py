"""
"""
import json
import pytest
import xmljson
import copy

from label_studio_sdk.config import LabelingConfig, PredictionValue
from label_studio_sdk.exceptions import LabelStudioValidationErrorSentryIgnored
from label_studio_sdk.label_config.control_tags import ControlTag, ChoicesTag, LabelsTag
# from label_studio_sdk.label_config.regions import Region
from . import configs as c


## testing basic functionality

def test_parse_configs():
    conf1 = LabelingConfig(c.SIMPLE_CONF)
    conf2 = LabelingConfig(c.VIDEO_CONF)
    conf3 = LabelingConfig(c.DYNAMIC_LABELS_CONF)
    
def test_accessors():
    conf = LabelingConfig(c.SIMPLE_CONF)

    c1 = conf.get_control()
    assert c1.name == c.FROM_NAME

    c2 = conf.get_control(c.FROM_NAME)
    assert c2.name == c.FROM_NAME

def test_parse_two_to_names():
    conf = LabelingConfig(c.TWO_TONAMES)
    ctrl = conf.get_control()

    assert isinstance(ctrl, ControlTag)
    
    with pytest.raises(Exception):
        obj = conf.get_object()
        
    obj1 = conf.get_object(c.TO_NAME)
    assert obj1.name == c.TO_NAME
    
    obj2 = conf.get_object(c.ANOTHER_TO_NAME)
    assert obj2.name == c.ANOTHER_TO_NAME       

# def test_parse_config_to_json():
#     json = LabelingConfig.parse_config_to_json(c.SIMPLE_CONF)
    
def test_to_name_validation():
    LabelingConfig._to_name_validation(None, c.SIMPLE_CONF)

    with pytest.raises(LabelStudioValidationErrorSentryIgnored):
        LabelingConfig._to_name_validation(None, c.SIMPLE_WRONG_CONF)


def test_unique_names_validation():
    with pytest.raises(LabelStudioValidationErrorSentryIgnored):
        LabelingConfig._unique_names_validation(None, c.SIMPLE_WRONG_CONF)

def test_get_sample_task():
    conf = LabelingConfig(c.SIMPLE_CONF)
    task, _, _ = conf._sample_task()
    value = c.VALUE[1:]
    
    assert value in task
    assert len(task[value])

def test_generate_sample_task():
    conf = LabelingConfig(c.SIMPLE_CONF)
    task = conf.generate_sample_task()
    value = c.VALUE[1:]
    
    assert value in task
    assert len(task[value])

## various edge cases


    
## testing validateion

def test_validate_region():
    r1 = c.CORRECT_REGION
    conf = LabelingConfig(c.SIMPLE_CONF)
    assert conf.validate_region(r1) is True

    r2 = copy.deepcopy(r1)
    r2["from_name"] = "wrong_name"
    with pytest.raises(Exception):
        conf.validate_region(r2)

    r3 = copy.deepcopy(r1)
    r3["value"]["choices"] = "WRONG_CLASS"
    assert conf.validate_region(r3) is False
        
    r4 = copy.deepcopy(r1)
    del r4["value"]["choices"]
    assert conf.validate_region(r4) is False

def validate_prediction():
    r1 = c.CORRECT_REGION
    conf = LabelingConfig(c.SIMPLE_CONF)

    pred = PredictionValue(model_version="0.10",
                           score="0.10",
                           rsults=[ r1 ])
    
    assert conf.validate_prediction(pred) is True
    
def test_validate_task():
    conf = LabelingConfig(c.SIMPLE_CONF)

    assert conf.validate_task({ "data": c.CORRECT_TASK }) is True
    assert conf.validate_task({ "data": { "wrong_var": "value" } }) is False
    
def test_config_essential_data_has_changed():
    conf = LabelingConfig(c.SIMPLE_CONF)
    assert conf.config_essential_data_has_changed(c.SIMPLE_CONF) is False

    new_conf = c.SIMPLE_CONF.replace(c.FROM_NAME, "wrong_name")
    assert conf.config_essential_data_has_changed(new_conf) is True

    new_conf_2 = c.SIMPLE_CONF.replace(c.LABEL1, "wrong_label")
    assert conf.config_essential_data_has_changed(new_conf_2) is True


# def test_get_task_from_labeling_config():
#     task_data, annotations, predictions = LabelingConfig.get_task_from_labeling_config(c.CONF_WITH_COMMENT)

#     assert task_data == "some_data"
#     assert annotations == "some_annotations"
#     assert predictions == "some_predictions"

def test_find_tags():
    conf = LabelingConfig(c.SIMPLE_CONF)
    tags = conf.find_tags(match_fn=lambda tag: tag.name == c.TO_NAME)

    assert len(tags) > 0
    assert tags[0].name == c.TO_NAME

def test_find_tags_by_class():
    conf = LabelingConfig(c.SIMPLE_CONF)
    tags = conf.find_tags_by_class(ChoicesTag)

    assert len(tags) > 0
    assert tags[0].name == c.FROM_NAME

    tags2 = conf.find_tags_by_class(LabelsTag)
    assert len(tags2) == 0
    
## testing generation

def test_task_generation():
    val = c.VALUE[1:]
    conf = LabelingConfig(c.SIMPLE_CONF)
    task = conf.generate_sample_task()

    assert val in task
    print(task)
    assert len(task.get(val))

## testing object tags

## testing control tags

def test_label_with_choices():
    conf = LabelingConfig(c.SIMPLE_CONF)
    region = conf.get_control().label(label=c.LABEL1)
    
    rjs = region.as_json()    
    assert isinstance(rjs, str)

    rpy = json.loads(rjs)    
    assert rpy["from_name"] == c.FROM_NAME
    assert rpy["to_name"] == c.TO_NAME
    assert "value" in rpy

    print(rpy)
    
    assert "choices" in rpy.get("value")
    assert c.LABEL1 in rpy["value"]["choices"]

## testing all other tags

## test other method

def test_load_task():
    conf = LabelingConfig(c.SIMPLE_CONF)
    var_name = c.VALUE[1:]
    value = "test"
    
    tree = conf.load_task({ var_name: value })

    assert isinstance(tree, LabelingConfig)
    assert tree.get_object(c.TO_NAME).value == value 

def test_load_random_task():
    conf = LabelingConfig(c.SIMPLE_CONF)
    task, _, _ = conf._sample_task()

    tree = conf.load_task(task)
    assert len(tree.get_object(c.TO_NAME).value)
    
