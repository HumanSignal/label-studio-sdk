import base64
import json
import sys
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from typer.testing import CliRunner

from label_studio_sdk._extensions.cli.main import app as root_app
from label_studio_sdk._extensions.interface import cli as interface_cli

runner = CliRunner()


def _jwt_token(token_type: str) -> str:
    def encode(value: dict[str, Any]) -> str:
        return base64.urlsafe_b64encode(json.dumps(value).encode("utf-8")).rstrip(b"=").decode("ascii")

    return f"{encode({'alg': 'HS256', 'typ': 'JWT'})}.{encode({'token_type': token_type})}.{encode({'sig': True})}"


def test_root_cli_includes_interface_group() -> None:
    result = runner.invoke(root_app, ["--help"])

    assert result.exit_code == 0
    assert "interface" in result.output


def test_init_scaffolds_interface_files(tmp_path: Path) -> None:
    result = runner.invoke(interface_cli.app, ["init", str(tmp_path)])

    assert result.exit_code == 0
    assert (tmp_path / "Screen.jsx").exists()
    assert (tmp_path / "task.json").exists()
    assert (tmp_path / "scenarios.js").exists()
    assert json.loads((tmp_path / "task.json").read_text(encoding="utf-8")) == {
        "text": "The interface CLI is ready to use."
    }

    second = runner.invoke(interface_cli.app, ["init", str(tmp_path)])
    assert second.exit_code == 2
    assert "refusing to overwrite" in second.output


class FakeResponse:
    def __init__(self, payload: dict[str, Any], status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code
        self.text = json.dumps(payload)
        self.request = type("Request", (), {"url": "http://ls/api/interfaces/"})()

    def json(self) -> dict[str, Any]:
        return self.payload

    def raise_for_status(self) -> None:
        return None


DEFAULT_INTERFACE_PAYLOAD: dict[str, Any] = {
    "id": 12,
    "title": "Existing",
    "code": "old",
    "compiled": "compiled-old",
    "versions": [
        {
            "id": 0,
            "code": "old",
            "compiled": "compiled-old",
            "createdAt": "2026-01-01T00:00:00Z",
        }
    ],
    "messages": [],
    "artifacts": [],
    "data_sample": {"text": "Existing task"},
    "metadata": {},
    "workspace": 3,
}


class FakeHttpClient:
    instances: list["FakeHttpClient"] = []
    interface_payload: dict[str, Any] = deepcopy(DEFAULT_INTERFACE_PAYLOAD)
    access_token: str = _jwt_token("access")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.calls: list[tuple[str, str, dict[str, Any] | None]] = []
        self.headers = kwargs.get("headers")
        FakeHttpClient.instances.append(self)

    def __enter__(self) -> "FakeHttpClient":
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def get(self, url: str) -> FakeResponse:
        self.calls.append(("GET", url, None))
        return FakeResponse(deepcopy(FakeHttpClient.interface_payload))

    def post(self, url: str, json: dict[str, Any] | None = None, **kwargs: Any) -> FakeResponse:
        self.calls.append(("POST", url, json))
        if url.endswith("/api/token/refresh/"):
            return FakeResponse({"access": FakeHttpClient.access_token})

        body = json or {}
        if url.endswith("/append_versions/"):
            existing = deepcopy(FakeHttpClient.interface_payload)
            existing_versions = existing.get("versions") or []
            appended_versions = [
                {
                    **version,
                    "id": len(existing_versions) + index,
                    "createdAt": "2026-01-02T00:00:00Z",
                    "createdBy": {"id": 7, "first_name": "SDK", "last_name": "User", "email": "sdk@example.com"},
                }
                for index, version in enumerate(body.get("versions") or [])
            ]
            for field in (
                "title",
                "code",
                "compiled",
                "messages",
                "artifacts",
                "input_schema",
                "output_schema",
                "metadata",
            ):
                if field in body:
                    existing[field] = body[field]
            existing["versions"] = [*existing_versions, *appended_versions]
            return FakeResponse(existing)

        versions = [
            {
                **version,
                "id": index,
                "createdAt": version.get("createdAt", "2026-01-02T00:00:00Z"),
            }
            for index, version in enumerate(body.get("versions") or [])
        ]
        return FakeResponse(
            {
                "id": 12,
                "title": body.get("title", "Demo"),
                "workspace": body.get("workspace"),
                "versions": versions,
            }
        )

    def patch(self, url: str, json: dict[str, Any] | None = None, **kwargs: Any) -> FakeResponse:
        self.calls.append(("PATCH", url, json))
        return FakeResponse({"id": 12, "title": json.get("title") if json else "Demo", "workspace": 3})


def _validator_report() -> dict[str, Any]:
    return {
        "ok": True,
        "compiled": "compiled-body",
        "metadata": {
            "inputSchema": {"type": "object"},
            "outputSchema": {"type": "object", "properties": {}},
            "paramsSchema": {"type": "object"},
        },
        "errors": [],
        "warnings": [],
        "exports": ["default"],
    }


def _reset_fake_http() -> None:
    FakeHttpClient.instances = []
    FakeHttpClient.interface_payload = deepcopy(DEFAULT_INTERFACE_PAYLOAD)
    FakeHttpClient.access_token = _jwt_token("access")


def test_sync_creates_interface_and_writes_sidecar(monkeypatch: Any, tmp_path: Path) -> None:
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })\n", encoding="utf-8")
    _reset_fake_http()
    monkeypatch.setattr(interface_cli, "_run_validator", lambda _file: _validator_report())
    monkeypatch.setattr(interface_cli.httpx, "Client", FakeHttpClient)

    result = runner.invoke(
        interface_cli.app,
        [
            "sync",
            str(file),
            "--title",
            "Demo",
            "--workspace",
            "3",
            "--token",
            "token",
            "--lse-url",
            "http://ls",
        ],
    )

    assert result.exit_code == 0, result.output
    client = FakeHttpClient.instances[-1]
    assert client.headers == {"Authorization": "Token token"}
    assert client.calls[0][0] == "POST"
    payload = client.calls[0][2]
    assert payload is not None
    assert payload["title"] == "Demo"
    assert payload["workspace"] == 3
    assert payload["compiled"] == "compiled-body"
    assert payload["input_schema"] == {"type": "object"}
    assert payload["metadata"]["paramsSchema"] == {"type": "object"}
    assert payload["versions"][0]["op"] == "api_push"
    assert payload["versions"][0]["unpublished"] is True

    sidecar = json.loads((tmp_path / "Screen.jsx.ls-interface.json").read_text(encoding="utf-8"))
    assert sidecar["http://ls"]["interface_id"] == 12
    assert sidecar["http://ls"]["source_version"] == 0


