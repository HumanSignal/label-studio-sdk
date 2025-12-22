import json
import os
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from label_studio_sdk.converter import Converter
from label_studio_sdk.converter.converter import Format


def _make_label_config(path):
    config = """
    <View>
      <Image name="image" value="$image"/>
      <RectangleLabels name="label" toName="image">
        <Label value="cat"/>
      </RectangleLabels>
    </View>
    """
    path.write_text(config)
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


@pytest.fixture
def storage_proxy_task(tmp_path):
    image_url = "/storage-data/uploaded/?filepath=upload/5/1.jpg"
    label_config_path = _make_label_config(tmp_path / "config.xml")
    task_json_path = _make_task_json(tmp_path / "task.json", image_url)
    return SimpleNamespace(
        image_url=image_url,
        label_config_path=label_config_path,
        task_json_path=task_json_path,
        output_dir=str(tmp_path / "out"),
    )


def test_yolo_with_images_storage_proxy(monkeypatch, storage_proxy_task):
    hostname = "https://labelstudio.example.com"
    token = "secret"
    requested = SimpleNamespace(url=None, headers=None)

    def fake_get(u, stream=False, headers=None, verify=None):
        requested.url = u
        requested.headers = headers or {}
        response = MagicMock()
        response.content = b"\x89PNG\r\n"  # minimal bytes
        response.raise_for_status = lambda: None
        return response

    monkeypatch.setattr(
        "label_studio_sdk._extensions.label_studio_tools.core.utils.io.requests.get",
        fake_get,
    )

    converter = Converter(
        config=storage_proxy_task.label_config_path,
        project_dir=".",
        hostname=hostname,
        access_token=token,
    )
    converter.convert(
        input_data=storage_proxy_task.task_json_path,
        output_data=storage_proxy_task.output_dir,
        format=Format.YOLO_WITH_IMAGES,
        is_dir=False,
    )

    images_dir = f"{storage_proxy_task.output_dir}/images"
    assert any(
        name.endswith("__1.jpg") for name in os.listdir(images_dir)
    ), "Downloaded image file with expected name not found"

    assert requested.url.startswith(
        f"{hostname}/storage-data/uploaded/?filepath=upload/5/1.jpg"
    )
    assert "Authorization" in requested.headers
    assert requested.headers["Authorization"] in (f"Token {token}", f"Bearer {token}")
