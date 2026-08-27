"""
Parity guard: editor prediction region types must have SDK value classes.

FIT-2686 — missing BitmaskLabels / TimelineLabels / Vector registrations caused
prediction validation to reject valid payloads. This test fails CI when a new
editor result type ships without a matching SDK `_TAG_TO_CLASS` entry that
exposes `_value_class`.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from label_studio_sdk.label_interface import control_tags as ct


# Non-region / non-prediction controls that appear in Result.js historically but
# are not validated as geometry value shapes via LabelInterface (or produce
# brush-shaped values covered by MagicWandTag → BrushValue).
# Prefer registering a real `_value_class` over growing this list.
_ALLOWLIST_WITHOUT_VALUE_CLASS: frozenset[str] = frozenset()


def _find_repo_root(start: Path) -> Path | None:
    """Locate hs-platform root via the editor package.

    SDK CI uses a sparse checkout of only `libs/lso-client-generator`, so the
    editor tree is absent there — callers must skip rather than fail hard.
    """
    for parent in [start, *start.parents]:
        if (parent / "services" / "lso" / "web" / "libs" / "editor").is_dir():
            return parent
    return None


def _parse_result_types(result_js: Path) -> list[str]:
    """Extract string literals from `const resultTypes = [...]` in Result.js."""
    text = result_js.read_text(encoding="utf-8")
    match = re.search(r"const\s+resultTypes\s*=\s*\[(.*?)\];", text, re.DOTALL)
    if not match:
        raise AssertionError(f"Could not find resultTypes array in {result_js}")
    # Parse as a Python list by wrapping quoted strings
    body = match.group(1)
    # Keep only double-quoted string literals
    types = re.findall(r'"([^"]+)"', body)
    if not types:
        raise AssertionError(f"No result type strings found in {result_js}")
    return types


def _sdk_tag_has_value_class(tag_key: str) -> bool:
    class_name = ct._TAG_TO_CLASS.get(tag_key)
    if not class_name:
        return False
    tag_cls = getattr(ct, class_name, None)
    if tag_cls is None:
        return False
    return hasattr(tag_cls, "_value_class")


def test_editor_result_types_have_sdk_value_classes():
    """Every editor Result.js region type must map to an SDK tag with _value_class."""
    repo_root = _find_repo_root(Path(__file__).resolve())
    if repo_root is None:
        pytest.skip(
            "Editor package not available (sparse SDK checkout); "
            "run this test in a full monorepo checkout"
        )
    result_js = repo_root / "services" / "lso" / "web" / "libs" / "editor" / "src" / "regions" / "Result.js"
    if not result_js.is_file():
        pytest.skip(f"Editor Result.js not available at {result_js}")

    result_types = _parse_result_types(result_js)
    missing_registration: list[str] = []
    missing_value_class: list[str] = []

    for result_type in result_types:
        if result_type in _ALLOWLIST_WITHOUT_VALUE_CLASS:
            continue
        if result_type not in ct._TAG_TO_CLASS:
            missing_registration.append(result_type)
            continue
        if not _sdk_tag_has_value_class(result_type):
            missing_value_class.append(result_type)

    assert not missing_registration, (
        "Editor result types missing from SDK _TAG_TO_CLASS "
        f"(add Value/Tag classes or allowlist): {missing_registration}"
    )
    assert not missing_value_class, (
        "SDK tags registered without _value_class "
        f"(prediction validation will reject all payloads): {missing_value_class}"
    )


def test_tag_to_class_entries_resolve_to_real_classes():
    """Every _TAG_TO_CLASS value must be an importable class in control_tags."""
    for key, class_name in ct._TAG_TO_CLASS.items():
        assert isinstance(class_name, str), f"{key} maps to non-string {class_name!r}"
        assert getattr(ct, class_name, None) is not None, (
            f"_TAG_TO_CLASS[{key!r}] = {class_name!r} but class is missing from control_tags"
        )


def test_control_tags_module_parses():
    """Sanity: control_tags.py remains valid Python (catches syntax errors early)."""
    path = Path(ct.__file__).resolve()
    ast.parse(path.read_text(encoding="utf-8"))
