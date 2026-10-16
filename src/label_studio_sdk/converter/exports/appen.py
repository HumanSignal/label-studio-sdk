"""LS JSON export → Appen classic Full report CSV (``type=full``; FIT-3091).

One row per active annotation. Flatten: choices / textarea / rating / number /
taxonomy; other result types → JSON of ``value``. Empty input → header only.
``mode`` is ``\"full\"`` only.

Canonical Appen references (parity target for "Appen CSV shape"):

- Results / report types (Full vs Aggregated vs Source):
  https://success.appen.com/appen-success-center/dashboards-reports/results
- API download (``type=full`` = Full report, every judgment):
  ``GET https://api.appen.com/v1/jobs/{job_id}.csv?type=full&key={api_key}``
  FAQ: https://success.appen.com/hc/en-us/articles/115000832063-Frequently-Asked-Questions
- Judgment object fields ⇔ Full CSV row (Integrating with the API):
  https://success.appen.com/hc/en-us/articles/202703445-Integrating-with-the-API
- First-time user guide (Full report definition):
  https://appen-success-center.s3.amazonaws.com/first_time_user_guide/Appen+Platform+First+Time+User+Guide_12-08-2020.pdf

Classic Full column order (pinned from public CrowdFlower/Appen Full downloads):
system prefix → answer columns → source columns. The system prefix is always::

    _unit_id,_created_at,_golden,_id,_missed,_started_at,_tainted,_channel,
    _trust,_worker_id,_country,_region,_city,_ip

``_started_at`` uses Appen meta when present; otherwise it falls back to the
annotation ``created_at`` (same as ``_created_at``) so consumers such as
CrowdTruth can compute judgment duration without tz-naive/aware errors.
"""

from __future__ import annotations

import csv
import io
import json
import os
from collections import OrderedDict
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

# Always emitted, classic Full leading block (public Appen/CrowdFlower Full CSVs).
CLASSIC_SYSTEM_COLUMNS: tuple[str, ...] = (
    "_unit_id",
    "_created_at",
    "_golden",
    "_id",
    "_missed",
    "_started_at",
    "_tainted",
    "_channel",
    "_trust",
    "_worker_id",
    "_country",
    "_region",
    "_city",
    "_ip",
)

# Extra Appen system fields: emit only when present under these exact names.
OPTIONAL_APPEN_SYSTEM_COLUMNS: tuple[str, ...] = (
    "_worker_trust",
    "_job_id",
)

# Meta/data keys looked up to fill classic + optional system columns (except
# _unit_id / _id / _created_at / _worker_id, which come from LS fields).
LOOKUP_SYSTEM_COLUMNS: tuple[str, ...] = (
    "_golden",
    "_missed",
    "_started_at",
    "_tainted",
    "_channel",
    "_trust",
    "_country",
    "_region",
    "_city",
    "_ip",
    *OPTIONAL_APPEN_SYSTEM_COLUMNS,
)

UNIT_ID_LOOKUP_KEYS: tuple[str, ...] = ("_unit_id", "unit_id")

SYSTEM_COLUMN_NAMES: frozenset[str] = frozenset(
    {*CLASSIC_SYSTEM_COLUMNS, *OPTIONAL_APPEN_SYSTEM_COLUMNS}
)

SOURCE_EXCLUDED_SYSTEM_KEYS: frozenset[str] = frozenset(
    {
        "_unit_id",
        *LOOKUP_SYSTEM_COLUMNS,
        *CLASSIC_SYSTEM_COLUMNS,
        *OPTIONAL_APPEN_SYSTEM_COLUMNS,
    }
)

ExportInput = Union[str, os.PathLike, Sequence[Mapping[str, Any]], Mapping[str, Any]]


class UnsupportedAppenReportMode(ValueError):
    """Raised when ``to_appen_report`` is called with an unsupported ``mode``."""


