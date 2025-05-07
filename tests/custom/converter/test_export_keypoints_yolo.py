import os
import shutil
import tempfile
from pathlib import Path

import pytest
from label_studio_sdk.converter import Converter
from .utils import check_equal_list_of_strings, get_os_walk

BASE_DIR = os.path.dirname(__file__)
TEST_DATA_PATH = os.path.join(BASE_DIR, 'data', 'test_export_yolo')
INPUT_JSON_PATH = os.path.join(BASE_DIR, TEST_DATA_PATH, 'data_keypoints.json')
LABEL_CONFIG_PATH = os.path.join(
    BASE_DIR, TEST_DATA_PATH, 'label_config_keypoints.xml'
)


@pytest.fixture
def create_temp_folder():
    # Create a temporary folder
    temp_dir = tempfile.mkdtemp()

    # Yield the temporary folder
    yield temp_dir

    # Remove the temporary folder after the test
    shutil.rmtree(temp_dir)


def test_convert_keypoints_to_yolo(create_temp_folder):
    """Test exporting keypoints in YOLO format from Label Studio annotations"""
    # Generates a temporary folder and return the absolute path
    tmp_folder = create_temp_folder

    output_dir = tmp_folder
    output_image_dir = os.path.join(output_dir, 'tmp_image')
    output_label_dir = os.path.join(output_dir, 'tmp_label')
    project_dir = '.'

    converter = Converter(LABEL_CONFIG_PATH, project_dir)
    converter.convert_to_yolo(
        INPUT_JSON_PATH,
        output_dir,
        output_image_dir=output_image_dir,
        output_label_dir=output_label_dir,
        is_dir=False,
        split_labelers=False,
    )

    abs_path_label_dir = os.path.abspath(output_label_dir)
    expected_paths = [
        os.path.join(abs_path_label_dir, 'image1.txt'),
    ]
    generated_paths = get_os_walk(abs_path_label_dir)

    # Check all files and subfolders have been generated
    assert check_equal_list_of_strings(
        expected_paths, generated_paths
    ), f'Generated files: \n  {generated_paths} \n do not match expected ones: \n {expected_paths}'

    # Check that the files contain the expected format for keypoints
    for file_path in generated_paths:
        with open(file_path) as f:
            lines = f.readlines()
            assert (
                len(lines) > 0
            ), f'Expected at least one annotation in file {file_path}'

            for line in lines:
                values = line.strip().split()

                # Basic YOLO format requires at least class_id, x, y, width, height
                assert (
                    len(values) >= 5
                ), f'Line does not have the basic YOLO format: {line}'

                # If keypoints are included, there should be more values (at least one keypoint = 2 or 3 more values)
                if len(values) > 5:
                    # Check that keypoint coordinates are valid numbers
                    keypoints = values[5:]
                    for kp_val in keypoints:
                        try:
                            float(kp_val)
                        except ValueError:
                            assert (
                                False
                            ), f'Invalid keypoint value in line: {line}'

                    # Keypoints should come in pairs (x,y) or triplets (x,y,visibility)
                    keypoint_count = len(keypoints)
                    assert (
                        keypoint_count % 2 == 0 or keypoint_count % 3 == 0
                    ), f'Keypoints should be in pairs (x,y) or triplets (x,y,v), but got {keypoint_count} values'


def test_keypoints_yolo_values(create_temp_folder):
    """Test that keypoints in YOLO format have correct values"""
    tmp_folder = create_temp_folder
    output_dir = tmp_folder
    output_image_dir = os.path.join(output_dir, 'tmp_image')
    output_label_dir = os.path.join(output_dir, 'tmp_label')
    project_dir = '.'

    converter = Converter(LABEL_CONFIG_PATH, project_dir)
    converter.convert_to_yolo(
        INPUT_JSON_PATH,
        output_dir,
        output_image_dir=output_image_dir,
        output_label_dir=output_label_dir,
        is_dir=False,
        split_labelers=False,
    )

    # Get the generated YOLO file
    abs_path_label_dir = os.path.abspath(output_label_dir)
    yolo_file_path = os.path.join(abs_path_label_dir, 'image1.txt')

    with open(yolo_file_path) as f:
        lines = f.readlines()
        assert (
            len(lines) > 0
        ), 'No annotations found in the generated YOLO file'

        # Check that at least one line contains keypoints
        keypoints_found = False
        for line in lines:
            values = line.strip().split()
            if (
                len(values) > 5
            ):  # Basic YOLO (class, x, y, w, h) plus at least one keypoint
                keypoints_found = True

                # Validate keypoint values are in valid range [0, 1]
                keypoints = values[5:]
                for i, kp_val in enumerate(keypoints):
                    # Visibility values (every 3rd value if using triplets) might be 0, 1, or 2
                    # x and y coordinates should be in range [0, 1]
                    if (i + 1) % 3 != 0:  # Not a visibility value
                        kp_float = float(kp_val)
                        assert (
                            0 <= kp_float <= 1
                        ), f'Keypoint coordinate {kp_float} is out of range [0, 1]'

        assert (
            keypoints_found
        ), f'No keypoints found in the generated YOLO file: {lines}'
