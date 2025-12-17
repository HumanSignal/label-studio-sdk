import math
import os
import shutil
import tempfile

import numpy as np
import pytest

from label_studio_sdk.converter import Converter
from label_studio_sdk.converter.utils import (
    convert_annotation_to_yolo,
    convert_annotation_to_yolo_obb,
    convert_yolo_obb_to_annotation,
)
from label_studio_sdk.converter.exports.yolo import process_keypoints_for_yolo
from .utils import almost_equal_1d, almost_equal_2d, get_os_walk, check_equal_list_of_strings

BASE_DIR = os.path.dirname(__file__)
TEST_DATA_PATH = os.path.join(BASE_DIR, "data", "test_export_yolo")
INPUT_JSON_PATH = os.path.join(BASE_DIR, TEST_DATA_PATH, "data.json")
INPUT_JSON_OBB_PATH = os.path.join(BASE_DIR, TEST_DATA_PATH, "data_obb.json")
LABEL_CONFIG_PATH = os.path.join(BASE_DIR, TEST_DATA_PATH, "label_config.xml")
LABEL_CONFIG_OBB_PATH = os.path.join(BASE_DIR, TEST_DATA_PATH, "label_config_obb.xml")
INPUT_JSON_PATH_POLYGONS = os.path.join(BASE_DIR, TEST_DATA_PATH, "data_polygons.json")
LABEL_CONFIG_PATH_POLYGONS = os.path.join(
    BASE_DIR, TEST_DATA_PATH, "label_config_polygons.xml"
)


@pytest.fixture
def create_temp_folder():
    # Create a temporary folder
    temp_dir = tempfile.mkdtemp()

    # Yield the temporary folder
    yield temp_dir

    # Remove the temporary folder after the test
    shutil.rmtree(temp_dir)


def test_convert_to_yolo(create_temp_folder):
    """Check converstion label_studio json exported file to yolo with multiple labelers"""

    # Generates a temporary folder and return the absolute path
    # The temporary folder contains all the data generate by the following function
    # For debugging replace create_temp_folder with "./tmp"
    tmp_folder = create_temp_folder

    output_dir = tmp_folder
    output_image_dir = os.path.join(output_dir, "tmp_image")
    output_label_dir = os.path.join(output_dir, "tmp_label")
    project_dir = "."

    converter = Converter(LABEL_CONFIG_PATH, project_dir)
    converter.convert_to_yolo(
        INPUT_JSON_PATH,
        output_dir,
        output_image_dir=output_image_dir,
        output_label_dir=output_label_dir,
        is_dir=False,
        split_labelers=True,
    )

    abs_path_label_dir = os.path.abspath(output_label_dir)
    expected_paths = [
        os.path.join(abs_path_label_dir, "1", "image1.txt"),
        os.path.join(abs_path_label_dir, "1", "image2.txt"),
        os.path.join(abs_path_label_dir, "2", "image1.txt"),
    ]
    generated_paths = get_os_walk(abs_path_label_dir)
    # Check all files and subfolders have been generated.
    assert check_equal_list_of_strings(
        expected_paths, generated_paths
    ), f"Generated file: \n  {generated_paths} \n does not match expected ones: \n {expected_paths}"
    # Check all the annotations have been converted to yolo
    for file in expected_paths:
        with open(file) as f:
            lines = f.readlines()
            assert (
                len(lines) == 2
            ), f"Expect different number of annotations in file {file}."


def test_convert_to_yolo_obb(create_temp_folder):
    """Check conversion label_studio json exported file to a yolo obb compatible format"""

    # Generates a temporary folder and return the absolute path
    # The temporary folder contains all the data generate by the following function
    # For debugging replace create_temp_folder with "./tmp"
    tmp_folder = create_temp_folder

    output_dir = tmp_folder
    output_image_dir = os.path.join(output_dir, "tmp_image")
    output_label_dir = os.path.join(output_dir, "tmp_label")
    project_dir = "."

    converter = Converter(LABEL_CONFIG_OBB_PATH, project_dir)
    converter.convert_to_yolo(
        INPUT_JSON_OBB_PATH,
        output_dir,
        output_image_dir=output_image_dir,
        output_label_dir=output_label_dir,
        is_dir=False,
        split_labelers=False,
        is_obb=True,
    )

    abs_path_label_dir = os.path.abspath(output_label_dir)
    expected_paths = [
        os.path.join(abs_path_label_dir, "image1.txt"),
        os.path.join(abs_path_label_dir, "image2.txt"),
        os.path.join(abs_path_label_dir, "image3.txt"),
    ]
    generated_paths = get_os_walk(abs_path_label_dir)
    # Check all files and subfolders have been generated.
    assert check_equal_list_of_strings(
        expected_paths, generated_paths
    ), f"Generated file: \n  {generated_paths} \n does not match expected ones: \n {expected_paths}"

    # Check all the annotations have been converted to yolo
    expected_annotations = [23, 1, 1]
    for fidx, file in enumerate(expected_paths):
        with open(file) as f:
            lines = f.readlines()
            assert (
                len(lines) == expected_annotations[fidx]
            ), f"Expect different number of annotations in file {file}."
            for idx, line in enumerate(lines):
                parameters = line.split(" ")
                total_parameters = len(parameters)
                assert (
                    total_parameters == 9
                ), f"Expected 9 parameters but got {total_parameters} in line {idx}"


