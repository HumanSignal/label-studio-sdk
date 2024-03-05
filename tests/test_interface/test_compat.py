## Testing compatibility functions
##
## Compatibility function is a function that was implemented in
## label_studio.core.label_config or tools and is reimplemented within
## SDK using new LabelInterface

import pytest

from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk.objects import PredictionValue

from . import configs as c


def test_get_first_tag_occurence_simple():
    conf = LabelInterface(c.SIMPLE_CONF)
    from_name, to_name, value = conf.get_first_tag_occurence("Choices", "Text")

    assert from_name == c.FROM_NAME
    assert to_name == c.TO_NAME
    assert value == c.VALUE_KEY

    with pytest.raises(ValueError):
        conf.get_first_tag_occurence("Choices", "Image")

    with pytest.raises(ValueError):
        conf.get_first_tag_occurence("Labels", "Text")

    with pytest.raises(ValueError):
        conf.get_first_tag_occurence("Labels", "Image")


def test_get_first_tag_occurence_complex():
    conf = LabelInterface(c.SIMPLE_CONF)
    from_name, to_name, value = conf.get_first_tag_occurence(
        "Choices",
        ("Image", "Text"),
        name_filter=lambda s: s.startswith(c.FROM_NAME_PREFIX),
        to_name_filter=lambda s: s == c.TO_NAME,
    )

    assert from_name == c.FROM_NAME
    assert to_name == c.TO_NAME
    assert value == c.VALUE_KEY

    with pytest.raises(ValueError):
        conf.get_first_tag_occurence(
            "Choices",
            ("Image", "Text"),
            name_filter=lambda s: s.startswith("wrong_prefix"),
        )

    with pytest.raises(ValueError):
        conf.get_first_tag_occurence(
            "Choices", ("Image", "Text"), to_name_filter=lambda s: s == "wrong_name"
        )


def test_is_video_object_tracking():
    conf1 = LabelInterface(c.SIMPLE_CONF)
    assert conf1.is_video_object_tracking() is False

    conf2 = LabelInterface(c.VIDEO_CONF)
    assert conf2.is_video_object_tracking() is True
