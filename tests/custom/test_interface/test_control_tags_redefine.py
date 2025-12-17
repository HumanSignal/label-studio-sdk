"""This is testing redefinition of control tag classes"""
import pytest

from label_studio_sdk.label_interface import LabelInterface
import label_studio_sdk.label_interface.control_tags as CT
import label_studio_sdk.label_interface.object_tags as OT

from . import configs as c


class CustomChoicesTag(CT.ChoicesTag):
    """ """
    def _request_model(self, data):
        """ """
        ## code to request the model is skipped
        # raise Exception(data)
        if data == "1":
            return c.LABEL1
        elif data == "2":
            return c.LABEL2

    def label(self, to_name=None, *args, **kwargs):
        ## send a request to the model
        ## you need to run li.load_task({ ...task data... }) first so
        ## that tag has access to the data
        to_name = self._resolve_to_name(to_name)
        obj = self.find_object_by_name(to_name)
        label = self._request_model(obj.value)

        return super().label(to_name=to_name, label=label)


def test_redefine():
    """ """
    li = LabelInterface(config=c.TWO_TONAMES, tags_mapping={
        'choices': CustomChoicesTag
    })

    li = li.load_task({
        "var": "1",
        "var2": "2"
    })

    chc = li.get_tag(c.FROM_NAME)
    reg = chc.label(to_name=c.TO_NAME)

    d = reg._dict()

    assert d.get("from_name") == c.FROM_NAME
    assert d.get("to_name") == c.TO_NAME
    assert d.get("type") == "choices"
    assert d.get("value") == { "choices": [ c.LABEL1 ] }

    reg = chc.label(to_name=c.ANOTHER_TO_NAME)
    d = reg._dict()

    assert d.get("value") == { "choices": [ c.LABEL2 ] }

