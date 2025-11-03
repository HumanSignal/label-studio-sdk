import json
import os


from label_studio_sdk.converter import Converter
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
