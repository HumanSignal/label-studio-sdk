from label_studio_sdk.label_interface.object_tags import (
    ObjectTag,
    VideoTag,
    MIN_PLAYBACK_SPEED,
    MAX_PLAYBACK_SPEED,
)
from lxml.etree import Element


def test_object_tag_validate_config_returns_empty():
    """ObjectTag.validate_config() is a no-op and returns empty list."""
    tag = Element("tag", {"name": "my_name", "value": "my_value"})
    object_tag = ObjectTag.parse_node(tag)
    assert object_tag.validate_config() == []


def test_video_tag_validate_config_valid():
    """VideoTag.validate_config() returns no errors for valid playback speed values."""
    tag = Element(
        "Video",
        {
            "name": "video",
            "value": "$video",
            "defaultPlaybackSpeed": "1",
            "minPlaybackSpeed": "0.25",
        },
    )
    video_tag = ObjectTag.parse_node(tag)
    assert isinstance(video_tag, VideoTag)
    assert video_tag.validate_config() == []


def test_video_tag_validate_config_no_playback_attrs():
    """VideoTag without playback speed attributes passes validation."""
    tag = Element("Video", {"name": "video", "value": "$video"})
    video_tag = ObjectTag.parse_node(tag)
    assert video_tag.validate_config() == []


def test_video_tag_validate_config_default_above_max():
    """VideoTag.validate_config() returns error when defaultPlaybackSpeed > 10."""
    tag = Element(
        "Video",
        {"name": "video", "value": "$video", "defaultPlaybackSpeed": "15"},
    )
    video_tag = ObjectTag.parse_node(tag)
    errors = video_tag.validate_config()
    assert len(errors) == 1
    assert "defaultPlaybackSpeed" in errors[0]
    assert "15" in errors[0]
    assert str(MAX_PLAYBACK_SPEED) in errors[0]


def test_video_tag_validate_config_min_above_max():
    """VideoTag.validate_config() returns error when minPlaybackSpeed > 10."""
    tag = Element(
        "Video",
        {"name": "video", "value": "$video", "minPlaybackSpeed": "12"},
    )
    video_tag = ObjectTag.parse_node(tag)
    errors = video_tag.validate_config()
    assert len(errors) == 1
    assert "minPlaybackSpeed" in errors[0]
    assert "12" in errors[0]


def test_video_tag_validate_config_min_exceeds_default():
    """VideoTag.validate_config() returns error when minPlaybackSpeed > defaultPlaybackSpeed."""
    tag = Element(
        "Video",
        {
            "name": "video",
            "value": "$video",
            "defaultPlaybackSpeed": "5",
            "minPlaybackSpeed": "10",
        },
    )
    video_tag = ObjectTag.parse_node(tag)
    errors = video_tag.validate_config()
    assert len(errors) == 1
    assert "minPlaybackSpeed" in errors[0]
    assert "must not exceed defaultPlaybackSpeed" in errors[0]


def test_video_tag_validate_config_default_below_min():
    """VideoTag.validate_config() returns error when defaultPlaybackSpeed < 0.05."""
    tag = Element(
        "Video",
        {"name": "video", "value": "$video", "defaultPlaybackSpeed": "0.01"},
    )
    video_tag = ObjectTag.parse_node(tag)
    errors = video_tag.validate_config()
    assert len(errors) == 1
    assert "defaultPlaybackSpeed" in errors[0]
    assert str(MIN_PLAYBACK_SPEED) in errors[0]


def test_parse():
    tag = Element("tag", {"name": "my_name", "value": "my_value"})
    object_tag = ObjectTag.parse_node(tag)

    assert object_tag.name == "my_name"
    assert object_tag.value == "my_value"
    assert object_tag.value_type == None


def test_validate():
    tag = Element("tag", {"name": "my_name", "value": "$my_value"})
    validation_result = ObjectTag.validate_node(tag)

    assert validation_result == True


def test_value_type():
    tag = Element(
        "tag", {"name": "my_name", "value": "my_value", "valueType": "string"}
    )
    object_tag = ObjectTag.parse_node(tag)
    tag_value_type = object_tag.value_type

    assert tag_value_type == "string"


def test_value_is_variable():
    tag = Element("tag", {"name": "my_name", "value": "$my_var"})
    object_tag = ObjectTag.parse_node(tag)
    is_variable = object_tag.value_is_variable

    assert is_variable == True
