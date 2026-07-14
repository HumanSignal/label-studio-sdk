import json
import os
import shutil
import tempfile
import zipfile
from unittest.mock import patch

import pytest

from label_studio_sdk.converter import Converter
from label_studio_sdk.converter.converter import Format
from label_studio_sdk.converter.exports import doclang as doclang_export
from label_studio_sdk.converter.utils import parse_config

BASE_DIR = os.path.dirname(__file__)
TEST_DATA_PATH = os.path.join(BASE_DIR, "data", "test_export_doclang")
INPUT_JSON_PATH = os.path.join(TEST_DATA_PATH, "data.json")

# Fake 1x1 PNG that _fetch_page_image will write when the exporter would
# otherwise try to hit the network.
FAKE_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x03\x03\x03\x00\x05\xfe\x02\xfe"
    b"\xa2\xef\xb6\xac\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest.fixture
def tmp_output_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def mock_page_image():
    def fetch(url, destination_dir, project_dir, upload_dir):
        path = os.path.join(destination_dir, f"1{doclang_export._image_extension(url)}")
        with open(path, "wb") as f:
            f.write(FAKE_PNG_BYTES)
        return path

    with patch.object(doclang_export, "_fetch_page_image", side_effect=fetch) as m:
        yield m


def test_exports_only_live_doclang_with_reference_packager(tmp_output_dir, mock_page_image):
    with patch.object(doclang_export, "pack", wraps=doclang_export.pack) as pack:
        count = doclang_export.convert_to_doclang(INPUT_JSON_PATH, tmp_output_dir, is_dir=False)

    assert count == 1
    assert os.listdir(tmp_output_dir) == ["task-1-annotation-11.dclx"]
    pack.assert_called_once()
    assert pack.call_args.kwargs["validate"] is False
    with zipfile.ZipFile(os.path.join(tmp_output_dir, "task-1-annotation-11.dclx")) as z:
        assert {"[Content_Types].xml", "_rels/.rels", "document.xml", "pages/1.png"} <= set(z.namelist())
        assert "application/vnd.doclang.document+xml" in z.read("[Content_Types].xml").decode()
        assert "http://doclang.ai/ns/package/2026/relationships/document" in z.read("_rels/.rels").decode()
        assert "<section>Intro</section>" in z.read("document.xml").decode()
        assert "pages/1.png" in z.namelist()
        assert z.read("pages/1.png") == FAKE_PNG_BYTES
    mock_page_image.assert_called_once()


def test_image_field_override(tmp_output_dir, mock_page_image):
    task = {
        "id": 99,
        "data": {"document_url": "https://example.com/scan.jpeg"},
        "annotations": [
            {
                "id": 990,
                "result": [
                    {
                        "from_name": "doclang",
                        "type": "textarea",
                        "value": {"text": ["<doclang/>"]},
                    }
                ],
            }
        ],
    }
    tasks_path = os.path.join(tmp_output_dir, "tasks.json")
    with open(tasks_path, "w") as f:
        json.dump([task], f)

    doclang_export.convert_to_doclang(tasks_path, tmp_output_dir, is_dir=False, image_key="document_url")

    archive = os.path.join(tmp_output_dir, "task-99-annotation-990.dclx")
    assert os.path.exists(archive)
    with zipfile.ZipFile(archive) as z:
        assert "pages/1.jpeg" in z.namelist()


