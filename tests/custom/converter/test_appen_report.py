"""Tests for to_appen_report(..., mode="full").

No live Appen CSV in CI. Shape is pinned to classic CrowdFlower/Appen Full
headers observed in public downloads, e.g.::

    _unit_id,_created_at,_golden,_id,_missed,_started_at,_tainted,_channel,
    _trust,_worker_id,_country,_region,_city,_ip
    [, optional _worker_trust/_job_id if present]
    [, answer columns...]
    [, source columns...]

Allowed diffs vs a live Appen ``type=full`` download (documented per FIT-3091):

- IDs / timestamps / worker ids come from the LS export, not Appen platform ids.
- Classic system cells are blank when the LS export has no matching meta
  (Appen often fills them; we do not invent values), except ``_started_at``
  which falls back to ``_created_at`` so CrowdTruth-style duration math works.
- Extra system fields ``_worker_trust`` / ``_job_id`` only when present under
  those exact names (not in the classic 14-column prefix).
- No ``_judgment`` / ``_updated_at`` columns (JSON judgment objects have a
  ``judgment`` index; classic Full CSV does not emit ``_judgment``).
- Booleans are lowercase ``true``/``false``; some Appen files use ``TRUE``/``FALSE``.
"""

import csv
import io
import json
from pathlib import Path

import pytest

from label_studio_sdk.converter.exports.appen import (
    CLASSIC_SYSTEM_COLUMNS,
    UnsupportedAppenReportMode,
    to_appen_report,
)

LS_EXPORT = Path(__file__).parent / "data" / "test_appen_report" / "ls_export.json"


def _rows(text: str):
    return list(csv.DictReader(io.StringIO(text)))


def _ann(ann_id, completed_by, *, created_at="2024-01-01T00:00:00Z", result=None, **flags):
    return {
        "id": ann_id,
        "completed_by": completed_by,
        "created_at": created_at,
        "skipped": flags.get("skipped", False),
        "was_cancelled": flags.get("was_cancelled", False),
        "result": result
        or [
            {
                "from_name": "sentiment",
                "to_name": "text",
                "type": "choices",
                "value": {"choices": ["negative"]},
            }
        ],
    }


def test_fixture_full_shape():
    text = to_appen_report(str(LS_EXPORT), mode="full")
    reader = csv.DictReader(io.StringIO(text))
    fields = reader.fieldnames
    rows = list(reader)

    assert len(rows) == 4
    assert fields is not None
    assert tuple(fields[: len(CLASSIC_SYSTEM_COLUMNS)]) == CLASSIC_SYSTEM_COLUMNS
    assert fields.index("sentiment") > fields.index("_ip")
    assert fields.index("text") > fields.index("sentiment")
    assert "_judgment" not in fields
    assert "_updated_at" not in fields
    assert "_missed" in fields

    first = next(r for r in rows if r["_id"] == "1001")
    assert first["_created_at"] == "2024-01-01T10:00:00.000000Z"
    # classic prefix always present; empty when meta absent — except _started_at
    # falls back to _created_at for CrowdTruth / Appen duration consumers
    assert first["_started_at"] == first["_created_at"]
    assert first["_missed"] == ""
    assert first["_channel"] == ""

    by_text = {r["text"]: [x for x in rows if x["text"] == r["text"]] for r in rows}
    assert all(r["_unit_id"] == "101" for r in by_text["hello world"])
    assert by_text["second unit"][0]["_unit_id"] == "999001"
    assert by_text["second unit"][0]["_trust"] == "0.95"
    assert by_text["second unit"][0]["_golden"] == "false"
    assert by_text["hello world"][0]["_trust"] == ""
    assert by_text["with data unit_id"][0]["_unit_id"] == "555"
    assert by_text["with data unit_id"][0]["unit_id"] == "555"
    assert first["sentiment"] == "positive" and first["comment"] == "looks good"


@pytest.mark.parametrize(
    "export",
    [
        pytest.param(lambda: str(LS_EXPORT), id="path"),
        pytest.param(lambda: json.loads(LS_EXPORT.read_text()), id="list"),
        pytest.param(lambda: LS_EXPORT.read_text(), id="json_string"),
    ],
)
def test_export_input_shapes(export):
    assert len(_rows(to_appen_report(export(), mode="full"))) == 4