def test_convert_polygons_to_yolo(create_temp_folder):
    """Check conversion label_studio json exported file to yolo with polygons"""

    # Generates a temporary folder and return the absolute path
    # The temporary folder contains all the data generate by the following function
    # For debugging replace create_temp_folder with "./tmp"
    tmp_folder = create_temp_folder

    output_dir = tmp_folder
    output_image_dir = os.path.join(output_dir, "tmp_image")
    output_label_dir = os.path.join(output_dir, "tmp_label")
    project_dir = "."

    converter = Converter(LABEL_CONFIG_PATH_POLYGONS, project_dir)
    converter.convert_to_yolo(
        INPUT_JSON_PATH_POLYGONS,
        output_dir,
        output_image_dir=output_image_dir,
        output_label_dir=output_label_dir,
        is_dir=False,
        split_labelers=False,
    )

    abs_path_label_dir = os.path.abspath(output_label_dir)
    expected_paths = [os.path.join(abs_path_label_dir, "image2.txt")]
    generated_paths = get_os_walk(abs_path_label_dir)
    # Check all files and subfolders have been generated.
    assert check_equal_list_of_strings(
        expected_paths, generated_paths
    ), f"Generated file: \n  {generated_paths} \n does not match expected ones: \n {expected_paths}"
    # Check all the annotations have been converted to yolo
    for file in expected_paths:
        with open(file) as f:
            lines = f.readlines()
            assert (
                len(lines) == 1
            ), f"Expect different number of annotations in file {file}."


def test_convert_annotation_to_yolo_format():
    """
    Verify conversion from LS annotation to normalized Yolo format.

    This test case evaluates the conversion of LS (Label Studio) annotations to normalized
    Yolo format. It iterates over a list of LS annotations and compares the result of the
    conversion to expected values.

    Test Procedure:
    1. Define LS annotations and their corresponding expected Yolo representations.
    2. Iterate over each LS annotation and perform the conversion.
    3. Compare the result to the expected Yolo format.
    """

    annotations = [
        {
            "x": 37.15846994535519,
            "y": 70.67395264116576,
            "width": 4.189435336976321,
            "height": 4.735883424408015,
        },
        {
            "x": 57.79102500413977,
            "y": 62.87464812054977,
            "width": 3.808577579069383,
            "height": 4.636529226693169,
        },
        {
            "x": 37.88706739526412,
            "y": 71.76684881602914,
            "width": 3.8251366120218573,
            "height": 4.553734061930784,
        },
    ]

    expectations = [
        (
            0.39253187613843354,
            0.7304189435336975,
            0.04189435336976321,
            0.04735883424408015,
        ),
        (
            0.5969531379367445,
            0.6519291273389635,
            0.03808577579069383,
            0.04636529226693169,
        ),
        (
            0.39799635701275043,
            0.7404371584699453,
            0.03825136612021857,
            0.04553734061930784,
        ),
    ]

    for idx, annotation in enumerate(annotations):
        result = convert_annotation_to_yolo(annotation)
        assert almost_equal_1d(
            result, expectations[idx]
        ), f"Converted LS annotation to normalized Yolo format does not match expected result at index {idx}"


