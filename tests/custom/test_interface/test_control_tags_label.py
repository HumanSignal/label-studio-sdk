"""Testing if all control tags are producing the right region after
calling label() mehtod"""
import pytest
import json
from lxml.etree import Element

from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk.label_interface.region import Region
import label_studio_sdk.label_interface.control_tags as CT
import label_studio_sdk.label_interface.object_tags as OT

from . import configs as c

EX_TEXT = "text"

# some meta parameteriation here 
# object tag, control tag, parameters to the label function, expected json output
params = [
    ## Image labeling
    (OT.ImageTag, CT.ChoicesTag, { "label": c.LABEL1 }, { "choices": [ c.LABEL1 ] }),
    (OT.ImageTag, CT.ChoicesTag, { "label": [ c.LABEL1, c.LABEL2 ] }, { "choices": [ c.LABEL1, c.LABEL2 ] }),

    (OT.ImageTag, CT.EllipseTag, { "x": 10, "y": 10, "radiusX": 10, "radiusY": 10 }, { "x": 10, "y": 10, "radiusX": 10, "radiusY": 10, "rotation": 0, }),
    (OT.ImageTag, CT.EllipseLabelsTag, { "x": 10, "y": 10, "radiusX": 10, "radiusY": 10, "label": c.LABEL1 }, { "x": 10, "y": 10, "radiusX": 10, "radiusY": 10, "rotation": 0, "ellipselabels": [ c.LABEL1 ] }),

    (OT.ImageTag, CT.KeyPointTag, { "x": 10, "y": 10 }, { "x": 10, "y": 10 }),
    (OT.ImageTag, CT.KeyPointLabelsTag, { "x": 10, "y": 10, "label": c.LABEL1 }, { "x": 10, "y": 10, "keypointlabels": [ c.LABEL1 ] }),
        
    (OT.ImageTag, CT.PolygonTag, { "points": [(1,2), (2,1)] }, { "points": [(1,2), (2,1)] }),
    (OT.ImageTag, CT.PolygonLabelsTag, { "points": [(1,2), (2,1)], "label": c.LABEL1 }, { "points": [(1,2), (2,1)], "polygonlabels": [ c.LABEL1 ] }),

    (OT.ImageTag, CT.RectangleTag, { "x": 10, "y": 10, "width": 10, "height": 10 }, { "x": 10.0, "y": 10.0, "width": 10.0, "height": 10.0, "rotation": 0 }),
    (OT.ImageTag, CT.RectangleLabelsTag, { "x": 10, "y": 10, "width": 10, "height": 10, "label": c.LABEL1 }, { "x": 10.0, "y": 10.0, "width": 10.0, "height": 10.0, "rotation": 0, "rectanglelabels": [ c.LABEL1 ] }),
    (OT.ImageTag, CT.TaxonomyTag, { "label": [ [ c.LABEL1 ] ] }, { "taxonomy": [ [ c.LABEL1 ] ] }),
    (OT.ImageTag, CT.TextAreaTag, { "label": [ EX_TEXT, EX_TEXT ] }, { "text": [ EX_TEXT, EX_TEXT ] }),

    (OT.ImageTag, CT.RatingTag, { "label": 3 }, { "rating": 3 }),
    
    (OT.ImageTag, CT.BrushTag, { "rle": [2,3,3,2] }, { "rle": [2,3,3,2], "format": "rle" }),
    (OT.ImageTag, CT.BrushLabelsTag, { "rle": [2,3,3,2], "label": c.LABEL1 }, { "rle": [2,3,3,2], "format": "rle", "brushlabels": [ c.LABEL1 ] }),

    ## Text labeling
    (OT.TextTag, CT.NumberTag, { "label": 5 }, { "number": 5 }),
    (OT.TextTag, CT.DateTimeTag, { "label": "2024-05-07" }, { "datetime": "2024-05-07" }),
    
    (OT.TextTag, CT.LabelsTag, { "label": c.LABEL1, "start": 1, "end": 10 }, { "labels": [ c.LABEL1 ], "start": 1, "end": 10 }),
    (OT.TextTag, CT.LabelsTag, { "label": [ c.LABEL1, c.LABEL2 ], "start": 1, "end": 10 }, { "labels": [ c.LABEL1, c.LABEL2 ], "start": 1, "end": 10 }),

    ## Hypertext labeling
    (OT.HyperTextTag, CT.HyperTextLabelsTag, { "start": 1, "end": 10, "startOffset": 10, "endOffset": 10, "label": c.LABEL1 }, { "start": 1, "end": 10, "startOffset": 10, "endOffset": 10, "htmllabels": [ c.LABEL1 ] }),

    ## Paragraphs labeling
    (OT.ParagraphsTag, CT.ParagraphLabelsTag, { "start": 0, "end": 0, "startOffset": 10, "endOffset": 10, "label": [ c.LABEL1 ] }, { "start": 0, "end": 0, "startOffset": 10, "endOffset": 10, "paragraphlabels": [ c.LABEL1 ] } ),
    (OT.ParagraphsTag, CT.ParagraphLabelsTag, { "utterance": 1, "startOffset": 10, "endOffset": 10, "label": [ c.LABEL1 ] }, { "start": 1, "end": 1, "startOffset": 10, "endOffset": 10, "paragraphlabels": [ c.LABEL1 ] } ),    

    ## List labeling
    (OT.ListTag, CT.RankerTag, { "rank": [ c.LABEL1, c.LABEL2 ] }, { "rank": [ c.LABEL1, c.LABEL2 ] }),

    ## Timeseries labeling
    (OT.TimeSeriesTag, CT.TimeSeriesLabelsTag, { "start": 10, "end": 12, "instant": False, "label": c.LABEL1 }, { "start": 10, "end": 12, "instant": False, "timeserieslabels": [ c.LABEL1 ] }),

    (OT.VideoTag, CT.VideoRectangleTag,
     { "label": c.LABEL1, "framesCount": 10, "duration": 10, "sequence": [ { "x": 10, "y": 10, "time": 0.5, "frame": 10, "width": 10, "height": 10 } ] },
     { "labels": [ c.LABEL1 ], "framesCount": 10, "duration": 10.0, "sequence": [ { "x": 10.0, "y": 10.0, "time": 0.5, "frame": 10, "width": 10.0, "height": 10.0, "rotation": 0 } ] })
]

