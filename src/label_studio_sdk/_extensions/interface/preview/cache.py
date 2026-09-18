from __future__ import annotations

import errno
import hashlib
import json
import os
import re
import shutil
import stat
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit

import appdirs
import httpx
from .protocol import PROTOCOL_VERSION, InvalidPreviewManifestError, PreviewManifest, ProtocolMismatchError

LOCAL_MANIFEST_PATH = "/react-app/local-playground/manifest.json"
LOCAL_ASSET_BASE = "/react-app/local-playground/"
EDITOR_MANIFEST_PATH = "/react-app/editor-standalone/manifest.json"
EDITOR_ASSET_BASE = "/react-app/editor-standalone/"
EDITOR_SHELL_PATH = "/react-app/editor-standalone/interface-shell.html"
VERIFICATION_FILE = ".verified.json"
CURRENT_FILE = "CURRENT"
LAST_FETCH_FILE = "LAST_FETCH"
LEASE_FILE = ".preview-lease"
SNAPSHOT_NAME_PATTERN = re.compile(r"snapshot-[0-9a-f]+")


class PreviewCacheError(RuntimeError):
    """A verified local preview bundle could not be selected."""


@dataclass(frozen=True)
class PreviewCacheSnapshot:
    root: Path
    protocol_version: int
    source: str
    warning: str | None = None

    @property
    def verified(self) -> bool:
        path = self.root / VERIFICATION_FILE
        return not path.is_symlink() and path.is_file()


@dataclass(frozen=True)
class PreviewCacheDiagnostics:
    cache_path: Path
    origin_key: str
    fingerprint: str | None
    protocol_version: int
    last_successful_fetch: str | None
    verified: bool


