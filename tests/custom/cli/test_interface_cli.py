import base64
import json
import sys
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx
import label_studio_sdk
from .preview_fakes import FakePreviewCache, FakePreviewServer
from label_studio_sdk._extensions.cli.main import app as root_app
from label_studio_sdk._extensions.interface import cli as interface_cli
from typer.testing import CliRunner

runner = CliRunner()


def _jwt_token(token_type: str) -> str:
    def encode(value: dict[str, Any]) -> str:
        return base64.urlsafe_b64encode(json.dumps(value).encode("utf-8")).rstrip(b"=").decode("ascii")

    # Label Studio tokens always carry `exp`; the SDK client rejects JWTs without one.
    claims = {"token_type": token_type, "exp": 4102444800}
    return f"{encode({'alg': 'HS256', 'typ': 'JWT'})}.{encode(claims)}.{encode({'sig': True})}"


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



def test_init_screen_template_uses_shell_region_callbacks(tmp_path: Path) -> None:
    # FIT-2953: the scaffold must follow DynamicScreenProps (no setRegions) so shell undo/redo records edits.
    runner.invoke(interface_cli.app, ["init", str(tmp_path)])
    screen = (tmp_path / "Screen.jsx").read_text(encoding="utf-8")

    assert "setRegions" not in screen
    assert "addRegion" in screen and "updateRegion" in screen
    assert screen.rstrip().endswith("})")


def test_init_scaffolds_design_system_controls(monkeypatch: Any, tmp_path: Path) -> None:
    # FIT-3447: offline or on hosts without interfaces_components (e.g. 2.37), the starter stays free of
    # window.InterfaceComponents so `interface validate` works without an editor-standalone bundle. When the target
    # host reports `interfaces_components` enabled via authoring-capabilities, init scaffolds the ChoiceGroup
    # variant and reads it by property (never destructuring the lazy window.InterfaceComponents Proxy).
    monkeypatch.delenv("LABEL_STUDIO_URL", raising=False)
    monkeypatch.delenv("LS_URL", raising=False)
    monkeypatch.delenv("LABEL_STUDIO_API_KEY", raising=False)

    offline_dir = tmp_path / "offline"
    res_offline = runner.invoke(interface_cli.app, ["init", str(offline_dir)])
    assert res_offline.exit_code == 0, res_offline.output
    offline_screen = (offline_dir / "Screen.jsx").read_text(encoding="utf-8")
    offline_scenarios = (offline_dir / "scenarios.js").read_text(encoding="utf-8")
    assert "<button" in offline_screen
    assert "InterfaceComponents" not in offline_screen
    assert 'getByRole("button", { name: "Positive" })' in offline_scenarios

    _reset_fake_http()
    FakeHttpClient.interface_payload = {
        "schema_version": 1,
        "capabilities": {"interfaces_components": False, "collection": False, "scenarios": True},
    }
    monkeypatch.setattr(interface_cli.httpx, "Client", FakeHttpClient)

    flag_off_dir = tmp_path / "flag_off"
    res_off = runner.invoke(
        interface_cli.app,
        ["init", str(flag_off_dir), "--lse-url", "http://ls", "--token", "token"],
    )
    assert res_off.exit_code == 0, res_off.output
    assert "InterfaceComponents" not in (flag_off_dir / "Screen.jsx").read_text(encoding="utf-8")

    _reset_fake_http()
    FakeHttpClient.interface_payload = {
        "schema_version": 1,
        "capabilities": {"interfaces_components": True, "collection": False, "scenarios": True},
    }
    flag_on_dir = tmp_path / "flag_on"
    res_on = runner.invoke(
        interface_cli.app,
        ["init", str(flag_on_dir), "--lse-url", "http://ls", "--token", "token"],
    )
    assert res_on.exit_code == 0, res_on.output
    assert FakeHttpClient.instances[-1].calls == [("GET", "http://ls/api/interfaces/authoring-capabilities/", None)]
    screen = (flag_on_dir / "Screen.jsx").read_text(encoding="utf-8")
    scenarios = (flag_on_dir / "scenarios.js").read_text(encoding="utf-8")

    assert "<button" not in screen
    assert "window.InterfaceComponents.ChoiceGroup" in screen
    assert "} = window.InterfaceComponents" not in screen
    assert 'getByRole("radio", { name: "Positive" })' in scenarios
    assert 'getByRole("button"' not in scenarios


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

    def request(self, method: str, url: str, json: dict[str, Any] | None = None, **kwargs: Any) -> FakeResponse:
        # The SDK client's token refresh goes through `request`.
        return self.post(url, json=json) if method == "POST" else self.get(url)

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
                "scenarios",
                "data_sample",
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


