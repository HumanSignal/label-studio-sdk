
from lxml.etree import Element

from label_studio_sdk.config import LabelingConfig
from . import configs as c

def test_region():
    # h.get_rect_interface()
    XVAL=10
    YVAL=10
    WVAL=20
    HVAL=20
    RVAL=0
    
    lpi = LabelingConfig(c.RECT_CONFIG)
    
    rect = lpi.get_control(c.FROM_NAME)
    img = rect.get_object()
    r = rect.label(x=XVAL, y=YVAL, width=WVAL, height=HVAL, rotation=RVAL)
    d = r._dict()
    
    assert d["from_name"] == c.FROM_NAME
    assert d["to_name"] == c.TO_NAME
    assert d["type"] == "rectangle"
    assert isinstance(d["value"], dict)

    assert d["value"]["x"] == XVAL
    assert d["value"]["y"] == YVAL
    assert d["value"]["width"] == WVAL
    assert d["value"]["height"] == HVAL
    assert d["value"]["rotation"] == RVAL
    
    # out = r.dict()
    