class PreviewAssetCache:
    """Origin- and protocol-scoped, immutable cache for local preview assets."""

    def __init__(
        self,
        origin: str,
        *,
        protocol_version: int = PROTOCOL_VERSION,
        cache_root: Path | None = None,
    ) -> None:
        self.origin = _normalize_origin(origin)
        self.protocol_version = protocol_version
        root = cache_root or Path(appdirs.user_cache_dir("label-studio-sdk", "HumanSignal")) / "interface-preview"
        self.origin_key = hashlib.sha256(self.origin.encode()).hexdigest()[:20]
        self.scope_dir = Path(root) / self.origin_key / f"protocol-{protocol_version}"

    def current_snapshot(self) -> PreviewCacheSnapshot | None:
        try:
            name = (self.scope_dir / CURRENT_FILE).read_text(encoding="utf-8").strip()
        except OSError:
            return None
        if SNAPSHOT_NAME_PATTERN.fullmatch(name) is None:
            return None
        root = self.scope_dir / name
        if not self._verify_snapshot(root):
            return None
        return PreviewCacheSnapshot(root=root, protocol_version=self.protocol_version, source="cache")

    def diagnostics(self) -> PreviewCacheDiagnostics:
        snapshot = self.current_snapshot()
        metadata = self._snapshot_metadata(snapshot.root) if snapshot is not None else None
        try:
            last_fetch = (self.scope_dir / LAST_FETCH_FILE).read_text(encoding="utf-8").strip() or None
        except OSError:
            last_fetch = None
        return PreviewCacheDiagnostics(
            cache_path=self.scope_dir,
            origin_key=self.origin_key,
            fingerprint=metadata.get("manifestFingerprint") if metadata is not None else None,
            protocol_version=self.protocol_version,
            last_successful_fetch=last_fetch,
            verified=snapshot is not None,
        )

    def resolve(
        self,
        *,
        client: httpx.Client,
        headers: dict[str, str],
        offline: bool = False,
    ) -> PreviewCacheSnapshot:
        cached = self.current_snapshot()
        if offline:
            if cached is None:
                raise PreviewCacheError("offline preview requires a verified cache")
            return cached
        if not headers.get("Authorization"):
            if cached is not None:
                return PreviewCacheSnapshot(
                    root=cached.root,
                    protocol_version=cached.protocol_version,
                    source="cache",
                    warning="authentication token missing; using verified preview cache",
                )
            raise PreviewCacheError("an API token is required to populate the preview cache")

        try:
            return self._download_and_activate(client=client, headers=headers)
        except ProtocolMismatchError:
            raise
        except (httpx.HTTPError, PreviewCacheError, InvalidPreviewManifestError) as exc:
            if cached is not None:
                return PreviewCacheSnapshot(
                    root=cached.root,
                    protocol_version=cached.protocol_version,
                    source="cache",
                    warning=f"preview asset refresh failed ({exc}); using verified cache",
                )
            if (
                isinstance(exc, httpx.HTTPStatusError)
                and exc.response is not None
                and exc.response.status_code in {401, 403}
            ):
                raise PreviewCacheError("authentication failed; cannot populate the preview cache") from exc
            if isinstance(exc, (PreviewCacheError, InvalidPreviewManifestError)):
                raise
            raise PreviewCacheError(f"failed to download preview assets and no verified cache exists: {exc}") from exc

    def _verify_api_auth(self, *, client: httpx.Client, headers: dict[str, str]) -> None:
        """Fail closed on invalid tokens before treating public static downloads as success."""
        response = client.get(self.origin + "/api/current-user/whoami", headers=headers, follow_redirects=False)
        response.raise_for_status()

    def _download_and_activate(
        self,
        *,
        client: httpx.Client,
        headers: dict[str, str],
    ) -> PreviewCacheSnapshot:
        self._verify_api_auth(client=client, headers=headers)
        local_response = client.get(self.origin + LOCAL_MANIFEST_PATH, headers=headers, follow_redirects=False)
        local_response.raise_for_status()
        local_payload = local_response.json()
        manifest = PreviewManifest.parse(local_payload)

        editor_response = client.get(self.origin + EDITOR_MANIFEST_PATH, headers=headers, follow_redirects=False)
        editor_response.raise_for_status()
        editor_manifest = editor_response.json()
        editor_assets = _editor_assets(editor_manifest)
        manifest_fingerprint = _manifest_fingerprint(local_payload, editor_manifest)
        cached = self.current_snapshot()
        if cached is not None:
            metadata = self._snapshot_metadata(cached.root)
            if metadata is not None and metadata.get("manifestFingerprint") == manifest_fingerprint:
                self._record_successful_fetch()
                return PreviewCacheSnapshot(
                    root=cached.root,
                    protocol_version=cached.protocol_version,
                    source="cache",
                )

        self.scope_dir.mkdir(parents=True, exist_ok=True)
        staging = self.scope_dir / f".staging-{uuid.uuid4().hex}"
        staging.mkdir()
        checksums: dict[str, str] = {}
        pointer_tmp: Path | None = None
        snapshot_root: Path | None = None
        activated = False
        try:
            for asset in manifest.assets:
                target_name = f"local-playground/{asset.path}"
                if asset.sha256 is None:
                    raise PreviewCacheError(f"missing sha256 for playground asset {asset.path}")
                asset_url = _allowlisted_asset_url(self.origin, LOCAL_ASSET_BASE, asset.url)
                content = self._fetch_asset(client, asset_url, headers)
                digest = hashlib.sha256(content).hexdigest()
                if digest != asset.sha256:
                    raise PreviewCacheError(
                        f"sha256 mismatch for {asset.path}: expected {asset.sha256}, downloaded {digest}"
                    )
                _write_asset(staging, target_name, content)
                checksums[target_name] = digest

            editor_manifest_bytes = editor_response.content
            _write_asset(staging, "editor-standalone/manifest.json", editor_manifest_bytes)
            checksums["editor-standalone/manifest.json"] = hashlib.sha256(editor_manifest_bytes).hexdigest()
            shell = self._fetch_asset(client, self.origin + EDITOR_SHELL_PATH, headers)
            _write_asset(staging, "editor-standalone/interface-shell.html", shell)
            checksums["editor-standalone/interface-shell.html"] = hashlib.sha256(shell).hexdigest()
            for path, url, expected_hash in editor_assets:
                target_name = f"editor-standalone/{path}"
                asset_url = _allowlisted_asset_url(self.origin, EDITOR_ASSET_BASE, url)
                content = self._fetch_asset(client, asset_url, headers)
                if not content:
                    raise PreviewCacheError(f"empty editor asset {path}")
                digest = hashlib.sha256(content).hexdigest()
                if expected_hash and digest != expected_hash:
                    raise PreviewCacheError(f"sha256 mismatch for editor asset {path}")
                _write_asset(staging, target_name, content)
                checksums[target_name] = digest

            verification = {
                "origin": self.origin,
                "protocolVersion": manifest.protocol_version,
                "manifestFingerprint": manifest_fingerprint,
                "entrypoint": f"local-playground/{manifest.entrypoint}",
                "checksums": checksums,
            }
            _write_asset(
                staging,
                VERIFICATION_FILE,
                json.dumps(verification, sort_keys=True, separators=(",", ":")).encode("utf-8"),
            )
            snapshot_name = f"snapshot-{uuid.uuid4().hex}"
            snapshot_root = self.scope_dir / snapshot_name
            os.replace(staging, snapshot_root)
            pointer_tmp = self.scope_dir / f".{CURRENT_FILE}-{uuid.uuid4().hex}"
            pointer_tmp.write_text(snapshot_name, encoding="utf-8")
            os.replace(pointer_tmp, self.scope_dir / CURRENT_FILE)
            pointer_tmp = None
            activated = True
            self._prune_old_snapshots(keep=snapshot_root)
            self._record_successful_fetch()
            return PreviewCacheSnapshot(
                root=snapshot_root,
                protocol_version=manifest.protocol_version,
                source="network",
            )
        except Exception:
            if pointer_tmp is not None:
                try:
                    pointer_tmp.unlink()
                except OSError:
                    pass
            if not activated:
                if snapshot_root is not None and snapshot_root.exists():
                    shutil.rmtree(snapshot_root, ignore_errors=True)
                else:
                    shutil.rmtree(staging, ignore_errors=True)
            raise

    @staticmethod
    def _fetch_asset(client: httpx.Client, url: str, headers: dict[str, str]) -> bytes:
        response = client.get(url, headers=headers, follow_redirects=False)
        response.raise_for_status()
        return response.content

    def _verify_snapshot(self, root: Path) -> bool:
        try:
            # Snapshot roots must be real directories — never symlinks or plain files.
            if root.is_symlink() or not root.is_dir():
                return False
            resolved_root = root.resolve()
            verification = self._snapshot_metadata(root)
            if verification is None:
                return False
            checksums = verification.get("checksums")
            entrypoint = verification.get("entrypoint")
            if (
                verification.get("origin") != self.origin
                or verification.get("protocolVersion") != self.protocol_version
                or not isinstance(checksums, dict)
                or not checksums
                or not isinstance(entrypoint, str)
                or entrypoint not in checksums
            ):
                return False
            for relative, expected in checksums.items():
                if not _is_safe_relative_path(relative) or not isinstance(expected, str):
                    return False
                if not _path_has_only_real_components(root, relative):
                    return False
                path = root / relative
                if not _is_resolved_under(resolved_root, path):
                    return False
                # Hash via O_NOFOLLOW fd open so a leaf cannot race into a symlink.
                if _sha256_regular_file(path) != expected:
                    return False
            return True
        except (OSError, ValueError, TypeError, KeyError):
            return False

    def _record_successful_fetch(self) -> None:
        self.scope_dir.mkdir(parents=True, exist_ok=True)
        target = self.scope_dir / LAST_FETCH_FILE
        temporary = self.scope_dir / f".{LAST_FETCH_FILE}-{uuid.uuid4().hex}"
        temporary.write_text(datetime.now(timezone.utc).isoformat(), encoding="utf-8")
        os.replace(temporary, target)

    def _prune_old_snapshots(self, *, keep: Path, retain: int = 2) -> None:
        """Keep active + most-recent-prior; never prune active/CURRENT or leased snapshots.

        Equal mtimes tie-break on snapshot directory name so retention is deterministic.
        Leased/active protection is hard and may retain more than ``retain``.
        """
        snapshots = sorted(
            (path for path in self.scope_dir.glob("snapshot-*") if path.is_dir()),
            key=lambda path: (path.stat().st_mtime_ns, path.name),
            reverse=True,
        )
        protected: set[Path] = {keep.resolve()}
        try:
            current_name = (self.scope_dir / CURRENT_FILE).read_text(encoding="utf-8").strip()
        except OSError:
            current_name = ""
        if SNAPSHOT_NAME_PATTERN.fullmatch(current_name):
            current = self.scope_dir / current_name
            if current.is_dir():
                protected.add(current.resolve())
        for path in snapshots:
            if _has_active_lease(path):
                protected.add(path.resolve())
        recent = {path.resolve() for path in snapshots[: max(retain, 0)]}
        retained = protected | recent
        for path in snapshots:
            if path.resolve() not in retained:
                shutil.rmtree(path, ignore_errors=True)

    def acquire_lease(self, root: Path) -> None:
        """Mark a snapshot as in use so prune will not delete it under another preview process."""
        root = Path(root)
        if not root.is_dir():
            return
        lease = root / LEASE_FILE
        lease.write_text(f"{os.getpid()}\n", encoding="utf-8")

    def release_lease(self, root: Path) -> None:
        lease = Path(root) / LEASE_FILE
        try:
            lease.unlink()
        except OSError:
            pass

    @staticmethod
    def _snapshot_metadata(root: Path) -> dict[str, Any] | None:
        try:
            if root.is_symlink() or not root.is_dir():
                return None
            path = root / VERIFICATION_FILE
            # Never follow a symlinked .verified.json — open with O_NOFOLLOW.
            raw = _read_regular_file(path)
            value = json.loads(raw.decode("utf-8"))
        except (OSError, ValueError, TypeError, UnicodeDecodeError):
            return None
        return value if isinstance(value, dict) else None


