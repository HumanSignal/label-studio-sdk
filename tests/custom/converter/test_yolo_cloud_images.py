"""FIT-2611: YOLO_WITH_IMAGES must not emit orphan labels when cloud image download fails."""

import json
import os
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from label_studio_sdk.converter import Converter
from label_studio_sdk.converter.converter import Format


def _make_label_config(path):
    path.write_text(
        """
    <View>
      <Image name="image" value="$image"/>
      <RectangleLabels name="label" toName="image">
        <Label value="cat"/>
      </RectangleLabels>
    </View>
    """
    )
    return str(path)


def _make_task_json(path, image_url):
    task = [
        {
            "id": 1,
            "data": {"image": image_url},
            "annotations": [
                {
                    "id": 1,
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
                            "id": "r1",
                            "from_name": "label",
                            "to_name": "image",
                            "type": "rectanglelabels",
                            "origin": "manual",
                        }
                    ],
                }
            ],
        }
    ]
    path.write_text(json.dumps(task))
    return str(path)


@pytest.mark.parametrize(
    "image_url",
    [
        "gs://bucket/prefix/photo.jpg",
        "s3://bucket/prefix/photo.jpg",
        "azure-blob://bucket/prefix/photo.jpg",
    ],
)
def test_yolo_with_images_skips_labels_when_cloud_download_fails(tmp_path, image_url):
    label_config_path = _make_label_config(tmp_path / "config.xml")
    task_json_path = _make_task_json(tmp_path / "task.json", image_url)
    output_dir = tmp_path / "out"

    with patch(
        "label_studio_sdk.converter.converter.get_local_path",
        side_effect=FileNotFoundError("presign failed"),
    ):
        converter = Converter(label_config_path, project_dir=".")
        converter.hostname = "https://labelstudio.example.com"
        converter.access_token = "secret"
        converter.convert(
            input_data=task_json_path,
            output_data=str(output_dir),
            format=Format.YOLO_WITH_IMAGES,
            is_dir=False,
        )

    labels_dir = output_dir / "labels"
    images_dir = output_dir / "images"
    assert images_dir.exists()
    assert labels_dir.exists()
    assert list(images_dir.iterdir()) == []
    assert list(labels_dir.iterdir()) == [], "must not write orphan label files without images"


def test_yolo_with_images_writes_image_on_cloud_download_success(monkeypatch, tmp_path):
    """Happy path (AC): successful cloud resolve places the image under images/."""
    Image = pytest.importorskip("PIL.Image")

    label_config_path = _make_label_config(tmp_path / "config.xml")
    task_json_path = _make_task_json(tmp_path / "task.json", "gs://bucket/prefix/photo.jpg")
    output_dir = tmp_path / "out"

    def fake_get_local_path(**kwargs):
        cache_dir = kwargs.get("cache_dir") or str(tmp_path)
        os.makedirs(cache_dir, exist_ok=True)
        image_path = os.path.join(cache_dir, "photo.jpg")
        Image.new("RGB", (100, 100), color=(10, 20, 30)).save(image_path)
        return image_path

    monkeypatch.setattr(
        "label_studio_sdk.converter.converter.get_local_path",
        fake_get_local_path,
    )

    converter = Converter(label_config_path, project_dir=".")
    converter.hostname = "https://labelstudio.example.com"
    converter.access_token = "secret"
    converter.convert(
        input_data=task_json_path,
        output_data=str(output_dir),
        format=Format.YOLO_WITH_IMAGES,
        is_dir=False,
    )

    images_dir = output_dir / "images"
    labels_dir = output_dir / "labels"
    assert images_dir.exists()
    image_files = list(images_dir.iterdir())
    assert len(image_files) == 1
    assert image_files[0].name == "photo.jpg"
    assert image_files[0].stat().st_size > 0
    assert labels_dir.exists()
    assert any(p.suffix == ".txt" for p in labels_dir.iterdir())


