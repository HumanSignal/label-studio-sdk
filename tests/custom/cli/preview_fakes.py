from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

from label_studio_sdk._extensions.interface.preview import PROTOCOL_VERSION

__all__ = ["FakePreviewCache", "FakePreviewServer", "preview_asset_root"]


def preview_asset_root(tmp_path: Path) -> Path:
    """Minimal on-disk layout accepted by LocalPreviewServer for integration tests."""
    root = tmp_path / "assets"
    (root / "local-playground").mkdir(parents=True, exist_ok=True)
    (root / "editor-standalone").mkdir(parents=True, exist_ok=True)
    (root / "local-playground/index.html").write_text("<html>local</html>", encoding="utf-8")
    (root / "editor-standalone/interface-shell.html").write_text("<html>sandbox</html>", encoding="utf-8")
    (root / "editor-standalone/main.js").write_text("editor", encoding="utf-8")
    return root


class FakePreviewCache:
    instances: list["FakePreviewCache"] = []
    error: Exception | None = None

    def __init__(self, origin: str) -> None:
        self.origin = origin
        self.calls: list[dict[str, Any]] = []
        FakePreviewCache.instances.append(self)

    def resolve(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return SimpleNamespace(
            root=Path("/verified/assets"),
            protocol_version=PROTOCOL_VERSION,
            source="cache" if kwargs.get("offline") else "network",
            warning=None,
        )

    def acquire_lease(self, root: Path) -> None:
        return None

    def release_lease(self, root: Path) -> None:
        return None


class FakePreviewServer:
    instances: list["FakePreviewServer"] = []

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self.url = "http://127.0.0.1:43210/capability/"
        self.updates: list[dict[str, Any]] = []
        FakePreviewServer.instances.append(self)

    def __enter__(self) -> "FakePreviewServer":
        return self

    def __exit__(self, *_args: Any) -> None:
        return None

    def publish_file_update(self, **kwargs: Any) -> int:
        self.updates.append(kwargs)
        return len(self.updates)
