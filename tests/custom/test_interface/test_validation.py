import json
import pytest
import xmljson
import copy

from label_studio_sdk.label_interface.objects import PredictionValue
from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk.label_interface.object_tags import ImageTag
from label_studio_sdk.label_interface.control_tags import (
    ControlTag,
    ChoicesTag,
    LabelsTag,
    BrushTag,
    BrushLabelsTag
)
from label_studio_sdk._legacy.exceptions import LabelStudioValidationErrorSentryIgnored

# from label_studio_sdk.label_config.regions import Region
from . import configs as c


def test_validate_region():
    r1 = c.CORRECT_REGION
    conf = LabelInterface(c.SIMPLE_CONF)
    assert conf.validate_region(r1) is True

    r2 = copy.deepcopy(r1)
    r2["from_name"] = "wrong_name"
    assert conf.validate_region(r2) is False

    r3 = copy.deepcopy(r1)
    r3["value"]["choices"] = "WRONG_CLASS"
    assert conf.validate_region(r3) is False

    r4 = copy.deepcopy(r1)
    del r4["value"]["choices"]
    assert conf.validate_region(r4) is False


def test_validate_prediction():
    r1 = c.CORRECT_REGION
    conf = LabelInterface(c.SIMPLE_CONF)

    pred = {"model_version": "0.10", "score": "0.10", "result": [r1]}

    assert conf.validate_prediction(pred) is True

    r2 = copy.deepcopy(r1)
    r2["from_name"] = "wrong_name"

    pred["result"] = [r2]

    assert conf.validate_prediction(pred) is False


def test_validate_task():
    conf = LabelInterface(c.SIMPLE_CONF)

    assert conf.validate_task({"data": c.CORRECT_TASK}) is True
    assert conf.validate_task({"data": {"wrong_var": "value"}}) is False


def test_validate_brush():
    """ """
    obj = ImageTag(name="img", value="$val", attr={}, tag="obj")
    tag = BrushTag(name="test", to_name=("img", ),
                      attr={}, tag="control")
    
    tag.set_object(obj)
    assert tag.validate_value({ "format": "rle", "rle": [ 1,2,3 ] }) is False
    assert tag.validate_value({ "format": "rle", "rle": [ 2,3,3,2 ] }) is True

    
def test_validate_annotation():
    """ """
    ## trying to just send a plain JSON in here
    js = '''{ "result": [
    {
        "value": {
            "start": 3,
            "end": 7,
            "text": "have",
            "labels": [
                "PER"
            ]
        },
        "id": "ER6FoirsCU",
        "from_name": "label",
        "to_name": "text",
        "type": "labels"
    },
    {
        "value": {
            "start": 10,
            "end": 25,
            "text": "trust",
            "labels": [
                "LOC"
            ]
        },
        "id": "yzPsD2eglo",
        "from_name": "label",
        "to_name": "text",
        "type": "labels"
    },
    {
        "value": {
            "choices": [
                "Positive"
            ]
        },
        "id": "mbfqaJ68nT",
        "from_name": "sentiment",
        "to_name": "text",
        "type": "choices"
    },
    {
        "from_id": "ER6FoirsCU",
        "to_id": "yzPsD2eglo",
        "type": "relation",
        "direction": "right"
    }
] }'''

    d = json.loads(js)
    
    li = LabelInterface(c.CONF_COMPLEX)
    assert li.validate_annotation(d) == True

    d2 = copy.deepcopy(d)
    d2["result"][0]["from_name"] = "non_existent"

    assert li.validate_annotation(d2) is False

    d3 = copy.deepcopy(d)
    d3["result"][0]["type"] = "non_existent"

    assert li.validate_annotation(d3) == False

    d4 = copy.deepcopy(d)
    del d4["result"][0]["value"]["start"]
    
    assert li.validate_annotation(d4) == False

    
def test_validate_relation():
    """ """
    conf = LabelInterface(c.SIMPLE_CONF)
    control = conf.get_tag(c.FROM_NAME)
    
    r1 = control.label(label=c.LABEL1)
    r2 = control.label(label=c.LABEL1)
    r3 = control.label(label=c.LABEL1)
    
    r1.add_relation(r2)
    assert r1.has_relations > 0
    
    d = r1._dict_relations()[0]
    
    assert conf.validate_relation(d, [ r1._dict(), r2._dict() ]) == True
    assert conf.validate_relation(d, [ r1._dict(), r3._dict() ]) == False
    assert conf.validate_relation(d, [ r2._dict(), r3._dict() ]) == False


def test_label_interface_validate_video_config_valid():
    """LabelInterface.validate() passes for valid Video config with playback speed attrs."""
    VIDEO_CONF_VALID = """
    <View>
    <Video name="video" value="$video" framerate="25" defaultPlaybackSpeed="2" minPlaybackSpeed="0.5"/>
    <VideoRectangle name="box" toName="video" />
    </View>
    """
    li = LabelInterface(VIDEO_CONF_VALID)
    li.validate()  # does not raise


def test_label_interface_validate_video_config_invalid_default_above_max():
    """LabelInterface.validate() raises when defaultPlaybackSpeed > 10."""
    VIDEO_CONF_INVALID_DEFAULT_ABOVE_MAX = """
    <View>
    <Video name="video" value="$video" defaultPlaybackSpeed="15"/>
    <VideoRectangle name="box" toName="video" />
    </View>
    """
    li = LabelInterface(VIDEO_CONF_INVALID_DEFAULT_ABOVE_MAX)
    with pytest.raises(LabelStudioValidationErrorSentryIgnored) as exc_info:
        li.validate()
    assert "defaultPlaybackSpeed" in str(exc_info.value)
    assert "15" in str(exc_info.value)


def test_label_interface_validate_video_config_invalid_min_above_default():
    """LabelInterface.validate() raises when minPlaybackSpeed > defaultPlaybackSpeed."""
    VIDEO_CONF_INVALID_MIN_ABOVE_DEFAULT = """
    <View>
    <Video name="video" value="$video" defaultPlaybackSpeed="5" minPlaybackSpeed="10"/>
    <VideoRectangle name="box" toName="video" />
    </View>
    """
    li = LabelInterface(VIDEO_CONF_INVALID_MIN_ABOVE_DEFAULT)
    with pytest.raises(LabelStudioValidationErrorSentryIgnored) as exc_info:
        li.validate()
    assert "minPlaybackSpeed" in str(exc_info.value)
    assert "must not exceed defaultPlaybackSpeed" in str(exc_info.value)


def test_label_interface_is_valid_false_for_invalid_video_config():
    """LabelInterface.is_valid returns False for invalid Video playback speed config."""
    VIDEO_CONF_INVALID_DEFAULT_ABOVE_MAX = """
    <View>
    <Video name="video" value="$video" defaultPlaybackSpeed="15"/>
    <VideoRectangle name="box" toName="video" />
    </View>
    """
    li = LabelInterface(VIDEO_CONF_INVALID_DEFAULT_ABOVE_MAX)
    assert li.is_valid is False

