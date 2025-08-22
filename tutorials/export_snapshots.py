"""This example demonstrates how to:

- Create an export snapshot
- Poll for export completion
- Download the resulting export file

- Convert the export to a specified format (optional if LABEL_STUDIO_EXPORT_TYPE is specified)
- Poll for conversion completion
- Download the resulting converted file

Environment variables used:
- LABEL_STUDIO_URL: Your LS URL (e.g. https://app.humansignal.com)
- LABEL_STUDIO_API_KEY: Personal access token (go to your account and generate it)
- LABEL_STUDIO_PROJECT_ID: Numeric project ID
- LABEL_STUDIO_EXPORT_TYPE: The type of export (CSV, COCO, JSON, etc.) to convert to (optional, default is JSON)

Usage:
```bash
LABEL_STUDIO_URL=https://app.humansignal.com LABEL_STUDIO_API_KEY=your_api_key \
LABEL_STUDIO_PROJECT_ID=123456 LABEL_STUDIO_EXPORT_TYPE=CSV \
python export_snapshots.py
```
"""

import os
import sys
import time
from pathlib import Path
import logging

from label_studio_sdk.client import LabelStudio
from label_studio_sdk.core.api_error import ApiError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("export_snapshots")


def export_and_download_snapshot():
    """Export project snapshot

    This example demonstrates how to:
    - Create an export snapshot
    - Poll for completion
    - Download the resulting file
    """
    base_url = os.getenv("LABEL_STUDIO_URL")
    api_key = os.getenv("LABEL_STUDIO_API_KEY")
    project_id_str = os.getenv("LABEL_STUDIO_PROJECT_ID")

    if not base_url or not api_key or not project_id_str:
        logger.error("set LABEL_STUDIO_URL, LABEL_STUDIO_API_KEY and LABEL_STUDIO_PROJECT_ID env vars")
        sys.exit(1)

    try:
        project_id = int(project_id_str)
    except ValueError:
        logger.error("LABEL_STUDIO_PROJECT_ID must be an integer")
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
    logger.info(f"Created export snapshot: id={export_id}, status={export_job.status}")

    # Poll until completed or failed
    start = time.time()
    timeout_sec = 300
    logger.info("Waiting for export snapshot to complete...")
    while True:
        job = ls.projects.exports.get(id=project_id, export_pk=export_id)
        elapsed = int(time.time() - start)
        logger.info(f"Export status: {job.status} (elapsed {elapsed}s)")
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

    logger.info(f"Export completed. File saved to: {out_path}")
    return export_id


def convert_snapshot(export_type: str, export_id: str = None):
    """Convert the latest project export snapshot to a specified format and download it.

    The conversion API is used to start a conversion on the Label Studio backend, then we poll export status
    until the specific converted format is completed, and finally download it.
    See docs: projects/exports/convert and projects/exports/list.

    Args:
        export_type: The type of export to convert to.
        export_id: The ID of the export to convert. If not provided, the latest export will be used.
    """
    base_url = os.getenv("LABEL_STUDIO_URL")
    api_key = os.getenv("LABEL_STUDIO_API_KEY")
    project_id_str = os.getenv("LABEL_STUDIO_PROJECT_ID")

    if not base_url or not api_key or not project_id_str:
        logger.error("set LABEL_STUDIO_URL, LABEL_STUDIO_API_KEY and LABEL_STUDIO_PROJECT_ID env vars")
        sys.exit(1)

    try:
        project_id = int(project_id_str)
    except ValueError:
        logger.error("LABEL_STUDIO_PROJECT_ID must be an integer")
        sys.exit(1)

    ls = LabelStudio(base_url=base_url, api_key=api_key)

    # Get the latest export snapshot for the project
    exports = ls.projects.exports.list(id=project_id)
    if not exports:
        raise ApiError(status_code=404, body="No export snapshots found for the project")
    exports = sorted(exports, key=lambda e: e.created_at, reverse=True)
    export = exports[0]
    export_id = export.id if not export_id else export_id

    # Start conversion
    conv = ls.projects.exports.convert(export_pk=export_id, id=project_id, export_type=export_type)
    converted_format_id = conv.converted_format
    logger.info(f"Started conversion: export_id={export_id}, export_type={export_type}, converted_format_id={converted_format_id}")

    # Poll converted format status
    start = time.time()
    timeout_sec = 300
    logger.info("Waiting for conversion to complete...")
    while True:
        cur = ls.projects.exports.get(id=project_id, export_pk=export_id)
        cf = None
        if cur.converted_formats:
            cf = next((c for c in cur.converted_formats if (converted_format_id and c.id == converted_format_id) or (c.export_type == export_type)), None)
        status = getattr(cf, "status", None)
        elapsed = int(time.time() - start)
        logger.info(f"Conversion status: {status or 'pending'} (format {export_type}, elapsed {elapsed}s)")
        if status in ("completed", "failed"):
            break
        if time.time() - start > timeout_sec:
            raise TimeoutError(f"Conversion timed out (export_id={export_id}, format={export_type}, status={status})")
        time.sleep(1.0)

    if status == "failed":
        raise ApiError(status_code=500, body=f"Conversion failed (export_id={export_id}, format={export_type})")

    # Download converted file using export_type param
    ext = "json" if export_type.upper().startswith("JSON") else export_type.lower()
    out_dir = Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"project_{project_id}_export_{export_id}.{ext}"

    with open(out_path, "wb") as f:
        for chunk in ls.projects.exports.download(id=project_id, export_pk=export_id, export_type=export_type, request_options={"chunk_size": 1024}):
            f.write(chunk)

    logger.info(f"Converted export downloaded. File saved to: {out_path}")


if __name__ == "__main__":
    
    export_id = export_and_download_snapshot()
    logger.info(f"Export ID: {export_id}")

    export_type = os.getenv("LABEL_STUDIO_EXPORT_TYPE", None)
    if export_type and export_type != "JSON":
        logger.info(f"Converting export to {export_type} format")
        convert_snapshot(export_type, export_id)
