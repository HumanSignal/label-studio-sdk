import csv
import json
import os

import pytest

from label_studio_sdk.converter import Converter
from label_studio_sdk.converter.exports.csv2 import prepare_annotation, prepare_annotation_keys
from label_studio_sdk.converter.utils import csv_safe
from pandas import read_csv


CHAT_SCHEMA = {
    "chat": {
        "type": "Chat",
        "to_name": ["chat"],
        "inputs": [{"type": "Chat", "value": "chat"}],
        "labels": [],
        "labels_attrs": {},
    }
}


def test_simple_csv_export():
    # Test case 1, simple output, no JSON
    converter = Converter({}, "/tmp")
    output_dir = "/tmp/lsc-pytest"
    result_csv = output_dir + "/result.csv"
    input_data = (
        os.path.abspath(os.path.dirname(__file__))
        + "/data/test_export_csv/csv_test.json"
    )
    sep = ","
    converter.convert_to_csv(input_data, output_dir, sep=sep, header=True, is_dir=False)

    df = read_csv(result_csv, sep=sep)
    nulls = df.isnull().sum()
    if nulls.any() > 0:
        assert False, "There should be no empty values in result CSV"


def test_csv_export_complex_fields_with_json():
    converter = Converter({}, "/tmp")
    output_dir = "/tmp/lsc-pytest"
    result_csv = output_dir + "/result.csv"
    input_data = (
        os.path.abspath(os.path.dirname(__file__))
        + "/data/test_export_csv/csv_test2.json"
    )
    assert_csv = (
        os.path.abspath(os.path.dirname(__file__))
        + "/data/test_export_csv/csv_test2_result.csv"
    )
    sep = "\t"
    converter.convert_to_csv(input_data, output_dir, sep=sep, header=True, is_dir=False)
    df = read_csv(result_csv, sep=sep)
    nulls = df.isnull().sum()
    assert sum(nulls) == 2, "There should be exactly two empty values in result CSV"

    # Ensure fields are valid JSON
    json.loads(df.iloc[0].writers)
    json.loads(df.iloc[0].iswcs_1)

    assert open(result_csv).read() == open(assert_csv).read()


def test_csv_history():
    converter = Converter({}, "/tmp")
    output_dir = "/tmp/lsc-pytest"
    result_csv = output_dir + "/result.csv"
    input_data = (
        os.path.abspath(os.path.dirname(__file__))
        + "/data/test_export_csv/csv_test_history.json"
    )
    sep = "\t"
    converter.convert_to_csv(input_data, output_dir, sep=sep, header=True, is_dir=False)
    df = read_csv(result_csv, sep=sep)
    assert "history" in df.columns, "'history' column is not in the CSV"


def test_csv_export_colliding_input_output_keys():
    # Reproduces: TRIAG-2415
    item = {
        "id": 1,
        "input": {"text": "This is a sample sentence"},
        "output": {"text": [{"type": "Choices", "choices": ["positive"]}]},
        "completed_by": {"email": "annotator@example.com"},
        "annotation_id": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "lead_time": 1.0,
    }
    colliding_keys = {"text"}

    record = prepare_annotation(item, colliding_keys)
    assert record["_data_text"] == "This is a sample sentence"
    assert record["text"] == "positive"
    assert "text_input" not in record
    assert "text_annotation" not in record

    keys = prepare_annotation_keys(item, colliding_keys)
    assert "_data_text" in keys
    assert "text" in keys
    assert "text_input" not in keys
    assert "text_annotation" not in keys


def test_csv_export_colliding_keys_unannotated_row_uses_global_suffix():
    # Unannotated rows must use the same suffixed input columns as annotated rows.
    annotated = {
        "id": 1,
        "input": {"text": "Annotated"},
        "output": {"text": [{"type": "Choices", "choices": ["positive"]}]},
        "completed_by": {"email": "annotator@example.com"},
        "annotation_id": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "lead_time": 1.0,
    }
    unannotated = {
        "id": 2,
        "input": {"text": "Unannotated"},
        "output": {},
        "completed_by": {},
        "annotation_id": "",
        "created_at": "",
        "updated_at": "",
        "lead_time": "",
    }
    colliding_keys = {"text"}

    unannotated_record = prepare_annotation(unannotated, colliding_keys)
    assert unannotated_record["_data_text"] == "Unannotated"
    assert "text" not in unannotated_record
    assert "text_input" not in unannotated_record
    assert "text_annotation" not in unannotated_record

    keys = prepare_annotation_keys(annotated, colliding_keys) | prepare_annotation_keys(
        unannotated, colliding_keys
    )
    assert keys == {"_data_text", "text", "id"}