@pytest.mark.parametrize(
    ("result", "expected_xml"),
    [
        (
            {
                "from_name": "generated_document",
                "type": "textarea",
                "value": {"text": ["<doclang><text>textarea</text></doclang>"]},
            },
            "<doclang><text>textarea</text></doclang>",
        ),
        (
            {
                "from_name": "custom_component",
                "type": "reactcode",
                "value": {
                    "reactcode": {
                        "output": {
                            "document": "<doclang xmlns='https://www.doclang.ai/ns/v0'><text>reactcode</text></doclang>"
                        }
                    }
                },
            },
            "<doclang xmlns='https://www.doclang.ai/ns/v0'><text>reactcode</text></doclang>",
        ),
        (
            {
                "from_name": "custom_output",
                "type": "documentai",
                "value": {
                    "metadata": {"kind": "document"},
                    "document": "<doclang><text>interface</text></doclang>",
                },
            },
            "<doclang><text>interface</text></doclang>",
        ),
        (
            {
                "from_name": "generated_document",
                "type": "textarea",
                "value": {"text": " \n<doclang><text>whitespace</text></doclang> \n"},
            },
            " \n<doclang><text>whitespace</text></doclang> \n",
        ),
    ],
)
def test_detects_doclang_by_content_across_supported_result_shapes(
    tmp_output_dir, mock_page_image, result, expected_xml
):
    task = {
        "id": 8,
        "data": {},
        "annotations": [{"id": 80, "result": [result]}],
    }
    tasks_path = os.path.join(tmp_output_dir, "tasks.json")
    with open(tasks_path, "w") as f:
        json.dump([task], f)

    n = doclang_export.convert_to_doclang(tasks_path, tmp_output_dir, is_dir=False, download_resources=False)

    assert n == 1
    with zipfile.ZipFile(os.path.join(tmp_output_dir, "task-8-annotation-80.dclx")) as z:
        assert z.read("document.xml").decode() == expected_xml


def test_ignores_doclang_text_inside_standard_non_document_results(tmp_output_dir):
    results = [
        {
            "from_name": "entity",
            "type": "labels",
            "value": {
                "labels": ["Document"],
                "text": "<doclang><text>source span</text></doclang>",
            },
        },
        {
            "from_name": "ocr",
            "type": "ocrlabels",
            "value": {
                "ocrlabels": ["Document"],
                "text": "<doclang><text>OCR text</text></doclang>",
            },
        },
    ]
    task = {
        "id": 9,
        "data": {},
        "annotations": [{"id": 90, "result": results}],
    }
    tasks_path = os.path.join(tmp_output_dir, "tasks.json")
    with open(tasks_path, "w") as f:
        json.dump([task], f)

    n = doclang_export.convert_to_doclang(tasks_path, tmp_output_dir, is_dir=False, download_resources=False)

    assert n == 0
    assert not os.path.exists(os.path.join(tmp_output_dir, "task-9-annotation-90.dclx"))


@pytest.mark.parametrize(
    "value",
    [
        "<not-doclang/>",
        "<doclang>",
        "<doclang xmlns='https://www.doclang.ai/ns/not-doclang'/>",
        '<!DOCTYPE doclang [<!ENTITY example "text">]><doclang>&example;</doclang>',
        "\ud800",
    ],
)
def test_rejects_non_doclang_xml_candidates(value):
    assert doclang_export._doclang_xml_bytes(value) is None


def test_nested_value_traversal_does_not_queue_beyond_node_budget(monkeypatch):
    class TrackingList(list):
        accesses = 0

        def __iter__(self):
            for item in super().__iter__():
                self.accesses += 1
                yield item

        def __reversed__(self):
            for item in super().__reversed__():
                self.accesses += 1
                yield item

    values = TrackingList(["first", *(str(index) for index in range(100))])
    monkeypatch.setattr(doclang_export, "_MAX_VALUE_NODES", 2)

    assert list(doclang_export._iter_string_values(values)) == ["first"]
    assert values.accesses <= 2


def test_doclang_detection_accepts_documents_over_previous_size_limit():
    xml = f"<doclang><text>{'x' * (17 * 1024 * 1024)}</text></doclang>"

    assert doclang_export._doclang_xml_bytes(xml) is not None


