"""Export project snapshot (v2 SDK)

This example demonstrates how to:
- Create an export snapshot
- Poll for completion
- Download the resulting file

Environment variables used:
- LABEL_STUDIO_URL: Your LS URL (e.g. https://app.humansignal.com)
- LABEL_STUDIO_API_KEY: Personal access token
- LABEL_STUDIO_PROJECT_ID: Numeric project ID
"""

import os
import sys
import time
from pathlib import Path

from label_studio_sdk.client import LabelStudio
from label_studio_sdk.core.api_error import ApiError


def main():
    base_url = os.getenv("LABEL_STUDIO_URL")
    api_key = os.getenv("LABEL_STUDIO_API_KEY")
    project_id_str = os.getenv("LABEL_STUDIO_PROJECT_ID")

    if not base_url or not api_key or not project_id_str:
        print("ERROR: set LABEL_STUDIO_URL, LABEL_STUDIO_API_KEY and LABEL_STUDIO_PROJECT_ID env vars")
        sys.exit(1)

    try:
        project_id = int(project_id_str)
    except ValueError:
        print("ERROR: LABEL_STUDIO_PROJECT_ID must be an integer")
        sys.exit(1)

    # Initialize v2 client
    ls = LabelStudio(base_url=base_url, api_key=api_key)

    # Fetch project and optional first view id
    project = ls.projects.get(id=project_id)
    views = ls.views.list(project=project_id)
    task_filter_options = {"view": views[0].id} if views else None

    # Create export snapshot
    create_kwargs = {
        "title": "Export SDK Snapshot",
        # task_filter_options follows API schema; pass only if a view is available
        # "task_filter_options": {"view": task_filter_options["view"]} if task_filter_options else None,
    }
    # Remove None keys to avoid sending them
    create_kwargs = {k: v for k, v in create_kwargs.items() if v is not None}

    export_job = ls.projects.exports.create(id=project_id, **create_kwargs)
    export_id = export_job.id
    print(f"Created export snapshot: id={export_id}, status={export_job.status}")

    # Poll until completed or failed
    start = time.time()
    timeout_sec = 300
    while True:
        job = ls.projects.exports.get(id=project_id, export_pk=export_id)
        if job.status in ("completed", "failed"):
            break
        if time.time() - start > timeout_sec:
            raise TimeoutError(f"Export job timed out (id={export_id}, status={job.status})")
        time.sleep(1.0)

    if job.status == "failed":
        raise ApiError(status_code=500, body=f"Export failed: {job}")

    # Download export as JSON to local file
    out_dir = Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"project_{project_id}_export_{export_id}.json"

    with open(out_path, "wb") as f:
        for chunk in ls.projects.exports.download(id=project_id, export_pk=export_id, export_type="JSON", request_options={"chunk_size": 1024}):
            f.write(chunk)

    print(f"Export completed. File saved to: {out_path}")


if __name__ == "__main__":
    main()