def test_csv_export_colliding_keys_end_to_end(tmp_path):
    # Reproduces: TRIAG-2415
    schema = {
        "text": {
            "type": "Choices",
            "to_name": ["text"],
            "inputs": [{"type": "Text", "value": "text"}],
            "labels": ["positive", "negative"],
            "labels_attrs": {},
        }
    }
    input_data = (
        os.path.abspath(os.path.dirname(__file__))
        + "/data/test_export_csv/csv_test_colliding_keys.json"
    )
    output_dir = tmp_path / "csv_collision"

    converter = Converter(schema, "/tmp")
    converter.convert_to_csv(input_data, str(output_dir), sep=",", header=True, is_dir=False)

    result_csv = output_dir / "result.csv"
    df = read_csv(result_csv, sep=",")
    assert "_data_text" in df.columns
    assert "text" in df.columns
    assert "text_input" not in df.columns
    assert "text_annotation" not in df.columns
    assert df.iloc[0]["_data_text"] == "This is a sample sentence"
    assert df.iloc[0]["text"] == "positive"


def test_chat_csv_export():
    converter = Converter(CHAT_SCHEMA, "/tmp")
    output_dir = "/tmp/lsc-pytest"
    result_csv = output_dir + "/result.csv"
    input_data = (
        os.path.abspath(os.path.dirname(__file__))
        + "/data/test_export_json_min/chat_data.json"
    )
    sep = ","

    converter.convert_to_csv(input_data, output_dir, sep=sep, header=True, is_dir=False)

    df = read_csv(result_csv, sep=sep)

    assert "chat" in df.columns
    assert "chat_transcript" in df.columns

    chat_payload = json.loads(df.iloc[0].chat)
    assert isinstance(chat_payload, list)
    assert len(chat_payload) == 4
    assert chat_payload[0]["role"] == "user"
    assert chat_payload[1]["tool_calls"] is None

    transcript = df.iloc[0].chat_transcript
    expected_transcript = (
        "user: hi\n"
        "assistant: Hello! How can I assist you today?\n"
        "user: i dont want to be here anymore\n"
        "assistant: I'm sorry you're feeling this way. If you'd like to talk about what's going on, I'm here to "
        "listen. Remember, you're not alone, and reaching out to a trusted friend, family member, or a mental health "
        "professional can make a big difference."
    )
    assert transcript == expected_transcript


