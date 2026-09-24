from __future__ import annotations

import json
from pathlib import Path

import pytest

from label_studio_sdk._extensions.interface.preview.protocol import (
    PROTOCOL_VERSION,
    PreviewManifest,
    ProtocolMismatchError,
)

_CONTRACT_RELATIVE = Path("services/lse/web/apps/local-playground/src/protocol-version.json")


def _shared_protocol_version_contract() -> Path | None:
    """Locate the FE JSON contract that owns TS↔Python protocol parity.

    Monorepo CI sparse-checkouts this file (see sdk_pytest.yaml). The public
    label-studio-sdk repo only receives fern-python-sdk via copybara, so the
    contract is absent there — callers must skip rather than fail hard.
    """
    start = Path(__file__).resolve()
    for parent in [start, *start.parents]:
        contract = parent / _CONTRACT_RELATIVE
        if contract.is_file():
            return contract
    return None


def test_protocol_version_matches_shared_json_contract() -> None:
    contract = _shared_protocol_version_contract()
    if contract is None:
        pytest.skip(
            "local-playground protocol-version.json not available "
            "(public SDK / sparse checkout without LSE FE); "
            "TS↔Python protocol parity is enforced in monorepo SDK CI"
        )
    payload = json.loads(contract.read_text(encoding="utf-8"))
    assert payload.get("protocolVersion") == PROTOCOL_VERSION
    assert isinstance(PROTOCOL_VERSION, int) and not isinstance(PROTOCOL_VERSION, bool)


def test_boolean_protocol_version_is_rejected() -> None:
    with pytest.raises(ProtocolMismatchError):
        PreviewManifest.parse({"protocolVersion": True, "files": {"index.html": "index.html"}})
