import pytest
from unittest.mock import patch
from label_studio_tools.core.utils.io import (
    get_local_path, _DIR_APP_NAME
)


def os_path_exists(url):
    return False


# List of test cases covering different storage options and URLs
test_cases = [
    # UI uploads
    ("upload/5/1.jpg", f"test-data-dir/.cache/{_DIR_APP_NAME}/ce6a9ac7__1.jpg"),
    ("/upload/5/1.jpg", f"test-data-dir/.cache/{_DIR_APP_NAME}/ce6a9ac7__1.jpg"),
    ("/data/upload/5/1.jpg", f"test-data-dir/.cache/{_DIR_APP_NAME}/ce6a9ac7__1.jpg"),
    # Local Storage
    ("/data/local-files?d=my_dir/1.jpg", f"test-data-dir/.cache/{_DIR_APP_NAME}/3e01c002__1.jpg"),
    ("/data/local-files?d=my_dir/2.jpg", f"test-data-dir/.cache/{_DIR_APP_NAME}/6ed75663__2.jpg"),
    # Cloud Storages
    ("s3://bucket/prefix/1.jpg", f"test-data-dir/.cache/{_DIR_APP_NAME}/4fca0572__1.jpg"),
    ("gs://bucket/prefix/1.jpg", f"test-data-dir/.cache/{_DIR_APP_NAME}/1e2682e4__1.jpg"),
    ("azure-blob://bucket/prefix/1.jpg", f"test-data-dir/.cache/{_DIR_APP_NAME}/1a4dc8b3__1.jpg"),
    # http(s) URLs
    ("http://example.com/1.jpg", f"test-data-dir/.cache/{_DIR_APP_NAME}/52ede693__1.jpg"),
]
@pytest.mark.parametrize("url,expected", test_cases)
@patch('label_studio_tools.core.utils.io.get_data_dir', return_value='test-data-dir/')
@patch('label_studio_tools.core.utils.io.get_cache_dir', return_value=f'test-data-dir/.cache/{_DIR_APP_NAME}')
def test_get_local_path(mock_get_data_dir, mock_get_cache_dir, url, expected):
    with patch('os.path.exists') as mock_exists:
        mock_exists.side_effect = os_path_exists

        x = get_local_path(
            url,
            access_token='secret',
            hostname='http://app.heartex.com',
            download_resources=False,
            task_id=1
        )
        print('\n ==> get_local_path = ', x)
        assert x == expected