def _mock_preview_runtime(monkeypatch: Any) -> None:
    FakePreviewServer.instances = []
    FakePreviewCache.instances = []
    FakePreviewCache.error = None
    monkeypatch.delenv("LABEL_STUDIO_API_KEY", raising=False)
    monkeypatch.setattr(interface_cli, "PreviewAssetCache", FakePreviewCache)
    monkeypatch.setattr(interface_cli, "LocalPreviewServer", FakePreviewServer)


def test_sync_creates_interface_and_writes_sidecar(monkeypatch: Any, tmp_path: Path) -> None:
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })\n", encoding="utf-8")
    task = tmp_path / "task.json"
    task.write_text('{"text": "Sample Task Content"}', encoding="utf-8")
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
    assert payload["data_sample"] == {"text": "Sample Task Content"}
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
    _mock_preview_runtime(monkeypatch)
    monkeypatch.setitem(sys.modules, "watchfiles", SimpleNamespace(watch=fake_watch))

    result = runner.invoke(interface_cli.app, ["preview", str(tmp_path), "--lse-url", "http://ls", "--no-open"])

    assert result.exit_code == 0, result.output
    payload = FakePreviewServer.instances[-1].updates[0]
    assert payload == {
        "code": "({ default: function Screen() { return null; } })",
        "task": {"text": "Example"},
        "interface_id": None,
        "lse_url": "http://ls",
        "workspace": None,
    }
    assert calls["watch_paths"] == (file.parent.resolve(),)


def test_preview_resolves_local_paths(monkeypatch: Any, tmp_path: Path) -> None:
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")

    # Create mock files to be referenced in task data
    image_relative = tmp_path / "posum.jpg"
    image_relative.write_bytes(b"mock image relative content")

    image_absolute = tmp_path / "another.png"
    image_absolute.write_bytes(b"mock image absolute content")

    task = tmp_path / "sample.json"
    task.write_text(
        json.dumps(
            {
                "image_rel": "posum.jpg",
                "image_abs": str(image_absolute),
                "some_text": "hello world",
                "web_url": "https://example.com/posum.jpg",
            }
        ),
        encoding="utf-8",
    )

    calls: dict[str, Any] = {}

    def fake_watch(*paths: Path, **kwargs: Any) -> Any:
        calls["watch_paths"] = paths
        calls["watch_kwargs"] = kwargs
        raise KeyboardInterrupt
        yield set()

    _reset_fake_http()
    _mock_preview_runtime(monkeypatch)
    monkeypatch.setitem(sys.modules, "watchfiles", SimpleNamespace(watch=fake_watch))

    result = runner.invoke(interface_cli.app, ["preview", str(tmp_path), "--lse-url", "http://ls", "--no-open"])

    assert result.exit_code == 0, result.output
    assert "embedded local file:" in result.output

    payload = FakePreviewServer.instances[-1].updates[0]

    expected_rel = f"data:image/jpeg;base64,{base64.b64encode(b'mock image relative content').decode('utf-8')}"
    expected_abs = f"data:image/png;base64,{base64.b64encode(b'mock image absolute content').decode('utf-8')}"

    assert payload["task"]["image_rel"] == expected_rel
    assert payload["task"]["image_abs"] == expected_abs
    assert payload["task"]["some_text"] == "hello world"
    assert payload["task"]["web_url"] == "https://example.com/posum.jpg"


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