def test_convert_invalid_annotation_to_yolo_format():
    """
    Verify conversion of incomplete or empty annotations to Yolo format.

    This test case evaluates the conversion of incomplete or empty annotations to Yolo format.
    It iterates over a list of annotations with missing keys or an empty dictionary and checks
    whether the function `convert_annotation_to_yolo` returns None for each invalid annotation.

    Test Procedure:
    1. Define a list of incomplete or empty annotations.
    2. Iterate over each annotation and call the conversion function.
    3. Verify that the function returns None for each invalid annotation.
    """
    annotations = [
        {
            "y": 70.67395264116576,
            "width": 4.189435336976321,
            "height": 4.735883424408015,
        },
        {
            "x": 57.79102500413977,
            "width": 3.808577579069383,
            "height": 4.636529226693169,
        },
        {"x": 37.88706739526412, "y": 71.76684881602914, "height": 4.553734061930784},
        {
            "x": 37.88706739526412,
            "y": 71.76684881602914,
            "width": 3.8251366120218573,
        },
        {
            # empty dict
        },
    ]

    for idx, annotation in enumerate(annotations):
        result = convert_annotation_to_yolo(annotation)
        assert result is None, f"Expected annotation at index {idx} to be invalid"


def test_convert_annotation_to_yolo_with_none_values():
    """
    Verify conversion handles None values safely by returning None.
    """
    annotations_with_none = [
        {"x": None, "y": 10.0, "width": 5.0, "height": 5.0},
        {"x": 10.0, "y": None, "width": 5.0, "height": 5.0},
        {"x": 10.0, "y": 10.0, "width": None, "height": 5.0},
        {"x": 10.0, "y": 10.0, "width": 5.0, "height": None},
    ]
    for idx, ann in enumerate(annotations_with_none):
        result = convert_annotation_to_yolo(ann)
        assert result is None, f"Expected None for annotation with None values at index {idx}"


def test_keypoints_yolo_export_with_empty_rectanglelabels(create_temp_folder):
    """
    Ensure keypoints export path doesn't raise IndexError when rectanglelabels is empty.
    """
    tmp_folder = create_temp_folder
    label_path = os.path.join(tmp_folder, "empty_rects.txt")

    # Categories and mapping (class names to ids)
    categories = [{"id": 0, "name": "classA"}]
    category_name_to_id = {"classA": 0}

    # Labels contain a rectangle with empty rectanglelabels (should be skipped safely)
    labels = [
        {
            "id": "6SX02sLq5c",
            "type": "rectanglelabels",
            "x": 91.90256747860435,
            "y": 59.97366688610929,
            "width": 0.658327847267941,
            "height": 2.106649111257404,
            "rotation": 0,
            "rectanglelabels": [],
        }
    ]

    # Should not raise; output file should be created and empty
    process_keypoints_for_yolo(
        labels, label_path, category_name_to_id, categories, is_obb=False, kp_order=[]
    )
    with open(label_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    assert content == ""


def test_keypoints_yolo_export_with_empty_keypointlabels(create_temp_folder):
    """
    Ensure keypoints export path doesn't raise IndexError when keypointlabels is empty.
    """
    tmp_folder = create_temp_folder
    label_path = os.path.join(tmp_folder, "empty_kps.txt")

    categories = [{"id": 0, "name": "classA"}]
    category_name_to_id = {"classA": 0}

    # First, provide a valid rectangle so rectangles dict is created
    labels = [
        {
            "id": "rect-1",
            "type": "rectanglelabels",
            "x": 10.0,
            "y": 10.0,
            "width": 10.0,
            "height": 10.0,
            "rotation": 0,
            "rectanglelabels": ["classA"],
        },
        {
            "id": "kp-1",
            "type": "keypointlabels",
            "parentID": "rect-1",
            "x": 15.0,
            "y": 15.0,
            "keypointlabels": [],
        },
    ]

    # Should not raise; output should contain one line (rectangle only, no keypoints contributed)
    process_keypoints_for_yolo(
        labels, label_path, category_name_to_id, categories, is_obb=False, kp_order=["nose"]
    )
    with open(label_path, "r", encoding="utf-8") as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip()]
    assert len(lines) == 1