def to_appen_report(
    export: ExportInput,
    mode: str = "full",
    output: Optional[Union[str, os.PathLike]] = None,
) -> str:
    """Transform an LS JSON export into an Appen Full report CSV.

    ``export`` may be a path, JSON string, task dict, or list of tasks.
    Column order is classic Full: system prefix → answers → source. Answer
    columns blank out when a judgment has no result for that control (source
    values never leak into answer columns). ``from_name`` values that match
    system columns are ignored. Returns CSV text, or ``output`` path when
    writing a file.
    """
    if mode != "full":
        raise UnsupportedAppenReportMode(
            f'Unsupported Appen report mode={mode!r}; only mode="full" is supported '
            "(classic job-level Full report / type=full)."
        )

    tasks = _load_tasks(export)
    rows, fieldnames = _tasks_to_appen_full_rows(tasks)
    csv_text = _rows_to_csv(rows, fieldnames)

    if output is not None:
        out_path = os.fspath(output)
        parent = os.path.dirname(out_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            f.write(csv_text)
        return out_path
    return csv_text


def _looks_like_json_payload(text: str) -> bool:
    stripped = text.lstrip()
    return bool(stripped) and stripped[0] in "{["


def _load_tasks(export: ExportInput) -> List[Mapping[str, Any]]:
    if isinstance(export, (str, os.PathLike)):
        path = os.fspath(export)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        elif _looks_like_json_payload(path):
            data = json.loads(path)
        else:
            raise FileNotFoundError(f"Export file not found: {path}")
    else:
        data = export

    if isinstance(data, Mapping):
        return [data]
    if isinstance(data, Sequence):
        return list(data)
    raise TypeError(
        "export must be a path to JSON, a JSON string, a task dict, or a list of tasks"
    )


def _resolve_unit_id(task: Mapping[str, Any]) -> Any:
    meta = task.get("meta") or {}
    data = task.get("data") or {}
    for key in UNIT_ID_LOOKUP_KEYS:
        if isinstance(meta, Mapping) and meta.get(key) is not None:
            return meta[key]
        if isinstance(data, Mapping) and data.get(key) is not None:
            return data[key]
    return task.get("id")


def _worker_id(annotation: Mapping[str, Any]) -> Optional[Any]:
    completed_by = annotation.get("completed_by")
    if isinstance(completed_by, Mapping):
        if completed_by.get("id") is not None:
            return completed_by["id"]
        return completed_by.get("email")
    if isinstance(completed_by, int):
        return completed_by
    if isinstance(completed_by, str) and completed_by:
        return completed_by
    return None


def _is_active_annotation(annotation: Mapping[str, Any]) -> bool:
    return not (
        annotation.get("skipped", False) or annotation.get("was_cancelled", False)
    )


def _flatten_answer_value(result_item: Mapping[str, Any]) -> Any:
    """Return a Python value (not a pre-encoded JSON string) for one result item."""
    value = result_item.get("value") or {}
    rtype = (result_item.get("type") or "").lower()

    if rtype == "choices":
        choices = value.get("choices") or []
        if len(choices) == 1:
            return choices[0]
        return list(choices) if choices else ""

    if rtype == "textarea":
        texts = value.get("text") or []
        if len(texts) == 1:
            return texts[0]
        return "\n".join(str(t) for t in texts) if texts else ""

    if rtype in ("rating", "number"):
        for key in ("rating", "number"):
            if key in value:
                return value[key]
        if len(value) == 1:
            return next(iter(value.values()))
        return dict(value)

    if rtype == "taxonomy":
        taxonomy = value.get("taxonomy")
        if taxonomy is not None:
            return taxonomy

    if len(value) == 1:
        only = next(iter(value.values()))
        if isinstance(only, list) and len(only) == 1:
            return only[0]
        return only
    return dict(value) if value else ""


def _serialize_answer_cell(val: Any) -> Any:
    """JSON-encode dict/list once; leave scalars for ``_format_cell``."""
    if isinstance(val, (dict, list)):
        return json.dumps(val, ensure_ascii=False)
    return val


def _answers_from_annotation(annotation: Mapping[str, Any]) -> Dict[str, Any]:
    answers: Dict[str, Any] = OrderedDict()
    reserved = SYSTEM_COLUMN_NAMES
    for result_item in annotation.get("result") or []:
        if not isinstance(result_item, Mapping):
            continue
        from_name = result_item.get("from_name")
        if not from_name or from_name in reserved:
            continue
        flat = _flatten_answer_value(result_item)
        if from_name in answers:
            existing = answers[from_name]
            if not isinstance(existing, list):
                answers[from_name] = [existing]
            answers[from_name].append(flat)
        else:
            answers[from_name] = flat
    for key, val in list(answers.items()):
        answers[key] = _serialize_answer_cell(val)
    return answers


def _lookup_system_meta(
    task: Mapping[str, Any], annotation: Mapping[str, Any]
) -> Dict[str, Any]:
    found: Dict[str, Any] = {}
    sources: List[Mapping[str, Any]] = []
    for candidate in (
        task.get("meta"),
        task.get("data"),
        annotation.get("meta") if isinstance(annotation.get("meta"), Mapping) else None,
    ):
        if isinstance(candidate, Mapping):
            sources.append(candidate)

    for col in LOOKUP_SYSTEM_COLUMNS:
        for src in sources:
            if col in src and src[col] is not None:
                found[col] = src[col]
                break
    return found


def _format_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _source_columns(task: Mapping[str, Any]) -> "OrderedDict[str, Any]":
    data = task.get("data") or {}
    if not isinstance(data, Mapping):
        return OrderedDict()
    out: "OrderedDict[str, Any]" = OrderedDict()
    for key, val in data.items():
        if key in SOURCE_EXCLUDED_SYSTEM_KEYS:
            continue
        out[key] = val
    return out


def _dedupe_preserve_order(names: Sequence[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for name in names:
        if name not in seen:
            seen.add(name)
            out.append(name)
    return out


def _tasks_to_appen_full_rows(
    tasks: Sequence[Mapping[str, Any]],
) -> tuple[List[Dict[str, str]], List[str]]:
    source_keys: "OrderedDict[str, None]" = OrderedDict()
    answer_keys: "OrderedDict[str, None]" = OrderedDict()
    optional_keys: "OrderedDict[str, None]" = OrderedDict()
    pending: List[Dict[str, Any]] = []

    for task in tasks:
        annotations = [
            a
            for a in (task.get("annotations") or task.get("completions") or [])
            if isinstance(a, Mapping) and _is_active_annotation(a)
        ]
        annotations = sorted(annotations, key=lambda a: a.get("created_at") or "")

        source = _source_columns(task)
        for k in source:
            source_keys.setdefault(k, None)

        unit_id = _resolve_unit_id(task)

        for annotation in annotations:
            answers = _answers_from_annotation(annotation)
            for k in answers:
                answer_keys.setdefault(k, None)

            meta = _lookup_system_meta(task, annotation)
            for col in OPTIONAL_APPEN_SYSTEM_COLUMNS:
                if col in meta:
                    optional_keys.setdefault(col, None)

            worker = _worker_id(annotation)
            created_at = annotation.get("created_at") or ""
            # CrowdTruth (and Appen Full consumers) subtract submitted-started;
            # empty _started_at with tz-aware _created_at breaks that. Prefer
            # explicit Appen meta, else fall back to created_at (zero duration).
            started_at = meta.get("_started_at", "")
            if started_at == "" or started_at is None:
                started_at = created_at
            system: Dict[str, Any] = {
                "_unit_id": unit_id,
                "_created_at": created_at,
                "_golden": meta.get("_golden", ""),
                "_id": annotation.get("id"),
                "_missed": meta.get("_missed", ""),
                "_started_at": started_at,
                "_tainted": meta.get("_tainted", ""),
                "_channel": meta.get("_channel", ""),
                "_trust": meta.get("_trust", ""),
                "_worker_id": worker if worker is not None else "",
                "_country": meta.get("_country", ""),
                "_region": meta.get("_region", ""),
                "_city": meta.get("_city", ""),
                "_ip": meta.get("_ip", ""),
            }
            optional = {
                col: meta[col]
                for col in OPTIONAL_APPEN_SYSTEM_COLUMNS
                if col in meta
            }
            pending.append(
                {
                    "system": system,
                    "optional": optional,
                    "answers": answers,
                    "source": source,
                }
            )

    ordered_optional = [c for c in OPTIONAL_APPEN_SYSTEM_COLUMNS if c in optional_keys]

    # Classic Full: system → answers → source. Answer names win over same-named source.
    fieldnames = _dedupe_preserve_order(
        list(CLASSIC_SYSTEM_COLUMNS)
        + ordered_optional
        + list(answer_keys.keys())
        + [k for k in source_keys.keys() if k not in answer_keys]
    )

    string_rows: List[Dict[str, str]] = []
    for item in pending:
        raw: Dict[str, Any] = {}
        raw.update(item["system"])
        raw.update(item["optional"])
        for name in answer_keys:
            # Once a name is an answer column, missing answers are blank (no source leak).
            raw[name] = item["answers"].get(name, "")
        for name, val in item["source"].items():
            if name in answer_keys or name in SYSTEM_COLUMN_NAMES:
                continue
            raw[name] = val
        string_rows.append(
            {name: _format_cell(raw.get(name, "")) for name in fieldnames}
        )
    return string_rows, fieldnames


def _rows_to_csv(rows: Sequence[Mapping[str, str]], fieldnames: Sequence[str]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=list(fieldnames),
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()
