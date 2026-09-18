from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, TypedDict

PROTOCOL_VERSION = 1


class ProtocolMismatchError(ValueError):
    """The downloaded playground cannot speak this SDK's local protocol."""


class InvalidPreviewManifestError(ValueError):
    """The local-playground manifest is malformed or unsafe."""


class PreviewFileUpdate(TypedDict):
    code: str
    task: dict[str, Any] | None
    interfaceId: int | None
    lseUrl: str


@dataclass(frozen=True)
class PreviewAsset:
    path: str
    url: str
    sha256: str | None = None


@dataclass(frozen=True)
class PreviewManifest:
    protocol_version: int
    assets: tuple[PreviewAsset, ...]
    entrypoint: str = "index.html"

    @classmethod
    def parse(cls, payload: Any) -> PreviewManifest:
        if not isinstance(payload, dict):
            raise InvalidPreviewManifestError("preview manifest must be a JSON object")
        version = payload.get("protocolVersion", payload.get("protocol_version"))
        # bool is a subclass of int (`True == 1`); reject non-int and bool explicitly.
        if not isinstance(version, int) or isinstance(version, bool) or version != PROTOCOL_VERSION:
            raise ProtocolMismatchError(
                f"preview protocol mismatch: server={version!r}, SDK={PROTOCOL_VERSION}; update one side before preview"
            )
        raw_files = payload.get("files", payload.get("assets"))
        if not isinstance(raw_files, (dict, list)):
            raise InvalidPreviewManifestError("preview manifest must contain mapped files")

        assets: list[PreviewAsset] = []
        entries = raw_files.items() if isinstance(raw_files, dict) else enumerate(raw_files)
        for key, value in entries:
            if isinstance(value, str):
                path = str(key)
                url = value
                digest = None
            elif isinstance(value, dict):
                path = str(value.get("path", key))
                url = value.get("url", value.get("file", value.get("src", path)))
                digest = value.get("sha256")
            else:
                raise InvalidPreviewManifestError(f"invalid asset mapping for {key!r}")
            if not isinstance(url, str) or not url:
                raise InvalidPreviewManifestError(f"asset {path!r} has no URL")
            _validate_relative_path(path)
            if digest is not None and (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(c not in "0123456789abcdefABCDEF" for c in digest)
            ):
                raise InvalidPreviewManifestError(f"asset {path!r} has an invalid sha256")
            assets.append(PreviewAsset(path=path, url=url, sha256=digest.lower() if digest else None))

        entrypoint = payload.get("entrypoint", "index.html")
        if not isinstance(entrypoint, str):
            raise InvalidPreviewManifestError("preview entrypoint must be a string")
        _validate_relative_path(entrypoint)
        if entrypoint not in {asset.path for asset in assets}:
            raise InvalidPreviewManifestError(f"preview entrypoint {entrypoint!r} is not mapped")
        return cls(protocol_version=version, assets=tuple(assets), entrypoint=entrypoint)


def _validate_relative_path(value: str) -> None:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "." == value:
        raise InvalidPreviewManifestError(f"unsafe preview asset path: {value!r}")