def test_preview_sends_last_task_data_on_code_change(monkeypatch: Any, tmp_path: Path) -> None:
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")
    task = tmp_path / "sample.json"
    task.write_text('{"text": "Example"}', encoding="utf-8")
    calls: dict[str, Any] = {}

    def fake_watch(*paths: Path, **kwargs: Any) -> Any:
        file.write_text("({ default: function Screen() { return 'changed'; } })", encoding="utf-8")
        yield [("modified", str(file))]
        raise KeyboardInterrupt

    _reset_fake_http()
    _mock_preview_runtime(monkeypatch)
    monkeypatch.setitem(sys.modules, "watchfiles", SimpleNamespace(watch=fake_watch))

    result = runner.invoke(interface_cli.app, ["preview", str(tmp_path), "--lse-url", "http://ls", "--no-open"])

    assert result.exit_code == 0, result.output
    updates = FakePreviewServer.instances[-1].updates
    assert len(updates) >= 2
    assert updates[0] == {
        "code": "({ default: function Screen() { return null; } })",
        "task": {"text": "Example"},
        "interface_id": None,
        "lse_url": "http://ls",
        "workspace": None,
    }
    assert updates[1] == {
        "code": "({ default: function Screen() { return 'changed'; } })",
        "task": {"text": "Example"},
        "interface_id": None,
        "lse_url": "http://ls",
        "workspace": None,
    }


def test_load_task_warns_when_local_media_file_is_missing(tmp_path: Path, capsys: Any) -> None:
    task_path = tmp_path / "task.json"
    task_path.write_text('{"image": "posum.jpg", "title": "Wildlife sample"}', encoding="utf-8")

    result = interface_cli._load_task(task_path)

    assert result == {"image": "posum.jpg", "title": "Wildlife sample"}
    err = capsys.readouterr().err
    assert "warning: task field 'image' references local media 'posum.jpg'" in err


def test_preview_warns_when_task_references_missing_local_media(monkeypatch: Any, tmp_path: Path) -> None:
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")
    task = tmp_path / "task.json"
    task.write_text('{"image": "posum.jpg", "title": "Wildlife sample"}', encoding="utf-8")

    _reset_fake_http()
    _mock_preview_runtime(monkeypatch)
    monkeypatch.setitem(
        sys.modules,
        "watchfiles",
        SimpleNamespace(watch=lambda *paths, **kwargs: (_ for _ in ()).throw(KeyboardInterrupt)),
    )

    result = runner.invoke(interface_cli.app, ["preview", str(tmp_path), "--lse-url", "http://ls", "--no-open"])

    assert result.exit_code == 0, result.output
    assert "warning: task field 'image' references local media 'posum.jpg'" in result.output


def test_preview_watches_and_discovers_task_file_later(monkeypatch: Any, tmp_path: Path) -> None:
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")

    # Task file does not exist initially
    task = tmp_path / "task.json"

    calls: dict[str, Any] = {}

    def fake_watch(*paths: Path, **kwargs: Any) -> Any:
        calls["watch_paths"] = paths
        # Create task file during watch loop execution
        task.write_text('{"text": "Discovered Task"}', encoding="utf-8")
        yield [("modified", str(file))]
        raise KeyboardInterrupt

    _reset_fake_http()
    _mock_preview_runtime(monkeypatch)
    monkeypatch.setitem(sys.modules, "watchfiles", SimpleNamespace(watch=fake_watch))

    result = runner.invoke(interface_cli.app, ["preview", str(tmp_path), "--lse-url", "http://ls", "--no-open"])

    assert result.exit_code == 0, result.output
    assert calls["watch_paths"] == (file.parent.resolve(),)

    updates = FakePreviewServer.instances[-1].updates
    # First event had no task data.
    assert updates[0].get("task") is None

    # Second event (after watcher triggered and discovered task.json).
    assert len(updates) >= 2
    assert updates[1]["task"] == {"text": "Discovered Task"}


def _png_data_uri(content: bytes) -> str:
    return f"data:image/png;base64,{base64.b64encode(content).decode('utf-8')}"


def test_preview_reembeds_local_media_added_after_task(monkeypatch: Any, tmp_path: Path) -> None:
    """FIT-2986: task.json written before its media file must load once the file lands."""
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")
    (tmp_path / "task.json").write_text('{"image": "photo.png"}', encoding="utf-8")
    image = tmp_path / "photo.png"

    def fake_watch(*paths: Path, **kwargs: Any) -> Any:
        image.write_bytes(b"late image")
        yield [("added", str(image))]
        raise KeyboardInterrupt

    _reset_fake_http()
    _mock_preview_runtime(monkeypatch)
    monkeypatch.setitem(sys.modules, "watchfiles", SimpleNamespace(watch=fake_watch))

    result = runner.invoke(interface_cli.app, ["preview", str(tmp_path), "--lse-url", "http://ls", "--no-open"])

    assert result.exit_code == 0, result.output
    updates = FakePreviewServer.instances[-1].updates
    assert updates[0]["task"] == {"image": "photo.png"}
    assert len(updates) == 2
    assert updates[1]["task"] == {"image": _png_data_uri(b"late image")}