def test_sync_refreshes_pat_before_interface_api(monkeypatch: Any, tmp_path: Path) -> None:
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })\n", encoding="utf-8")
    refresh_token = _jwt_token("refresh")
    access_token = _jwt_token("access")
    _reset_fake_http()
    FakeHttpClient.access_token = access_token
    monkeypatch.setattr(interface_cli, "_run_validator", lambda _file: _validator_report())
    monkeypatch.setattr(interface_cli.httpx, "Client", FakeHttpClient)

    result = runner.invoke(
        interface_cli.app,
        [
            "sync",
            str(file),
            "--title",
            "Demo",
            "--token",
            refresh_token,
            "--lse-url",
            "http://ls",
        ],
    )

    assert result.exit_code == 0, result.output
    refresh_client = FakeHttpClient.instances[0]
    sync_client = FakeHttpClient.instances[-1]
    assert refresh_client.calls == [("POST", "http://ls/api/token/refresh/", {"refresh": refresh_token})]
    assert sync_client.headers == {"Authorization": f"Bearer {access_token}"}
    assert sync_client.calls[0][1] == "http://ls/api/interfaces/"


def test_sync_updates_interface_by_appending_local_draft(monkeypatch: Any, tmp_path: Path) -> None:
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return <div>new</div>; } })\n", encoding="utf-8")
    _reset_fake_http()
    monkeypatch.setattr(interface_cli, "_run_validator", lambda _file: _validator_report())
    monkeypatch.setattr(interface_cli.httpx, "Client", FakeHttpClient)

    result = runner.invoke(
        interface_cli.app,
        [
            "sync",
            str(file),
            "--id",
            "12",
            "--message",
            "Tighten parser",
            "--token",
            "token",
            "--lse-url",
            "http://ls",
        ],
    )

    assert result.exit_code == 0, result.output
    client = FakeHttpClient.instances[-1]
    assert client.calls[0] == ("GET", "http://ls/api/interfaces/12/", None)
    assert client.calls[1][0] == "POST"
    assert client.calls[1][1] == "http://ls/api/interfaces/12/append_versions/"
    payload = client.calls[1][2]
    assert payload is not None
    assert payload["versions"][0]["code"] == "({ default: function Screen() { return <div>new</div>; } })"
    assert payload["versions"][0]["unpublished"] is True
    assert payload["versions"][0]["op"] == "api_push"
    assert "createdAt" not in payload["versions"][0]
    assert payload["messages"][0]["content"] == "Tighten parser"

    sidecar = json.loads((tmp_path / "Screen.jsx.ls-interface.json").read_text(encoding="utf-8"))
    assert sidecar["http://ls"]["source_version"] == 1


