from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import httpx
import pytest

from label_studio_sdk._extensions.interface.preview import (
    PROTOCOL_VERSION,
    PreviewAssetCache,
    PreviewCacheError,
    ProtocolMismatchError,
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _responses(
    origin: str, *, protocol: int = PROTOCOL_VERSION, app: bytes = b"console.log('preview')"
) -> dict[str, tuple[int, bytes]]:
    shell = b"<html>preview</html>"
    editor_js = b"editor"
    editor_css = b"body{}"
    editor_shell = b"<html>sandbox shell</html>"
    return {
        f"{origin}/api/current-user/whoami": (200, b'{"id":1}'),
        f"{origin}/react-app/local-playground/manifest.json": (
            200,
            json.dumps(
                {
                    "protocolVersion": protocol,
                    "files": {
                        "index.html": {"url": "index.html", "sha256": _sha(shell)},
                        "app.js": {"url": "app.js", "sha256": _sha(app)},
                    },
                }
            ).encode(),
        ),
        f"{origin}/react-app/local-playground/index.html": (200, shell),
        f"{origin}/react-app/local-playground/app.js": (200, app),
        f"{origin}/react-app/editor-standalone/manifest.json": (
            200,
            json.dumps({"main.js": "main-abc.js", "main.css": "main-abc.css"}).encode(),
        ),
        f"{origin}/react-app/editor-standalone/main-abc.js": (200, editor_js),
        f"{origin}/react-app/editor-standalone/main-abc.css": (200, editor_css),
        f"{origin}/react-app/editor-standalone/interface-shell.html": (200, editor_shell),
    }


def _client(responses: dict[str, tuple[int, bytes]], calls: list[httpx.Request]) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        status, content = responses.get(str(request.url), (404, b"missing"))
        return httpx.Response(status, content=content, request=request)

    return httpx.Client(transport=httpx.MockTransport(handler))


def _set_mtime(path: Path, mtime: float) -> None:
    os.utime(path, (mtime, mtime))


def test_cache_download_activates_atomic_verified_snapshot(tmp_path: Path) -> None:
    origin = "https://one.example"
    calls: list[httpx.Request] = []
    cache = PreviewAssetCache(origin, cache_root=tmp_path)

    with _client(_responses(origin), calls) as client:
        snapshot = cache.resolve(client=client, headers={"Authorization": "Token secret"})

    assert snapshot.verified
    assert snapshot.protocol_version == PROTOCOL_VERSION
    assert snapshot.root.name.startswith("snapshot-")
    assert (snapshot.root / "local-playground/index.html").read_bytes() == b"<html>preview</html>"
    assert (snapshot.root / "editor-standalone/main-abc.js").read_bytes() == b"editor"
    assert (snapshot.root / "editor-standalone/interface-shell.html").read_bytes() == b"<html>sandbox shell</html>"
    assert (cache.scope_dir / "CURRENT").read_text(encoding="utf-8").strip() == snapshot.root.name
    assert not list(cache.scope_dir.glob(".staging-*"))
    assert not list(cache.scope_dir.glob(".CURRENT-*"))
    assert all(request.headers["Authorization"] == "Token secret" for request in calls)
    diagnostics = cache.diagnostics()
    assert diagnostics.cache_path == cache.scope_dir
    assert diagnostics.origin_key == cache.scope_dir.parent.name
    assert diagnostics.fingerprint
    assert diagnostics.last_successful_fetch
    assert diagnostics.verified


def test_prior_snapshot_stays_immutable_after_newer_activation(tmp_path: Path) -> None:
    origin = "https://pin.example"
    cache = PreviewAssetCache(origin, cache_root=tmp_path)
    with _client(_responses(origin, app=b"first"), []) as client:
        first = cache.resolve(client=client, headers={"Authorization": "Token secret"})
    first_app = (first.root / "local-playground/app.js").read_bytes()

    with _client(_responses(origin, app=b"second"), []) as client:
        second = cache.resolve(client=client, headers={"Authorization": "Token secret"})

    assert first.root.exists()
    assert second.root != first.root
    assert (first.root / "local-playground/app.js").read_bytes() == first_app == b"first"
    assert (second.root / "local-playground/app.js").read_bytes() == b"second"
    assert (cache.scope_dir / "CURRENT").read_text(encoding="utf-8").strip() == second.root.name


def test_prune_retains_active_and_most_recent_prior(tmp_path: Path) -> None:
    origin = "https://prune.example"
    cache = PreviewAssetCache(origin, cache_root=tmp_path)
    with _client(_responses(origin, app=b"first"), []) as client:
        first = cache.resolve(client=client, headers={"Authorization": "Token secret"})
    with _client(_responses(origin, app=b"second"), []) as client:
        second = cache.resolve(client=client, headers={"Authorization": "Token secret"})
    # Explicit ordering: avoid depending on filesystem timestamp resolution.
    _set_mtime(first.root, 100.0)
    _set_mtime(second.root, 200.0)

    with _client(_responses(origin, app=b"third"), []) as client:
        third = cache.resolve(client=client, headers={"Authorization": "Token secret"})
    _set_mtime(third.root, 300.0)

    remaining = {path.name for path in cache.scope_dir.glob("snapshot-*") if path.is_dir()}
    assert remaining == {second.root.name, third.root.name}
    assert not first.root.exists()
    assert (cache.scope_dir / "CURRENT").read_text(encoding="utf-8").strip() == third.root.name


def test_prune_equal_mtimes_tie_breaks_by_snapshot_name(tmp_path: Path) -> None:
    cache = PreviewAssetCache("https://tie.example", cache_root=tmp_path)
    cache.scope_dir.mkdir(parents=True)
    names = ("snapshot-aaaa", "snapshot-bbbb", "snapshot-cccc")
    for name in names:
        (cache.scope_dir / name).mkdir()
        _set_mtime(cache.scope_dir / name, 1_700_000_000.0)
    keep = cache.scope_dir / "snapshot-bbbb"
    (cache.scope_dir / "CURRENT").write_text(keep.name, encoding="utf-8")

    cache._prune_old_snapshots(keep=keep, retain=2)

    remaining = sorted(path.name for path in cache.scope_dir.glob("snapshot-*") if path.is_dir())
    # Reverse sort by (mtime, name): cccc, bbbb, aaaa → retain active+most-recent-prior.
    assert remaining == ["snapshot-bbbb", "snapshot-cccc"]


def test_prune_never_removes_leased_or_active_snapshots(tmp_path: Path) -> None:
    cache = PreviewAssetCache("https://lease.example", cache_root=tmp_path)
    cache.scope_dir.mkdir(parents=True)
    oldest = cache.scope_dir / "snapshot-aaaa"
    middle = cache.scope_dir / "snapshot-bbbb"
    newest = cache.scope_dir / "snapshot-cccc"
    for path in (oldest, middle, newest):
        path.mkdir()
    (cache.scope_dir / "CURRENT").write_text(newest.name, encoding="utf-8")
    cache.acquire_lease(oldest)
    # Re-pin mtimes after lease write so directory mtime updates cannot reshuffle order.
    for index, path in enumerate((oldest, middle, newest), start=1):
        _set_mtime(path, float(index))

    cache._prune_old_snapshots(keep=newest, retain=2)

    remaining = {path.name for path in cache.scope_dir.glob("snapshot-*") if path.is_dir()}
    # Soft retain keeps newest+middle; hard protect keeps leased oldest as well.
    assert remaining == {oldest.name, middle.name, newest.name}


def test_unchanged_manifests_reuse_verified_assets_after_short_revalidation(tmp_path: Path) -> None:
    origin = "https://reuse.example"
    cache = PreviewAssetCache(origin, cache_root=tmp_path)
    with _client(_responses(origin), []) as client:
        first = cache.resolve(client=client, headers={"Authorization": "Token secret"})

    calls: list[httpx.Request] = []
    with _client(_responses(origin), calls) as client:
        second = cache.resolve(client=client, headers={"Authorization": "Token secret"})

    assert second.root == first.root
    assert [request.url.path for request in calls] == [
        "/api/current-user/whoami",
        "/react-app/local-playground/manifest.json",
        "/react-app/editor-standalone/manifest.json",
    ]


def test_offline_uses_verified_cache_without_network(tmp_path: Path) -> None:
    origin = "https://offline.example"
    cache = PreviewAssetCache(origin, cache_root=tmp_path)
    with _client(_responses(origin), []) as client:
        warm = cache.resolve(client=client, headers={"Authorization": "Token secret"})

    with _client({}, []) as client:
        offline = cache.resolve(client=client, headers={}, offline=True)

    assert offline.root == warm.root
    assert offline.source == "cache"


@pytest.mark.parametrize("status", [401, 503])
def test_auth_or_network_error_falls_back_only_to_verified_cache(tmp_path: Path, status: int) -> None:
    origin = "https://fallback.example"
    cache = PreviewAssetCache(origin, cache_root=tmp_path)
    with _client(_responses(origin), []) as client:
        warm = cache.resolve(client=client, headers={"Authorization": "Token secret"})

    calls: list[httpx.Request] = []
    failing = {f"{origin}/api/current-user/whoami": (status, b"failed")}
    with _client(failing, calls) as client:
        fallback = cache.resolve(client=client, headers={"Authorization": "Token bad"})

    assert fallback.root == warm.root
    assert fallback.warning
    assert [request.url.path for request in calls] == ["/api/current-user/whoami"]


def test_cache_miss_requires_token_and_origins_are_isolated(tmp_path: Path) -> None:
    one = PreviewAssetCache("https://one.example", cache_root=tmp_path)
    two = PreviewAssetCache("https://two.example", cache_root=tmp_path)
    assert one.scope_dir != two.scope_dir

    with _client({}, []) as client, pytest.raises(PreviewCacheError, match="token"):
        one.resolve(client=client, headers={})
    with _client({}, []) as client, pytest.raises(PreviewCacheError, match="verified"):
        one.resolve(client=client, headers={}, offline=True)


def test_cache_miss_rejects_bad_token_even_when_static_assets_are_public(tmp_path: Path) -> None:
    """Real LSE serves playground static files without auth; invalid tokens must still fail closed."""
    origin = "https://auth.example"
    cache = PreviewAssetCache(origin, cache_root=tmp_path)
    responses = _responses(origin)
    responses[f"{origin}/api/current-user/whoami"] = (401, b"bad token")
    calls: list[httpx.Request] = []
    with _client(responses, calls) as client, pytest.raises(PreviewCacheError, match="authentication failed"):
        cache.resolve(client=client, headers={"Authorization": "Token definitely-invalid-token"})

    assert cache.current_snapshot() is None
    assert not list(cache.scope_dir.glob("snapshot-*"))
    assert [request.url.path for request in calls] == ["/api/current-user/whoami"]


def test_manifest_asset_url_cannot_exfiltrate_token(tmp_path: Path) -> None:
    origin = "https://auth.example"
    cache = PreviewAssetCache(origin, cache_root=tmp_path)
    responses = _responses(origin)
    manifest = json.loads(responses[f"{origin}/react-app/local-playground/manifest.json"][1])
    manifest["files"]["app.js"]["url"] = "https://attacker.example/steal.js"
    responses[f"{origin}/react-app/local-playground/manifest.json"] = (200, json.dumps(manifest).encode())
    calls: list[httpx.Request] = []
    with _client(responses, calls) as client, pytest.raises(PreviewCacheError, match="outside"):
        cache.resolve(client=client, headers={"Authorization": "Token secret"})
    assert all(request.url.host != "attacker.example" for request in calls)
    assert cache.current_snapshot() is None
    assert not list(cache.scope_dir.glob(".staging-*"))


def test_encoded_path_traversal_in_manifest_asset_url_is_rejected(tmp_path: Path) -> None:
    origin = "https://auth.example"
    cache = PreviewAssetCache(origin, cache_root=tmp_path)
    responses = _responses(origin)
    manifest = json.loads(responses[f"{origin}/react-app/local-playground/manifest.json"][1])
    # Encoded `..` still prefixes the raw path with the allowlisted base until decoded.
    manifest["files"]["app.js"]["url"] = "%2e%2e/%2e%2e/steal.js"
    responses[f"{origin}/react-app/local-playground/manifest.json"] = (200, json.dumps(manifest).encode())
    calls: list[httpx.Request] = []
    with _client(responses, calls) as client, pytest.raises(PreviewCacheError, match="outside"):
        cache.resolve(client=client, headers={"Authorization": "Token secret"})
    assert not any(request.url.path.endswith("steal.js") for request in calls)


def test_bad_hash_never_activates_and_cleans_staging(tmp_path: Path) -> None:
    origin = "https://hash.example"
    responses = _responses(origin)
    manifest = json.loads(responses[f"{origin}/react-app/local-playground/manifest.json"][1])
    manifest["files"]["app.js"]["sha256"] = "0" * 64
    responses[f"{origin}/react-app/local-playground/manifest.json"] = (200, json.dumps(manifest).encode())
    cache = PreviewAssetCache(origin, cache_root=tmp_path)

    with _client(responses, []) as client, pytest.raises(PreviewCacheError, match="sha256"):
        cache.resolve(client=client, headers={"Authorization": "Token secret"})

    assert cache.current_snapshot() is None
    assert not (cache.scope_dir / "CURRENT").exists()
    assert not list(cache.scope_dir.glob(".staging-*"))
    assert not list(cache.scope_dir.glob(".CURRENT-*"))
    assert not list(cache.scope_dir.glob("snapshot-*"))


def test_missing_playground_hash_never_activates(tmp_path: Path) -> None:
    origin = "https://hash.example"
    responses = _responses(origin)
    manifest = json.loads(responses[f"{origin}/react-app/local-playground/manifest.json"][1])
    del manifest["files"]["app.js"]["sha256"]
    responses[f"{origin}/react-app/local-playground/manifest.json"] = (200, json.dumps(manifest).encode())
    cache = PreviewAssetCache(origin, cache_root=tmp_path)

    with _client(responses, []) as client, pytest.raises(PreviewCacheError, match="missing sha256"):
        cache.resolve(client=client, headers={"Authorization": "Token secret"})

    assert cache.current_snapshot() is None
    assert not list(cache.scope_dir.glob(".staging-*"))


def test_duplicate_destination_paths_never_activate(tmp_path: Path) -> None:
    origin = "https://dup.example"
    cache = PreviewAssetCache(origin, cache_root=tmp_path)
    shell = b"<html>preview</html>"
    app = b"app"
    other = b"other"
    responses = _responses(origin, app=app)
    responses[f"{origin}/react-app/local-playground/manifest.json"] = (
        200,
        json.dumps(
            {
                "protocolVersion": PROTOCOL_VERSION,
                "files": {
                    "index.html": {"url": "index.html", "sha256": _sha(shell)},
                    "app.js": {"path": "shared.js", "url": "app.js", "sha256": _sha(app)},
                    "other.js": {"path": "shared.js", "url": "other.js", "sha256": _sha(other)},
                },
            }
        ).encode(),
    )
    responses[f"{origin}/react-app/local-playground/other.js"] = (200, other)

    with _client(responses, []) as client, pytest.raises(PreviewCacheError, match="duplicate preview asset path"):
        cache.resolve(client=client, headers={"Authorization": "Token secret"})

    assert cache.current_snapshot() is None
    assert not list(cache.scope_dir.glob(".staging-*"))
    assert not list(cache.scope_dir.glob("snapshot-*"))


@pytest.mark.parametrize(
    ("checksums", "entrypoint"),
    [
        ({}, "local-playground/index.html"),
        ({"../outside.html": _sha(b"preview")}, "../outside.html"),
        ({"/tmp/outside.html": _sha(b"preview")}, "/tmp/outside.html"),
        ({"local-playground/index.html": _sha(b"preview")}, "local-playground/not-checked.html"),
    ],
)
def test_current_snapshot_rejects_unsafe_or_incomplete_verification_metadata(
    tmp_path: Path, checksums: dict[str, str], entrypoint: str
) -> None:
    cache = PreviewAssetCache("https://verify.example", cache_root=tmp_path)
    root = cache.scope_dir / "snapshot-deadbeef"
    (root / "local-playground").mkdir(parents=True)
    (root / "local-playground/index.html").write_bytes(b"preview")
    (root / ".verified.json").write_text(
        json.dumps(
            {
                "origin": cache.origin,
                "protocolVersion": PROTOCOL_VERSION,
                "entrypoint": entrypoint,
                "checksums": checksums,
            }
        ),
        encoding="utf-8",
    )
    (cache.scope_dir / "CURRENT").write_text(root.name, encoding="utf-8")

    assert cache.current_snapshot() is None


def test_current_snapshot_rejects_symlink_verified_files(tmp_path: Path) -> None:
    cache = PreviewAssetCache("https://symlink.example", cache_root=tmp_path)
    # Name must match snapshot-[0-9a-f]+ so current_snapshot reaches _verify_snapshot.
    root = cache.scope_dir / "snapshot-aaa111e1"
    target_dir = root / "local-playground"
    target_dir.mkdir(parents=True)
    real_file = target_dir / "real.html"
    linked = target_dir / "index.html"
    real_file.write_bytes(b"preview")
    linked.symlink_to(real_file)
    (root / ".verified.json").write_text(
        json.dumps(
            {
                "origin": cache.origin,
                "protocolVersion": PROTOCOL_VERSION,
                "entrypoint": "local-playground/index.html",
                "checksums": {"local-playground/index.html": _sha(b"preview")},
            }
        ),
        encoding="utf-8",
    )
    (cache.scope_dir / "CURRENT").write_text(root.name, encoding="utf-8")

    assert cache.current_snapshot() is None


def test_current_snapshot_rejects_symlinked_parent_directory(tmp_path: Path) -> None:
    cache = PreviewAssetCache("https://symlink-parent.example", cache_root=tmp_path)
    outside = tmp_path / "outside-assets"
    outside.mkdir()
    (outside / "index.html").write_bytes(b"preview")
    root = cache.scope_dir / "snapshot-bbb222e2"
    root.mkdir(parents=True)
    (root / "local-playground").symlink_to(outside)
    (root / ".verified.json").write_text(
        json.dumps(
            {
                "origin": cache.origin,
                "protocolVersion": PROTOCOL_VERSION,
                "entrypoint": "local-playground/index.html",
                "checksums": {"local-playground/index.html": _sha(b"preview")},
            }
        ),
        encoding="utf-8",
    )
    (cache.scope_dir / "CURRENT").write_text(root.name, encoding="utf-8")

    assert cache.current_snapshot() is None


def test_current_snapshot_rejects_symlink_snapshot_root(tmp_path: Path) -> None:
    cache = PreviewAssetCache("https://symlink-root.example", cache_root=tmp_path)
    real = cache.scope_dir / "real-snapshot-dir"
    (real / "local-playground").mkdir(parents=True)
    (real / "local-playground/index.html").write_bytes(b"preview")
    (real / ".verified.json").write_text(
        json.dumps(
            {
                "origin": cache.origin,
                "protocolVersion": PROTOCOL_VERSION,
                "entrypoint": "local-playground/index.html",
                "checksums": {"local-playground/index.html": _sha(b"preview")},
            }
        ),
        encoding="utf-8",
    )
    linked = cache.scope_dir / "snapshot-ccc333e3"
    linked.symlink_to(real)
    (cache.scope_dir / "CURRENT").write_text(linked.name, encoding="utf-8")

    assert cache.current_snapshot() is None


def test_write_asset_rejects_symlink_parent_escape(tmp_path: Path) -> None:
    from label_studio_sdk._extensions.interface.preview.cache import _write_asset

    staging = tmp_path / "staging"
    staging.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (staging / "local-playground").symlink_to(outside)

    with pytest.raises(PreviewCacheError, match="unsafe preview asset path"):
        _write_asset(staging, "local-playground/evil.js", b"exfiltrated")

    assert not (outside / "evil.js").exists()
    assert list(outside.iterdir()) == []


def test_current_snapshot_rejects_symlinked_verification_metadata(tmp_path: Path) -> None:
    cache = PreviewAssetCache("https://symlink-meta.example", cache_root=tmp_path)
    root = cache.scope_dir / "snapshot-ddd444e4"
    (root / "local-playground").mkdir(parents=True)
    (root / "local-playground/index.html").write_bytes(b"preview")
    outside = tmp_path / "leaked-verified.json"
    outside.write_text(
        json.dumps(
            {
                "origin": cache.origin,
                "protocolVersion": PROTOCOL_VERSION,
                "entrypoint": "local-playground/index.html",
                "checksums": {"local-playground/index.html": _sha(b"preview")},
            }
        ),
        encoding="utf-8",
    )
    (root / ".verified.json").symlink_to(outside)
    (cache.scope_dir / "CURRENT").write_text(root.name, encoding="utf-8")

    assert cache.current_snapshot() is None
    assert cache._snapshot_metadata(root) is None


def test_write_asset_rejects_symlinked_verification_metadata_leaf(tmp_path: Path) -> None:
    from label_studio_sdk._extensions.interface.preview.cache import VERIFICATION_FILE, _write_asset

    staging = tmp_path / "staging"
    staging.mkdir()
    outside = tmp_path / "outside-verified.json"
    outside.write_text("{}", encoding="utf-8")
    (staging / VERIFICATION_FILE).symlink_to(outside)

    with pytest.raises(PreviewCacheError, match="duplicate preview asset path"):
        _write_asset(staging, VERIFICATION_FILE, b'{"ok":true}')

    assert outside.read_text(encoding="utf-8") == "{}"


def test_current_snapshot_rejects_parent_directory_pointer(tmp_path: Path) -> None:
    cache = PreviewAssetCache("https://verify.example", cache_root=tmp_path)
    cache.scope_dir.mkdir(parents=True)
    (cache.scope_dir / "CURRENT").write_text("..", encoding="utf-8")

    assert cache.current_snapshot() is None


def test_corrupt_current_snapshot_is_refetched_instead_of_served(tmp_path: Path) -> None:
    origin = "https://corrupt.example"
    cache = PreviewAssetCache(origin, cache_root=tmp_path)
    with _client(_responses(origin), []) as client:
        first = cache.resolve(client=client, headers={"Authorization": "Token secret"})

    (first.root / "local-playground/app.js").write_bytes(b"corrupt")
    assert cache.current_snapshot() is None

    calls: list[httpx.Request] = []
    with _client(_responses(origin), calls) as client:
        repaired = cache.resolve(client=client, headers={"Authorization": "Token secret"})

    assert repaired.root != first.root
    assert repaired.verified
    assert [request.url.path for request in calls][:3] == [
        "/api/current-user/whoami",
        "/react-app/local-playground/manifest.json",
        "/react-app/editor-standalone/manifest.json",
    ]


def test_protocol_mismatch_is_reported(tmp_path: Path) -> None:
    origin = "https://protocol.example"
    cache = PreviewAssetCache(origin, cache_root=tmp_path)
    with _client(_responses(origin), []) as client:
        cache.resolve(client=client, headers={"Authorization": "Token secret"})

    with _client(_responses(origin, protocol=PROTOCOL_VERSION + 1), []) as client:
        with pytest.raises(ProtocolMismatchError):
            cache.resolve(client=client, headers={"Authorization": "Token secret"})
