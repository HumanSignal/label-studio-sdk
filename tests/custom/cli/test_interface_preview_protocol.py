from __future__ import annotations

import json
from pathlib import Path

import pytest

from label_studio_sdk._extensions.interface.preview.protocol import (
    PROTOCOL_VERSION,
    PreviewManifest,
    ProtocolMismatchError,
)


def _shared_protocol_version_contract() -> Path:
    """Layer-3 owns TS↔Python protocol parity via the FE JSON contract file."""
    repo_root = Path(__file__).resolve().parents[8]
    contract = repo_root / "services/lse/web/apps/local-playground/src/protocol-version.json"
    if not contract.is_file():
        raise AssertionError(
            f"shared protocol-version.json is missing; layer-3 owns TypeScript↔Python protocol parity via {contract}"
        )
    return contract


def test_protocol_version_matches_shared_json_contract() -> None:
    payload = json.loads(_shared_protocol_version_contract().read_text(encoding="utf-8"))
    assert payload.get("protocolVersion") == PROTOCOL_VERSION
    assert isinstance(PROTOCOL_VERSION, int) and not isinstance(PROTOCOL_VERSION, bool)


def test_protocol_version_true_is_not_accepted_as_version_one() -> None:
    with pytest.raises(ProtocolMismatchError):
        PreviewManifest.parse({"protocolVersion": True, "files": {"index.html": "index.html"}})