def test_preview_reembeds_local_media_when_file_changes(monkeypatch: Any, tmp_path: Path) -> None:
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")
    (tmp_path / "task.json").write_text('{"image": "photo.png"}', encoding="utf-8")
    image = tmp_path / "photo.png"
    image.write_bytes(b"first image")

    def fake_watch(*paths: Path, **kwargs: Any) -> Any:
        image.write_bytes(b"second image")
        yield [("modified", str(image))]
        raise KeyboardInterrupt

    _reset_fake_http()
    _mock_preview_runtime(monkeypatch)
    monkeypatch.setitem(sys.modules, "watchfiles", SimpleNamespace(watch=fake_watch))

    result = runner.invoke(interface_cli.app, ["preview", str(tmp_path), "--lse-url", "http://ls", "--no-open"])

    assert result.exit_code == 0, result.output
    updates = FakePreviewServer.instances[-1].updates
    assert updates[0]["task"] == {"image": _png_data_uri(b"first image")}
    assert len(updates) == 2
    assert updates[1]["task"] == {"image": _png_data_uri(b"second image")}


def test_preview_ignores_changes_to_unreferenced_files(monkeypatch: Any, tmp_path: Path) -> None:
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })", encoding="utf-8")
    (tmp_path / "task.json").write_text('{"image": "photo.png"}', encoding="utf-8")
    other = tmp_path / "notes.png"

    def fake_watch(*paths: Path, **kwargs: Any) -> Any:
        other.write_bytes(b"unrelated")
        yield [("added", str(other))]
        raise KeyboardInterrupt

    _reset_fake_http()
    _mock_preview_runtime(monkeypatch)
    monkeypatch.setitem(sys.modules, "watchfiles", SimpleNamespace(watch=fake_watch))

    result = runner.invoke(interface_cli.app, ["preview", str(tmp_path), "--lse-url", "http://ls", "--no-open"])

    assert result.exit_code == 0, result.output
    assert len(FakePreviewServer.instances[-1].updates) == 1


