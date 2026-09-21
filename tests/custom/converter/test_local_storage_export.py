"""Exports with images must not copy server files that a task references as Local Storage."""

import json
from unittest.mock import patch

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
                        "value": {
                            "x": 10,
                            "y": 10,
                            "width": 20,
                            "height": 20,
                            "rotation": 0,
                            "rectanglelabels": ["cat"],
                        },
                        "id": f"r{task_id}",
                        "from_name": "label",
                        "to_name": "image",
                        "type": "rectanglelabels",
                    }
                ],
            }
        ],
    }


def _convert(tmp_path, fmt, image_urls, **converter_kwargs):
    input_path = tmp_path / "input.json"
    input_path.write_text(json.dumps([_task(i, url) for i, url in enumerate(image_urls, start=1)]))
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    converter = Converter(config=LABEL_CONFIG, project_dir=None, download_resources=False, **converter_kwargs)
    converter.convert(str(input_path), str(output_dir), fmt, is_dir=False)
    return sorted(path.read_bytes() for path in (output_dir / "images").glob("*"))


@pytest.fixture
def server_file(tmp_path, monkeypatch):
    monkeypatch.delenv("LABEL_STUDIO_URL", raising=False)
    monkeypatch.delenv("LABEL_STUDIO_HOST", raising=False)
    secret = tmp_path / "secret.txt"
    secret.write_bytes(b"server secret")
    return secret


@pytest.mark.parametrize("fmt", FORMATS_WITH_IMAGES)
@pytest.mark.parametrize("root", [None, "/"])
def test_local_storage_files_are_not_read_without_explicit_root(tmp_path, server_file, fmt, root):
    urls = [f"/data/local-files/?d={server_file}", f"/data/local-files/?d={str(server_file).lstrip('/')}"]

    with patch.object(io_utils, "LOCAL_FILES_DOCUMENT_ROOT", root):
        images = _convert(tmp_path, fmt, urls)

    assert images == []


@pytest.mark.parametrize("fmt", FORMATS_WITH_IMAGES)
def test_resolver_decides_which_local_storage_files_are_exported(tmp_path, server_file, fmt):
    allowed = tmp_path / "dataset" / "cat.jpg"
    allowed.parent.mkdir()
    allowed.write_bytes(b"allowed image")
    requested = []

    def resolver(relative_path):
        requested.append(relative_path)
        return str(allowed) if relative_path == "dataset/cat.jpg" else None

    images = _convert(
        tmp_path,
        fmt,
        ["/data/local-files/?d=dataset/cat.jpg", f"/data/local-files/?d={server_file}"],
        local_files_resolver=resolver,
    )

    assert images == [b"allowed image"]
    assert sorted(requested) == sorted(["dataset/cat.jpg", str(server_file)])
    # The resolver only applies inside convert()
    assert io_utils._local_files_resolver.get() is None