def test_write_to_path_and_reject_mode(tmp_path):
    out = tmp_path / "out.csv"
    assert to_appen_report(str(LS_EXPORT), mode="full", output=str(out)) == str(out)
    assert len(_rows(out.read_text())) == 4
    with pytest.raises(UnsupportedAppenReportMode, match="full"):
        to_appen_report(str(LS_EXPORT), mode="aggregated")
    with pytest.raises(FileNotFoundError, match="Export file not found"):
        to_appen_report("/tmp/appen-report-missing-export-xyz.json", mode="full")


@pytest.mark.parametrize(
    "flag",
    [pytest.param({"was_cancelled": True}, id="cancelled"), pytest.param({"skipped": True}, id="skipped")],
)
def test_skips_inactive_annotations(flag):
    inactive = _ann(10, {"id": 1}, result=[], **flag)
    active = _ann(11, {"id": 2}, created_at="2024-01-01T01:00:00Z")
    rows = _rows(to_appen_report([{"id": 1, "data": {"text": "x"}, "annotations": [inactive, active]}]))
    assert len(rows) == 1 and rows[0]["_id"] == "11"


@pytest.mark.parametrize(
    "tasks, expect_fields_extra, expect_n",
    [
        pytest.param([], [], 0, id="empty_list"),
        pytest.param(
            [{"id": 1, "data": {"text": "lonely"}, "annotations": [_ann(1, 1, skipped=True, result=[])]}],
            ["text"],
            0,
            id="all_inactive",
        ),
    ],
)
def test_header_only_when_no_active_judgments(tasks, expect_fields_extra, expect_n):
    reader = csv.DictReader(io.StringIO(to_appen_report(tasks, mode="full")))
    fields = reader.fieldnames or []
    assert tuple(fields[: len(CLASSIC_SYSTEM_COLUMNS)]) == CLASSIC_SYSTEM_COLUMNS
    for col in expect_fields_extra:
        assert col in fields
    assert "_judgment" not in fields
    assert "_updated_at" not in fields
    assert len(list(reader)) == expect_n


def test_answer_overrides_source_once():
    tasks = [
        {
            "id": 1,
            "data": {"sentiment": "from_data", "text": "hello"},
            "annotations": [
                _ann(
                    9,
                    1,
                    result=[
                        {
                            "from_name": "sentiment",
                            "to_name": "text",
                            "type": "choices",
                            "value": {"choices": ["from_ann"]},
                        }
                    ],
                )
            ],
        }
    ]
    reader = csv.DictReader(io.StringIO(to_appen_report(tasks, mode="full")))
    assert reader.fieldnames.count("sentiment") == 1
    row = list(reader)[0]
    assert row["sentiment"] == "from_ann" and row["text"] == "hello"


def test_answer_column_blank_when_judgment_missing_result():
    """Source must not leak into an answer column for judgments without that result."""
    tasks = [
        {
            "id": 1,
            "data": {"label": "SOURCE_VALUE", "text": "x"},
            "annotations": [
                _ann(
                    1,
                    1,
                    created_at="2024-01-01T00:00:00Z",
                    result=[
                        {
                            "from_name": "label",
                            "to_name": "text",
                            "type": "choices",
                            "value": {"choices": ["pos"]},
                        }
                    ],
                ),
                _ann(2, 2, created_at="2024-01-01T01:00:00Z", result=[]),
            ],
        }
    ]
    rows = sorted(_rows(to_appen_report(tasks)), key=lambda r: r["_id"])
    assert rows[0]["label"] == "pos"
    assert rows[1]["label"] == ""
    assert "label" in (csv.DictReader(io.StringIO(to_appen_report(tasks))).fieldnames or [])