def test_doctor_reports_cache_identity_and_separates_reachability_from_api_auth(
    monkeypatch: Any, tmp_path: Path
) -> None:
    class DiagnosticCache:
        def __init__(self, origin: str) -> None:
            assert origin == "https://ls.example"

        def diagnostics(self) -> Any:
            return SimpleNamespace(
                cache_path=tmp_path / "origin-key" / "protocol-1",
                origin_key="origin-key",
                fingerprint="artifact-fingerprint",
                protocol_version=1,
                last_successful_fetch="2026-09-17T12:00:00+00:00",
                verified=True,
            )

    def fake_get(url: str, **kwargs: Any) -> FakeResponse:
        if url.endswith("/api/current-user/whoami"):
            assert kwargs["headers"] == {"Authorization": "Token secret"}
            return FakeResponse({"detail": "Invalid token"}, status_code=401)
        return FakeResponse({}, status_code=200)

    monkeypatch.setenv("LABEL_STUDIO_API_KEY", "secret")
    monkeypatch.setattr(interface_cli, "PreviewAssetCache", DiagnosticCache)
    monkeypatch.setattr(interface_cli, "_ensure_validator_ready", lambda **_kwargs: tmp_path / "validator")
    monkeypatch.setattr(interface_cli.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(interface_cli.httpx, "get", fake_get)

    result = runner.invoke(interface_cli.app, ["doctor", "--lse-url", "https://ls.example"])

    assert result.exit_code == 1
    assert "OK LSE reachability: https://ls.example -> HTTP 200" in result.output
    assert "FAIL API auth: https://ls.example/api/current-user/whoami -> HTTP 401" in result.output
    assert f"OK preview cache path: {tmp_path}/origin-key/protocol-1" in result.output
    assert "OK preview origin key: origin-key" in result.output
    assert "OK preview fingerprint: artifact-fingerprint" in result.output
    assert "OK preview last fetch: 2026-09-17T12:00:00+00:00" in result.output


def test_start_omits_workspace_when_workspace_id_is_none(monkeypatch: Any, tmp_path: Path) -> None:
    """FIT-3445: Personal Sandbox / shared interfaces have workspace=None; POST /api/projects/ must omit workspace."""
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })\n", encoding="utf-8")

    project_bodies: list[dict[str, Any]] = []
    real_httpx_client = httpx.Client
    real_label_studio = label_studio_sdk.LabelStudio

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/interfaces/":
            body = json.loads(request.content.decode("utf-8"))
            return httpx.Response(
                201,
                json={
                    "id": 82,
                    "title": body["title"],
                    "code": body["code"],
                    "compiled": body["compiled"],
                    "workspace": None,
                    "versions": [{**body["versions"][0], "id": 0}],
                },
            )
        if request.url.path == "/api/projects/":
            body = json.loads(request.content.decode("utf-8"))
            project_bodies.append(body)
            if "workspace" in body and body["workspace"] is None:
                return httpx.Response(
                    400,
                    json={
                        "detail": "Validation error",
                        "validation_errors": {"workspace": ["This field may not be null."]},
                    },
                )
            return httpx.Response(201, json={"id": 101, "title": body.get("title")})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(interface_cli, "_run_validator", lambda _file: _validator_report())
    monkeypatch.setattr(
        interface_cli.httpx,
        "Client",
        lambda *args, **kwargs: real_httpx_client(*args, transport=transport, **kwargs),
    )
    monkeypatch.setattr(
        label_studio_sdk,
        "LabelStudio",
        lambda *args, **kwargs: real_label_studio(
            *args,
            httpx_client=real_httpx_client(transport=transport),
            **kwargs,
        ),
    )

    result = runner.invoke(
        interface_cli.app,
        [
            "start",
            str(file),
            "--no-validate",
            "--no-open",
            "--token",
            "token",
            "--lse-url",
            "http://ls",
        ],
    )

    assert result.exit_code == 0, f"{result.output}\n{result.exception!r}"
    assert "created project #101" in result.output
    assert len(project_bodies) == 1
    assert "workspace" not in project_bodies[0]
    assert project_bodies[0]["source_interface_id"] == 82
    assert project_bodies[0]["source_interface_version"] == 0

    explicit_project = interface_cli._create_project(
        api_key="token",
        base_url="http://ls",
        title="Explicit Workspace Project",
        description="",
        workspace_id=7,
        interface_id=82,
        source_version=0,
        params=None,
    )
    assert getattr(explicit_project, "id", None) == 101
    assert project_bodies[1]["workspace"] == 7


