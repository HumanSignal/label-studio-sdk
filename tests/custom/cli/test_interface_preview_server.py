from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from .preview_fakes import preview_asset_root

from label_studio_sdk._extensions.interface.preview import LocalPreviewServer


def _assets(tmp_path: Path) -> Path:
    return preview_asset_root(tmp_path)


def test_server_uses_host_and_sandbox_loopback_origins_with_capability_config(tmp_path: Path) -> None:
    with LocalPreviewServer(asset_root=_assets(tmp_path), upstream_origin="https://ls.example") as server:
        assert server.host_address[0] == "127.0.0.1"
        assert server.sandbox_address[0] == "127.0.0.1"
        assert server.host_address[1] != server.sandbox_address[1]
        assert server.url.startswith(f"http://127.0.0.1:{server.host_address[1]}/{server.capability}/")

        parsed = urlsplit(server.url)
        config = parse_qs(parsed.query)
        assert config["eventsPath"] == [f"/{server.capability}/events"]
        assert "bffBasePath" not in config
        assert "saveEnabled" not in config
        assert config["sandboxShellUrl"] == [server.sandbox_shell_url]
        assert urlsplit(server.sandbox_shell_url).port == server.sandbox_address[1]

        host_response = httpx.get(server.url)
        assert host_response.status_code == 200
        assert "Access-Control-Allow-Origin" not in host_response.headers
        host_csp = host_response.headers["Content-Security-Policy"]
        assert "script-src 'self' 'unsafe-eval' blob:" in host_csp
        assert "connect-src 'self'" in host_csp
        assert f"frame-src {server.sandbox_origin}" in host_csp
        assert "https://ls.example" not in host_csp
        assert host_response.headers["Referrer-Policy"] == "no-referrer"
        assert host_response.headers["X-Content-Type-Options"] == "nosniff"
        assert httpx.get(f"http://127.0.0.1:{server.host_address[1]}/wrong/").status_code == 403
        assert httpx.get(f"{server.host_origin}/{server.capability}/../secret").status_code == 403
        assert httpx.get(f"{server.host_origin}/{server.capability}/%2e%2e/secret").status_code == 404

        shell_response = httpx.get(server.sandbox_shell_url)
        assert shell_response.status_code == 200
        assert "Access-Control-Allow-Origin" not in shell_response.headers
        csp = shell_response.headers["Content-Security-Policy"]
        assert f"frame-ancestors http://127.0.0.1:{server.host_address[1]}" in csp
        assert "connect-src 'self'" in csp
        assert shell_response.headers["Referrer-Policy"] == "no-referrer"
        assert httpx.get(f"http://127.0.0.1:{server.sandbox_address[1]}/wrong/interface-shell.html").status_code == 403
        assert httpx.get(f"{server.sandbox_origin}/{server.sandbox_capability}/../secret").status_code == 403
        assert httpx.get(f"{server.sandbox_origin}/{server.sandbox_capability}/%2e%2e/secret").status_code == 404


def test_sse_replays_current_file_and_publishes_updates(tmp_path: Path) -> None:
    with LocalPreviewServer(
        asset_root=_assets(tmp_path),
        upstream_origin="https://ls.example",
    ) as server:
        first = server.publish_file_update(
            code="first", task={"text": "one"}, interface_id=12, lse_url="https://ls.example"
        )
        server.publish_file_update(code="second", task={"text": "two"}, interface_id=None, lse_url="https://ls.example")

        with httpx.stream(
            "GET",
            f"{server.host_origin}/{server.capability}/events",
            headers={"Last-Event-ID": str(first)},
            timeout=2,
        ) as response:
            lines = response.iter_lines()
            assert response.status_code == 200
            assert next(lines) == "id: 2"
            assert next(lines) == "event: file-update"
            payload = json.loads(next(lines).removeprefix("data: "))
            # Null publish keeps the authoritative bind on the outbound stream.
            assert set(payload) <= {"code", "task", "interfaceId", "lseUrl"}
            assert payload == {
                "code": "second",
                "task": {"text": "two"},
                "interfaceId": 12,
                "lseUrl": "https://ls.example",
            }
            assert "must-not-leak" not in json.dumps(payload)


def test_publish_rejects_bool_interface_id(tmp_path: Path) -> None:
    with LocalPreviewServer(asset_root=_assets(tmp_path), upstream_origin="https://ls.example") as server:
        with pytest.raises(TypeError, match="interface_id"):
            server.publish_file_update(code="x", task=None, interface_id=True, lse_url="https://ls.example")  # type: ignore[arg-type]


def test_sse_waiter_receives_later_update(tmp_path: Path) -> None:
    received: dict[str, Any] = {}
    with LocalPreviewServer(asset_root=_assets(tmp_path), upstream_origin="https://ls.example") as server:

        def consume() -> None:
            with httpx.stream(
                "GET",
                f"{server.host_origin}/{server.capability}/events",
                timeout=3,
            ) as response:
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        received.update(json.loads(line[6:]))
                        return

        thread = threading.Thread(target=consume)
        thread.start()
        server.publish_file_update(code="later", task=None, interface_id=None, lse_url="https://ls.example")
        thread.join(timeout=2)

    assert received["code"] == "later"
    assert received["interfaceId"] is None
