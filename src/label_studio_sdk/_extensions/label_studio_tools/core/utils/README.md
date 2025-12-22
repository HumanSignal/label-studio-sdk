# Label Studio Tools Core Utils

## Overview
Utilities used by Label Studio converters. `io.py` resolves task media references to **local file paths**, downloading and caching when needed. This is critical for `*_WITH_IMAGES` exports—failed downloads lead to empty `images/` folders.

Also, these tools are used in Label Studio ML backend. 

---

## Diagram 1: Where URLs Come From

```mermaid
flowchart TD
  subgraph sources [MediaSources]
    uiUpload[UI Upload] --> fileUpload[FileUploadModel]
    importLocal[Import Local Storage] --> localFiles["/data/local-files?d=..."]
    importHttp[Import HTTP URL] --> httpUrl["http(s)://..."]
    importCloud[Import Project Cloud Storage] --> cloudUri["s3|gs|azure-blob://..."]
    importProtected[Import Protected HTTP] --> fileProxy["/api/projects/pk/file-proxy?url=b64"]
  end

  subgraph taskData [Task Data Representations]
    fileUpload --> uploadKey["upload/project/file"]
    uploadKey --> snapshotJson[Export Snapshot JSON]
    uploadKey --> dataManagerApi[Data Manager API]

    dataManagerApi --> resolveUri[Task.resolve_uri]
    resolveUri --> cloudDefault[CLOUD_FILE_STORAGE_ENABLED = true]
    cloudDefault --> storageProxy["/storage-data/uploaded?filepath=upload/project/file"]
    resolveUri --> fsDefault[CLOUD_FILE_STORAGE_ENABLED = false]
    fsDefault --> dataUpload["/data/upload/project/file"]

    cloudUri --> presignApi["/tasks/taskId/presign?fileuri=cloudUri"]
    cloudUri --> storagesProxy["/api/storages/task-storage-data-presign?fileuri=b64"]
  end
```

---

## Diagram 2: Downloader Flow (`get_local_path`)
```mermaid
flowchart TD
  converter[ConverterWithImages] --> getLocalPath[get_local_path]

  getLocalPath -->|file exists| localHit[Use local file]
  getLocalPath -->|need download| normalize[Normalize URL]

  normalize --> uploadProxy["upload/data-upload => storage-data proxy"]
  normalize --> localStorage["/data/local-files?d=..."]
  normalize --> cloudStorage["s3|gs|azure-blob => presign"]
  normalize --> directHttp["http(s) direct"]
  normalize --> proxyHttp["LS proxy endpoints (/api/storages..., file-proxy)"]

  uploadProxy --> download[download_and_cache]
  localStorage --> download
  cloudStorage --> download
  directHttp --> download
  proxyHttp --> download

  download --> cached[Cached file path]
  cached --> exportZip[Images included in export zip]
```

---

## Diagram 3: URL Shapes & Normalization
```mermaid
flowchart LR
  uploadKey["upload/<project>/<file>"] --> proxyUrl["/storage-data/uploaded/?filepath=upload/..."]
  proxyUrl -->|HTTP fail + FileSystemStorage| dataUpload["/data/upload/<project>/<file> (fallback)"]
  dataUpload --> download[Download]

  localFiles["/data/local-files?d=..."] --> localRead["Read LOCAL_FILES_DOCUMENT_ROOT or download"]
  cloudUri["s3|gs|azure-blob://..."] --> presign["/tasks/<id>/presign?fileuri=..."] --> download
  httpUrl["http(s)://..."] --> download
  fileProxy["/api/projects/pk/file-proxy?url=b64"] --> download
  storagesProxy["/api/storages/.../task-storage-data-..."] --> download
```

---

## Key Points
- **Upload key is always stored as** `upload/<project>/<file>` (snapshots keep this).
- **Local FileSystemStorage (default)**:
  - Downloader tries `/storage-data/uploaded/?filepath=upload/...`; on HTTP failure (e.g., nginx + FileSystemStorage), it falls back to `/data/upload/<project>/<file>`.
- **Cloud default storage (S3/GCS/Azure/minio)**:
  - Downloads via `/storage-data/uploaded/?filepath=upload/<project>/<file>` with auth; `/data/upload/...` is not expected to exist.
- **Project storage**:
  - Local Storage: `/data/local-files?d=...` (read locally or download from host).
  - Project cloud storage: `s3://…`, `gs://…`, `azure-blob://…` → `/tasks/<task_id>/presign/?fileuri=...`.
- **Direct URLs**: `http(s)://...` (auth only if host matches `hostname`).
- **Auth**: `Token <token>` for legacy API tokens; `Bearer <token>` for JWT access tokens (when host matches `hostname`).

## Usage
```python
from label_studio_sdk._extensions.label_studio_tools.core.utils.io import get_local_path

local_path = get_local_path(
    url=item["input"]["image"],
    hostname="https://my-ls.example.com",
    access_token=os.environ["LABEL_STUDIO_API_KEY"],
    cache_dir="/tmp/export/images",
    download_resources=True,
    task_id=item["id"],
)
```

## Environment Variables
- `LABEL_STUDIO_URL` / `LABEL_STUDIO_HOST`
- `LABEL_STUDIO_API_KEY` / `LABEL_STUDIO_ACCESS_TOKEN`
- `LOCAL_FILES_DOCUMENT_ROOT`
- `VERIFY_SSL`

## API Reference
- `get_local_path(...)`: resolve & download to local path.
- `download_and_cache(...)`: low-level download/cache helper.
- `get_base64_content(...)`: download and return base64.

## Development Notes
- Tests in `tests/custom/label_studio_tools/` cover URL normalization, auth, and upload→proxy→fallback.
- Converter regressions in `tests/custom/converter/` for image-inclusive formats.

## Other Points
- Snapshots may contain raw upload keys; downloader must handle both raw uploads and proxy URLs.
- Some LS proxy endpoints embed filenames in query params—extend filename inference as needed (pattern: `/storage-data/uploaded/?filepath=...`).
