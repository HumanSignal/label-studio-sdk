import base64
import hashlib
import os
import tempfile
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import pytest

from label_studio_sdk._extensions.label_studio_tools.core.utils.io import (
    get_local_path,
    get_base64_content,
    _DIR_APP_NAME,
)


def os_path_exists(url):
    return False


# List of test cases covering different storage options and URLs
test_cases = [
    # UI uploads
    # NOTE: these normalize to the authenticated storage proxy URL:
    # http://app.heartex.com/storage-data/uploaded/?filepath=upload/5/1.jpg
    ("upload/5/1.jpg", f"test-data-dir/.cache/{_DIR_APP_NAME}/4988107b__1.jpg"),
    ("/upload/5/1.jpg", f"test-data-dir/.cache/{_DIR_APP_NAME}/4988107b__1.jpg"),
    ("/data/upload/5/1.jpg", f"test-data-dir/.cache/{_DIR_APP_NAME}/4988107b__1.jpg"),

    # Local Storage
    (
        "/data/local-files?d=my_dir/1.jpg",
        f"test-data-dir/.cache/{_DIR_APP_NAME}/3e01c002__1.jpg",
    ),
    (
        "/data/local-files?d=my_dir/2.jpg",
        f"test-data-dir/.cache/{_DIR_APP_NAME}/6ed75663__2.jpg",
    ),
    # Cloud Storages
    (
        "s3://bucket/prefix/1.jpg",
        f"test-data-dir/.cache/{_DIR_APP_NAME}/4fca0572__1.jpg",
    ),
    (
        "gs://bucket/prefix/1.jpg",
        f"test-data-dir/.cache/{_DIR_APP_NAME}/1e2682e4__1.jpg",
    ),
    (
        "azure-blob://bucket/prefix/1.jpg",
        f"test-data-dir/.cache/{_DIR_APP_NAME}/1a4dc8b3__1.jpg",
    ),
    # http(s) URLs
    (
        "http://example.com/1.jpg",
        f"test-data-dir/.cache/{_DIR_APP_NAME}/52ede693__1.jpg",
    ),
]


@pytest.mark.parametrize("url,expected", test_cases)
@patch(
    "label_studio_sdk._extensions.label_studio_tools.core.utils.io.get_data_dir",
    return_value="test-data-dir/",
)
@patch(
    "label_studio_sdk._extensions.label_studio_tools.core.utils.io.get_cache_dir",
    return_value=f"test-data-dir/.cache/{_DIR_APP_NAME}",
)
def test_get_local_path(mock_get_data_dir, mock_get_cache_dir, url, expected):
    with patch("os.path.exists") as mock_exists:
        mock_exists.side_effect = os_path_exists

        x = get_local_path(
            url,
            access_token="secret",
            hostname="http://app.heartex.com",
            download_resources=False,
            task_id=1,
        )
        print("\n ==> get_local_path = ", x)
        assert x == expected


@pytest.mark.parametrize(
    "url, raises_error",
    [
        # Valid local file
        ("/data/local-files?d=my_dir/1.jpg", False),
        # Attempted directory traversal
        ("/data/local-files?d=../../etc/passwd", True),
    ],
)
@patch("label_studio_sdk._extensions.label_studio_tools.core.utils.io.get_data_dir", return_value="test-data-dir/")
@patch("label_studio_sdk._extensions.label_studio_tools.core.utils.io.get_cache_dir", return_value="test-data-dir/.cache/label-studio")
@patch("label_studio_sdk._extensions.label_studio_tools.core.utils.io.LOCAL_FILES_DOCUMENT_ROOT", "/my_files")
def test_get_local_path_safe_build(mock_data_dir, mock_cache_dir, url, raises_error):
    # Mock file-existence checks so the call proceeds to path-building logic
    with patch("os.path.exists", return_value=True):
        if raises_error:
            with pytest.raises(ValueError, match="Invalid path"):
                result = get_local_path(url, access_token="secret", hostname="http://app.heartex.com")
        else:
            local_path = get_local_path(url, access_token="secret", hostname="http://app.heartex.com")
            assert "my_dir/1.jpg" in local_path


