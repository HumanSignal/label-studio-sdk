"""
"""
import json
import pytest
import xmljson
import copy

from label_studio_sdk.objects import PredictionValue
from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk.label_interface.control_tags import (
    ControlTag,
    ChoicesTag,
    LabelsTag,
    Region,
)
from label_studio_sdk.exceptions import LabelStudioValidationErrorSentryIgnored

# from label_studio_sdk.label_config.regions import Region
import tests.test_interface.configs as c


## testing basic functionality


def test_parse_configs():
    conf1 = LabelInterface(c.SIMPLE_CONF)
    conf2 = LabelInterface(c.VIDEO_CONF)
    conf3 = LabelInterface(c.DYNAMIC_LABELS_CONF)


def test_accessors():
    conf = LabelInterface(c.SIMPLE_CONF)

    c1 = conf.get_control()
    assert c1.name == c.FROM_NAME

    c2 = conf.get_control(c.FROM_NAME)
    assert c2.name == c.FROM_NAME

    o1 = conf.get_object(c.TO_NAME)
    assert o1.name == c.TO_NAME

    o2 = c2.get_object(c.TO_NAME)
    assert o2.name == c.TO_NAME


def test_parse_two_to_names():
    conf = LabelInterface(c.TWO_TONAMES)
    ctrl = conf.get_control()

    assert isinstance(ctrl, ControlTag)

    with pytest.raises(Exception):
        obj = conf.get_object()

    obj1 = conf.get_object(c.TO_NAME)
    assert obj1.name == c.TO_NAME

    obj2 = conf.get_object(c.ANOTHER_TO_NAME)
    assert obj2.name == c.ANOTHER_TO_NAME


def test_parse_textarea():
    conf = LabelInterface(c.TEXTAREA_CONF)


# def test_parse_config_to_json():
#     json = LabelInterface.parse_config_to_json(c.SIMPLE_CONF)


def test_to_name_validation():
    LabelInterface._to_name_validation(None, c.SIMPLE_CONF)

    with pytest.raises(LabelStudioValidationErrorSentryIgnored):
        LabelInterface._to_name_validation(None, c.SIMPLE_WRONG_CONF)


def test_unique_names_validation():
    with pytest.raises(LabelStudioValidationErrorSentryIgnored):
        LabelInterface._unique_names_validation(None, c.SIMPLE_WRONG_CONF)


def test_get_sample_task():
    conf = LabelInterface(c.SIMPLE_CONF)
    task, _, _ = conf._sample_task()
    value = c.VALUE[1:]

    assert value in task
    assert len(task[value])


## various edge cases


def test_config_essential_data_has_changed():
    conf = LabelInterface(c.SIMPLE_CONF)
    assert conf.config_essential_data_has_changed(c.SIMPLE_CONF) is False

    new_conf = c.SIMPLE_CONF.replace(c.FROM_NAME, "wrong_name")
    assert conf.config_essential_data_has_changed(new_conf) is True

    new_conf_2 = c.SIMPLE_CONF.replace(c.LABEL1, "wrong_label")
    assert conf.config_essential_data_has_changed(new_conf_2) is True


def test_get_task_from_labeling_config():
    task_data, annotations, predictions = LabelInterface.get_task_from_labeling_config(
        c.CONF_WITH_COMMENT
    )

    # assert task_data == "some_data"
    # assert annotations == "some_annotations"
    # assert predictions == "some_predictions"


def test_find_tags():
    conf = LabelInterface(c.SIMPLE_CONF)
    tags = conf.find_tags(match_fn=lambda tag: tag.name == c.TO_NAME)

    assert len(tags) > 0
    assert tags[0].name == c.TO_NAME


def test_find_tags_by_class():
    conf = LabelInterface(c.SIMPLE_CONF)
    tags = conf.find_tags_by_class(ChoicesTag)

    assert len(tags) > 0
    assert tags[0].name == c.FROM_NAME

    tags2 = conf.find_tags_by_class(LabelsTag)
    assert len(tags2) == 0


## testing generation


def test_task_generation():
    val = c.VALUE[1:]
    conf = LabelInterface(c.SIMPLE_CONF)
    task = conf.generate_sample_task()

    assert val in task
    print(task)
    assert len(task.get(val))


## testing object tags

## testing control tags


def test_label_with_choices():
    conf = LabelInterface(c.SIMPLE_CONF)
    region: Region = conf.get_control().label(label=c.LABEL1)

    rjs = region.to_json()
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
    conf = LabelInterface(c.SIMPLE_CONF)
    var_name = c.VALUE[1:]
    value = "test"

    tree = conf.load_task({var_name: value})

    assert isinstance(tree, LabelInterface)
    assert tree.get_object(c.TO_NAME).value == value


def test_load_random_task():
    conf = LabelInterface(c.SIMPLE_CONF)
    task, _, _ = conf._sample_task()

    tree = conf.load_task(task)
    assert len(tree.get_object(c.TO_NAME).value)


def test_empty_value_config():
    conf = LabelInterface(c.EMPTY_VALUE_CONF)
    conf = LabelInterface(c.NO_VALUE_CONF)
