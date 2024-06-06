
from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk.objects import PredictionValue

from . import configs as c


MODEL_VERSION = "0.0.1"
SCORE = 0.10


def test_prediction_value():
    """ """    
    li = LabelInterface(c.SIMPLE_CONF)
    chc = li.get_control()
    
    r = chc.label(label=c.LABEL1)
    p = PredictionValue(model_version=MODEL_VERSION, score=SCORE, result=[ r ])
    
    expected = {
        "model_version": MODEL_VERSION,
        "score": SCORE,
        "result": [
            {
                "id": r.id,
                "from_name": c.FROM_NAME,
                "to_name": c.TO_NAME,
                "type": "choices",
                "value": {
                    "choices": [ c.LABEL1 ]
                }
            }
        ]
    }
    
    assert p.serialize() == expected
    

def test_prediction_value_relation():
    """ """
    li = LabelInterface(c.SIMPLE_CONF)
    chc = li.get_control()
    
    r = chc.label(label=c.LABEL1)
    r2 = chc.label(label=c.LABEL2)

    r.add_relation(r2)
    
    p = PredictionValue(model_version=MODEL_VERSION, score=SCORE, result=[ r, r2 ])

    # we will pick the last item which should be a relation by default
    # (all relations should be last items in the array)
    res = p.serialize()
    relation = res.get("result")[-1]

    assert relation == [{
        "direction": "right",
        "from_id": r.id,
        "to_id": r2.id,
        "type": "relation"
    }]
