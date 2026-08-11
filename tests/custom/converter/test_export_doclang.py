import base64
import json
import os
import shutil
import tempfile
import zipfile
from types import SimpleNamespace
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
    def fetch(urls, destination_dir, project_dir, upload_dir, hostname, access_token, task_id):
        pages = {}
        for page_number, url in enumerate(urls, start=1):
            path = os.path.join(destination_dir, f"{page_number}{doclang_export._image_extension(url)}")
            with open(path, "wb") as f:
                f.write(FAKE_PNG_BYTES)
            pages[page_number] = path
        return pages

    with patch.object(doclang_export, "_fetch_page_images", side_effect=fetch) as m:
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


def test_extensionless_page_image_url_defaults_to_png(tmp_output_dir, mock_page_image):
    task = {
        "id": 98,
        "data": {"image": "https://example.com/render?id=page"},
        "annotations": [
            {
                "id": 980,
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

    doclang_export.convert_to_doclang(tasks_path, tmp_output_dir, is_dir=False)

    archive = os.path.join(tmp_output_dir, "task-98-annotation-980.dclx")
    with zipfile.ZipFile(archive) as z:
        assert "pages/1.png" in z.namelist()


def test_picture_src_images_are_packaged_as_assets(tmp_output_dir):
    chart_bytes = b"chart-image"
    diagram_bytes = b"diagram-image"
    task = {
        "id": 77,
        "data": {},
        "annotations": [
            {
                "id": 770,
                "result": [
                    {
                        "from_name": "doclang",
                        "type": "textarea",
                        "value": {
                            "text": [
                                "<doclang>"
                                '<picture><src uri="https://example.com/figures/chart.png"/></picture>'
                                '<picture><src uri="https://example.com/figures/diagram.jpg"/></picture>'
                                '<picture><src uri="data:image/png;base64,AAAA"/></picture>'
                                "</doclang>"
                            ]
                        },
                    }
                ],
            }
        ],
    }
    tasks_path = os.path.join(tmp_output_dir, "tasks.json")
    with open(tasks_path, "w") as f:
        json.dump([task], f)

    def download_asset(url, output_dir, **kwargs):
        filename = os.path.basename(url)
        path = os.path.join(output_dir, filename)
        with open(path, "wb") as f:
            f.write(chart_bytes if filename == "chart.png" else diagram_bytes)
        return path

    with patch.object(doclang_export, "download", side_effect=download_asset) as download:
        doclang_export.convert_to_doclang(tasks_path, tmp_output_dir, is_dir=False)

    archive = os.path.join(tmp_output_dir, "task-77-annotation-770.dclx")
    with zipfile.ZipFile(archive) as z:
        assert "assets/chart.png" in z.namelist()
        assert "assets/diagram.jpg" in z.namelist()
        assert z.read("assets/chart.png") == chart_bytes
        assert z.read("assets/diagram.jpg") == diagram_bytes
        document_xml = z.read("document.xml").decode()
        assert 'uri="assets/chart.png"' in document_xml
        assert 'uri="assets/diagram.jpg"' in document_xml
        assert "https://example.com/figures" not in document_xml
        assert 'uri="data:image/png;base64,AAAA"' in document_xml
    assert download.call_count == 2


def test_picture_src_images_are_not_downloaded_when_resources_disabled(tmp_output_dir):
    task = {
        "id": 78,
        "data": {},
        "annotations": [
            {
                "id": 780,
                "result": [
                    {
                        "from_name": "doclang",
                        "type": "textarea",
                        "value": {
                            "text": [
                                "<doclang>"
                                '<picture><src uri="https://example.com/figures/chart.png"/></picture>'
                                "</doclang>"
                            ]
                        },
                    }
                ],
            }
        ],
    }
    tasks_path = os.path.join(tmp_output_dir, "tasks.json")
    with open(tasks_path, "w") as f:
        json.dump([task], f)

    with patch.object(doclang_export, "download") as download:
        doclang_export.convert_to_doclang(
            tasks_path,
            tmp_output_dir,
            is_dir=False,
            download_resources=False,
        )

    archive = os.path.join(tmp_output_dir, "task-78-annotation-780.dclx")
    with zipfile.ZipFile(archive) as z:
        assert not any(name.startswith("assets/") for name in z.namelist())
        assert 'uri="https://example.com/figures/chart.png"' in z.read("document.xml").decode()
    download.assert_not_called()


def test_picture_src_extensionless_images_default_to_png_assets(tmp_output_dir):
    image_bytes = b"extensionless-image"
    task = {
        "id": 79,
        "data": {},
        "annotations": [
            {
                "id": 790,
                "result": [
                    {
                        "from_name": "doclang",
                        "type": "textarea",
                        "value": {
                            "text": [
                                '<doclang><picture><src uri="https://example.com/render?id=chart"/></picture></doclang>'
                            ]
                        },
                    }
                ],
            }
        ],
    }
    tasks_path = os.path.join(tmp_output_dir, "tasks.json")
    with open(tasks_path, "w") as f:
        json.dump([task], f)

    def download_asset(url, output_dir, **kwargs):
        path = os.path.join(output_dir, "render")
        with open(path, "wb") as f:
            f.write(image_bytes)
        return path

    with patch.object(doclang_export, "download", side_effect=download_asset):
        doclang_export.convert_to_doclang(tasks_path, tmp_output_dir, is_dir=False)

    archive = os.path.join(tmp_output_dir, "task-79-annotation-790.dclx")
    with zipfile.ZipFile(archive) as z:
        assert "assets/render.png" in z.namelist()
        assert z.read("assets/render.png") == image_bytes
        assert 'uri="assets/render.png"' in z.read("document.xml").decode()


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

    def copy_to_destination(url, **kwargs):
        shutil.copy(source, kwargs["cache_dir"])
        return str(source)

    with patch.object(doclang_export, "get_local_path", side_effect=copy_to_destination):
        page_path = doclang_export._fetch_page_image(
            "/data/local-files/?d=folder/page.jpeg",
            str(destination),
            1,
            project_dir=None,
            upload_dir=None,
            hostname=None,
            access_token=None,
            task_id=None,
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


def test_exports_doclang_from_draft_when_annotation_is_layout_only(tmp_output_dir, mock_page_image):
    """Regression for FIT-2369: DocLang only in draft, not on committed annotation."""
    task = {
        "id": 279288350,
        "data": {"image": "https://example.com/pages/page-2.png"},
        "annotations": [
            {
                "id": 100629122,
                "result": [
                    {
                        "from_name": "docling",
                        "to_name": "docling",
                        "type": "rectanglelabels",
                        "value": {
                            "x": 1.0,
                            "y": 2.0,
                            "width": 3.0,
                            "height": 4.0,
                            "rectanglelabels": ["Text"],
                        },
                    }
                ],
            }
        ],
        "drafts": [
            {
                "id": 29602202,
                "annotation": 100629122,
                "result": [
                    {
                        "id": "doclang_wd9akrb0z",
                        "from_name": "doclang",
                        "to_name": "docling",
                        "type": "textarea",
                        "value": {
                            "text": ["<doclang><section>Draft-only DocLang</section></doclang>"]
                        },
                    }
                ],
            }
        ],
    }
    tasks_path = os.path.join(tmp_output_dir, "tasks.json")
    with open(tasks_path, "w") as f:
        json.dump([task], f)

    count = doclang_export.convert_to_doclang(tasks_path, tmp_output_dir, is_dir=False)

    assert count == 1
    archive = os.path.join(tmp_output_dir, "task-279288350-draft-29602202.dclx")
    assert os.path.exists(archive)
    with zipfile.ZipFile(archive) as z:
        assert "<section>Draft-only DocLang</section>" in z.read("document.xml").decode()


def test_exports_doclang_from_prediction(tmp_output_dir, mock_page_image):
    task = {
        "id": 42,
        "data": {"image": "https://example.com/page.png"},
        "annotations": [],
        "predictions": [
            {
                "id": 9001,
                "model_version": "docling-v1",
                "result": [
                    {
                        "from_name": "doclang",
                        "type": "textarea",
                        "value": {"text": ["<doclang><text>predicted</text></doclang>"]},
                    }
                ],
            }
        ],
    }
    tasks_path = os.path.join(tmp_output_dir, "tasks.json")
    with open(tasks_path, "w") as f:
        json.dump([task], f)

    count = doclang_export.convert_to_doclang(tasks_path, tmp_output_dir, is_dir=False)

    assert count == 1
    archive = os.path.join(tmp_output_dir, "task-42-prediction-9001.dclx")
    assert os.path.exists(archive)
    with zipfile.ZipFile(archive) as z:
        assert "<text>predicted</text>" in z.read("document.xml").decode()


def test_skips_draft_when_linked_annotation_already_exported_doclang(tmp_output_dir, mock_page_image):
    doclang_xml = "<doclang><text>committed</text></doclang>"
    task = {
        "id": 43,
        "data": {},
        "annotations": [
            {
                "id": 430,
                "result": [
                    {
                        "from_name": "doclang",
                        "type": "textarea",
                        "value": {"text": [doclang_xml]},
                    }
                ],
            }
        ],
        "drafts": [
            {
                "id": 431,
                "annotation": 430,
                "result": [
                    {
                        "from_name": "doclang",
                        "type": "textarea",
                        "value": {"text": ["<doclang><text>draft update</text></doclang>"]},
                    }
                ],
            }
        ],
    }
    tasks_path = os.path.join(tmp_output_dir, "tasks.json")
    with open(tasks_path, "w") as f:
        json.dump([task], f)

    count = doclang_export.convert_to_doclang(tasks_path, tmp_output_dir, is_dir=False, download_resources=False)

    assert count == 1
    assert os.path.exists(os.path.join(tmp_output_dir, "task-43-annotation-430.dclx"))
    assert not os.path.exists(os.path.join(tmp_output_dir, "task-43-draft-431.dclx"))


def test_fetches_page_images_once_for_multiple_sources_on_same_task(tmp_output_dir, mock_page_image):
    """Page rasters are task-level resources; do not re-download per DocLang source."""
    task = {
        "id": 44,
        "data": {"image": "https://example.com/page.png"},
        "annotations": [
            {
                "id": 440,
                "result": [
                    {
                        "from_name": "doclang",
                        "type": "textarea",
                        "value": {"text": ["<doclang><text>annotation</text></doclang>"]},
                    }
                ],
            }
        ],
        "predictions": [
            {
                "id": 441,
                "result": [
                    {
                        "from_name": "doclang",
                        "type": "textarea",
                        "value": {"text": ["<doclang><text>prediction</text></doclang>"]},
                    }
                ],
            }
        ],
    }
    tasks_path = os.path.join(tmp_output_dir, "tasks.json")
    with open(tasks_path, "w") as f:
        json.dump([task], f)

    count = doclang_export.convert_to_doclang(tasks_path, tmp_output_dir, is_dir=False)

    assert count == 2
    mock_page_image.assert_called_once()
    assert os.path.exists(os.path.join(tmp_output_dir, "task-44-annotation-440.dclx"))
    assert os.path.exists(os.path.join(tmp_output_dir, "task-44-prediction-441.dclx"))


def test_valid_annotations_skips_non_dict_entries():
    task = {
        "annotations": [
            None,
            "bad",
            {"id": 1, "was_cancelled": True, "result": []},
            {
                "id": 2,
                "result": [
                    {
                        "from_name": "doclang",
                        "type": "textarea",
                        "value": {"text": ["<doclang><text>ok</text></doclang>"]},
                    }
                ],
            },
        ]
    }
    assert [ann["id"] for ann in doclang_export._valid_annotations(task)] == [2]


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


def test_doclang_storage_proxy_page_image(tmp_output_dir, monkeypatch):
    """Storage proxy URLs resolve via get_local_path with hostname and token."""
    image_url = "/storage-data/uploaded/?filepath=upload/275114/page.jpg"
    requested = SimpleNamespace(url=None, headers=None)

    def fake_get_local_path(url, **kwargs):
        assert url == image_url
        assert kwargs["hostname"] == "https://labelstudio.example.com"
        assert kwargs["access_token"] == "secret"
        assert kwargs["task_id"] == 279288349
        path = os.path.join(kwargs["cache_dir"], "page.jpg")
        with open(path, "wb") as f:
            f.write(FAKE_PNG_BYTES)
        return path

    monkeypatch.setattr(doclang_export, "get_local_path", fake_get_local_path)

    task = {
        "id": 279288349,
        "data": {"image": image_url},
        "annotations": [
            {
                "id": 1,
                "result": [
                    {
                        "from_name": "doclang",
                        "type": "textarea",
                        "value": {"text": ["<doclang><section>Intro</section></doclang>"]},
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
        hostname="https://labelstudio.example.com",
        access_token="secret",
    )

    archive = os.path.join(tmp_output_dir, "task-279288349-annotation-1.dclx")
    with zipfile.ZipFile(archive) as z:
        assert "pages/1.jpg" in z.namelist()
        assert z.read("pages/1.jpg") == FAKE_PNG_BYTES


def test_doclang_base64_page_raster(tmp_output_dir):
    jpeg_bytes = b"\xff\xd8\xff\xd8-page"
    data_url = f"data:image/jpeg;base64,{base64.b64encode(jpeg_bytes).decode('ascii')}"
    task = {
        "id": 42,
        "data": {"image": data_url},
        "annotations": [
            {
                "id": 420,
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

    doclang_export.convert_to_doclang(tasks_path, tmp_output_dir, is_dir=False)

    archive = os.path.join(tmp_output_dir, "task-42-annotation-420.dclx")
    with zipfile.ZipFile(archive) as z:
        assert "pages/1.jpg" in z.namelist()
        assert z.read("pages/1.jpg") == jpeg_bytes


def test_doclang_multi_page_pack(tmp_output_dir):
    page_one = b"\xff\xd8\xffpage1"
    page_two = b"\xff\xd8\xffpage2"
    task = {
        "id": 55,
        "data": {
            "pages": [
                f"data:image/jpeg;base64,{base64.b64encode(page_one).decode('ascii')}",
                f"data:image/jpeg;base64,{base64.b64encode(page_two).decode('ascii')}",
            ]
        },
        "annotations": [
            {
                "id": 550,
                "result": [
                    {
                        "from_name": "doclang",
                        "type": "textarea",
                        "value": {
                            "text": [
                                "<doclang><section>P1</section><page_break/><section>P2</section></doclang>"
                            ]
                        },
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
        image_key="image",
        image_list_key="pages",
    )

    archive = os.path.join(tmp_output_dir, "task-55-annotation-550.dclx")
    with zipfile.ZipFile(archive) as z:
        assert "pages/1.jpg" in z.namelist()
        assert "pages/2.jpg" in z.namelist()
        assert z.read("pages/1.jpg") == page_one
        assert z.read("pages/2.jpg") == page_two


def test_page_image_failure_still_writes_document_xml(tmp_output_dir, caplog):
    task = {
        "id": 66,
        "data": {"image": "/storage-data/uploaded/?filepath=upload/1/missing.jpg"},
        "annotations": [
            {
                "id": 660,
                "result": [
                    {
                        "from_name": "doclang",
                        "type": "textarea",
                        "value": {"text": ["<doclang><section>Still here</section></doclang>"]},
                    }
                ],
            }
        ],
    }
    tasks_path = os.path.join(tmp_output_dir, "tasks.json")
    with open(tasks_path, "w") as f:
        json.dump([task], f)

    with patch.object(
        doclang_export,
        "get_local_path",
        side_effect=FileNotFoundError("Can't resolve url"),
    ):
        with caplog.at_level("WARNING"):
            count = doclang_export.convert_to_doclang(
                tasks_path,
                tmp_output_dir,
                is_dir=False,
                hostname="https://labelstudio.example.com",
                access_token="secret",
            )

    assert count == 1
    archive = os.path.join(tmp_output_dir, "task-66-annotation-660.dclx")
    with zipfile.ZipFile(archive) as z:
        assert "document.xml" in z.namelist()
        assert "<section>Still here</section>" in z.read("document.xml").decode()
        assert not any(name.startswith("pages/") for name in z.namelist())
    assert any("Failed to fetch page image" in record.message for record in caplog.records)


def test_converter_passes_hostname_and_token_to_doclang(tmp_output_dir, monkeypatch):
    captured = {}

    def fake_convert(*args, **kwargs):
        captured.update(kwargs)
        return 0

    monkeypatch.setattr(doclang_export, "convert_to_doclang", fake_convert)

    converter = Converter(
        config={},
        project_dir=".",
        hostname="https://labelstudio.example.com",
        access_token="secret",
    )
    converter.convert(
        input_data=INPUT_JSON_PATH,
        output_data=tmp_output_dir,
        format="DOCLANG",
        is_dir=False,
    )

    assert captured["hostname"] == "https://labelstudio.example.com"
    assert captured["access_token"] == "secret"


def test_resolve_image_data_keys_from_label_config():
    config_xml = (
        '<View><Image name="image" valueList="$pages"/>'
        '<TextArea name="doclang" toName="image"/></View>'
    )
    single_key, list_key = doclang_export.resolve_image_data_keys(config=config_xml)
    assert single_key is None
    assert list_key == "pages"


def test_converter_auto_resolves_image_list_key(tmp_output_dir, monkeypatch):
    captured = {}

    def fake_convert(*args, **kwargs):
        captured.update(kwargs)
        return 0

    monkeypatch.setattr(doclang_export, "convert_to_doclang", fake_convert)

    config = parse_config(
        '<View><Image name="image" value="$image"/>'
        '<TextArea name="doclang" toName="image"/></View>'
    )
    converter = Converter(config=config, project_dir=".")
    converter.convert(
        input_data=INPUT_JSON_PATH,
        output_data=tmp_output_dir,
        format="DOCLANG",
        is_dir=False,
    )

    assert captured["image_key"] == "image"
    assert captured.get("image_list_key") is None