def _normalize_origin(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"invalid Label Studio origin: {value!r}")
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), "", "", ""))


def _fully_unquote_path(path: str) -> str:
    decoded = path
    while True:
        next_decoded = unquote(decoded)
        if next_decoded == decoded:
            return decoded
        decoded = next_decoded


def _is_safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        return False
    path = PurePosixPath(value)
    # PurePosixPath normalizes harmless `a/./b` away; reject `..` and absolute forms only.
    return not path.is_absolute() and ".." not in path.parts and path != PurePosixPath(".")


def _is_resolved_under(root: Path, candidate: Path) -> bool:
    """True when ``candidate`` resolves to a path at or under ``root`` (both resolved)."""
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False


def _path_has_only_real_components(root: Path, relative: str) -> bool:
    """Reject any symlink among intermediate directories or the final path component."""
    cursor = root
    for part in PurePosixPath(relative).parts:
        cursor = cursor / part
        if cursor.is_symlink():
            return False
    return True


def _open_regular_file(path: Path, flags: int) -> int:
    """Open a path without following a final-component symlink (O_NOFOLLOW on Linux)."""
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    open_flags = flags
    if nofollow:
        open_flags |= nofollow
    elif path.is_symlink():
        raise OSError(errno.ELOOP, "symbolic link not allowed", os.fspath(path))
    fd = os.open(os.fspath(path), open_flags)
    try:
        # Non-Linux fallback: re-check after open; residual TOCTOU is accepted off-target.
        if not nofollow and path.is_symlink():
            raise OSError(errno.ELOOP, "symbolic link not allowed", os.fspath(path))
        mode = os.fstat(fd).st_mode
        if not stat.S_ISREG(mode):
            raise OSError(errno.EINVAL, "not a regular file", os.fspath(path))
    except Exception:
        os.close(fd)
        raise
    return fd