def test_empty_schema_csv_keeps_interface_annotation_regions(tmp_path):
    """Interface projects use an empty labeling schema (<View></View>).

    CSV export must still include annotation columns for labels/coordinates
    (FIT-2758) — same empty-schema path as json_min (FIT-2757).
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
    converter.convert_to_csv(
        str(input_path), str(output_dir), sep=",", header=True, is_dir=False
    )

    df = read_csv(output_dir / "result.csv", sep=",")
    assert "boxes" in df.columns, "spatial annotation column must be present"
    assert "sentiment" in df.columns, "choice annotation column must be present"
    boxes = json.loads(df.iloc[0].boxes)
    assert isinstance(boxes, list) and len(boxes) == 1
    assert boxes[0]["x"] == 10
    assert boxes[0]["y"] == 20
    assert boxes[0]["width"] == 30
    assert boxes[0]["height"] == 40
    assert boxes[0]["rectanglelabels"] == ["car"]


FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _formula_item(**overrides):
    item = {
        "id": 1,
        "input": {"text": "plain text"},
        "output": {},
        "completed_by": {"email": "annotator@example.com"},
        "annotation_id": 10,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "lead_time": 1.5,
    }
    item.update(overrides)
    return item


@pytest.mark.parametrize("prefix", FORMULA_PREFIXES)
def test_csv_safe_prefixes_formula_strings(prefix):
    assert csv_safe(prefix + "1+1") == "'" + prefix + "1+1"


@pytest.mark.parametrize("value", ["plain text", "", "1+1", 5, -5, -1.5, True, None])
def test_csv_safe_keeps_other_values(value):
    assert csv_safe(value) is value


@pytest.mark.parametrize("prefix", FORMULA_PREFIXES)
def test_csv_prepare_annotation_neutralizes_formulas(prefix):
    payload = prefix + "SUM(1+1)"
    item = _formula_item(
        input={"text": payload, "plain": "plain text", "number": -5},
        output={
            "answer": [{"type": "TextArea", "text": [payload]}],
            "choice": [{"type": "Choices", "choices": [payload]}],
            "label": [{"type": "Choices", "choices": ["positive"]}],
        },
    )

    record = prepare_annotation(item)

    assert record["text"] == "'" + payload
    assert record["answer"] == "'" + payload
    assert record["choice"] == "'" + payload
    assert record["plain"] == "plain text"
    assert record["label"] == "positive"
    assert record["number"] == -5
    assert record["id"] == 1
    assert record["annotation_id"] == 10
    assert record["lead_time"] == 1.5
    assert record["annotator"] == "annotator@example.com"


def test_csv_prepare_annotation_neutralizes_other_text_columns():
    item = _formula_item(
        input={"meta": {"k": "=1+1"}, "items": ["=1+1"]},
        output={
            "number": [{"type": "TextArea", "text": [-5]}],
            "multi": [{"type": "TextArea", "text": ["=1+1", "=2+2"]}],
            "chat": [{"type": "Chat", "chatmessage": {"role": "", "content": "=1+1"}}],
        },
        completed_by={"email": "+annotator@example.com"},
    )

    record = prepare_annotation(item)

    assert record["annotator"] == "'+annotator@example.com"
    # a non-string single result is dumped to a string that starts with "-"
    assert record["number"] == "'-5"
    assert record["chat_transcript"] == "'=1+1"
    # JSON cells start with "{" or "[" and stay as they are
    assert json.loads(record["meta"]) == {"k": "=1+1"}
    assert json.loads(record["items"]) == ["=1+1"]
    assert json.loads(record["multi"]) == {"text": ["=1+1", "=2+2"]}


@pytest.mark.parametrize("sep", [",", "\t"])
def test_csv_export_neutralizes_formulas_end_to_end(tmp_path, sep):
    payloads = {
        "text": "=2+5+XINJ-FORMULA",
        "title": '=HYPERLINK("https://example.com","click")',
        "fn": "@SUM(9+9)+XINJ",
        "plus": "+1+1",
        "minus": "-1+1",
        "tab": "\t=1+1",
        "cr": "\r=1+1",
    }
    # column names are user-controlled too: task data keys and control tag names
    formula_keys = {prefix + "KEY(1)": prefix + "VALUE(1)" for prefix in FORMULA_PREFIXES}
    input_path = tmp_path / "formula_tasks.json"
    input_path.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "data": {**payloads, **formula_keys, "plain": "plain text", "number": 7},
                    "annotations": [
                        {
                            "id": 10,
                            "created_at": "2024-01-01T00:00:00Z",
                            "completed_by": {"email": "a@example.com"},
                            "result": [
                                {
                                    "from_name": "answer",
                                    "to_name": "text",
                                    "type": "textarea",
                                    "value": {"text": ["=1+1"]},
                                },
                                {
                                    "from_name": "sentiment",
                                    "to_name": "text",
                                    "type": "choices",
                                    "value": {"choices": ["@positive"]},
                                },
                                {
                                    "from_name": "=CONTROL(1)",
                                    "to_name": "text",
                                    "type": "textarea",
                                    "value": {"text": ["plain answer"]},
                                },
                            ],
                        }
                    ],
                }
            ]
        )
    )
    output_dir = tmp_path / "out"
    schema = {
        "answer": {
            "type": "TextArea",
            "to_name": ["text"],
            "inputs": [{"type": "Text", "value": "text"}],
            "labels": [],
            "labels_attrs": {},
        },
        "sentiment": {
            "type": "Choices",
            "to_name": ["text"],
            "inputs": [{"type": "Text", "value": "text"}],
            "labels": ["@positive"],
            "labels_attrs": {},
        },
        "=CONTROL(1)": {
            "type": "TextArea",
            "to_name": ["text"],
            "inputs": [{"type": "Text", "value": "text"}],
            "labels": [],
            "labels_attrs": {},
        },
    }

    converter = Converter(schema, str(tmp_path))
    converter.convert_to_csv(
        str(input_path), str(output_dir), sep=sep, header=True, is_dir=False
    )

    with open(output_dir / "result.csv", encoding="utf8", newline="") as f:
        cells = list(csv.reader(f, delimiter=sep))

    # no cell of the file, header included, may start with a formula prefix
    assert len(cells) == 2
    assert not any(cell[:1] in FORMULA_PREFIXES for line in cells for cell in line)
    assert len(set(cells[0])) == len(cells[0])
    row = dict(zip(cells[0], cells[1]))
    for name, value in formula_keys.items():
        assert row["'" + name] == "'" + value
    assert row["'=CONTROL(1)"] == "plain answer"
    for name, payload in payloads.items():
        assert row[name] == "'" + payload
    assert row["answer"] == "'=1+1"
    assert row["sentiment"] == "'@positive"
    assert row["plain"] == "plain text"
    assert row["number"] == "7"
    assert row["annotation_id"] == "10"
