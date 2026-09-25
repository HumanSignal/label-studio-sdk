"""Exports with images must fetch task media through the session the caller passes."""

import json
from unittest.mock import MagicMock, patch

import pytest

from label_studio_sdk._extensions.label_studio_tools.core.utils import io as io_utils
from label_studio_sdk.converter import Converter

LABEL_CONFIG = """
<View>
  <Image name="image" value="$image"/>
  <RectangleLabels name="label" toName="image">
    <Label value="cat"/>
  </RectangleLabels>
</View>
"""

FORMATS_WITH_IMAGES = ["COCO_WITH_IMAGES", "YOLO_WITH_IMAGES", "YOLO_OBB_WITH_IMAGES"]


def _task(task_id, image_url):
    return {
        "id": task_id,
        "data": {"image": image_url},
        "annotations": [
            {
                "id": task_id,
                "completed_by": 1,
                "result": [
                    {
                        "original_width": 100,
                        "original_height": 100,
                        "image_rotation": 0,
                        "value": {"x": 10, "y": 10, "width": 20, "height": 20, "rotation": 0, "rectanglelabels": ["cat"]},
                        "id": f"r{task_id}",
                        "from_name": "label",
                        "to_name": "image",
                        "type": "rectanglelabels",
                    }
                ],
            }
        ],
    }


@pytest.mark.parametrize("fmt", FORMATS_WITH_IMAGES)
def test_media_is_downloaded_through_the_session(tmp_path, monkeypatch, fmt):
    monkeypatch.delenv("LABEL_STUDIO_URL", raising=False)
    monkeypatch.delenv("LABEL_STUDIO_HOST", raising=False)
    input_path = tmp_path / "input.json"
    input_path.write_text(json.dumps([_task(1, "http://169.254.169.254/latest/meta-data.png")]))
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    session = MagicMock()
    session.get.side_effect = ConnectionError("blocked")
    converter = Converter(config=LABEL_CONFIG, project_dir=None, download_resources=True, http_session=session)

    with patch.object(io_utils.requests, "get", side_effect=AssertionError("plain requests must not be used")):
        converter.convert(str(input_path), str(output_dir), fmt, is_dir=False)

    assert session.get.call_args.args[0] == "http://169.254.169.254/latest/meta-data.png"
    assert list((output_dir / "images").glob("*")) == []
    # The session only applies inside convert()
    assert io_utils._http_session.get() is None
