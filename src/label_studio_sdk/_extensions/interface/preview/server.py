from __future__ import annotations

import json
import mimetypes
import secrets
import threading
from collections import deque
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlencode, urlsplit

from .protocol import PROTOCOL_VERSION, PreviewFileUpdate


def _is_safe_asset_relative(value: str) -> bool:
    if not value or "\\" in value or "\x00" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and path != PurePosixPath(".")


def _coerce_interface_id(value: int | None) -> int | None:
    if value is None:
        return None
    # bool is a subclass of int (`True == 1`); reject it explicitly.
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"interface_id must be an int or None, got {type(value).__name__}")
    return value


class _LoopbackHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class LocalPreviewServer:
    """Two-listener loopback server for static assets and live-reload SSE.

    Save BFF / upstream proxying lands in stack layer 4.
    """

    def __init__(
        self,
        *,
        asset_root: Path,
        upstream_origin: str,
        capability: str | None = None,
        host_capability: str | None = None,
        sandbox_capability: str | None = None,
        bound_interface_id: int | None = None,
    ) -> None:
        self.asset_root = Path(asset_root).resolve()
        self.upstream_origin = upstream_origin.rstrip("/")
        # Host and sandbox use distinct capability tokens so a leaked sandbox URL
        # cannot authorize host SSE (ticket: per-origin capability).
        self.host_capability = host_capability or capability or secrets.token_urlsafe(32)
        self.sandbox_capability = sandbox_capability or secrets.token_urlsafe(32)
        if self.host_capability == self.sandbox_capability:
            self.sandbox_capability = secrets.token_urlsafe(32)
        self._bound_interface_id = _coerce_interface_id(bound_interface_id)
        self._events: deque[tuple[int, PreviewFileUpdate]] = deque(maxlen=100)
        self._next_event_id = 1
        self._condition = threading.Condition()
        self._stopping = False
        self._host_server: _LoopbackHTTPServer | None = None
        self._sandbox_server: _LoopbackHTTPServer | None = None
        self._threads: list[threading.Thread] = []

    @property
    def capability(self) -> str:
        """Host capability token (kept for callers/tests that still use `.capability`)."""
        return self.host_capability

    @property
    def host_address(self) -> tuple[str, int]:
        if self._host_server is None:
            raise RuntimeError("preview server has not started")
        host, port = self._host_server.server_address[:2]
        return str(host), int(port)

    @property
    def sandbox_address(self) -> tuple[str, int]:
        if self._sandbox_server is None:
            raise RuntimeError("preview server has not started")
        host, port = self._sandbox_server.server_address[:2]
        return str(host), int(port)

    @property
    def host_origin(self) -> str:
        host, port = self.host_address
        return f"http://{host}:{port}"

    @property
    def sandbox_origin(self) -> str:
        host, port = self.sandbox_address
        return f"http://{host}:{port}"

    @property
    def sandbox_shell_url(self) -> str:
        return f"{self.sandbox_origin}/{self.sandbox_capability}/interface-shell.html"

    @property
    def url(self) -> str:
        prefix = f"/{self.host_capability}"
        query = urlencode(
            {
                "eventsPath": f"{prefix}/events",
                "sandboxShellUrl": self.sandbox_shell_url,
                "protocolVersion": PROTOCOL_VERSION,
            }
        )
        return f"{self.host_origin}{prefix}/?{query}"

    def start(self) -> LocalPreviewServer:
        if self._host_server is not None:
            return self
        if not self.asset_root.is_dir():
            raise FileNotFoundError(f"preview asset root does not exist: {self.asset_root}")
        self._host_server = _LoopbackHTTPServer(("127.0.0.1", 0), self._host_handler())
        self._sandbox_server = _LoopbackHTTPServer(("127.0.0.1", 0), self._sandbox_handler())
        for name, server in (("host", self._host_server), ("sandbox", self._sandbox_server)):
            thread = threading.Thread(target=server.serve_forever, name=f"interface-preview-{name}", daemon=True)
            thread.start()
            self._threads.append(thread)
        return self

    def stop(self) -> None:
        with self._condition:
            self._stopping = True
            self._condition.notify_all()
        for server in (self._host_server, self._sandbox_server):
            if server is not None:
                server.shutdown()
                server.server_close()
        for thread in self._threads:
            thread.join(timeout=2)
        self._host_server = None
        self._sandbox_server = None
        self._threads.clear()

    def __enter__(self) -> LocalPreviewServer:
        return self.start()

    def __exit__(self, *_args: Any) -> None:
        self.stop()

    def publish_file_update(
        self,
        *,
        code: str,
        task: dict[str, Any] | None,
        interface_id: int | None,
        lse_url: str,
    ) -> int:
        coerced_id = _coerce_interface_id(interface_id)
        with self._condition:
            # Never clear a create/SSE bind on null publishes (live reload without sidecar).
            if coerced_id is not None:
                self._bound_interface_id = coerced_id
            # Outbound stream always carries the authoritative bind so the FE stays a dumb consumer.
            payload: PreviewFileUpdate = {
                "code": code,
                "task": task,
                "interfaceId": self._bound_interface_id,
                "lseUrl": lse_url,
            }
            event_id = self._next_event_id
            self._next_event_id += 1
            self._events.append((event_id, payload))
            self._condition.notify_all()
            return event_id

    def _host_handler(self) -> type[BaseHTTPRequestHandler]:
        owner = self

        class HostHandler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def end_headers(self) -> None:
                self.send_header("Content-Security-Policy", owner._host_csp())
                self.send_header("Referrer-Policy", "no-referrer")
                self.send_header("X-Content-Type-Options", "nosniff")
                super().end_headers()

            def do_GET(self) -> None:
                parsed = urlsplit(self.path)
                relative = self._capability_relative(parsed.path)
                if relative is None:
                    return
                if relative == "events":
                    self._events()
                else:
                    self._serve_local_asset(relative)

            def do_POST(self) -> None:
                self.send_error(HTTPStatus.NOT_FOUND)

            def do_PATCH(self) -> None:
                self.send_error(HTTPStatus.NOT_FOUND)

            def do_OPTIONS(self) -> None:
                if self._capability_relative(urlsplit(self.path).path) is None:
                    return
                self.send_response(HTTPStatus.NO_CONTENT)
                self.send_header("Allow", "GET, OPTIONS")
                self.send_header("Content-Length", "0")
                self.end_headers()

            def _capability_relative(self, path: str) -> str | None:
                prefix = f"/{owner.host_capability}/"
                if not path.startswith(prefix):
                    self.send_error(HTTPStatus.FORBIDDEN)
                    return None
                return path[len(prefix) :]

            def _serve_local_asset(self, relative: str) -> None:
                asset_relative = f"local-playground/{relative or 'index.html'}"
                if not _is_safe_asset_relative(asset_relative):
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                pure = PurePosixPath(asset_relative)
                target = (owner.asset_root / pure).resolve()
                if not target.is_relative_to(owner.asset_root) or not target.is_file():
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                content = target.read_bytes()
                content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(content)

            def _events(self) -> None:
                try:
                    last_id = int(self.headers.get("Last-Event-ID", "0"))
                except ValueError:
                    last_id = 0
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "close")
                self.end_headers()
                while True:
                    with owner._condition:
                        pending = [(event_id, data) for event_id, data in owner._events if event_id > last_id]
                        if not pending and not owner._stopping:
                            owner._condition.wait(timeout=15)
                            pending = [(event_id, data) for event_id, data in owner._events if event_id > last_id]
                        if owner._stopping and not pending:
                            return
                    try:
                        if not pending:
                            self.wfile.write(b": keepalive\n\n")
                            self.wfile.flush()
                        for event_id, data in pending:
                            encoded = json.dumps(data, separators=(",", ":")).encode()
                            self.wfile.write(f"id: {event_id}\nevent: file-update\ndata: ".encode() + encoded + b"\n\n")
                            self.wfile.flush()
                            last_id = event_id
                    except (BrokenPipeError, ConnectionResetError):
                        return

            def log_message(self, _format: str, *_args: Any) -> None:
                return

        return HostHandler

    def _sandbox_handler(self) -> type[BaseHTTPRequestHandler]:
        owner = self

        class SandboxHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                parsed = urlsplit(self.path)
                prefix = f"/{owner.sandbox_capability}/"
                if not parsed.path.startswith(prefix):
                    self.send_error(HTTPStatus.FORBIDDEN)
                    return
                relative = parsed.path[len(prefix) :]
                if not relative or not _is_safe_asset_relative(relative):
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                pure = PurePosixPath(relative)
                target = (owner.asset_root / "editor-standalone" / pure).resolve()
                editor_root = (owner.asset_root / "editor-standalone").resolve()
                if not target.is_relative_to(editor_root) or not target.is_file():
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                content = target.read_bytes()
                content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Referrer-Policy", "no-referrer")
                if relative == "interface-shell.html":
                    self.send_header("Content-Security-Policy", owner._sandbox_csp())
                self.end_headers()
                self.wfile.write(content)

            def log_message(self, _format: str, *_args: Any) -> None:
                return

        return SandboxHandler

    def _sandbox_csp(self) -> str:
        return "; ".join(
            (
                "default-src 'none'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' blob:",
                "style-src 'self' 'unsafe-inline' blob:",
                "img-src 'self' data: blob: http: https:",
                "media-src 'self' data: blob: http: https:",
                "font-src 'self' data:",
                "worker-src blob:",
                "connect-src 'self'",
                f"frame-ancestors {self.host_origin}",
            )
        )

    def _host_csp(self) -> str:
        return "; ".join(
            (
                "default-src 'none'",
                "script-src 'self' 'unsafe-eval' blob:",
                "style-src 'self' 'unsafe-inline' data: blob:",
                "img-src 'self' data: blob:",
                "media-src 'self' data: blob:",
                "font-src 'self' data:",
                "worker-src 'self' blob:",
                "connect-src 'self'",
                f"frame-src {self.sandbox_origin}",
                "object-src 'none'",
                "base-uri 'none'",
                "form-action 'none'",
                "frame-ancestors 'none'",
            )
        )