def _read_regular_file(path: Path) -> bytes:
    """Read a regular file without following a final-component symlink."""
    fd = _open_regular_file(path, os.O_RDONLY)
    try:
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


def _sha256_regular_file(path: Path) -> str:
    """Hash a regular file without following a final-component symlink (O_NOFOLLOW on Linux)."""
    fd = _open_regular_file(path, os.O_RDONLY)
    try:
        hasher = hashlib.sha256()
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
        return hasher.hexdigest()
    finally:
        os.close(fd)


def _has_active_lease(path: Path) -> bool:
    return (path / LEASE_FILE).is_file()


def _allowlisted_asset_url(origin: str, base_path: str, value: str) -> str:
    url = urljoin(origin + base_path, value)
    parsed = urlsplit(url)
    expected = urlsplit(origin)
    if (parsed.scheme, parsed.netloc) != (expected.scheme, expected.netloc):
        raise PreviewCacheError(f"preview manifest asset URL is outside {base_path}: {value!r}")
    decoded_path = _fully_unquote_path(parsed.path)
    if ".." in PurePosixPath(decoded_path).parts or not decoded_path.startswith(base_path):
        raise PreviewCacheError(f"preview manifest asset URL is outside {base_path}: {value!r}")
    return urlunsplit((parsed.scheme, parsed.netloc, decoded_path, parsed.query, parsed.fragment))


