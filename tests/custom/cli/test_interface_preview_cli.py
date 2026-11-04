from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
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
    # FIT-3237: offline serves only Interface Components files a previous run fetched.
    assert FakePreviewServer.instances[0].kwargs["fetch_components"] is False


@pytest.mark.parametrize("offline", [False, True], ids=["online", "offline"])
def test_preview_fetches_components_on_demand_unless_offline(monkeypatch: Any, tmp_path: Path, offline: bool) -> None:
    FakePreviewCache.instances = []
    FakePreviewCache.error = None
    FakePreviewServer.instances = []
    monkeypatch.setattr(cli, "PreviewAssetCache", FakePreviewCache)
    monkeypatch.setattr(cli, "LocalPreviewServer", FakePreviewServer)
    monkeypatch.setitem(sys.modules, "watchfiles", SimpleNamespace(watch=_stop_watch))
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")

    args = ["preview", str(file), "--no-open", "--token", "secret", "--lse-url", "https://ls.example"]
    result = runner.invoke(cli.app, args + (["--offline"] if offline else []))

    assert result.exit_code == 0, result.output
    assert FakePreviewServer.instances[0].kwargs["fetch_components"] is (not offline)


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


def _jwt(token_type: str, jti: str, *, expires_in: int = 3600) -> str:
    import time

    import jwt

    return jwt.encode(
        {"token_type": token_type, "jti": jti, "exp": int(time.time()) + expires_in}, "test-secret", algorithm="HS256"
    )


def _run_preview_with_upstream(monkeypatch: Any, tmp_path: Path, upstream: Any, token: str, on_watch: Any) -> Any:
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

    def watch(*_args: Any, **_kwargs: Any) -> Any:
        on_watch(servers[-1])
        raise KeyboardInterrupt
        yield

    class MockedClient(preview_server_module.httpx.Client):
        # A subclass, not a factory: the SDK token refresh checks `isinstance(client, httpx.Client)`.
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            kwargs.setdefault("transport", httpx.MockTransport(upstream))
            super().__init__(*args, **kwargs)

    FakePreviewCache.instances = []
    monkeypatch.setattr(preview_server_module.httpx, "Client", MockedClient)
    monkeypatch.setattr(cli, "PreviewAssetCache", TrackingCache)
    monkeypatch.setattr(cli, "LocalPreviewServer", TrackingServer)
    monkeypatch.setitem(sys.modules, "watchfiles", SimpleNamespace(watch=watch))
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")
    return runner.invoke(
        cli.app, ["preview", str(file), "--token", token, "--lse-url", "https://ls.example", "--no-open"]
    )