def test_get_local_path_cloud_presign_uses_base64_fileuri(monkeypatch, tmp_path):
    from unittest.mock import MagicMock

    from label_studio_sdk._extensions.label_studio_tools.core.utils.io import (
        encode_presign_fileuri,
        get_local_path,
    )

    cloud_uri = "gs://bucket/prefix/photo.jpg"
    hostname = "https://labelstudio.example.com"
    requested = SimpleNamespace(url=None)

    def fake_get(u, stream=False, headers=None, verify=None):
        requested.url = u
        response = MagicMock()
        response.content = b"img"
        response.raise_for_status = lambda: None
        return response

    monkeypatch.setattr(
        "label_studio_sdk._extensions.label_studio_tools.core.utils.io.requests.get",
        fake_get,
    )

    get_local_path(
        url=cloud_uri,
        cache_dir=str(tmp_path),
        hostname=hostname,
        access_token="secret",
        download_resources=True,
        task_id=42,
    )

    encoded = encode_presign_fileuri(cloud_uri)
    assert requested.url == f"{hostname}/tasks/42/presign/?fileuri={encoded}"
    assert "gs://" not in requested.url.split("fileuri=", 1)[1]


def test_download_cloud_uri_requires_task_context():
    from label_studio_sdk.converter.utils import download

    with pytest.raises(ValueError, match="hostname and task_id"):
        download("gs://bucket/prefix/photo.jpg", output_dir="/tmp")


def test_download_cloud_uri_delegates_to_get_local_path(monkeypatch, tmp_path):
    from label_studio_sdk.converter import utils as converter_utils

    calls = {}

    def fake_get_local_path(**kwargs):
        calls.update(kwargs)
        dest = tmp_path / "photo.jpg"
        dest.write_bytes(b"img")
        return str(dest)

    monkeypatch.setattr(
        "label_studio_sdk._extensions.label_studio_tools.core.utils.io.get_local_path",
        fake_get_local_path,
    )

    out = converter_utils.download(
        "gs://bucket/prefix/photo.jpg",
        output_dir=str(tmp_path / "out"),
        hostname="https://labelstudio.example.com",
        access_token="secret",
        task_id=7,
        download_resources=True,
    )

    assert calls["url"] == "gs://bucket/prefix/photo.jpg"
    assert calls["task_id"] == 7
    assert calls["hostname"] == "https://labelstudio.example.com"
    assert os.path.basename(out) == "photo.jpg"


def test_voc_export_uses_get_local_path_for_cloud_uri(monkeypatch, tmp_path):
    """VOC must resolve cloud images via get_local_path (same as COCO/YOLO), not download()."""
    from label_studio_sdk.converter import Converter
    from label_studio_sdk.converter.converter import Format

    label_config_path = _make_label_config(tmp_path / "config.xml")
    task_json_path = _make_task_json(tmp_path / "task.json", "gs://bucket/prefix/photo.jpg")
    output_dir = tmp_path / "out"
    seen = {}

    def fake_get_local_path(**kwargs):
        seen.update(kwargs)
        image_path = tmp_path / "cached_photo.jpg"
        # minimal valid JPEG so get_image_size_and_channels can open it if needed
        Image = pytest.importorskip("PIL.Image")
        Image.new("RGB", (10, 10), color=(1, 2, 3)).save(image_path)
        return str(image_path)

    monkeypatch.setattr(
        "label_studio_sdk.converter.converter.get_local_path",
        fake_get_local_path,
    )

    converter = Converter(label_config_path, project_dir=".")
    converter.hostname = "https://labelstudio.example.com"
    converter.access_token = "secret"
    converter.convert(
        input_data=task_json_path,
        output_data=str(output_dir),
        format=Format.VOC,
        is_dir=False,
    )

    assert seen.get("url") == "gs://bucket/prefix/photo.jpg"
    assert seen.get("task_id") == 1
    assert seen.get("hostname") == "https://labelstudio.example.com"