@pytest.mark.parametrize("obj_cls,control_cls,label_params,expected_output", params)
def test_generic(obj_cls, control_cls, label_params, expected_output):
    """ """
    obj = obj_cls(name="img", value="$val", attr={}, tag="obj")
    tag = control_cls(name="test", to_name=("img", ),
                      attr={}, tag="control")

    tag.set_object(obj)
    r = tag.label(to_name="img", **label_params)
    d = r._dict()
    
    assert d.get("from_name") == "test"
    assert d.get("to_name") == "img"
    assert d.get("type") == "control"
    assert d.get("value") == expected_output


def test_pairwise():
    """ """
    txt1 = OT.TextTag(name="txt1", value="$val1", attr={}, tag="text")
    txt2 = OT.TextTag(name="txt2", value="$val2", attr={}, tag="text")

    tag = CT.PairwiseTag(name="test", to_name=("txt1", "txt2"),
                      attr={}, tag="control")

    tag.set_objects([ txt1, txt2 ])
    r = tag.label("left")
    d = r._dict()

    assert d.get("from_name") == "test"
    assert d.get("to_name") == "test"
    assert d.get("type") == "control"
    assert d.get("value") == { "selected": "left" }


def test_relations():
    """ """
    obj = OT.ImageTag(name="img", value="$val", attr={}, tag="obj")
    control = CT.RectangleTag(name="test", to_name=("img", ), attr={}, tag="control")

    control.set_object(obj)

    r1 = control.label(x=10, y=10, width=10, height=10)
    r2 = control.label(x=20, y=20, width=20, height=20)

    r1.add_relation(r2)

    rels = r1._dict_relations()

    assert rels[0] == { "from_id": r1.id, "to_id": r2.id, "type": "relation", "direction": "right" }

    r1.add_relation(r2, label=[ c.LABEL1, c.LABEL2]) 

    rels2 = r1._dict_relations()

    assert len(rels2) == 2
    assert "labels" in rels2[1]
    assert rels2[1]["labels"] == [ c.LABEL1, c.LABEL2]
    
