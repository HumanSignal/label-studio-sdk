from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx
from .preview_fakes import FakePreviewCache, FakePreviewServer, preview_asset_root
from typer.testing import CliRunner

from label_studio_sdk._extensions.interface import cli
from label_studio_sdk._extensions.interface.preview import LocalPreviewServer, ProtocolMismatchError
from label_studio_sdk._extensions.interface.preview import server as preview_server_module

runner = CliRunner()


def _stop_watch(*_args: Any, **_kwargs: Any) -> Any:
    raise KeyboardInterrupt
    yield


def test_preview_cli_sidecar_seeds_real_server_bff_gate(monkeypatch: Any, tmp_path: Path) -> None:
    """Cross-layer e2e: CLI sidecar → real LocalPreviewServer → BFF allow/deny + null-publish durability."""
    asset_root = preview_asset_root(tmp_path)
    servers: list[LocalPreviewServer] = []
    probe: dict[str, int] = {}

    class TrackingCache(FakePreviewCache):
        def resolve(self, **kwargs: Any) -> Any:
            self.calls.append(kwargs)
            return SimpleNamespace(root=asset_root, protocol_version=1, source="cache", warning=None)

    class TrackingServer(LocalPreviewServer):
        def __init__(self, **kwargs: Any) -> None:
            super().__init__(**kwargs)
            servers.append(self)

    def watch_and_probe(*_args: Any, **_kwargs: Any) -> Any:
        server = servers[-1]
        bff = f"{server.host_origin}/{server.capability}/bff"
        probe["patch_bound"] = httpx.patch(f"{bff}/api/interfaces/42/", json={"title": "ok"}).status_code
        probe["patch_wrong"] = httpx.patch(f"{bff}/api/interfaces/99/", json={"title": "no"}).status_code
        probe["create_forbidden"] = httpx.post(f"{bff}/api/interfaces/", json={"title": "no"}).status_code
        server.publish_file_update(code="changed", task=None, interface_id=None, lse_url="https://ls.example")
        probe["create_after_null"] = httpx.post(f"{bff}/api/interfaces/", json={"title": "no"}).status_code
        probe["patch_after_null"] = httpx.patch(f"{bff}/api/interfaces/42/", json={"title": "still"}).status_code
        raise KeyboardInterrupt
        yield

    def upstream(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True}, request=request)

    original_client = preview_server_module.httpx.Client

    def client_factory(*args: Any, **kwargs: Any) -> httpx.Client:
        kwargs = dict(kwargs)
        kwargs.setdefault("transport", httpx.MockTransport(upstream))
        kwargs.setdefault("timeout", 30.0)
        return original_client(*args, **kwargs)

    FakePreviewCache.instances = []
    monkeypatch.setattr(preview_server_module.httpx, "Client", client_factory)
    monkeypatch.setattr(cli, "PreviewAssetCache", TrackingCache)
    monkeypatch.setattr(cli, "LocalPreviewServer", TrackingServer)
    monkeypatch.setitem(sys.modules, "watchfiles", SimpleNamespace(watch=watch_and_probe))

    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")
    (tmp_path / "Screen.jsx.ls-interface.json").write_text(
        json.dumps({"https://ls.example": {"interface_id": 42}}),
        encoding="utf-8",
    )

    result = runner.invoke(
        cli.app,
        ["preview", str(file), "--token", "secret", "--lse-url", "https://ls.example/", "--no-open"],
    )

    assert result.exit_code == 0, result.output
    assert "/interfaces/playground" not in result.output
    assert len(servers) == 1
    assert probe == {
        "patch_bound": 200,
        "patch_wrong": 403,
        "create_forbidden": 403,
        "create_after_null": 403,
        "patch_after_null": 200,
    }


def test_preview_save_create_persists_sidecar_for_next_run(monkeypatch: Any, tmp_path: Path) -> None:
    asset_root = preview_asset_root(tmp_path)
    servers: list[LocalPreviewServer] = []

    class TrackingCache(FakePreviewCache):
        def resolve(self, **kwargs: Any) -> Any:
            self.calls.append(kwargs)
            return SimpleNamespace(root=asset_root, protocol_version=2, source="cache", warning=None)

    class TrackingServer(LocalPreviewServer):
        def __init__(self, **kwargs: Any) -> None:
            super().__init__(**kwargs)
            servers.append(self)

    def watch_and_create(*_args: Any, **_kwargs: Any) -> Any:
        server = servers[-1]
        response = httpx.post(
            f"{server.host_origin}/{server.capability}/bff/api/interfaces/",
            json={"title": "Saved locally", "workspace": 7},
        )
        assert response.status_code == 201
        raise KeyboardInterrupt
        yield

    def upstream(request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, json={"id": 77, "title": "Saved locally", "workspace": 7}, request=request)

    original_client = preview_server_module.httpx.Client

    def client_factory(*args: Any, **kwargs: Any) -> httpx.Client:
        kwargs = dict(kwargs)
        kwargs.setdefault("transport", httpx.MockTransport(upstream))
        kwargs.setdefault("timeout", 30.0)
        return original_client(*args, **kwargs)

    FakePreviewCache.instances = []
    monkeypatch.setattr(preview_server_module.httpx, "Client", client_factory)
    monkeypatch.setattr(cli, "PreviewAssetCache", TrackingCache)
    monkeypatch.setattr(cli, "LocalPreviewServer", TrackingServer)
    monkeypatch.setitem(sys.modules, "watchfiles", SimpleNamespace(watch=watch_and_create))

    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")

    result = runner.invoke(
        cli.app,
        ["preview", str(file), "--token", "secret", "--lse-url", "https://ls.example/", "--no-open"],
    )

    assert result.exit_code == 0, result.output
    assert json.loads((tmp_path / "Screen.jsx.ls-interface.json").read_text()) == {
        "https://ls.example": {
            "interface_id": 77,
            "title": "Saved locally",
            "workspace": 7,
        }
    }


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