def test_convert_annotation_to_yolo_obb_format():
    """
    Verify conversion from LS annotation to normalized Yolo OBB format.

    This test case evaluates the conversion of LS (Label Studio) annotations to normalized
    Yolo Oriented Bounding Box (OBB) format. It iterates over a list of LS annotations and
    compares the result of the conversion to expected values.

    Test Procedure:
    1. Define LS annotations and their corresponding expected Yolo OBB representations.
    2. Iterate over each LS annotation and perform the conversion.
    3. Compare the result to the expected Yolo OBB format.
    """

    annotations = [
        {
            "original_width": 597,
            "original_height": 768,
            "x": 11.552474514692952,
            "y": 80.83731446979957,
            "width": 19.0454700246567,
            "height": 6.629026203797071,
            "rotation": 328.33240366032836,
        },
        {
            "original_width": 597,
            "original_height": 768,
            "x": 32.94000909818857,
            "y": 77.3890916826675,
            "width": 8.108689897439085,
            "height": 7.490685233798283,
            "rotation": 345.3894551068102,
        },
        {
            "original_width": 597,
            "original_height": 768,
            "x": 16.814074232397514,
            "y": 57.43596079245723,
            "width": 18.218991060518677,
            "height": 6.298347014251024,
            "rotation": 43.67748910099408,
        },
    ]

    expectations = [
        [
            (0.11552474514692952, 0.8083731446979957),  # top left
            (0.27762229351938456, 0.7306489626734597),  # top right
            (0.3223923846720476, 0.7870691452334665),  # bottom right
            (0.16029483629959254, 0.8647933272580025),  # bottom left
        ],
        [
            (0.32940009098188566, 0.7738909168266751),  # top left
            (0.4078648636432219, 0.7579911558782483),  # top right
            (0.43217208011269465, 0.830475727539231),  # bottom right
            (0.35370730745135837, 0.8463754884876579),  # bottom left
        ],
        [
            (0.16814074232397513, 0.5743596079245723),  # top left
            (0.29990750552628187, 0.6721650332758418),  # top right
            (0.24395249444460837, 0.7177171056620688),  # bottom right
            (0.11218573124230163, 0.6199116803107994),  # bottom left
        ],
    ]

    for idx, annotation in enumerate(annotations):
        result = convert_annotation_to_yolo_obb(annotation)
        print("result = ", result)
        assert almost_equal_2d(
            result, expectations[idx]
        ), f"Converted LS annotation to normalized Yolo OBB-format does not match expected result at index {idx}"


def test_convert_invalid_annotation_to_yolo_obb_format():
    """
    Verify conversion of incomplete or empty annotations.

    This test iterates over incomplete or empty annotations to simulate invalid input scenarios.
    It checks if `convert_annotation_to_yolo_obb` returns None for each invalid annotation.

    Annotations include cases with missing keys and an empty annotation.

    Test Procedure:
    1. Define incomplete or empty annotations.
    2. Iterate over each annotation and call the conversion function.
    3. Verify the function returns None for each invalid annotation.
    """

    # Annotations with missing keys to simulate invalid annotations...
    annotations = [
        {
            "original_height": 768,
            "x": 16.814074232397514,
            "y": 57.43596079245723,
            "width": 18.218991060518677,
            "height": 6.298347014251024,
            "rotation": 345.3894551068102,
        },
        {
            "original_width": 597,
            "x": 16.814074232397514,
            "y": 57.43596079245723,
            "width": 18.218991060518677,
            "height": 6.298347014251024,
            "rotation": 345.3894551068102,
        },
        {
            "original_width": 597,
            "original_height": 768,
            "y": 57.43596079245723,
            "width": 18.218991060518677,
            "height": 6.298347014251024,
            "rotation": 345.3894551068102,
        },
        {
            "original_width": 597,
            "original_height": 768,
            "x": 16.814074232397514,
            "width": 18.218991060518677,
            "height": 6.298347014251024,
            "rotation": 345.3894551068102,
        },
        {
            "original_width": 597,
            "original_height": 768,
            "x": 16.814074232397514,
            "y": 57.43596079245723,
            "height": 6.298347014251024,
            "rotation": 345.3894551068102,
        },
        {
            "original_width": 597,
            "original_height": 768,
            "x": 16.814074232397514,
            "y": 57.43596079245723,
            "width": 18.218991060518677,
            "rotation": 345.3894551068102,
        },
        {
            "original_width": 597,
            "original_height": 768,
            "x": 16.814074232397514,
            "y": 57.43596079245723,
            "width": 18.218991060518677,
            "height": 6.298347014251024,
        },
        {
            # empty annotation
        },
    ]

    for idx, annotation in enumerate(annotations):
        result = convert_annotation_to_yolo_obb(annotation)
        assert (
            result is None
        ), f"Expected annotation for OBB at index {idx} to be invalid"