def test_preview_renews_expired_access_token_before_save(monkeypatch: Any, tmp_path: Path) -> None:
    """FIT-3310 e2e: the access token minted at startup has expired by Save time; Save sends a renewed one."""
    pat = _jwt("refresh", "pat")
    minted: list[str] = []
    upstream_auth: list[str] = []
    probe: dict[str, int] = {}

    def upstream(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/token/refresh/":
            assert json.loads(request.content) == {"refresh": pat}
            # The first access token is already expired when Save runs; later ones are valid.
            minted.append(_jwt("access", f"access-{len(minted)}", expires_in=-1 if not minted else 300))
            return httpx.Response(200, json={"access": minted[-1]}, request=request)
        upstream_auth.append(request.headers["Authorization"])
        if request.headers["Authorization"] != f"Bearer {minted[-1]}" or len(minted) < 2:
            return httpx.Response(401, json={"detail": "Token is expired"}, request=request)
        return httpx.Response(201, json={"id": 5, "title": "Saved", "workspace": 1}, request=request)

    def save(server: LocalPreviewServer) -> None:
        probe["save"] = httpx.post(
            f"{server.host_origin}/{server.capability}/bff/api/interfaces/", json={"title": "Saved"}
        ).status_code

    result = _run_preview_with_upstream(monkeypatch, tmp_path, upstream, pat, save)

    assert result.exit_code == 0, result.output
    assert probe == {"save": 201}
    # Renewed before sending: the expired startup token never reaches the interface API.
    assert upstream_auth == [f"Bearer {minted[1]}"]
    assert len(minted) == 2


@pytest.mark.parametrize("failure", ["revoked", "not-json"])
def test_preview_refresh_failure_keeps_running_and_reports_auth_failure(
    monkeypatch: Any, tmp_path: Path, failure: str
) -> None:
    pat = _jwt("refresh", "pat")
    refresh_calls: list[int] = []
    probe: dict[str, Any] = {}

    def upstream(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/token/refresh/":
            refresh_calls.append(1)
            if len(refresh_calls) == 1:
                return httpx.Response(200, json={"access": _jwt("access", "startup", expires_in=-1)}, request=request)
            if failure == "revoked":
                # The PAT itself was revoked while the preview was running.
                return httpx.Response(401, json={"detail": "Token is blacklisted"}, request=request)
            # A proxy login page answers 200 with HTML instead of JSON.
            return httpx.Response(200, text="<html>Sign in</html>", request=request)
        return httpx.Response(200, json=[], request=request)

    def save(server: LocalPreviewServer) -> None:
        response = httpx.get(f"{server.host_origin}/{server.capability}/bff/api/workspaces/")
        probe["status"], probe["body"] = response.status_code, response.json()

    result = _run_preview_with_upstream(monkeypatch, tmp_path, upstream, pat, save)

    assert result.exit_code == 0, result.output
    assert probe == {"status": 401, "body": {"detail": "Label Studio authentication failed"}}
    assert len(refresh_calls) == 2


def test_preview_expired_pat_without_cache_fails_with_the_sdk_error(monkeypatch: Any, tmp_path: Path) -> None:
    FakePreviewCache.instances = []
    FakePreviewServer.instances = []
    monkeypatch.setattr(cli, "PreviewAssetCache", FakePreviewCache)
    monkeypatch.setattr(cli, "LocalPreviewServer", FakePreviewServer)
    monkeypatch.setattr(FakePreviewCache, "current_snapshot", lambda self: None, raising=False)
    monkeypatch.setitem(sys.modules, "watchfiles", SimpleNamespace(watch=_stop_watch))
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")

    expired = _jwt("refresh", "pat", expires_in=-60)
    result = runner.invoke(
        cli.app, ["preview", str(file), "--no-open", "--token", expired, "--lse-url", "https://ls.example"]
    )

    assert result.exit_code == 1
    assert "API key has expired" in result.output
    assert FakePreviewServer.instances == []


def test_preview_legacy_token_provider_sends_token_header(monkeypatch: Any, tmp_path: Path) -> None:
    FakePreviewCache.instances = []
    FakePreviewCache.error = None
    FakePreviewServer.instances = []
    monkeypatch.setattr(cli, "PreviewAssetCache", FakePreviewCache)
    monkeypatch.setattr(cli, "LocalPreviewServer", FakePreviewServer)
    monkeypatch.setitem(sys.modules, "watchfiles", SimpleNamespace(watch=_stop_watch))
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")

    args = ["preview", str(file), "--no-open", "--token", "legacy-key", "--lse-url", "https://ls.example"]
    result = runner.invoke(cli.app, args)

    assert result.exit_code == 0, result.output
    provider = FakePreviewServer.instances[0].kwargs["auth_header_provider"]
    assert provider() == provider(refresh=True) == {"Authorization": "Token legacy-key"}


def test_auth_headers_send_access_token_as_bearer_without_exchange(monkeypatch: Any) -> None:
    """Service Account tokens are access tokens; posting one to /api/token/refresh/ is rejected as the wrong type."""
    import httpx

    real_client = httpx.Client

    def reject(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Token has wrong type"})

    class RejectingClient(real_client):  # type: ignore[misc, valid-type]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            kwargs["transport"] = httpx.MockTransport(reject)
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(httpx, "Client", RejectingClient)
    access = _jwt("access", "service-account")

    assert cli._auth_headers(access, base_url="https://ls.example") == {"Authorization": f"Bearer {access}"}
