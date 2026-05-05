import json
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from label_studio_sdk._extensions.cli.main import app as root_app
from label_studio_sdk._extensions.interface import cli as interface_cli

runner = CliRunner()


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


class FakeHttpClient:
    instances: list["FakeHttpClient"] = []

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
        return FakeResponse({"id": 12, "title": "Existing", "code": "old", "versions": [], "messages": [], "artifacts": []})

    def post(self, url: str, json: dict[str, Any] | None = None, **kwargs: Any) -> FakeResponse:
        self.calls.append(("POST", url, json))
        return FakeResponse({"id": 12, "title": json.get("title") if json else "Demo", "workspace": json.get("workspace")})

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


def test_sync_creates_interface_and_writes_sidecar(monkeypatch: Any, tmp_path: Path) -> None:
    file = tmp_path / "Screen.jsx"
    file.write_text("({ default: function Screen() { return null; } })\n", encoding="utf-8")
    FakeHttpClient.instances = []
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

    sidecar = json.loads((tmp_path / "Screen.jsx.ls-interface.json").read_text(encoding="utf-8"))
    assert sidecar["http://ls"]["interface_id"] == 12
    assert sidecar["http://ls"]["source_version"] == 0


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
