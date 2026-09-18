from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from .preview_fakes import FakePreviewCache, FakePreviewServer
from typer.testing import CliRunner

from label_studio_sdk._extensions.interface import cli
from label_studio_sdk._extensions.interface.preview import ProtocolMismatchError

runner = CliRunner()


def _stop_watch(*_args: Any, **_kwargs: Any) -> Any:
    raise KeyboardInterrupt
    yield


def test_preview_offline_passes_no_auth_requirement_to_cache(monkeypatch: Any, tmp_path: Path) -> None:
    FakePreviewCache.instances = []
    FakePreviewCache.error = None
    FakePreviewServer.instances = []
    monkeypatch.setattr(cli, "PreviewAssetCache", FakePreviewCache)
    monkeypatch.setattr(cli, "LocalPreviewServer", FakePreviewServer)
    monkeypatch.setitem(sys.modules, "watchfiles", SimpleNamespace(watch=_stop_watch))

    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")

    result = runner.invoke(cli.app, ["preview", str(file), "--offline", "--no-open"])

    assert result.exit_code == 0, result.output
    assert FakePreviewCache.instances[0].calls[0]["offline"] is True
    assert FakePreviewCache.instances[0].calls[0]["headers"] == {}


def test_protocol_mismatch_fails_before_browser_or_server(monkeypatch: Any, tmp_path: Path) -> None:
    FakePreviewCache.instances = []
    FakePreviewCache.error = ProtocolMismatchError("server=2 SDK=1")
    FakePreviewServer.instances = []
    opened: list[str] = []
    monkeypatch.setattr(cli, "PreviewAssetCache", FakePreviewCache)
    monkeypatch.setattr(cli, "LocalPreviewServer", FakePreviewServer)
    monkeypatch.setattr(cli.webbrowser, "open", opened.append)
    monkeypatch.setitem(sys.modules, "watchfiles", SimpleNamespace(watch=_stop_watch))

    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")

    result = runner.invoke(cli.app, ["preview", str(file), "--token", "secret"])

    assert result.exit_code == 1
    assert "protocol" in result.output
    assert opened == []
    assert FakePreviewServer.instances == []
