import pytest

from label_studio_sdk._legacy.label_interface import LabelInterface
from label_studio_sdk._legacy.exceptions import LabelStudioValidationErrorSentryIgnored

from . import configs as c
from .mockups import SummaryMockup


def test_validate_summary():
    li = LabelInterface(c.CONF_COMPLEX)
    summary = SummaryMockup()

    li.validate_config_using_summary(summary)

    # lets replace a label
    c2 = c.CONF_COMPLEX.replace("PER", "DOESNOTEXIST")
    li = LabelInterface(c2)

    with pytest.raises(LabelStudioValidationErrorSentryIgnored):
        li.validate_config_using_summary(summary)

    # lets replace control name
    c3 = c.CONF_COMPLEX.replace("label", "DOESNOTEXIST")
    li = LabelInterface(c3)

    with pytest.raises(LabelStudioValidationErrorSentryIgnored):
        li.validate_config_using_summary(summary)

    # lets replace object name
    c4 = c.CONF_COMPLEX.replace("text", "DOESNOTEXIST")
    li = LabelInterface(c4)

    with pytest.raises(LabelStudioValidationErrorSentryIgnored):
        li.validate_config_using_summary(summary)
