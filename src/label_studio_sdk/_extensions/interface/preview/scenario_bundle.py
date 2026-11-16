from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import secrets
import shutil
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit

import appdirs
import httpx
from .cache import (
    _EDITOR_COMPONENTS_KEY,
    _EDITOR_SHELL_KEY,
    _HASHED_EDITOR_BUNDLE,
    CURRENT_FILE,
    EDITOR_ASSET_BASE,
    EDITOR_BUNDLE_API_PATH,
    EDITOR_MANIFEST_PATH,
    EDITOR_SHELL_PATH,
    SNAPSHOT_NAME_PATTERN,
    VERIFICATION_FILE,
    PreviewAssetCache,
    PreviewCacheError,
    _allowlisted_asset_url,
    _editor_assets,
    _is_hashed_editor_bundle,
    _normalize_origin,
)
from .protocol import PROTOCOL_VERSION, InvalidPreviewManifestError, ProtocolMismatchError
from .server import _COMPONENT_FILE_RE, _MAX_COMPONENT_FILE_BYTES, _is_safe_asset_relative, _LoopbackHTTPServer

_SCENARIO_BUNDLE_DIR_NAME = "scenario-editor-standalone"


class ScenarioBundleError(RuntimeError):
    """Raised when `validate --scenario` needs `window.InterfaceComponents` but no editor bundle is available."""


def screen_uses_interface_components(source: str) -> bool:
    """Return True if the Screen source references `InterfaceComponents` or `requiredComponents`."""
    return (
        "InterfaceComponents" in source
        or "requiredComponents" in source
        or "@humansignal/interface-components" in source
    )


def _default_preview_cache_root() -> Path:
    env_override = os.environ.get("LS_INTERFACE_PREVIEW_CACHE_DIR")
    if env_override:
        return Path(env_override)
    return Path(appdirs.user_cache_dir("label-studio-sdk", "HumanSignal")) / "interface-preview"


def _has_usable_editor_bundle(editor_dir: Path) -> bool:
    return (
        (editor_dir / "manifest.json").is_file()
        and (editor_dir / "interface-shell.html").is_file()
        and (editor_dir / "components" / "manifest.json").is_file()
    )