def test_annotation_to_yolo_obb_and_back():
    label_data = {
        "original_width": 1024,
        "original_height": 768,
        "x": 40.0,
        "y": 30.0,
        "width": 20.0,
        "height": 10.0,
        "rotation": 45.0,
    }

    yolo_obb = convert_annotation_to_yolo_obb(label_data, normalize=False)

    label_converted_back = convert_yolo_obb_to_annotation(
        [coord for point in yolo_obb for coord in point],
        label_data["original_width"],
        label_data["original_height"],
    )

    return (
        math.isclose(label_data["x"], label_converted_back["x"], rel_tol=1e-5),
        math.isclose(label_data["y"], label_converted_back["y"], rel_tol=1e-5),
        math.isclose(label_data["width"], label_converted_back["width"], rel_tol=1e-5),
        math.isclose(
            label_data["height"], label_converted_back["height"], rel_tol=1e-5
        ),
        math.isclose(
            label_data["rotation"], label_converted_back["rotation"], rel_tol=1e-5
        ),
    )


def test_yolo_obb_to_annotation_to_yolo():
    inv_data = [
        10,
        20,
        39.54423259036624,
        26.511806662509885,
        33.98749090502447,
        65.9041167829982,
        4.443258314658229,
        59.39231012048832,
    ]
    original_width = 10
    original_height = 10

    annotation_data = convert_yolo_obb_to_annotation(
        inv_data, original_width, original_height
    )
    yolo_data = convert_annotation_to_yolo_obb(annotation_data, normalize=False)

    assert np.allclose(
        yolo_data, np.array(inv_data).reshape((4, 2)), rtol=1, atol=1  # 1 pixel tolerance
    ), f"Test failed: {yolo_data} != {inv_data}"


def test_convert_directory_to_yolo(create_temp_folder):
    """Test directory input processing with is_dir=True - should match single JSON file output"""
    import json

    # Setup test directories
    tmp_folder = create_temp_folder
    input_dir = os.path.join(tmp_folder, "input_tasks")
    os.makedirs(input_dir)

    # Create separate output directories for comparison
    dir_output_dir = os.path.join(tmp_folder, "dir_output")
    dir_output_image_dir = os.path.join(dir_output_dir, "tmp_image")
    dir_output_label_dir = os.path.join(dir_output_dir, "tmp_label")

    single_output_dir = os.path.join(tmp_folder, "single_output")
    single_output_image_dir = os.path.join(single_output_dir, "tmp_image")
    single_output_label_dir = os.path.join(single_output_dir, "tmp_label")

    # Load original test data
    with open(INPUT_JSON_PATH, 'r') as f:
        tasks = json.load(f)

    # Split tasks into individual JSON files
    for i, task in enumerate(tasks):
        task_file = os.path.join(input_dir, f"task_{task['id']}.json")
        with open(task_file, 'w') as f:
            json.dump([task], f)  # Each file contains a list with one task

    project_dir = "."
    converter = Converter(LABEL_CONFIG_PATH, project_dir)

    # Convert directory with is_dir=True
    converter.convert_to_yolo(
        input_dir,
        dir_output_dir,
        output_image_dir=dir_output_image_dir,
        output_label_dir=dir_output_label_dir,
        is_dir=True,
        split_labelers=True,
    )

    # Convert single JSON file with is_dir=False for comparison
    converter.convert_to_yolo(
        INPUT_JSON_PATH,
        single_output_dir,
        output_image_dir=single_output_image_dir,
        output_label_dir=single_output_label_dir,
        is_dir=False,
        split_labelers=True,
    )

    # Verify directory processing produces same structure as single file
    dir_generated_paths = get_os_walk(os.path.abspath(dir_output_label_dir))
    single_generated_paths = get_os_walk(os.path.abspath(single_output_label_dir))

    # Convert to relative paths for comparison
    dir_relative_paths = [os.path.relpath(p, os.path.abspath(dir_output_label_dir)) for p in dir_generated_paths]
    single_relative_paths = [os.path.relpath(p, os.path.abspath(single_output_label_dir)) for p in single_generated_paths]

    # Should produce identical file structures
    assert check_equal_list_of_strings(
        dir_relative_paths, single_relative_paths
    ), f"Directory output: \n  {dir_relative_paths} \n does not match single file output: \n {single_relative_paths}"

    # Compare actual file contents
    for dir_file in dir_generated_paths:
        # Get corresponding single file path
        relative_path = os.path.relpath(dir_file, os.path.abspath(dir_output_label_dir))
        single_file = os.path.join(os.path.abspath(single_output_label_dir), relative_path)

        # Read both files and compare content
        with open(dir_file, 'r') as f:
            dir_content = f.read().strip()
        with open(single_file, 'r') as f:
            single_content = f.read().strip()

        assert dir_content == single_content, \
            f"Content mismatch in {relative_path}:\nDirectory: {dir_content}\nSingle: {single_content}"