@pytest.mark.parametrize(
    "completed_by, expected",
    [
        ({"email": "ann@example.com"}, "ann@example.com"),
        ({"id": 77, "email": "ann@example.com"}, "77"),
    ],
)
def test_worker_id_id_then_email(completed_by, expected):
    row = _rows(to_appen_report([{"id": 1, "data": {"text": "x"}, "annotations": [_ann(1, completed_by)]}]))[0]
    assert row["_worker_id"] == expected


def test_started_at_uses_meta_when_present():
    row = _rows(
        to_appen_report(
            [
                {
                    "id": 1,
                    "data": {"text": "x"},
                    "meta": {"_started_at": "2024-01-01T09:59:00.000000Z"},
                    "annotations": [_ann(1, 1, created_at="2024-01-01T10:00:00.000000Z")],
                }
            ]
        )
    )[0]
    assert row["_started_at"] == "2024-01-01T09:59:00.000000Z"
    assert row["_created_at"] == "2024-01-01T10:00:00.000000Z"


def test_source_job_id_kept_not_aliased():
    """Legit source columns job_id / external_type stay as source (no aliases)."""
    row = _rows(
        to_appen_report(
            [
                {
                    "id": 1,
                    "data": {"text": "x", "job_id": "customer-batch-7", "external_type": "cf_internal"},
                    "annotations": [_ann(1, 1)],
                }
            ]
        )
    )[0]
    assert row["job_id"] == "customer-batch-7"
    assert row["external_type"] == "cf_internal"
    assert row.get("_job_id", "") == ""
    assert row.get("_channel", "") == ""

    keep = _rows(
        to_appen_report(
            [
                {
                    "id": 1,
                    "data": {"text": "x"},
                    "meta": {"_channel": "keep_me", "_job_id": 99},
                    "annotations": [_ann(1, 1)],
                }
            ]
        )
    )[0]
    assert keep["_channel"] == "keep_me"
    assert keep["_job_id"] == "99"


def test_multi_result_serialized_once():
    """Per-region / multi-result values must not be double-encoded as JSON strings."""
    result = [
        {
            "from_name": "ner",
            "to_name": "text",
            "type": "labels",
            "value": {"start": 0, "end": 5, "text": "hello", "labels": ["A"]},
        },
        {
            "from_name": "ner",
            "to_name": "text",
            "type": "labels",
            "value": {"start": 10, "end": 15, "text": "world", "labels": ["B"]},
        },
    ]
    row = _rows(to_appen_report([{"id": 1, "data": {"text": "x"}, "annotations": [_ann(1, 1, result=result)]}]))[0]
    parsed = json.loads(row["ner"])
    assert isinstance(parsed, list) and len(parsed) == 2
    assert isinstance(parsed[0], dict) and parsed[0]["start"] == 0
    assert isinstance(parsed[1], dict) and parsed[1]["labels"] == ["B"]


@pytest.mark.parametrize(
    "result, col, check",
    [
        pytest.param(
            [{"from_name": "tags", "to_name": "text", "type": "choices", "value": {"choices": ["a", "b"]}}],
            "tags",
            lambda v: json.loads(v) == ["a", "b"],
            id="multi_choice",
        ),
        pytest.param(
            [
                {
                    "from_name": "label",
                    "to_name": "image",
                    "type": "rectanglelabels",
                    "value": {"x": 10, "y": 20, "width": 30, "height": 40, "rectanglelabels": ["car"]},
                }
            ],
            "label",
            lambda v: json.loads(v)["rectanglelabels"] == ["car"],
            id="spatial_json",
        ),
        pytest.param(
            [
                {"from_name": "_id", "to_name": "text", "type": "textarea", "value": {"text": ["nope"]}},
                {
                    "from_name": "sentiment",
                    "to_name": "text",
                    "type": "choices",
                    "value": {"choices": ["positive"]},
                },
            ],
            "sentiment",
            lambda v: v == "positive",
            id="system_from_name_ignored",
        ),
    ],
)
def test_answer_flatten_edges(result, col, check):
    row = _rows(
        to_appen_report([{"id": 1, "data": {"text": "x"}, "annotations": [_ann(99, 1, result=result)]}])
    )[0]
    assert check(row[col])
    if col != "_id":
        assert row["_id"] == "99"
