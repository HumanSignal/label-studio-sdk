"""
Export a snapshot with tasks filtered by the first available view using SDK 2.0+

- Uses post-1.0 client: from label_studio_sdk.client import LabelStudio
- Mirrors getting-started: ls = LabelStudio(base_url=..., api_key=...)
- Community Edition supports synchronous export via ls.projects.exports.download_sync
  but we use the higher-level helper ls.projects.exports.as_json which handles
  Enterprise vs Community differences automatically.
"""

import os
from pathlib import Path

from label_studio_sdk.client import LabelStudio

LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", default="http://localhost:8080")
API_KEY = os.getenv("LABEL_STUDIO_API_KEY")
PROJECT_ID = int(os.getenv("LABEL_STUDIO_PROJECT_ID", "1"))


def main() -> None:
    ls = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=API_KEY)

    # Ensure project exists and try to use the first view as a filter (if any)
    _ = ls.projects.get(id=PROJECT_ID)
    views = ls.views.list(project=PROJECT_ID)
    task_filter_options = {"view": views[0].id} if views else None

    # Create export snapshot and download JSON
    out_dir = Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)

    # If a view exists, pass it via create_kwargs. Otherwise export all annotated tasks.
    create_kwargs = {
        "title": "Export SDK Snapshot",
        "task_filter_options": task_filter_options,
    }
    # Remove None to avoid sending it
    create_kwargs = {k: v for k, v in create_kwargs.items() if v is not None}

    data = ls.projects.exports.as_json(
        PROJECT_ID,
        create_kwargs=create_kwargs,
        download_kwargs={"export_type": "JSON"},
    )

    out_path = out_dir / f"project_{PROJECT_ID}_export.json"
    with open(out_path, "w", encoding="utf-8") as f:
        import json

        json.dump(data, f)
    print(f"Export completed. File saved to: {out_path}")


if __name__ == "__main__":
    main()
