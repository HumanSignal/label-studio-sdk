import json
import pathlib

import numpy as np
import pytest

from label_studio_sdk.converter.brush import mask2rle
from label_studio_sdk.converter.exports.brush_to_coco import convert_to_coco


@pytest.mark.parametrize('extension', ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'WEBP'])
def test_brush_export_preserves_supported_image_formats(tmp_path: pathlib.Path, extension: str) -> None:
    mask = np.zeros((8, 8), dtype=np.uint8)
    mask[2:6, 1:5] = 255
    image_name = f'segmented_image.{extension}'
    items = [
        {
            'id': 1,
            'input': {'image': image_name},
            'output': {
                'mask': [
                    {
                        'type': 'brushlabels',
                        'brushlabels': ['foreground'],
                        'rle': mask2rle(mask),
                        'original_width': 8,
                        'original_height': 8,
                    }
                ]
            },
            'completed_by': {'email': 'annotator@example.com'},
        }
    ]

    output_file = convert_to_coco(items, str(tmp_path))
    result = json.loads(pathlib.Path(output_file).read_text())

    assert len(result['images']) == 1
    image = result['images'][0]
    assert image['file_name'] == image_name
    assert (image['width'], image['height']) == (8, 8)
    assert len(result['annotations']) == 1
    annotation = result['annotations'][0]
    assert annotation['image_id'] == image['id']
    assert annotation['bbox'] == [1, 2, 4, 4]
    assert annotation['area'] == 9
    assert len(annotation['segmentation'][0]) == 8
    assert result['categories'][0]['name'] == 'foreground'
