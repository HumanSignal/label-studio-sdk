
import json
import pytest
import xmljson
import copy

from label_studio_sdk.objects import PredictionValue
from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk.label_interface.control_tags import ControlTag, ChoicesTag, LabelsTag
from label_studio_sdk.exceptions import LabelStudioValidationErrorSentryIgnored
# from label_studio_sdk.label_config.regions import Region
import tests.test_interface.configs as c


def test_validate_region():
    r1 = c.CORRECT_REGION
    conf = LabelInterface(c.SIMPLE_CONF)
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

def test_validate_prediction():
    r1 = c.CORRECT_REGION
    conf = LabelInterface(c.SIMPLE_CONF)

    pred = {
        "model_version": "0.10",
        "score": "0.10",
        "result": [ r1 ]
    }
    
    assert conf.validate_prediction(pred) is True

    r2 = copy.deepcopy(r1)
    r2["from_name"] = "wrong_name"

    pred["result"] = [ r2 ]

    with pytest.raises(Exception):
        conf.validate_prediction(pred)

    
def test_validate_task():
    conf = LabelInterface(c.SIMPLE_CONF)

    assert conf.validate_task({ "data": c.CORRECT_TASK }) is True
    assert conf.validate_task({ "data": { "wrong_var": "value" } }) is False
