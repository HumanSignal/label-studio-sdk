import json
import os


from label_studio_sdk.converter import Converter
from label_studio_sdk.converter.exports.csv2 import prepare_annotation, prepare_annotation_keys
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
