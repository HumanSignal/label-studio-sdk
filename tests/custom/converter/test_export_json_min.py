from label_studio_sdk.converter import Converter
import json
import os

BASE_DIR = os.path.dirname(__file__)
TEST_DATA_PATH = os.path.join(BASE_DIR, "data", "test_export_json_min")
INPUT_JSON_PATH = os.path.join(BASE_DIR, TEST_DATA_PATH, "data.json")
LABEL_CONFIG_PATH = os.path.join(BASE_DIR, TEST_DATA_PATH, "label_config.xml")
INPUT_JSON_PATH_REPEATER = os.path.join(BASE_DIR, TEST_DATA_PATH, "data_repeater.json")
LABEL_CONFIG_JSON_PATH_REPEATER = os.path.join(
    BASE_DIR, TEST_DATA_PATH, "label_config_repeater.json"
)
CHAT_JSON_PATH = os.path.join(TEST_DATA_PATH, "chat_data.json")

CHAT_SCHEMA = {
    "chat": {
        "type": "chatmessage",
        "to_name": ["chat"],
        "inputs": [{"type": "chatmessage", "value": "chat"}],
        "labels": [],
        "labels_attrs": {},
    }
}


def test_simple_json_min():
    converter = Converter(LABEL_CONFIG_PATH, "/tmp")
    output_dir = "/tmp/lsc-pytest"
    result_json = output_dir + "/result.json"
    input_data = INPUT_JSON_PATH
    converter.convert_to_json_min(input_data, output_dir, is_dir=False)

    loaded_json_min = json.load(open(result_json, "r"))

    assert len(loaded_json_min) == 1
    assert "label" in loaded_json_min[0]


def test_repeater_json_min():
    # The config parser built into LSC doesn't recognize regexes in the label config
    # so we used a previously parsed JSON config instead
    json_config = json.load(open(LABEL_CONFIG_JSON_PATH_REPEATER, "r"))
    converter = Converter(json_config, "/tmp")
    output_dir = "/tmp/lsc-pytest"
    result_json = output_dir + "/result.json"
    input_data = INPUT_JSON_PATH_REPEATER
    converter.convert_to_json_min(input_data, output_dir, is_dir=False)

    loaded_json_min = json.load(open(result_json, "r"))

    assert len(loaded_json_min) == 1
    assert "labels_0" in loaded_json_min[0]
    assert "categories_0" in loaded_json_min[0]


def test_chat_json_min():
    converter = Converter(CHAT_SCHEMA, "/tmp")
    output_dir = "/tmp/lsc-pytest"
    result_json = os.path.join(output_dir, "result.json")
    input_data = CHAT_JSON_PATH

    converter.convert_to_json_min(input_data, output_dir, is_dir=False)

    loaded_json_min = json.load(open(result_json, "r"))

    assert len(loaded_json_min) == 1
    assert "chat" in loaded_json_min[0]
    messages = loaded_json_min[0]["chat"]
    assert isinstance(messages, list)
    assert len(messages) == 4
    assert messages[0]["role"] == "user"
    assert messages[1]["content"].startswith("Hello! How can I assist you today?")
    assert "tool_calls" in messages[1]
    assert messages[1]["tool_calls"] is None


def test_empty_schema_json_min_keeps_interface_annotation_regions(tmp_path):
    """Interface projects use an empty labeling schema (<View></View>).

    json_min must still export annotation regions keyed by from_name
    (FIT-2757) — labels and coordinates must not be dropped.
    """
    input_path = tmp_path / "interface_task.json"
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    input_path.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "data": {"image": "https://example.com/a.jpg"},
                    "annotations": [
                        {
                            "id": 10,
                            "created_at": "2024-01-01T00:00:00Z",
                            "completed_by": {"email": "a@example.com"},
                            "result": [
                                {
                                    "from_name": "boxes",
                                    "to_name": "image",
                                    "type": "rectanglelabels",
                                    "original_width": 100,
                                    "original_height": 100,
                                    "value": {
                                        "x": 10,
                                        "y": 20,
                                        "width": 30,
                                        "height": 40,
                                        "rectanglelabels": ["car"],
                                    },
                                },
                                {
                                    "from_name": "sentiment",
                                    "to_name": "image",
                                    "type": "choices",
                                    "value": {"choices": ["positive"]},
                                },
                            ],
                        }
                    ],
                }
            ]
        )
    )

    converter = Converter({}, str(tmp_path))
    converter.convert_to_json_min(str(input_path), str(output_dir), is_dir=False)

    loaded = json.load(open(output_dir / "result.json"))
    assert len(loaded) == 1
    assert "boxes" in loaded[0], "spatial annotation regions must be exported"
    assert "sentiment" in loaded[0], "choice annotation regions must be exported"
    boxes = loaded[0]["boxes"]
    assert isinstance(boxes, list) and len(boxes) == 1
    assert boxes[0]["x"] == 10
    assert boxes[0]["y"] == 20
    assert boxes[0]["width"] == 30
    assert boxes[0]["height"] == 40
    assert boxes[0]["rectanglelabels"] == ["car"]
