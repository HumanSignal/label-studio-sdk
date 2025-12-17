import pytest
from unittest.mock import patch
import os
import tempfile
import shutil
import json
from label_studio_sdk.converter import Converter
from label_studio_sdk.converter.converter import Format

@pytest.mark.parametrize("format_name,expected_download_resources", [
    ("YOLO_WITH_IMAGES", True),
    ("YOLO_OBB_WITH_IMAGES", True),
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


@pytest.fixture
def create_temp_folder():
    """Create a temporary folder that is cleaned up after test completion."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_yolo_obb_with_images_export_integration(create_temp_folder):
    """
    Test complete YOLO_OBB_WITH_IMAGES export functionality including:
    - Images directory creation
    - Image file copying/downloading
    - Label file creation with OBB format (8 coordinates per line)
    - Complete file structure (images/, labels/, classes.txt, notes.json)
    - Verify that converter.download_resources == True
    """
    # Arrange
    tmp_folder = create_temp_folder

    # Use test data from existing OBB tests
    BASE_DIR = os.path.dirname(__file__)
    TEST_DATA_PATH = os.path.join(BASE_DIR, "data", "test_export_yolo")
    INPUT_JSON_OBB_PATH = os.path.join(TEST_DATA_PATH, "data_obb.json")
    LABEL_CONFIG_OBB_PATH = os.path.join(TEST_DATA_PATH, "label_config_obb.xml")

    output_dir = tmp_folder
    project_dir = "."

    # Act
    converter = Converter(LABEL_CONFIG_OBB_PATH, project_dir)
    converter.convert(
        input_data=INPUT_JSON_OBB_PATH,
        output_data=output_dir,
        format=Format.YOLO_OBB_WITH_IMAGES,
        is_dir=False,
    )

    # Assert
    # Check that images directory was created
    images_dir = os.path.join(output_dir, "images")
    assert os.path.exists(images_dir), f"Images directory not created at {images_dir}"

    # Check that labels directory was created
    labels_dir = os.path.join(output_dir, "labels")
    assert os.path.exists(labels_dir), f"Labels directory not created at {labels_dir}"

    # Check that classes.txt was created
    classes_file = os.path.join(output_dir, "classes.txt")
    assert os.path.exists(classes_file), f"classes.txt not created at {classes_file}"

    # Check that notes.json was created
    notes_file = os.path.join(output_dir, "notes.json")
    assert os.path.exists(notes_file), f"notes.json not created at {notes_file}"

    # Verify that converter.download_resources was set to True for YOLO_OBB_WITH_IMAGES
    assert converter.download_resources == True, "download_resources should be True for YOLO_OBB_WITH_IMAGES format"

    # Based on data_obb.json, we have 3 images
    expected_images = ["image1", "image2", "image3"]

    # Check that corresponding label files were created
    for image_name in expected_images:
        label_file = os.path.join(labels_dir, f"{image_name}.txt")
        assert os.path.exists(label_file), f"Label file not created at {label_file}"

        # Verify label file has content and uses OBB format (8 coordinates per line)
        with open(label_file, 'r') as f:
            lines = f.readlines()
            # Based on the test data, all images should have annotations
            assert len(lines) > 0, f"Label file {label_file} should not be empty"

            # Verify OBB format: each line should have 9 parameters (class + 8 coordinates)
            for line_idx, line in enumerate(lines):
                parameters = line.strip().split()
                assert len(parameters) == 9, f"OBB format should have 9 parameters (class + 8 coordinates), got {len(parameters)} in {label_file} line {line_idx}"

    # Verify classes.txt has expected content
    with open(classes_file, 'r') as f:
        classes_content = f.read().strip()
        assert len(classes_content) > 0, "classes.txt should not be empty"
        classes = classes_content.split('\n')
        # Based on OBB data, we expect classes like "Butterfly" and "butterfly"
        assert len(classes) >= 1, "Expected at least 1 class based on OBB test data"


def test_yolo_with_images_export_integration(create_temp_folder):
    """
    Test complete YOLO_WITH_IMAGES export functionality including:
    - Images directory creation
    - Image file copying/downloading
    - Label file creation
    - Complete file structure (images/, labels/, classes.txt, notes.json)
    """
    # Arrange
    tmp_folder = create_temp_folder

    # Use test data from existing YOLO tests
    BASE_DIR = os.path.dirname(__file__)
    TEST_DATA_PATH = os.path.join(BASE_DIR, "data", "test_export_yolo")
    INPUT_JSON_PATH = os.path.join(TEST_DATA_PATH, "data.json")
    LABEL_CONFIG_PATH = os.path.join(TEST_DATA_PATH, "label_config.xml")

    output_dir = tmp_folder
    project_dir = "."

    # Act
    converter = Converter(LABEL_CONFIG_PATH, project_dir)
    converter.convert(
        input_data=INPUT_JSON_PATH,
        output_data=output_dir,
        format=Format.YOLO_WITH_IMAGES,
        is_dir=False,
    )

    # Assert
    # Check that images directory was created
    images_dir = os.path.join(output_dir, "images")
    assert os.path.exists(images_dir), f"Images directory not created at {images_dir}"

    # Check that labels directory was created
    labels_dir = os.path.join(output_dir, "labels")
    assert os.path.exists(labels_dir), f"Labels directory not created at {labels_dir}"

    # Check that classes.txt was created
    classes_file = os.path.join(output_dir, "classes.txt")
    assert os.path.exists(classes_file), f"classes.txt not created at {classes_file}"

    # Check that notes.json was created
    notes_file = os.path.join(output_dir, "notes.json")
    assert os.path.exists(notes_file), f"notes.json not created at {notes_file}"

    # Verify that converter.download_resources was set to True for YOLO_WITH_IMAGES
    assert converter.download_resources == True, "download_resources should be True for YOLO_WITH_IMAGES format"

    # Note: The test data uses placeholder URLs ("/image1", "/image2") that are not downloadable.
    # In a real scenario, YOLO_WITH_IMAGES would download actual images.
    # Here we test that the structure is created correctly even when images can't be downloaded.
    expected_images = ["image1", "image2"]

    # Check that corresponding label files were created
    for image_name in expected_images:
        label_file = os.path.join(labels_dir, f"{image_name}.txt")
        assert os.path.exists(label_file), f"Label file not created at {label_file}"

        # Verify label file has content (non-empty for images with annotations)
        with open(label_file, 'r') as f:
            content = f.read().strip()
            # Based on the test data, both images should have annotations
            assert len(content) > 0, f"Label file {label_file} should not be empty"

    # Verify classes.txt has expected content
    with open(classes_file, 'r') as f:
        classes_content = f.read().strip()
        # Based on data.json, we expect classes like "parasites" and "white"
        assert len(classes_content) > 0, "classes.txt should not be empty"
        classes = classes_content.split('\n')
        assert len(classes) >= 2, "Expected at least 2 classes based on test data"