def test_sync_uploads_scenarios_and_tracks_scenarios_in_hash(monkeypatch: Any, tmp_path: Path) -> None:
    """FIT-3445: sibling scenarios.js uploads to /api/interfaces/ and participates in change detection."""
    file = tmp_path / "Screen.jsx"
    code = "({ default: function Screen() { return null; } })"
    file.write_text(code + "\n", encoding="utf-8")
    scenarios_file = tmp_path / "scenarios.js"
    initial_scenarios = 'export default [{ name: "initial" }];'
    scenarios_file.write_text(initial_scenarios + "\n", encoding="utf-8")

    _reset_fake_http()
    monkeypatch.setattr(interface_cli, "_run_validator", lambda _file: _validator_report())
    monkeypatch.setattr(interface_cli.httpx, "Client", FakeHttpClient)

    create_res = runner.invoke(
        interface_cli.app,
        ["sync", str(file), "--title", "Scenario UI", "--token", "token", "--lse-url", "http://ls"],
    )
    assert create_res.exit_code == 0, create_res.output
    create_payload = FakeHttpClient.instances[-1].calls[0][2]
    assert create_payload is not None
    assert create_payload["scenarios"] == initial_scenarios
    assert create_payload["versions"][0]["scenarios"] == initial_scenarios

    # Unchanged code + unchanged scenarios.js skips without hitting the API.
    skip_res = runner.invoke(
        interface_cli.app,
        ["sync", str(file), "--token", "token", "--lse-url", "http://ls"],
    )
    assert skip_res.exit_code == 0, skip_res.output
    assert "no changes" in skip_res.output

    # Editing only scenarios.js changes the sidecar hash and triggers append_versions.
    FakeHttpClient.interface_payload = {
        **deepcopy(DEFAULT_INTERFACE_PAYLOAD),
        "id": 12,
        "title": "Scenario UI",
        "code": code,
        "scenarios": initial_scenarios,
        "versions": [
            {
                "id": 0,
                "code": code,
                "compiled": "compiled-body",
                "scenarios": initial_scenarios,
                "createdAt": "2026-01-01T00:00:00Z",
            }
        ],
    }
    updated_scenarios = 'export default [{ name: "updated" }];'
    scenarios_file.write_text(updated_scenarios + "\n", encoding="utf-8")

    update_res = runner.invoke(
        interface_cli.app,
        ["sync", str(file), "--token", "token", "--lse-url", "http://ls"],
    )
    assert update_res.exit_code == 0, update_res.output
    update_calls = FakeHttpClient.instances[-1].calls
    assert update_calls[1][1] == "http://ls/api/interfaces/12/append_versions/"
    update_payload = update_calls[1][2]
    assert update_payload is not None
    assert update_payload["scenarios"] == updated_scenarios
    assert update_payload["versions"][0]["scenarios"] == updated_scenarios

    # Editing scenarios.js again also triggers --publish (does not match older published version).
    FakeHttpClient.interface_payload = {
        **FakeHttpClient.interface_payload,
        "scenarios": updated_scenarios,
        "versions": [
            {
                "id": 0,
                "code": code,
                "compiled": "compiled-body",
                "scenarios": updated_scenarios,
                "createdAt": "2026-01-01T00:00:00Z",
            }
        ],
    }
    published_scenarios = 'export default [{ name: "published" }];'
    scenarios_file.write_text(published_scenarios + "\n", encoding="utf-8")

    publish_res = runner.invoke(
        interface_cli.app,
        ["sync", str(file), "--publish", "--token", "token", "--lse-url", "http://ls"],
    )
    assert publish_res.exit_code == 0, publish_res.output
    publish_calls = FakeHttpClient.instances[-1].calls
    assert publish_calls[1][1] == "http://ls/api/interfaces/12/append_versions/"
    publish_payload = publish_calls[1][2]
    assert publish_payload is not None
    assert publish_payload["scenarios"] == published_scenarios
    assert publish_payload["versions"][0]["scenarios"] == published_scenarios


