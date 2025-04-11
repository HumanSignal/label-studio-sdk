"""
Convert brush annotations and polygon annotations to COCO format.
This module handles RLE encoded brush masks and converts them to COCO segmentation format.
"""
import logging
import random
import io
import os
import json
import numpy as np
import cv2
from copy import deepcopy
from datetime import datetime

from label_studio_sdk.converter.utils import ensure_dir, get_annotator
import label_studio_sdk.converter.brush as brush_module

logger = logging.getLogger(__name__)


def generate_random_color():
    """Generates a random hex color for category visualization"""
    return '#{:02x}{:02x}{:02x}'.format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def flatten(item):
    """Flatten nested lists for segmentation format"""
    if isinstance(item, list):
        for subitem in item:
            yield from flatten(subitem)
    else:
        yield item


def generate_contour_from_rle(rle, original_width, original_height):
    """Convert RLE encoded masks to COCO segmentation format
    
    Args:
        rle: RLE encoded mask data
        original_width: Width of the original image
        original_height: Height of the original image
        
    Returns:
        tuple: (segmentation, bbox_list, area_list) in COCO format
    """
    # Ensure rle is bytes, not string
    if isinstance(rle, str):
        rle = rle.encode('utf-8')
        
    # Decode RLE
    try:
        rle_binary = brush_module.decode_rle(rle)
    except Exception as e:
        logger.warning(f"Failed to decode RLE: {e}")
        return [], [], []
    
    # Reshape to image dimensions with 4 channels (RGBA)
    try:
        reshaped_image = np.reshape(rle_binary, [original_height, original_width, 4])
    except Exception as e:
        logger.warning(f"Failed to reshape RLE data: {e}")
        return [], [], []
    
    # Use only the alpha channel for contour detection
    alpha_channel = np.array(reshaped_image[:, :, 3]).astype('uint8')
    
    # Find contours
    contours, _ = cv2.findContours(
        alpha_channel, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    segmentation = []
    bbox_list = []
    area_list = []
    for contour in contours:
        # OpenCV contours are in format [[[x1,y1]], [[x2,y2]], ...], 
        # we need to convert to a flat list [x1,y1,x2,y2,...]
        contour_points = [point[0] for point in contour]
        
        # Flatten to a single list
        contour_flat = []
        for point in contour_points:
            contour_flat.extend(point.tolist())
        
        # Check if we have at least 3 points (6 coordinates) for a valid polygon
        if len(contour_points) >= 3:
            segmentation.append(contour_flat)

            x, y, w, h = cv2.boundingRect(contour)
            bbox_list.append([x, y, w, h])   # Format: [top-left x, top-left y, width, height]

            # Compute the area of the contour
            area = cv2.contourArea(contour)
            area_list.append(int(area))

    return segmentation, bbox_list, area_list


def generate_contour_from_polygon(points, original_width, original_height):
    """Convert polygon annotations to COCO segmentation format
    
    Args:
        points: List of [x, y] points in percentage format
        original_width: Width of the original image
        original_height: Height of the original image
        
    Returns:
        tuple: (segmentation, bbox, area) in COCO format
    """
    # Convert from percentage to absolute coordinates
    modified_points = [
        [round(x * original_width / 100), round(y * original_height / 100)]
        for x, y in points
    ]

    # Initialize lists
    segmentation = [list(flatten(modified_points))]

    # Convert points to a NumPy array and reshape for OpenCV
    contour = np.array(modified_points, dtype=np.float32).reshape((-1, 1, 2))

    # Calculate bounding box
    bbox = cv2.boundingRect(contour)
    bbox = [int(coordinate) for coordinate in bbox]

    # Compute the area of the contour
    area = cv2.contourArea(contour)

    return segmentation, bbox, int(area)


def convert_to_coco(items, output_dir, output_image_dir=None):
    """Convert Label Studio annotations to COCO format

    Args:
        items: Iterable of annotation items
        output_dir: Directory where to save the resulting COCO JSON
        output_image_dir: Optional directory for images

    Returns:
        Path to the generated COCO JSON file
    """
    ensure_dir(output_dir)
    output_file = os.path.join(output_dir, "result_coco.json")
    
    if output_image_dir is not None:
        ensure_dir(output_image_dir)
    else:
        output_image_dir = os.path.join(output_dir, "images")
        os.makedirs(output_image_dir, exist_ok=True)

    # Initialize COCO JSON structure
    coco_data = {
        'images': [],
        'annotations': [],
        'categories': [],
        'info': {
            'year': datetime.now().year,
            'version': '1.0',
            'description': 'Converted from Label Studio',
            'contributor': 'Label Studio Converter',
            'date_created': str(datetime.now()),
        }
    }

    category_map = {}  # To track unique categories
    annotation_id = 0

    # Process each item
    for image_id, item in enumerate(items):
        # Extract image information
        image_path = None
        for key, value in item['input'].items():
            if isinstance(value, str) and any(value.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
                image_path = value
                break
        
        if not image_path:
            logger.warning(f"No image path found for item {item.get('id')}. Skipping.")
            continue

        image_info = {
            'id': image_id,
            'file_name': os.path.basename(image_path),
            'path': image_path,
            'width': None,  # Will be filled from annotations
            'height': None  # Will be filled from annotations
        }

        # Skip tasks without annotations
        if not item['output']:
            logger.warning(f"No annotations found for item {item.get('id')}")
            continue

        valid_annotations = False

        # Process all annotations
        for output_key, annotations in item['output'].items():
            for annotation in annotations:
                # Get image dimensions from the first annotation
                if image_info['width'] is None and 'original_width' in annotation:
                    image_info['width'] = annotation['original_width']
                    image_info['height'] = annotation['original_height']
                
                # Identify annotation type and extract labels
                annotation_type = annotation.get('type', '').lower()
                labels = []
                
                if 'brushlabels' in annotation:
                    labels = annotation['brushlabels']
                    type_key = 'brushlabels'
                elif 'polygonlabels' in annotation:
                    labels = annotation['polygonlabels']
                    type_key = 'polygonlabels'
                elif 'rectanglelabels' in annotation:
                    labels = annotation['rectanglelabels']
                    type_key = 'rectanglelabels'
                elif 'labels' in annotation:
                    labels = annotation['labels']
                    type_key = 'labels'
                else:
                    logger.debug(f"Unsupported annotation type: {annotation_type}")
                    continue
                
                # Process each label
                for label in labels:
                    # Add new categories to the map
                    if label not in category_map:
                        category_id = len(category_map) + 1
                        category_map[label] = category_id
                        coco_data['categories'].append({
                            'id': category_id,
                            'name': label,
                            'supercategory': '',
                            'color': generate_random_color(),
                            'metadata': {}
                        })
                    
                    category_id = category_map[label]
                    
                    # Convert annotation based on type
                    if 'rle' in annotation and type_key == 'brushlabels':

                        # check required keys exist
                        if not all(k in annotation for k in ['rle', 'original_width', 'original_height']):
                            logger.warning(f"Missing required keys for RLE annotation. Skipping.")
                            continue

                        # Process brush annotation (RLE encoded mask)
                        segmentations, bboxes, areas = generate_contour_from_rle(
                            annotation['rle'], 
                            annotation['original_width'], 
                            annotation['original_height']
                        )
                        
                        # Create separate annotation for each contour
                        for i, (segmentation, bbox, area) in enumerate(zip(segmentations, bboxes, areas)):
                            coco_annotation = {
                                'id': annotation_id,
                                'image_id': image_id,
                                'category_id': category_id,
                                'segmentation': [segmentation],  # COCO format requires double nesting
                                'area': area,
                                'bbox': bbox,
                                'iscrowd': 0,
                                'annotator': get_annotator(item, "unknown")
                            }
                            coco_data['annotations'].append(coco_annotation)
                            annotation_id += 1
                            valid_annotations = True
                    
                    elif 'points' in annotation and type_key == 'polygonlabels':
                        # check required keys exist
                        if not all(k in annotation for k in ['points', 'original_width', 'original_height']):
                            logger.warning(f"Missing required keys for polygon annotation. Skipping.")
                            continue
                        # Process polygon annotation
                        segmentation, bbox, area = generate_contour_from_polygon(
                            annotation['points'], 
                            annotation['original_width'], 
                            annotation['original_height']
                        )
                        
                        coco_annotation = {
                            'id': annotation_id,
                            'image_id': image_id,
                            'category_id': category_id,
                            'segmentation': segmentation,
                            'area': area,
                            'bbox': bbox,
                            'iscrowd': 0,
                            'annotator': get_annotator(item, "unknown")
                        }
                        coco_data['annotations'].append(coco_annotation)
                        annotation_id += 1
                        valid_annotations = True
                    
                    elif annotation_type == 'rectanglelabels' or type_key == 'labels':
                        # check required keys exist
                        if not all(k in annotation for k in ['x', 'y', 'width', 'height', 'original_width', 'original_height']):
                            logger.warning(f"Missing required keys for rectangle annotation. Skipping.")
                            continue

                        # Convert from percentage to absolute coordinates
                        x = annotation['x'] * annotation['original_width'] / 100
                        y = annotation['y'] * annotation['original_height'] / 100
                        w = annotation['width'] * annotation['original_width'] / 100
                        h = annotation['height'] * annotation['original_height'] / 100
                        
                        coco_annotation = {
                            'id': annotation_id,
                            'image_id': image_id,
                            'category_id': category_id,
                            'segmentation': [],  # Empty for bounding boxes
                            'area': w * h,
                            'bbox': [x, y, w, h],
                            'iscrowd': 0,
                            'annotator': get_annotator(item, "unknown")
                        }
                        coco_data['annotations'].append(coco_annotation)
                        annotation_id += 1
                        valid_annotations = True
        
        # Add image to the dataset if it has valid dimensions
        if image_info['width'] is not None and image_info['height'] is not None and valid_annotations:
            coco_data['images'].append(image_info)

    # Write COCO JSON to file
    with io.open(output_file, 'w', encoding='utf8') as f:
        json.dump(coco_data, f, indent=2, ensure_ascii=False)
    
    return output_file