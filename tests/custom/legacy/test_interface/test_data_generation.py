from lxml.etree import Element

from label_studio_sdk._legacy.label_interface import LabelInterface
from label_studio_sdk._legacy.label_interface.object_tags import ObjectTag
from . import configs as c


def test_generate_sample_task():
    conf = LabelInterface(c.SIMPLE_CONF)
    task = conf.generate_sample_task()
    value = c.VALUE[1:]

    print(task)

    assert value in task
    assert len(task[value])


def test_generate_url():
    """Quick check that each object tag generates the right data
    """

    def url_validator(url):
        assert url.startswith("https://") or url.startswith("http://")

    # TODO need to add other validators
    m = {
        "Audio": url_validator,
        "Image": url_validator,
        # "Table": None,
        "Text": url_validator,
        "Video": url_validator,
        # "HyperText": None,
        # "List": None,
        "Paragraphs": url_validator,
        # "TimeSeries": url_validator
    }

    for tag_name, validator in m.items():

        tag = Element(tag_name, {"name": "my_name", "value": "my_value"})
        inst = ObjectTag.parse_node(tag)

        res = inst.generate_example_value(mode="editor_preview", secure_mode=True)
        validator(res)