def test_sync_publish_appends_published_version(monkeypatch: Any, tmp_path: Path) -> None:
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return <div>published</div>; } })\n", encoding="utf-8")
    _reset_fake_http()
    monkeypatch.setattr(interface_cli, "_run_validator", lambda _file: _validator_report())
    monkeypatch.setattr(interface_cli.httpx, "Client", FakeHttpClient)

    result = runner.invoke(
        interface_cli.app,
        [
            "sync",
            str(file),
            "--id",
            "12",
            "--publish",
            "--token",
            "token",
            "--lse-url",
            "http://ls",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = FakeHttpClient.instances[-1].calls[1][2]
    assert payload is not None
    assert "unpublished" not in payload["versions"][0]


def test_sync_publish_does_not_skip_matching_local_draft(monkeypatch: Any, tmp_path: Path) -> None:
    file = tmp_path / "Screen.jsx"
    file.write_text("old\n", encoding="utf-8")
    _reset_fake_http()
    FakeHttpClient.interface_payload = {
        **deepcopy(DEFAULT_INTERFACE_PAYLOAD),
        "code": "old",
        "versions": [
            {
                "id": 0,
                "code": "old",
                "compiled": "compiled-old",
                "createdAt": "2026-01-01T00:00:00Z",
                "unpublished": True,
            }
        ],
    }
    (tmp_path / "Screen.jsx.ls-interface.json").write_text(
        json.dumps(
            {
                "http://ls": {
                    "interface_id": 12,
                    "title": "Existing",
                    "source_version": 0,
                    "last_pushed_hash": interface_cli._source_hash("old"),
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(interface_cli, "_run_validator", lambda _file: _validator_report())
    monkeypatch.setattr(interface_cli.httpx, "Client", FakeHttpClient)

    result = runner.invoke(
        interface_cli.app,
        [
            "sync",
            str(file),
            "--id",
            "12",
            "--publish",
            "--token",
            "token",
            "--lse-url",
            "http://ls",
        ],
    )

    assert result.exit_code == 0, result.output
    client = FakeHttpClient.instances[-1]
    assert client.calls[0][0] == "GET"
    assert client.calls[1][1] == "http://ls/api/interfaces/12/append_versions/"
    payload = client.calls[1][2]
    assert payload is not None
    assert "unpublished" not in payload["versions"][0]


def test_pull_writes_local_bundle_and_sidecar(monkeypatch: Any, tmp_path: Path) -> None:
    _reset_fake_http()
    FakeHttpClient.interface_payload = {
        **deepcopy(DEFAULT_INTERFACE_PAYLOAD),
        "title": "Pulled Interface",
        "code": "top-level source",
        "data_sample": {"text": "Pulled task"},
        "metadata": {
            "paramsSchema": {
                "type": "object",
                "properties": {"fallback": {"type": "string", "default": "metadata-default"}},
            }
        },
        "versions": [
            {
                "id": 4,
                "code": "selected version source",
                "compiled": "compiled-selected",
                "createdAt": "2026-01-02T00:00:00Z",
                "paramsSchema": {
                    "type": "object",
                    "properties": {"mode": {"type": "string", "default": "review"}},
                },
            }
        ],
    }
    monkeypatch.setattr(interface_cli.httpx, "Client", FakeHttpClient)

    result = runner.invoke(
        interface_cli.app,
        [
            "pull",
            "--id",
            "12",
            "--version",
            "4",
            str(tmp_path),
            "--token",
            "token",
            "--lse-url",
            "http://ls",
        ],
    )

    assert result.exit_code == 0, result.output
    assert (tmp_path / "Screen.jsx").read_text(encoding="utf-8") == "selected version source\n"
    assert json.loads((tmp_path / "task.json").read_text(encoding="utf-8")) == {"text": "Pulled task"}
    assert json.loads((tmp_path / "params.json").read_text(encoding="utf-8")) == {"mode": "review"}

    sidecar = json.loads((tmp_path / "Screen.jsx.ls-interface.json").read_text(encoding="utf-8"))
    assert sidecar["http://ls"]["interface_id"] == 12
    assert sidecar["http://ls"]["title"] == "Pulled Interface"
    assert sidecar["http://ls"]["workspace"] == 3
    assert sidecar["http://ls"]["source_version"] == 4


def test_preview_accepts_interface_directory(monkeypatch: Any, tmp_path: Path) -> None:
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")
    task = tmp_path / "sample.json"
    task.write_text('{"text": "Example"}', encoding="utf-8")
    calls: dict[str, Any] = {}

    def fake_watch(*paths: Path, **kwargs: Any) -> Any:
        calls["watch_paths"] = paths
        calls["watch_kwargs"] = kwargs
        raise KeyboardInterrupt
        yield set()

    _reset_fake_http()
    monkeypatch.setitem(sys.modules, "watchfiles", SimpleNamespace(watch=fake_watch))
    monkeypatch.setattr(interface_cli.httpx, "Client", FakeHttpClient)

    result = runner.invoke(interface_cli.app, ["preview", str(tmp_path), "--lse-url", "http://ls", "--no-open"])

    assert result.exit_code == 0, result.output
    client = FakeHttpClient.instances[-1]
    assert client.calls[0][0] == "POST"
    payload = client.calls[0][2]
    assert payload == {
        "code": "({ default: function Screen() { return null; } })",
        "task": {"text": "Example"},
    }
    assert calls["watch_paths"] == (file.resolve(), task.resolve())


def test_start_syncs_then_creates_project(monkeypatch: Any, tmp_path: Path) -> None:
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")
    params = tmp_path / "params.json"
    params.write_text('{"mode": "review"}', encoding="utf-8")
    calls: dict[str, Any] = {}

    def fake_sync(**kwargs: Any) -> interface_cli.SyncResult:
        calls["sync"] = kwargs
        return interface_cli.SyncResult(
            interface_id=12,
            title="Demo",
            status="created",
            base_url="http://ls",
            source_hash="abc",
            source_version=2,
            workspace_id=7,
        )

    def fake_create_project(**kwargs: Any) -> dict[str, Any]:
        calls["project"] = kwargs
        return {"id": 45}

    opened: list[str] = []
    monkeypatch.setattr(interface_cli, "_sync_interface", fake_sync)
    monkeypatch.setattr(interface_cli, "_create_project", fake_create_project)
    monkeypatch.setattr(interface_cli.webbrowser, "open", opened.append)

    result = runner.invoke(
        interface_cli.app,
        [
            "start",
            str(file),
            "--project-title",
            "Started Project",
            "--workspace",
            "7",
            "--params",
            str(params),
            "--token",
            "token",
            "--lse-url",
            "http://ls",
        ],
    )

    assert result.exit_code == 0, result.output
    assert calls["sync"]["file"] == file
    assert calls["sync"]["publish"] is True
    assert calls["project"] == {
        "api_key": "token",
        "base_url": "http://ls",
        "title": "Started Project",
        "description": "",
        "workspace_id": 7,
        "interface_id": 12,
        "source_version": 2,
        "params": {"mode": "review"},
    }
    assert opened == ["http://ls/projects/45/data"]


def test_start_accepts_interface_directory_and_params_default(monkeypatch: Any, tmp_path: Path) -> None:
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")
    params = tmp_path / "params.json"
    params.write_text('{"mode": "review"}', encoding="utf-8")
    calls: dict[str, Any] = {}

    def fake_sync(**kwargs: Any) -> interface_cli.SyncResult:
        calls["sync"] = kwargs
        return interface_cli.SyncResult(
            interface_id=12,
            title="Demo",
            status="created",
            base_url="http://ls",
            source_hash="abc",
            source_version=2,
            workspace_id=7,
        )

    def fake_create_project(**kwargs: Any) -> dict[str, Any]:
        calls["project"] = kwargs
        return {"id": 45}

    monkeypatch.setattr(interface_cli, "_sync_interface", fake_sync)
    monkeypatch.setattr(interface_cli, "_create_project", fake_create_project)
    monkeypatch.setattr(interface_cli.webbrowser, "open", lambda _url: None)

    result = runner.invoke(
        interface_cli.app,
        [
            "start",
            str(tmp_path),
            "--token",
            "token",
            "--lse-url",
            "http://ls",
            "--no-open",
        ],
    )

    assert result.exit_code == 0, result.output
    assert calls["sync"]["file"] == file
    assert calls["sync"]["publish"] is True
    assert calls["project"]["params"] == {"mode": "review"}