def test_fetch_page_image_uses_staged_copy_without_moving_source(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    source = source_dir / "page.jpeg"
    source.write_bytes(FAKE_PNG_BYTES)
    destination = tmp_path / "stage"
    destination.mkdir()

    def copy_to_destination(url, output_dir, **kwargs):
        shutil.copy(source, output_dir)
        return str(source)

    with patch.object(doclang_export, "download", side_effect=copy_to_destination):
        page_path = doclang_export._fetch_page_image(
            "/data/local-files/?d=folder/page.jpeg",
            str(destination),
            project_dir=None,
            upload_dir=None,
        )

    assert source.exists()
    assert page_path == str(destination / "1.jpeg")
    assert (destination / "1.jpeg").read_bytes() == FAKE_PNG_BYTES


@pytest.mark.parametrize(
    ("data", "download_resources"),
    [
        ({}, True),
        ({"image": "https://example.com/page.png"}, False),
    ],
)
def test_page_image_is_optional(tmp_output_dir, mock_page_image, data, download_resources):
    task = {
        "id": 5,
        "data": data,
        "annotations": [
            {
                "id": 50,
                "result": [
                    {
                        "from_name": "doclang",
                        "type": "textarea",
                        "value": {"text": ["<doclang/>"]},
                    }
                ],
            }
        ],
    }
    tasks_path = os.path.join(tmp_output_dir, "tasks.json")
    with open(tasks_path, "w") as f:
        json.dump([task], f)

    doclang_export.convert_to_doclang(
        tasks_path,
        tmp_output_dir,
        is_dir=False,
        download_resources=download_resources,
    )

    with zipfile.ZipFile(os.path.join(tmp_output_dir, "task-5-annotation-50.dclx")) as z:
        assert not any(n.startswith("pages/") for n in z.namelist())
    mock_page_image.assert_not_called()


def test_format_registered_in_all_formats():
    converter = Converter(config={}, project_dir=".")
    formats = converter.all_formats()
    assert Format.DOCLANG in formats
    info = formats[Format.DOCLANG]
    assert info["title"] == "DocLang (.dclx)"
    assert "docling" in info["tags"]


@pytest.mark.parametrize(
    ("config", "supported"),
    [
        ({}, False),
        (
            parse_config('<View><Text name="text" value="$text"/><TextArea name="answer" toName="text"/></View>'),
            True,
        ),
        (
            parse_config(
                '<View><Text name="text" value="$text"/><Text name="context" value="$context"/>'
                '<TextArea name="answer" toName="text,context"/></View>'
            ),
            True,
        ),
        (
            parse_config('<View><ReactCode name="custom" toName="custom" outputs="document"/></View>'),
            True,
        ),
        (
            {"custom": {"type": "CustomInterface", "inputs": []}},
            True,
        ),
        (
            parse_config(
                '<View><Image name="image" value="$image"/>'
                '<RectangleLabels name="label" toName="image"><Label value="Object"/></RectangleLabels></View>'
            ),
            False,
        ),
    ],
)
def test_doclang_format_applicability(config, supported):
    converter = Converter(config=config, project_dir=".")

    assert (Format.DOCLANG.name in converter.supported_formats) is supported


def test_converter_dispatch_to_doclang(tmp_output_dir, mock_page_image):
    """Format string routing through Converter.convert() reaches convert_to_doclang."""
    converter = Converter(config={}, project_dir=".")
    converter.convert(
        input_data=INPUT_JSON_PATH,
        output_data=tmp_output_dir,
        format="DOCLANG",
        is_dir=False,
    )
    assert os.path.exists(os.path.join(tmp_output_dir, "task-1-annotation-11.dclx"))


def test_directory_input_iterates_all_json_files(tmp_output_dir, mock_page_image):
    """is_dir=True should pull tasks from every *.json file in the directory."""
    task_a = {
        "id": 100,
        "data": {},
        "annotations": [
            {
                "id": 1000,
                "result": [
                    {
                        "from_name": "doclang",
                        "type": "textarea",
                        "value": {"text": ["<doclang><text>a</text></doclang>"]},
                    }
                ],
            }
        ],
    }
    task_b = {
        "id": 200,
        "data": {},
        "annotations": [
            {
                "id": 2000,
                "result": [
                    {
                        "from_name": "doclang",
                        "type": "textarea",
                        "value": {"text": ["<doclang><text>b</text></doclang>"]},
                    }
                ],
            }
        ],
    }
    input_dir = tempfile.mkdtemp()
    try:
        with open(os.path.join(input_dir, "a.json"), "w") as f:
            json.dump([task_a], f)
        with open(os.path.join(input_dir, "b.json"), "w") as f:
            json.dump(task_b, f)  # single dict, not list — supported by ijson root=dict path

        n = doclang_export.convert_to_doclang(input_dir, tmp_output_dir, is_dir=True, download_resources=False)
        assert n == 2
        names = set(os.listdir(tmp_output_dir))
        assert "task-100-annotation-1000.dclx" in names
        assert "task-200-annotation-2000.dclx" in names
    finally:
        shutil.rmtree(input_dir, ignore_errors=True)
