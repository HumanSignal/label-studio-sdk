import pytest
from unittest.mock import patch
from label_studio_sdk.converter import Converter

@pytest.mark.parametrize("format_name,expected_download_resources", [
    ("YOLO_WITH_IMAGES", True),
    ("YOLO", False)
])
def test_download_resources(format_name, expected_download_resources):
    """Test that download_resources is True for YOLO_WITH_IMAGES and False for simple YOLO"""
    with patch.object(Converter, 'convert_to_yolo', return_value=None) as mock_convert:
        converter = Converter(config={}, project_dir=".")
        converter.convert(
            input_data="dummy_input",
            output_data="dummy_output",
            format=format_name,
            is_dir=False,
        )
        assert converter.download_resources == expected_download_resources
        mock_convert.assert_called_once()
