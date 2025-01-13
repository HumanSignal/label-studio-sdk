from unittest.mock import patch
import pytest
from label_studio_sdk.converter import Converter

def test_yolo_with_images_download_resources():
    """Test that download_resources is set correctly for YOLO_WITH_IMAGES format"""

    with patch.object(Converter, 'convert_to_yolo', return_value=None) as mock_method:
        converter = Converter(config={}, project_dir=".")
        converter.convert(
            input_data="dummy_input",
            output_data="dummy_output",
            format="YOLO_WITH_IMAGES",
            is_dir=False,
        )
        assert converter.download_resources is True
        mock_method.assert_called_once()