def test_get_local_path_storage_proxy_filename_and_auth(monkeypatch, tmp_path):
    """
    Ensure storage proxy URLs use `filepath` for filename, rewrite to hostname,
    and attach auth for matching host.
    """
    url = "/storage-data/uploaded/?filepath=upload/5/1.jpg"
    hostname = "https://labelstudio.example.com"
    token = "secret"
    cache_dir = tmp_path

    requested = SimpleNamespace(url=None, headers=None)

    def fake_get(u, stream=False, headers=None, verify=None):
        requested.url = u
        requested.headers = headers or {}
        response = MagicMock()
        response.content = b"imgdata"
        response.raise_for_status = lambda: None
        return response

    monkeypatch.setattr("label_studio_sdk._extensions.label_studio_tools.core.utils.io.requests.get", fake_get)

    local_path = get_local_path(
        url=url,
        cache_dir=str(cache_dir),
        hostname=hostname,
        access_token=token,
        download_resources=True,
        task_id=123,
    )

    # filename should come from filepath and keep extension
    url_hash = hashlib.md5(f"{hostname}{url}".encode()).hexdigest()[:8]
    assert local_path.endswith(f"{url_hash}__1.jpg")

    # ensure request url was rewritten to hostname
    assert requested.url.startswith(f"{hostname}/storage-data/uploaded/?filepath=upload/5/1.jpg")
    # ensure auth header is attached
    assert "Authorization" in requested.headers
    assert requested.headers["Authorization"] in (f"Token {token}", f"Bearer {token}")


def test_get_base64_content_storage_proxy_rewrite(monkeypatch):
    url = "/storage-data/uploaded/?filepath=upload/5/1.jpg"
    hostname = "https://labelstudio.example.com"
    token = "secret"

    requested = SimpleNamespace(url=None, headers=None)

    def fake_get(u, headers=None, verify=None):
        requested.url = u
        requested.headers = headers or {}
        response = MagicMock()
        response.content = b"abc"
        response.raise_for_status = lambda: None
        return response

    monkeypatch.setattr("label_studio_sdk._extensions.label_studio_tools.core.utils.io.requests.get", fake_get)

    content_b64 = get_base64_content(
        url=url,
        hostname=hostname,
        access_token=token,
        task_id=123,
    )

    assert content_b64 == base64.b64encode(b"abc").decode("utf-8")
    assert requested.url.startswith(f"{hostname}/storage-data/uploaded/?filepath=upload/5/1.jpg")
    assert "Authorization" in requested.headers
    assert requested.headers["Authorization"] in (f"Token {token}", f"Bearer {token}")


def test_get_local_path_upload_is_rewritten_to_storage_proxy(monkeypatch, tmp_path):
    """Ensure raw upload keys are rewritten to /storage-data/uploaded for downloads.

    This specifically covers the rewrite block in io.get_local_path:
    - normalizes upload/<project>/<file> to /data/upload/...
    - then rewrites to /storage-data/uploaded/?filepath=upload/<project>/<file>
    """

    url = "upload/5/1.jpg"
    hostname = "https://labelstudio.example.com"
    token = "secret"

    requested = SimpleNamespace(url=None, headers=None)

    def fake_get(u, stream=False, headers=None, verify=None):
        requested.url = u
        requested.headers = headers or {}
        response = MagicMock()
        response.content = b"imgdata"
        response.raise_for_status = lambda: None
        return response

    monkeypatch.setattr(
        "label_studio_sdk._extensions.label_studio_tools.core.utils.io.requests.get",
        fake_get,
    )

    local_path = get_local_path(
        url=url,
        cache_dir=str(tmp_path),
        hostname=hostname,
        access_token=token,
        download_resources=True,
        task_id=123,
    )

    expected_full_url = f"{hostname}/storage-data/uploaded/?filepath=upload/5/1.jpg"
    expected_hash = hashlib.md5(expected_full_url.encode()).hexdigest()[:8]
    assert local_path.endswith(f"{expected_hash}__1.jpg")

    assert requested.url == expected_full_url
    assert "Authorization" in requested.headers
    assert requested.headers["Authorization"] in (f"Token {token}", f"Bearer {token}")
    assert "/data/upload/" not in requested.url