def _write_atomic(target: Path, content: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.with_name(f".{target.name}.{secrets.token_hex(8)}.tmp")
    try:
        staging.write_bytes(content)
        os.replace(staging, target)
    finally:
        staging.unlink(missing_ok=True)


def _fetch_remote_editor_manifests(
    client: httpx.Client,
    normalized: str,
    req_headers: dict[str, str],
) -> tuple[bytes, str, bytes, list[tuple[str, str, str | None]]]:
    """Fetch and validate upstream editor + components manifests without downloading bundle assets."""
    editor_payload: dict[str, Any] | None = None
    editor_manifest_bytes: bytes | None = None
    shell_name: str | None = None
    components_hint: str | None = None

    if req_headers.get("Authorization"):
        try:
            api_resp = client.get(
                normalized + EDITOR_BUNDLE_API_PATH,
                headers=req_headers,
                follow_redirects=False,
            )
            if api_resp.status_code == HTTPStatus.OK:
                parsed = api_resp.json()
                if _is_hashed_editor_bundle(parsed):
                    editor_payload = dict(parsed)
                    bundle = {name: parsed[name] for name in _HASHED_EDITOR_BUNDLE}
                    editor_manifest_bytes = json.dumps(bundle, sort_keys=True, separators=(",", ":")).encode("utf-8")
                    raw_shell = editor_payload.pop(_EDITOR_SHELL_KEY, None)
                    raw_comp = editor_payload.pop(_EDITOR_COMPONENTS_KEY, None)
                    shell_name = raw_shell if isinstance(raw_shell, str) and raw_shell else None
                    components_hint = raw_comp if isinstance(raw_comp, str) and raw_comp else None
        except (httpx.HTTPError, ValueError):
            editor_payload = None

    if editor_payload is None:
        manifest_resp = client.get(normalized + EDITOR_MANIFEST_PATH, headers=req_headers, follow_redirects=False)
        manifest_resp.raise_for_status()
        parsed = manifest_resp.json()
        if not isinstance(parsed, dict):
            raise ScenarioBundleError(f"Invalid editor-standalone manifest from {normalized}")
        editor_payload = dict(parsed)
        # Only the authenticated API names hashed shell/components copies; never trust them from CDN manifest.
        editor_payload.pop(_EDITOR_SHELL_KEY, None)
        editor_payload.pop("shell", None)
        editor_payload.pop(_EDITOR_COMPONENTS_KEY, None)
        editor_payload.pop("componentsManifest", None)
        editor_manifest_bytes = manifest_resp.content

    if editor_manifest_bytes is None:
        raise ScenarioBundleError(f"Missing editor-standalone manifest payload from {normalized}")

    shell_path = EDITOR_ASSET_BASE + shell_name if shell_name else EDITOR_SHELL_PATH
    components_path = (
        EDITOR_ASSET_BASE + components_hint if components_hint else EDITOR_ASSET_BASE + "components/manifest.json"
    )
    assets = _editor_assets(editor_payload)

    comp_resp = client.get(normalized + components_path, headers=req_headers, follow_redirects=False)
    comp_resp.raise_for_status()
    comp_json = comp_resp.json()
    if not isinstance(comp_json, dict) or not isinstance(comp_json.get("components"), dict):
        raise ScenarioBundleError(
            f"Instance at {normalized} does not expose a valid Interface Components manifest ({components_path})."
        )

    return editor_manifest_bytes, shell_path, comp_resp.content, assets


def _editor_dir_matches_manifests(
    editor_dir: Path,
    editor_manifest_bytes: bytes,
    comp_bytes: bytes,
    assets: list[tuple[str, str, str | None]],
    *,
    expected_shell_path: str | None = None,
) -> bool:
    """Return True when `editor_dir` already holds exact matching manifests and verified assets."""
    if not _has_usable_editor_bundle(editor_dir):
        return False
    try:
        if (editor_dir / "manifest.json").read_bytes() != editor_manifest_bytes:
            return False
        if (editor_dir / "components" / "manifest.json").read_bytes() != comp_bytes:
            return False
        shell_marker = editor_dir / ".shell-path"
        if expected_shell_path is not None and shell_marker.is_file():
            if shell_marker.read_text(encoding="utf-8").strip() != expected_shell_path:
                return False
        for rel_path, _url, expected_sha in assets:
            asset_file = editor_dir / rel_path
            if not asset_file.is_file():
                return False
            if expected_sha and hashlib.sha256(asset_file.read_bytes()).hexdigest() != expected_sha:
                return False
    except OSError:
        return False
    return True


def _replace_directory_atomic(staging_dir: Path, target_dir: Path) -> None:
    """Swap `staging_dir` into `target_dir` and delete any previous `target_dir` contents."""
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    old_dir: Path | None = None
    if target_dir.exists() or target_dir.is_symlink():
        old_dir = target_dir.with_name(f".{target_dir.name}.{secrets.token_hex(8)}.old")
        os.replace(target_dir, old_dir)
    try:
        os.replace(staging_dir, target_dir)
    except Exception:
        if old_dir is not None and old_dir.exists() and not target_dir.exists():
            try:
                os.replace(old_dir, target_dir)
            except OSError:
                pass
        raise
    finally:
        if old_dir is not None and old_dir.exists():
            shutil.rmtree(old_dir, ignore_errors=True)
        if staging_dir.exists():
            shutil.rmtree(staging_dir, ignore_errors=True)


def _fetch_editor_standalone_bundle(
    origin: str,
    target_dir: Path,
    *,
    headers: dict[str, str] | None = None,
    cached_snapshot_editor_dir: Path | None = None,
) -> Path:
    """Revalidate `target_dir` (or `cached_snapshot_editor_dir`) against `origin`, refreshing on deploy change."""
    normalized = _normalize_origin(origin)
    req_headers = headers or {}
    with httpx.Client(timeout=15.0) as client:
        editor_manifest_bytes, shell_path, comp_bytes, assets = _fetch_remote_editor_manifests(
            client, normalized, req_headers
        )

        if cached_snapshot_editor_dir is not None and _editor_dir_matches_manifests(
            cached_snapshot_editor_dir,
            editor_manifest_bytes,
            comp_bytes,
            assets,
        ):
            return cached_snapshot_editor_dir

        if _editor_dir_matches_manifests(
            target_dir,
            editor_manifest_bytes,
            comp_bytes,
            assets,
            expected_shell_path=shell_path,
        ):
            return target_dir

        staging_dir = target_dir.parent / f".{target_dir.name}.{secrets.token_hex(8)}.tmp"
        staging_dir.mkdir(parents=True, exist_ok=True)
        try:
            shell_resp = client.get(normalized + shell_path, headers=req_headers, follow_redirects=False)
            shell_resp.raise_for_status()

            _write_atomic(staging_dir / "manifest.json", editor_manifest_bytes)
            _write_atomic(staging_dir / "interface-shell.html", shell_resp.content)
            _write_atomic(staging_dir / "components" / "manifest.json", comp_bytes)
            _write_atomic(staging_dir / ".origin", normalized.encode("utf-8"))
            _write_atomic(staging_dir / ".shell-path", shell_path.encode("utf-8"))

            for rel_path, url, expected_sha in assets:
                asset_url = _allowlisted_asset_url(normalized, EDITOR_ASSET_BASE, url)
                asset_resp = client.get(asset_url, headers=req_headers, follow_redirects=False)
                asset_resp.raise_for_status()
                if expected_sha and hashlib.sha256(asset_resp.content).hexdigest() != expected_sha:
                    raise ScenarioBundleError(f"SHA-256 mismatch for editor asset {rel_path} from {normalized}")
                _write_atomic(staging_dir / rel_path, asset_resp.content)

            _replace_directory_atomic(staging_dir, target_dir)
        finally:
            if staging_dir.exists():
                shutil.rmtree(staging_dir, ignore_errors=True)
        return target_dir


def _find_any_cached_editor_bundle(
    cache_root: Path,
) -> tuple[Path, str | None, Callable[[], None]] | None:
    """Return the newest verified cached `editor-standalone` directory across origins in `cache_root`."""
    if not cache_root.is_dir():
        return None

    candidates: list[tuple[float, PreviewAssetCache, Path, str | None]] = []
    for origin_dir in cache_root.iterdir():
        if not origin_dir.is_dir():
            continue
        scope_dir = origin_dir / f"protocol-{PROTOCOL_VERSION}"
        current_file = scope_dir / CURRENT_FILE
        if current_file.is_file():
            try:
                snap_name = current_file.read_text(encoding="utf-8").strip()
            except OSError:
                snap_name = ""
            if SNAPSHOT_NAME_PATTERN.fullmatch(snap_name):
                snap_root = scope_dir / snap_name
                verification_file = snap_root / VERIFICATION_FILE
                editor_dir = snap_root / "editor-standalone"
                if verification_file.is_file() and _has_usable_editor_bundle(editor_dir):
                    try:
                        meta = json.loads(verification_file.read_text(encoding="utf-8"))
                        origin = meta.get("origin") if isinstance(meta, dict) else None
                        if isinstance(origin, str) and origin:
                            cache = PreviewAssetCache(origin, cache_root=cache_root)
                            verified = cache.current_snapshot()
                            if verified is not None and _has_usable_editor_bundle(verified.root / "editor-standalone"):
                                mtime = verified.root.stat().st_mtime
                                candidates.append((mtime, cache, verified.root, cache.origin))
                    except (OSError, ValueError, PreviewCacheError):
                        pass

        standalone_dir = origin_dir / _SCENARIO_BUNDLE_DIR_NAME
        if _has_usable_editor_bundle(standalone_dir):
            try:
                mtime = (standalone_dir / "manifest.json").stat().st_mtime
                origin_file = standalone_dir / ".origin"
                saved_origin = origin_file.read_text(encoding="utf-8").strip() if origin_file.is_file() else None
                candidates.append((mtime, None, standalone_dir, saved_origin or None))  # type: ignore[arg-type]
            except OSError:
                pass

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    _, best_cache, best_root, best_origin = candidates[0]
    if best_cache is not None:
        best_cache.acquire_lease(best_root)
        return best_root / "editor-standalone", best_origin, lambda: best_cache.release_lease(best_root)
    return best_root, best_origin, lambda: None


def resolve_scenario_editor_bundle(
    *,
    explicit_base_url: str | None,
    auth_headers: dict[str, str] | None = None,
    cache_root: Path | None = None,
    allow_cross_origin_cache_fallback: bool = True,
) -> tuple[Path, str | None, Callable[[], None]]:
    """Resolve an `editor-standalone` directory for `validate --scenario` on `InterfaceComponents` screens."""
    root = cache_root or _default_preview_cache_root()

    if explicit_base_url:
        try:
            cache = PreviewAssetCache(explicit_base_url, cache_root=root)
        except (PreviewCacheError, ValueError) as exc:
            raise ScenarioBundleError(str(exc)) from exc

        if auth_headers and auth_headers.get("Authorization"):
            try:
                with httpx.Client(timeout=15.0) as client:
                    snapshot = cache.resolve(client=client, headers=auth_headers)
                editor_dir = snapshot.root / "editor-standalone"
                if _has_usable_editor_bundle(editor_dir):
                    cache.acquire_lease(snapshot.root)
                    return editor_dir, cache.origin, lambda: cache.release_lease(snapshot.root)
            except (PreviewCacheError, InvalidPreviewManifestError, ProtocolMismatchError, httpx.HTTPError):
                pass

        cached = cache.current_snapshot()
        cached_editor = (
            cached.root / "editor-standalone"
            if cached is not None and _has_usable_editor_bundle(cached.root / "editor-standalone")
            else None
        )
        scenario_dir = root / cache.origin_key / _SCENARIO_BUNDLE_DIR_NAME

        try:
            resolved_dir = _fetch_editor_standalone_bundle(
                cache.origin,
                scenario_dir,
                headers=auth_headers,
                cached_snapshot_editor_dir=cached_editor,
            )
            if cached is not None and cached_editor is not None and resolved_dir == cached_editor:
                cache.acquire_lease(cached.root)
                return cached_editor, cache.origin, lambda: cache.release_lease(cached.root)
            return resolved_dir, cache.origin, lambda: None
        except (httpx.HTTPError, PreviewCacheError, ScenarioBundleError, ValueError) as exc:
            if isinstance(exc, httpx.HTTPError):
                if _has_usable_editor_bundle(scenario_dir):
                    return scenario_dir, cache.origin, lambda: None
                if cached is not None and cached_editor is not None:
                    cache.acquire_lease(cached.root)
                    return cached_editor, cache.origin, lambda: cache.release_lease(cached.root)
            if allow_cross_origin_cache_fallback:
                found = _find_any_cached_editor_bundle(root)
                if found is not None:
                    return found
            raise ScenarioBundleError(
                f"Failed to fetch editor-standalone bundle for window.InterfaceComponents from {cache.origin}: {exc}"
            ) from exc

    found = _find_any_cached_editor_bundle(root)
    if found is not None:
        return found

    raise ScenarioBundleError(
        "Screen references window.InterfaceComponents, which requires the Label Studio editor-standalone bundle "
        "to run browser scenarios. Set LABEL_STUDIO_URL (or pass --lse-url) so the CLI can fetch it, or run "
        "'label-studio-sdk interface preview' once to populate the local preview cache."
    )


def _manifest_declared_component_paths(editor_dir: Path) -> set[str]:
    """Return relative paths (`components/...`) explicitly declared in `components/manifest.json`."""
    manifest_file = editor_dir / "components" / "manifest.json"
    allowed: set[str] = set()
    try:
        data = json.loads(manifest_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return allowed
    components = data.get("components") if isinstance(data, dict) else None
    if not isinstance(components, dict):
        return allowed
    for entry in components.values():
        if not isinstance(entry, dict):
            continue
        for key in ("chunk", "css"):
            val = entry.get(key)
            if isinstance(val, str) and val.startswith("components/") and _is_safe_asset_relative(val):
                allowed.add(val)
        workers = entry.get("workers")
        if isinstance(workers, list):
            for worker in workers:
                if isinstance(worker, str) and worker.startswith("components/") and _is_safe_asset_relative(worker):
                    allowed.add(worker)
    return allowed


class ScenarioEditorBundleServer:
    """Loopback server hosting `editor-standalone` + on-demand component chunks for `scenario-runner.mjs`."""

    def __init__(self, *, editor_dir: Path, upstream_origin: str | None = None) -> None:
        self.editor_dir = editor_dir.resolve()
        self.upstream_origin = upstream_origin.rstrip("/") if upstream_origin else None
        self.capability = secrets.token_urlsafe(24)
        self._declared_component_paths = _manifest_declared_component_paths(self.editor_dir)
        self._client = httpx.Client(timeout=15.0) if self.upstream_origin else None
        self._server = _LoopbackHTTPServer(("127.0.0.1", 0), self._make_handler())
        self._thread: threading.Thread | None = None

    @property
    def bundle_base_url(self) -> str:
        port = int(self._server.server_address[1])
        return f"http://127.0.0.1:{port}/{self.capability}"

    def start(self) -> None:
        self._thread = threading.Thread(target=self._server.serve_forever, name="ls-scenario-bundle", daemon=True)
        self._thread.start()

    def close(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        if self._client is not None:
            self._client.close()

    def _can_fetch_component(self, relative: str) -> bool:
        if not self.upstream_origin or self._client is None or not relative.startswith("components/"):
            return False
        if relative in self._declared_component_paths:
            return True
        sub = relative.removeprefix("components/")
        return bool(_COMPONENT_FILE_RE.fullmatch(sub))

    def _fetch_component(self, relative: str) -> bool:
        if not self._can_fetch_component(relative):
            return False
        if self._client is None or self.upstream_origin is None:
            return False
        url = f"{self.upstream_origin}/react-app/editor-standalone/{relative}"
        body = bytearray()
        try:
            with self._client.stream("GET", url, follow_redirects=False) as response:
                if response.status_code != HTTPStatus.OK:
                    return False
                for chunk in response.iter_bytes():
                    body.extend(chunk)
                    if len(body) > _MAX_COMPONENT_FILE_BYTES:
                        return False
        except httpx.HTTPError:
            return False
        _write_atomic(self.editor_dir / relative, bytes(body))
        return True

    def _make_handler(self) -> type[BaseHTTPRequestHandler]:
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                parsed = urlsplit(self.path)
                prefix = f"/{owner.capability}/"
                if not parsed.path.startswith(prefix):
                    self.send_error(HTTPStatus.FORBIDDEN)
                    return
                relative = parsed.path[len(prefix) :]
                if not relative or not _is_safe_asset_relative(relative):
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                target = (owner.editor_dir / PurePosixPath(relative)).resolve()
                if not target.is_relative_to(owner.editor_dir):
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                if not target.is_file() and not owner._fetch_component(relative):
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                content = target.read_bytes()
                content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()
                self.wfile.write(content)

            def log_message(self, _format: str, *_args: Any) -> None:
                return

        return Handler


@contextmanager
def serve_scenario_editor_bundle(
    *,
    explicit_base_url: str | None,
    auth_headers: dict[str, str] | None = None,
    cache_root: Path | None = None,
    allow_cross_origin_cache_fallback: bool = True,
) -> Iterator[str]:
    """Resolve and serve `editor-standalone` over loopback, yielding its capability-scoped base URL."""
    editor_dir, upstream_origin, release = resolve_scenario_editor_bundle(
        explicit_base_url=explicit_base_url,
        auth_headers=auth_headers,
        cache_root=cache_root,
        allow_cross_origin_cache_fallback=allow_cross_origin_cache_fallback,
    )
    server = ScenarioEditorBundleServer(editor_dir=editor_dir, upstream_origin=upstream_origin)
    server.start()
    try:
        yield server.bundle_base_url
    finally:
        try:
            server.close()
        finally:
            release()
