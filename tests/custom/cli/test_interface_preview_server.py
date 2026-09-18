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
        assert config["bffBasePath"] == [f"/{server.capability}/bff"]
        assert config["sandboxShellUrl"] == [server.sandbox_shell_url]
        assert config["saveEnabled"] == ["0"]
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
        auth_headers={"Authorization": "Token must-not-leak"},
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
            assert set(payload) <= {"code", "task", "interfaceId", "lseUrl", "workspace"}
            assert payload == {
                "code": "second",
                "task": {"text": "two"},
                "interfaceId": 12,
                "lseUrl": "https://ls.example",
                "workspace": None,
            }
            assert "must-not-leak" not in json.dumps(payload)


def test_create_bind_is_pushed_on_sse_for_fe_consumer(tmp_path: Path) -> None:
    """FE learns the bind from SSE after create — no sticky client policy required."""

    def upstream(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            return httpx.Response(201, json={"id": 77, "title": "Created"}, request=request)
        return httpx.Response(200, json={"ok": True}, request=request)

    with (
        httpx.Client(transport=httpx.MockTransport(upstream)) as upstream_client,
        LocalPreviewServer(
            asset_root=_assets(tmp_path),
            upstream_origin="https://ls.example",
            auth_headers={"Authorization": "Bearer server-secret"},
            upstream_client=upstream_client,
        ) as server,
    ):
        server.publish_file_update(
            code="draft", task=None, interface_id=None, lse_url="https://ls.example", workspace=7
        )
        created = httpx.post(f"{server.host_origin}/{server.capability}/bff/api/interfaces/", json={"title": "Demo"})
        assert created.status_code == 201

        with httpx.stream("GET", f"{server.host_origin}/{server.capability}/events", timeout=2) as stream:
            payloads = []
            for line in stream.iter_lines():
                if line.startswith("data: "):
                    payloads.append(json.loads(line[6:]))
                    if len(payloads) >= 2:
                        break

    assert payloads[0]["interfaceId"] is None
    assert payloads[0]["code"] == "draft"
    assert payloads[0]["workspace"] == 7
    assert payloads[1] == {
        "code": "draft",
        "task": None,
        "interfaceId": 77,
        "lseUrl": "https://ls.example",
        "workspace": 7,
    }


def test_create_before_first_file_update_does_not_publish_empty_code(tmp_path: Path) -> None:
    def upstream(request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, json={"id": 77}, request=request)

    with (
        httpx.Client(transport=httpx.MockTransport(upstream)) as upstream_client,
        LocalPreviewServer(
            asset_root=_assets(tmp_path),
            upstream_origin="https://ls.example",
            auth_headers={"Authorization": "Bearer server-secret"},
            upstream_client=upstream_client,
        ) as server,
    ):
        created = httpx.post(f"{server.host_origin}/{server.capability}/bff/api/interfaces/", json={"title": "Demo"})
        assert created.status_code == 201

        server.publish_file_update(code="draft", task=None, interface_id=None, lse_url="https://ls.example")
        with httpx.stream("GET", f"{server.host_origin}/{server.capability}/events", timeout=2) as stream:
            lines = stream.iter_lines()
            assert next(lines) == "id: 1"
            assert next(lines) == "event: file-update"
            payload = json.loads(next(lines).removeprefix("data: "))

    assert payload["code"] == "draft"
    assert payload["interfaceId"] == 77


def test_save_bff_allowlist_auth_and_bind_durability(tmp_path: Path) -> None:
    """BFF shape allowlist, auth forwarding, create/SSE bind, and null-publish durability."""
    requests: list[httpx.Request] = []

    def upstream(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "POST" and request.url.path == "/api/interfaces/":
            return httpx.Response(
                201, json={"id": 77, "title": "Created", "url": "https://evil.example/x"}, request=request
            )
        return httpx.Response(200, json={"ok": True}, request=request)

    with (
        httpx.Client(transport=httpx.MockTransport(upstream)) as upstream_client,
        LocalPreviewServer(
            asset_root=_assets(tmp_path),
            upstream_origin="https://ls.example",
            auth_headers={"Authorization": "Bearer server-secret"},
            upstream_client=upstream_client,
        ) as server,
    ):
        assert parse_qs(urlsplit(server.url).query)["saveEnabled"] == ["1"]
        bff = f"{server.host_origin}/{server.capability}/bff"

        assert httpx.post(f"{bff}/api/tasks/1/", json={}).status_code == 403
        listed = httpx.get(f"{bff}/api/workspaces/")
        assert httpx.patch(f"{bff}/api/interfaces/12/", json={"title": "Demo"}).status_code == 403

        created = httpx.post(f"{bff}/api/interfaces/", json={"title": "Demo"})
        assert created.status_code == 201

        server.publish_file_update(code="changed", task=None, interface_id=None, lse_url="https://ls.example")
        assert httpx.post(f"{bff}/api/interfaces/", json={"title": "Other"}).status_code == 403
        assert httpx.patch(f"{bff}/api/interfaces/99/", json={"title": "Nope"}).status_code == 403
        updated = httpx.patch(f"{bff}/api/interfaces/77/", json={"title": "Demo"})

        server.publish_file_update(code="seeded", task=None, interface_id=12, lse_url="https://ls.example")
        assert httpx.patch(f"{bff}/api/interfaces/77/", json={"title": "stale"}).status_code == 403
        seeded = httpx.patch(f"{bff}/api/interfaces/12/", json={"title": "Seeded"})

    assert listed.status_code == 200
    assert updated.status_code == 200
    assert seeded.status_code == 200
    assert all("Access-Control-Allow-Origin" not in response.headers for response in (listed, created, updated, seeded))
    assert [request.url.path for request in requests] == [
        "/api/workspaces/",
        "/api/interfaces/",
        "/api/interfaces/77/",
        "/api/interfaces/12/",
    ]
    assert all(request.headers["Authorization"] == "Bearer server-secret" for request in requests)
    assert all("server-secret" not in response.text for response in (listed, created, updated, seeded))


def test_save_bff_rejects_oversized_bodies(tmp_path: Path) -> None:
    with LocalPreviewServer(
        asset_root=_assets(tmp_path),
        upstream_origin="https://ls.example",
        auth_headers={"Authorization": "Bearer server-secret"},
    ) as server:
        response = httpx.post(
            f"{server.host_origin}/{server.capability}/bff/api/interfaces/",
            content=b"x" * (5 * 1024 * 1024 + 1),
            headers={"Content-Type": "application/json"},
        )
    assert response.status_code == 413


def test_publish_rejects_bool_interface_id(tmp_path: Path) -> None:
    with LocalPreviewServer(asset_root=_assets(tmp_path), upstream_origin="https://ls.example") as server:
        with pytest.raises(TypeError, match="interface_id"):
            server.publish_file_update(code="x", task=None, interface_id=True, lse_url="https://ls.example")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("method", "path", "bound_interface_id"),
    (
        ("GET", "/api/workspaces/", None),
        ("POST", "/api/interfaces/", None),
        ("PATCH", "/api/interfaces/12/", 12),
    ),
)
def test_save_bff_rejects_all_requests_without_auth_headers(
    tmp_path: Path, method: str, path: str, bound_interface_id: int | None
) -> None:
    requests: list[httpx.Request] = []

    def upstream(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=[], request=request)

    with (
        httpx.Client(transport=httpx.MockTransport(upstream)) as upstream_client,
        LocalPreviewServer(
            asset_root=_assets(tmp_path),
            upstream_origin="https://ls.example",
            upstream_client=upstream_client,
            bound_interface_id=bound_interface_id,
        ) as server,
    ):
        response = httpx.request(method, f"{server.host_origin}/{server.capability}/bff{path}")

    assert response.status_code == 401
    assert response.json() == {"detail": "Label Studio authentication failed"}
    assert requests == []


def test_save_bff_sanitizes_auth_failures_and_upstream_timeouts(tmp_path: Path) -> None:
    def unauthorized(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": request.headers["Authorization"]}, request=request)

    with (
        httpx.Client(transport=httpx.MockTransport(unauthorized)) as upstream_client,
        LocalPreviewServer(
            asset_root=_assets(tmp_path),
            upstream_origin="https://ls.example",
            auth_headers={"Authorization": "Bearer server-secret"},
            upstream_client=upstream_client,
        ) as server,
    ):
        response = httpx.get(f"{server.host_origin}/{server.capability}/bff/api/workspaces/")

    assert response.status_code == 401
    assert response.json() == {"detail": "Label Studio authentication failed"}
    assert "server-secret" not in response.text

    def timeout(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    with (
        httpx.Client(transport=httpx.MockTransport(timeout)) as upstream_client,
        LocalPreviewServer(
            asset_root=_assets(tmp_path),
            upstream_origin="https://ls.example",
            auth_headers={"Authorization": "Bearer server-secret"},
            upstream_client=upstream_client,
        ) as server,
    ):
        response = httpx.post(
            f"{server.host_origin}/{server.capability}/bff/api/interfaces/",
            json={"title": "Demo"},
        )

    assert response.status_code == 502
    assert response.json() == {"detail": "upstream request failed"}


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
