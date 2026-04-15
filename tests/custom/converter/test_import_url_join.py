import pytest

from label_studio_sdk.converter.utils import join_input_url


def test_join_input_url_local_files_root_with_windows_style_path_from_issue():
    result = join_input_url("/data/local-files/?d=", r"images\test.jpg")

    assert result == "/data/local-files/?d=images/test.jpg"


def test_join_input_url_local_files_root_with_existing_prefix_and_spaces():
    result = join_input_url("/data/local-files/?d=val2017", "sub dir/image 1.jpg")

    assert result == "/data/local-files/?d=val2017/sub%20dir/image%201.jpg"


def test_join_input_url_http_root_encodes_url_path():
    result = join_input_url("https://example.com/images", "sub dir/image 1.jpg")

    assert result == "https://example.com/images/sub%20dir/image%201.jpg"


def test_join_input_url_s3_root_keeps_prefix_and_slashes():
    result = join_input_url("s3://bucket/coco/val2017/", "nested/image.jpg")

    assert result == "s3://bucket/coco/val2017/nested/image.jpg"


def test_join_input_url_local_files_root_with_multiple_parts():
    result = join_input_url("/data/local-files/?d=", "images\\nested", "test.jpg")

    assert result == "/data/local-files/?d=images/nested/test.jpg"


def test_join_input_url_rejects_empty_root_url():
    with pytest.raises(ValueError, match="root_url must be a non-empty string"):
        join_input_url("", "image.jpg")


def test_join_input_url_rejects_empty_path_parts_after_normalization():
    with pytest.raises(ValueError, match="At least one file path part must be provided"):
        join_input_url("/data/local-files/?d=", "", "/", None)