def _manifest_fingerprint(local_payload: Any, editor_payload: Any) -> str:
    canonical = json.dumps(
        {"local": local_payload, "editor": editor_payload},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(canonical).hexdigest()


def _editor_assets(payload: Any) -> list[tuple[str, str, str | None]]:
    if not isinstance(payload, dict):
        raise PreviewCacheError("editor-standalone manifest must be a JSON object")
    assets: list[tuple[str, str, str | None]] = []
    for logical_name, value in payload.items():
        if isinstance(value, str):
            path, url, digest = value, value, None
        elif isinstance(value, dict):
            url = value.get("url", value.get("file"))
            path = value.get("path", url)
            digest = value.get("sha256")
            if "sha256" in value and (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(character not in "0123456789abcdefABCDEF" for character in digest)
            ):
                raise PreviewCacheError(f"invalid sha256 for editor asset {path!r}")
            digest = digest.lower() if digest is not None else None
        else:
            raise PreviewCacheError(f"invalid editor asset mapping for {logical_name!r}")
        if not isinstance(path, str) or not isinstance(url, str):
            raise PreviewCacheError(f"invalid editor asset mapping for {logical_name!r}")
        pure_path = PurePosixPath(path)
        if pure_path.is_absolute() or ".." in pure_path.parts:
            raise PreviewCacheError(f"unsafe editor asset path: {path!r}")
        assets.append((path, url, digest))
    if not assets:
        raise PreviewCacheError("editor-standalone manifest contains no assets")
    return assets


def _write_asset(root: Path, relative: str, content: bytes) -> None:
    if not _is_safe_relative_path(relative):
        raise PreviewCacheError(f"unsafe preview asset path: {relative!r}")
    if root.is_symlink() or not root.is_dir():
        raise PreviewCacheError(f"unsafe preview asset root: {root!r}")

    resolved_root = root.resolve()
    parts = PurePosixPath(relative).parts
    cursor = root
    # Create missing parents one level at a time; fail closed on any symlink parent.
    for part in parts[:-1]:
        cursor = cursor / part
        if cursor.exists() or cursor.is_symlink():
            if cursor.is_symlink() or not cursor.is_dir():
                raise PreviewCacheError(f"unsafe preview asset path: {relative!r}")
        else:
            try:
                cursor.mkdir(mode=0o755)
            except FileExistsError as exc:
                if cursor.is_symlink() or not cursor.is_dir():
                    raise PreviewCacheError(f"unsafe preview asset path: {relative!r}") from exc

    target = root / relative
    if target.exists() or target.is_symlink():
        raise PreviewCacheError(f"duplicate preview asset path: {relative!r}")

    parent = target.parent
    try:
        resolved_target = parent.resolve() / target.name
        resolved_target.relative_to(resolved_root)
    except (ValueError, OSError) as exc:
        raise PreviewCacheError(f"unsafe preview asset path: {relative!r}") from exc

    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    if nofollow:
        flags |= nofollow
    fd = os.open(os.fspath(target), flags, 0o644)
    try:
        view = memoryview(content)
        while view:
            written = os.write(fd, view)
            view = view[written:]
    finally:
        os.close(fd)
