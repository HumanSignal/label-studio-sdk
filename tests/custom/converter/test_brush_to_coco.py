# This file contains tests for brush_to_coco.py functionality

import json
import os
import tempfile
import numpy as np
import pytest
from unittest.mock import patch, MagicMock
import cv2

from label_studio_sdk.converter.exports.brush_to_coco import (
    generate_random_color,
    flatten,
    generate_contour_from_rle,
    generate_contour_from_polygon,
    convert_to_coco
)


def test_generate_random_color():
    """Test random color generation returns valid hex color"""
    color = generate_random_color()
    assert isinstance(color, str)
    assert color.startswith('#')
    assert len(color) == 7  # #RRGGBB format
    # Check that the hex characters are valid
    assert all(c in '0123456789abcdef' for c in color[1:].lower())


def test_flatten():
    """Test flattening of nested lists"""
    nested_list = [[1, 2], [3, 4], [5, 6]]
    flattened = list(flatten(nested_list))
    assert flattened == [1, 2, 3, 4, 5, 6]

    # Test with deeper nesting
    deeply_nested = [[[1, 2], 3], [4, [5, 6]]]
    flattened_deep = list(flatten(deeply_nested))
    assert flattened_deep == [1, 2, 3, 4, 5, 6]

    # Test with non-list
    assert list(flatten(5)) == [5]

@patch('cv2.findContours')
@patch('label_studio_sdk.converter.exports.brush_to_coco.brush_module.decode_rle')
def test_generate_contour_from_rle(mock_decode_rle, mock_find_contours):
    """Test contour generation from RLE data"""
    # Define parameters
    width, height = 10, 10
    channels = 4  # RGBA

    # Create a numpy array of zeros with the correct shape
    # Important: The mock return value needs to be the right size for
    # np.reshape(rle_binary, [height, width, channels]) to work properly
    mock_decoded_data = np.zeros(width * height * channels, dtype=np.uint8)

    # Set some data in the alpha channel (every 4th byte)
    for i in range(3, width * height * channels, channels):
        mock_decoded_data[i] = 255  # Set alpha channel to opaque

    # Setup the mock return value
    mock_decode_rle.return_value = mock_decoded_data

    # Mock the CV2 findContours return value
    contour = np.array([[[0, 0]], [[0, 10]], [[10, 10]], [[10, 0]]])
    mock_find_contours.return_value = ([contour], None)

    # Call the function under test - use bytes instead of string
    segmentation, bbox_list, area_list = generate_contour_from_rle(b"fake_rle", width, height)

    # Verify the results
    assert len(segmentation) == 1
    assert len(bbox_list) == 1
    assert len(area_list) == 1

    # Verify the contour was flattened correctly
    # The contour [[0,0], [0,5], [5,5], [5,0]] should be flattened to [0,0,0,5,5,5,5,0]
    assert segmentation[0] == [0, 0, 0, 10, 10, 10, 10, 0]

    # Verify bbox calculation - should be [x, y, width, height]
    assert bbox_list[0] == [0, 0, 10+1, 10+1]

    # Verify area calculation
    mock_find_contours.assert_called_once()


def test_generate_contour_from_polygon():
    """Test contour generation from polygon points"""
    # Points in percentage format
    points = [[10, 10], [10, 90], [90, 90], [90, 10]]

    # Call the function
    segmentation, bbox, area = generate_contour_from_polygon(points, 100, 100)

    # Verify results
    assert segmentation == [[10, 10, 10, 90, 90, 90, 90, 10]]
    assert bbox == [10, 10, 80+1, 80+1]
    assert isinstance(area, int)
    assert area > 0


@pytest.fixture
def sample_annotation_items():
    """Create sample annotation items for testing"""
    return [
        {
            'id': 1,
            'input': {
                'image': 'test_image.jpg'
            },
            'output': {
                'result': [
                    {
                        'type': 'brushlabels',
                        'brushlabels': ['class1'],
                        'rle': b"fake_rle_data",
                        'original_width': 100,
                        'original_height': 100
                    }
                ]
            },
            'completed_by': {'email': 'test@example.com'}  # Add completed_by field
        },
        {
            'id': 2,
            'input': {
                'image': 'test_image2.jpg'
            },
            'output': {
                'result': [
                    {
                        'type': 'polygonlabels',
                        'polygonlabels': ['class2'],
                        'points': [[10, 10], [10, 90], [90, 90], [90, 10]],
                        'original_width': 100,
                        'original_height': 100
                    }
                ]
            },
            'completed_by': {'email': 'test@example.com'}  # Add completed_by field
        }
    ]