def test_pull_writes_scenarios_and_preserves_round_trip(monkeypatch: Any, tmp_path: Path) -> None:
    """FIT-3445: sync -> pull preserves scenarios.js with matching content hash; empty scenarios omits scenarios.js."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    code = "({ default: function Screen() { return <div>ok</div>; } })"
    scenarios = 'export default [\n  { name: "round-trip" }\n];'
    (src_dir / "Screen.jsx").write_text(code + "\n", encoding="utf-8")
    (src_dir / "task.json").write_text('{"text": "Hello"}\n', encoding="utf-8")
    (src_dir / "scenarios.js").write_text(scenarios + "\n", encoding="utf-8")

    stored: dict[str, Any] = {}
    real_httpx_client = httpx.Client

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/api/interfaces/":
            body = json.loads(request.content.decode("utf-8"))
            stored.update(
                {
                    "id": 55,
                    "title": body["title"],
                    "code": body["code"],
                    "compiled": body["compiled"],
                    "scenarios": body.get("scenarios", ""),
                    "data_sample": body.get("data_sample") or {},
                    "metadata": body.get("metadata") or {},
                    "workspace": body.get("workspace"),
                    "versions": [{**body["versions"][0], "id": 0}],
                }
            )
            return httpx.Response(201, json=stored)
        if request.method == "GET" and request.url.path == "/api/interfaces/55/":
            return httpx.Response(200, json=stored)
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(interface_cli, "_run_validator", lambda _file: _validator_report())
    monkeypatch.setattr(
        interface_cli.httpx,
        "Client",
        lambda *args, **kwargs: real_httpx_client(*args, transport=transport, **kwargs),
    )

    sync_res = runner.invoke(
        interface_cli.app,
        ["sync", str(src_dir), "--publish", "--token", "token", "--lse-url", "http://ls"],
    )
    assert sync_res.exit_code == 0, sync_res.output

    pulled_dir = tmp_path / "pulled"
    pull_res = runner.invoke(
        interface_cli.app,
        ["pull", str(pulled_dir), "--id", "55", "--token", "token", "--lse-url", "http://ls"],
    )
    assert pull_res.exit_code == 0, pull_res.output
    assert (pulled_dir / "scenarios.js").read_text(encoding="utf-8") == scenarios + "\n"

    # Existing scenarios.js is protected from overwrite unless --force is passed.
    refuse_res = runner.invoke(
        interface_cli.app,
        ["pull", str(pulled_dir), "--id", "55", "--token", "token", "--lse-url", "http://ls"],
    )
    assert refuse_res.exit_code == 2
    assert "scenarios.js" in refuse_res.output

    # Syncing the pulled directory without edits skips cleanly (both draft and --publish).
    noop_sync = runner.invoke(
        interface_cli.app,
        ["sync", str(pulled_dir), "--token", "token", "--lse-url", "http://ls"],
    )
    assert noop_sync.exit_code == 0, noop_sync.output
    assert "no changes" in noop_sync.output

    noop_publish_sync = runner.invoke(
        interface_cli.app,
        ["sync", str(pulled_dir), "--publish", "--token", "token", "--lse-url", "http://ls"],
    )
    assert noop_publish_sync.exit_code == 0, noop_publish_sync.output
    assert "no changes vs published interface #55" in noop_publish_sync.output

    # Pulling without --version prefers the latest version's scenarios (including local drafts)
    # even when top-level interface.scenarios still holds an earlier published version's suite.
    draft_scenarios = 'export default [{ name: "local-draft" }];'
    stored["versions"].append(
        {
            **stored["versions"][0],
            "id": 1,
            "unpublished": True,
            "scenarios": draft_scenarios,
        }
    )
    draft_dir = tmp_path / "pulled_latest_draft"
    draft_pull = runner.invoke(
        interface_cli.app,
        ["pull", str(draft_dir), "--id", "55", "--token", "token", "--lse-url", "http://ls"],
    )
    assert draft_pull.exit_code == 0, draft_pull.output
    assert (draft_dir / "scenarios.js").read_text(encoding="utf-8") == draft_scenarios + "\n"

    # Pulling an explicit --version uses that version's snapshotted scenarios.
    stored["scenarios"] = 'export default [{ name: "newer-top-level" }];'
    versioned_dir = tmp_path / "pulled_v0"
    v0_pull = runner.invoke(
        interface_cli.app,
        ["pull", str(versioned_dir), "--id", "55", "--version", "0", "--token", "token", "--lse-url", "http://ls"],
    )
    assert v0_pull.exit_code == 0, v0_pull.output
    assert (versioned_dir / "scenarios.js").read_text(encoding="utf-8") == scenarios + "\n"

    # Legacy/system interfaces with no version-level scenarios fall back to top-level scenarios.
    stored["versions"] = [{k: v for k, v in stored["versions"][0].items() if k != "scenarios"}]
    fallback_dir = tmp_path / "pulled_fallback"
    fallback_pull = runner.invoke(
        interface_cli.app,
        ["pull", str(fallback_dir), "--id", "55", "--token", "token", "--lse-url", "http://ls"],
    )
    assert fallback_pull.exit_code == 0, fallback_pull.output
    assert (fallback_dir / "scenarios.js").read_text(encoding="utf-8") == 'export default [{ name: "newer-top-level" }];\n'

    # Empty remote scenarios does not materialize scenarios.js.
    stored["scenarios"] = "   "
    stored["versions"] = [{k: v for k, v in stored["versions"][0].items() if k != "scenarios"}]
    empty_dir = tmp_path / "empty_scenarios"
    empty_pull = runner.invoke(
        interface_cli.app,
        ["pull", str(empty_dir), "--id", "55", "--token", "token", "--lse-url", "http://ls"],
    )
    assert empty_pull.exit_code == 0, empty_pull.output
    assert not (empty_dir / "scenarios.js").exists()