@patch('label_studio_sdk.converter.exports.brush_to_coco.generate_contour_from_rle')
@patch('label_studio_sdk.converter.exports.brush_to_coco.generate_contour_from_polygon')
def test_convert_to_coco(mock_gen_polygon, mock_gen_rle, sample_annotation_items, tmp_path):
    """Test conversion of Label Studio annotations to COCO format"""
    # Mock the contour generation functions
    mock_gen_rle.return_value = ([[0, 0, 10, 10, 10, 0]], [[0, 0, 10, 10]], [100])
    mock_gen_polygon.return_value = ([[10, 10, 90, 90, 10, 90]], [10, 10, 80, 80], 6400)

    # Call the converter
    output_dir = str(tmp_path)
    output_file = convert_to_coco(sample_annotation_items, output_dir)

    # Verify output file exists
    assert os.path.exists(output_file)

    # Load and validate the JSON structure
    with open(output_file, 'r') as f:
        coco_data = json.load(f)

    # Verify structure
    assert 'images' in coco_data
    assert 'annotations' in coco_data
    assert 'categories' in coco_data

    # Check basic content
    assert len(coco_data['images']) == 2
    assert len(coco_data['annotations']) == 2
    assert len(coco_data['categories']) == 2

    # Check category names
    category_names = [cat['name'] for cat in coco_data['categories']]
    assert 'class1' in category_names
    assert 'class2' in category_names


@patch('label_studio_sdk.converter.exports.brush_to_coco.generate_contour_from_rle')
def test_convert_to_coco_with_missing_keys(mock_gen_rle, sample_annotation_items, tmp_path):
    """Test converter with missing required keys"""
    # Remove required keys
    incomplete_items = sample_annotation_items.copy()
    del incomplete_items[0]['output']['result'][0]['original_width']

    # Mock the contour generation function
    mock_gen_rle.return_value = ([[0, 0, 10, 10, 10, 0]], [[0, 0, 10, 10]], [100])

    # Call the converter
    output_dir = str(tmp_path)
    output_file = convert_to_coco(incomplete_items, output_dir)

    # Load and validate the JSON structure
    with open(output_file, 'r') as f:
        coco_data = json.load(f)

    # Only the polygon annotation should be processed
    assert len(coco_data['images']) == 1
    assert len(coco_data['annotations']) == 1


@patch('label_studio_sdk.converter.exports.brush_to_coco.generate_contour_from_rle')
def test_convert_to_coco_with_empty_annotations(mock_gen_rle, tmp_path):
    """Test converter with empty annotations"""
    empty_items = [
        {
            'id': 1,
            'input': {
                'image': 'test_image.jpg'
            },
            'output': {},
            'completed_by': {'email': 'test@example.com'}  # Add completed_by field
        }
    ]

    # Call the converter
    output_dir = str(tmp_path)
    output_file = convert_to_coco(empty_items, output_dir)

    # Load and validate the JSON structure
    with open(output_file, 'r') as f:
        coco_data = json.load(f)

    # No images or annotations should be processed
    assert len(coco_data['images']) == 0
    assert len(coco_data['annotations']) == 0


def test_convert_to_coco_with_custom_output_dir(sample_annotation_items, tmp_path):
    """Test converter with custom output directory"""
    # Create separate directories
    output_dir = os.path.join(tmp_path, "output")
    image_dir = os.path.join(tmp_path, "images")

    # Mock the contour generation functions
    with patch('label_studio_sdk.converter.exports.brush_to_coco.generate_contour_from_rle') as mock_gen_rle, \
         patch('label_studio_sdk.converter.exports.brush_to_coco.generate_contour_from_polygon') as mock_gen_polygon:

        mock_gen_rle.return_value = ([[0, 0, 10, 10, 10, 0]], [[0, 0, 10, 10]], [100])
        mock_gen_polygon.return_value = ([[10, 10, 90, 90, 10, 90]], [10, 10, 80, 80], 6400)

        # Call the converter with custom image directory
        output_file = convert_to_coco(sample_annotation_items, output_dir, image_dir)

    # Verify output file exists
    assert os.path.exists(output_file)
    assert os.path.exists(image_dir)

