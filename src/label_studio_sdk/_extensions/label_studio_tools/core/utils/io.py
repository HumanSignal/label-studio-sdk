import hashlib
import io
import logging
import os
import shutil
import base64
from contextlib import contextmanager
from tempfile import mkdtemp
from urllib.parse import parse_qs, urlparse
import jwt

import requests
from appdirs import user_cache_dir, user_data_dir

from label_studio_sdk._extensions.label_studio_tools.core.utils.params import get_env

_DIR_APP_NAME = "label-studio"
LOCAL_FILES_DOCUMENT_ROOT = get_env(
    "LOCAL_FILES_DOCUMENT_ROOT", default=os.path.abspath(os.sep)
)
VERIFY_SSL = get_env("VERIFY_SSL", default=True, is_bool=True)

logger = logging.getLogger(__name__)


def concat_urls(base_url, url):
    return base_url.rstrip("/") + "/" + url.lstrip("/")


def get_data_dir():
    data_dir = user_data_dir(appname=_DIR_APP_NAME)
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_cache_dir():
    cache_dir = user_cache_dir(appname=_DIR_APP_NAME)
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def safe_build_path(base_dir: str, user_path: str) -> str:
    combined_path = os.path.join(base_dir, user_path)
    absolute_path = os.path.abspath(combined_path)
    base_dir_abs = os.path.abspath(base_dir)

    if os.path.commonpath([absolute_path, base_dir_abs]) != base_dir_abs:
        raise ValueError(f"Invalid path: {user_path}")

    return absolute_path


def is_jwt_well_formed(token: str) -> bool:
    try:
        jwt.get_unverified_header(token)
        return True
    except Exception:
        return False


def _build_headers(target_url, hostname, access_token):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
    }
    if access_token and hostname:
        if urlparse(target_url).netloc == urlparse(hostname).netloc:
            if is_jwt_well_formed(access_token):
                headers["Authorization"] = "Bearer " + access_token
            else:
                headers["Authorization"] = "Token " + access_token
    return headers


def get_local_path(
    url,
    cache_dir=None,
    project_dir=None,
    hostname=None,
    image_dir=None,
    access_token=None,
    download_resources=True,
    task_id=None,
):
    f"""This helper function is used to download (cache) url and return local path to it.

    All possible URL types:
      **Persistent Django storage (FileUpload)**
      - Stored key is always: upload/<project-id>/<filename> (regardless of backend)
      - Local FileSystemStorage:
        - If USE_NGINX_FOR_UPLOADS=False: downloader first tries /storage-data/uploaded/?filepath=upload/…; 
            if that 401/404s, it falls back to /data/upload/<project-id>/<filename>.
        - If USE_NGINX_FOR_UPLOADS=True: /storage-data/uploaded/ will 400 for FileSystemStorage; 
            fallback to /data/upload/<project-id>/<filename> is used.
      - Cloud storage (S3/GCS/Azure/minio):
        - Download via /storage-data/uploaded/?filepath=upload/<project-id>/<filename> (auth required, hostname rewrite). 
            /data/upload is not expected to exist in this mode.

      **Project storage**
      - Local Storage: /data/local-files?d=dir/1.jpg
        → Reads from LOCAL_FILES_DOCUMENT_ROOT if present; otherwise downloads from https://<hostname>/data/local-files?d=…
      - Project cloud storage: s3://… gs://… azure-blob://…
        → https://<hostname>/tasks/<task_id>/presign/?fileuri=<cloud-uri> then download

      **Direct http(s) URLs**
      - http(s)://example.com/1.jpg (downloaded directly; auth only if host matches hostname)

    :param url: File URL to download, it can be a uploaded file, local storage, cloud storage file or just http(s) url
    :param cache_dir: Cache directory to download or copy files
    :param project_dir: Project directory
    :param hostname: Label Studio Hostname, it will be used for uploaded files, local storage files and cloud storage files
      if not provided, it will be taken from LABEL_STUDIO_URL env variable
    :param image_dir: Image and other media upload directory
    :param access_token: Label Studio access token, it will be used for uploaded files, local storage files and cloud storage files
      if not provided, it will be taken from LABEL_STUDIO_API_KEY env variable
    :param download_resources: Download and cache a file from URL
    :param task_id: Label Studio Task ID, required for cloud storage files 
      because the URL will be rebuilt to `{hostname}/tasks/{task_id}/presign/?fileuri={url}` 

    :return: filepath
    """
    logger.debug("get_local_path() called with the following arguments:\n"
          f"  url: {url}\n"
          f"  cache_dir: {cache_dir}\n"
          f"  project_dir: {project_dir}\n"
          f"  hostname: {hostname}\n"
          f"  image_dir: {image_dir}\n"
          f"  access_token: {access_token}\n"
          f"  download_resources: {download_resources}\n"
          f"  task_id: {task_id}")
    
    # get environment variables
    hostname = (
        hostname
        or os.getenv("LABEL_STUDIO_URL", "")
        or os.getenv("LABEL_STUDIO_HOST", "")
    )
    access_token = (
        access_token
        or os.getenv("LABEL_STUDIO_API_KEY", "")
        or os.getenv("LABEL_STUDIO_ACCESS_TOKEN", "")
    )
    if "localhost" in hostname:
        logger.warning(
            f"Using `localhost` ({hostname}) in LABEL_STUDIO_URL, "
            f"`localhost` is not accessible inside of docker containers. "
            f"You can check your IP with utilities like `ifconfig` and set it as LABEL_STUDIO_URL."
        )
    if hostname and not (
        hostname.startswith("http://") or hostname.startswith("https://")
    ):
        raise ValueError(
            f"Invalid hostname in LABEL_STUDIO_URL: {hostname}. "
            "Please provide full URL starting with protocol (http:// or https://)."
        )

    # fix file upload url
    if url.startswith("upload") or url.startswith("/upload"):
        url = "/data" + ("" if url.startswith("/") else "/") + url

    is_uploaded_file = url.startswith("/data/upload")
    is_local_storage_file = url.startswith("/data/") and "?d=" in url
    is_cloud_storage_file = (
        url.startswith("s3:") or url.startswith("gs:") or url.startswith("azure-blob:")
    )
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    storage_filepath = query_params.get("filepath", [None])[0]
    is_storage_data_file = parsed_url.path.startswith("/storage-data/uploaded") or parsed_url.path.startswith(
        "storage-data/uploaded"
    )

    # Local storage file: try to load locally otherwise download below
    # this code allow to read Local Storage files directly from a directory
    # instead of downloading them from LS instance
    if is_local_storage_file:
        filepath = url.split("?d=")[1]
        filepath = safe_build_path(LOCAL_FILES_DOCUMENT_ROOT, filepath)
        shutil.copy(filepath, cache_dir, follow_symlinks=True)
        if os.path.exists(filepath):
            logger.debug(
                f"Local Storage file path exists locally, use it as a local file: {filepath}"
            )
            return filepath

    # try to get local directories
    if image_dir is None:
        upload_dir = os.path.join(get_data_dir(), "media", "upload")
        image_dir = project_dir and os.path.join(project_dir, "upload") or upload_dir
        logger.debug(
            f"Image and upload dirs: image_dir={image_dir}, upload_dir={upload_dir}"
        )

    # Uploaded file: try to load locally otherwise download below
    # this code allow to read Uploaded files directly from a directory
    # instead of downloading them from LS instance
    if is_uploaded_file and os.path.exists(image_dir):
        project_id = url.split("/")[-2]  # To retrieve project_id
        filepath = os.path.join(image_dir, project_id, os.path.basename(url))
        if os.path.exists(filepath):
            if cache_dir and download_resources:
                shutil.copy(filepath, cache_dir)
            logger.debug(f"Uploaded file: Path exists in image_dir: {filepath}")
            return filepath

    # Export snapshots can contain raw upload keys (upload/<project>/<file>), while the
    # web app/API may expose them via the authenticated storage proxy endpoint
    # /storage-data/uploaded/?filepath=upload/<project>/<file>.
    #
    # When the default Django storage is cloud-backed (S3/GCS/Azure via django-storages),
    # fetching such files via /data/upload/... can fail (files aren't on local disk).
    # Rewriting to the storage proxy keeps downloads working across both local and cloud
    # default storage backends.
    # 
    # FileSystemStorage can be downloaded both using 
    # /storage-data/uploaded/?filepath=upload/<project-id>/filename or /data/upload/<project-id>/filename
    # but USE_NGINX_FOR_UPLOADS should be OFF for FileSystemStorage since it doesn't support `storage_url=True` mode. 
    fallback_upload_url = None
    if is_uploaded_file and not is_storage_data_file:
        upload_path = url.lstrip("/")
        if upload_path.startswith("data/"):
            upload_path = upload_path[len("data/") :]
        storage_filepath = storage_filepath or upload_path
        url = f"/storage-data/uploaded/?filepath={storage_filepath}"
        parsed_url = urlparse(url)
        is_storage_data_file = True
        is_uploaded_file = False            
        if hostname:
            legacy_path = "/data/" + upload_path if not upload_path.startswith("data/") else "/" + upload_path
            fallback_upload_url = concat_urls(hostname, legacy_path)

    # Upload, Local Storage, Storage Proxy or Cloud Storage file
    if is_uploaded_file or is_local_storage_file or is_cloud_storage_file or is_storage_data_file:
        # hostname check
        if not hostname:
            raise FileNotFoundError(
                f"Can't resolve url, neither hostname or project_dir passed: {url}. "
                "You can set LABEL_STUDIO_URL environment variable to use it as a hostname."
            )
        # uploaded and local storage file
        elif is_uploaded_file or is_local_storage_file:
            url = concat_urls(hostname, url)
            logger.info("Resolving url using hostname [" + hostname + "]: " + url)
        # s3, gs, azure-blob file
        elif is_cloud_storage_file:
            if task_id is None:
                raise Exception(
                    "Label Studio Task ID is required for cloud storage files"
                )
            url = concat_urls(hostname, f"/tasks/{task_id}/presign/?fileuri={url}")
            logger.info(
                "Cloud storage file: Resolving url using hostname ["
                + hostname
                + "]: "
                + url
            )
        elif is_storage_data_file:
            resolved_path = parsed_url.path or "/storage-data/uploaded/"
            url = concat_urls(hostname, resolved_path)
            if parsed_url.query:
                url = url + "?" + parsed_url.query
            logger.info(
                "Storage proxy file: Resolving url using hostname ["
                + hostname
                + "]: "
                + url
            )

        # check access token
        if not access_token:
            raise FileNotFoundError(
                "To access uploaded and local storage files you have to "
                "set LABEL_STUDIO_API_KEY environment variable."
            )

    filepath = download_and_cache(
        url,
        cache_dir,
        download_resources,
        hostname,
        access_token,
        is_local_storage_file,
        is_cloud_storage_file,
        is_storage_data_file,
        storage_filepath,
        fallback_upload_url,
    )
    return filepath


def download_and_cache(
    url,
    cache_dir,
    download_resources,
    hostname,
    access_token,
    is_local_storage_file,
    is_cloud_storage_file,
    is_storage_data_file,
    storage_filepath,
    fallback_upload_url=None,
):
    def _filename_for(target_url, storage_fp=None):
        parsed = urlparse(target_url)
        if is_local_storage_file:
            return os.path.basename(target_url.split("?d=")[1])
        if is_cloud_storage_file:
            return os.path.basename(target_url)
        if is_storage_data_file:
            sfp = storage_fp or parse_qs(parsed.query).get("filepath", [None])[0]
            name = os.path.basename(sfp or "")
            return name or os.path.basename(parsed.path)
        return os.path.basename(parsed.path)

    def _cache_path(target_url, fname):
        return os.path.join(cache_dir, hashlib.md5(target_url.encode()).hexdigest()[:8] + "__" + fname)

    cache_dir = cache_dir or get_cache_dir()
    current_filename = _filename_for(url, storage_filepath)
    current_filepath = _cache_path(url, current_filename)

    if os.path.exists(current_filepath):
        return current_filepath

    if not download_resources:
        return current_filepath

    headers = _build_headers(url, hostname, access_token)
    try:
        r = requests.get(url, stream=True, headers=headers, verify=VERIFY_SSL)
        r.raise_for_status()
        target_url = url
        target_filepath = current_filepath
    except requests.exceptions.SSLError as e:
        logger.error(
            f"SSL error during requests.get('{url}'): {e}\n"
            f"Try to set VERIFY_SSL=False in environment variables to bypass SSL verification."
        )
        raise e
    except requests.exceptions.HTTPError as e:
        if not fallback_upload_url:
            raise e
        logger.info("Download failed for proxy URL, retrying legacy upload path: %s", fallback_upload_url)
        fb_filename = os.path.basename(urlparse(fallback_upload_url).path)
        fb_filepath = _cache_path(fallback_upload_url, fb_filename)
        if os.path.exists(fb_filepath):
            return fb_filepath
        fb_headers = _build_headers(fallback_upload_url, hostname, access_token)
        try:
            r = requests.get(fallback_upload_url, stream=True, headers=fb_headers, verify=VERIFY_SSL)
            r.raise_for_status()
            target_url = fallback_upload_url
            target_filepath = fb_filepath
        except Exception:
            raise e
    with io.open(target_filepath, mode="wb") as fout:
        fout.write(r.content)
        logger.info(f"File downloaded to {target_filepath}")
    return target_filepath


@contextmanager
def get_temp_dir():
    dirpath = mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)


def get_all_files_from_dir(d):
    out = []
    for name in os.listdir(d):
        filepath = os.path.join(d, name)
        if os.path.isfile(filepath):
            out.append(filepath)
    return out


def get_base64_content(
    url,
    hostname=None,
    access_token=None,
    task_id=None,
):
    """This helper function is used to download a file and return its base64 representation without saving to filesystem.

    :param url: File URL to download, it can be a uploaded file, local storage, cloud storage file or just http(s) url
    :param hostname: Label Studio Hostname, it will be used for uploaded files, local storage files and cloud storage files
      if not provided, it will be taken from LABEL_STUDIO_URL env variable
    :param access_token: Label Studio access token, it will be used for uploaded files, local storage files and cloud storage files
      if not provided, it will be taken from LABEL_STUDIO_API_KEY env variable
    :param task_id: Label Studio Task ID, required for cloud storage files
      because the URL will be rebuilt to `{hostname}/tasks/{task_id}/presign/?fileuri={url}`

    :return: base64 encoded file content
    """
    # get environment variables
    hostname = (
        hostname
        or os.getenv("LABEL_STUDIO_URL", "")
        or os.getenv("LABEL_STUDIO_HOST", "")
    )
    access_token = (
        access_token
        or os.getenv("LABEL_STUDIO_API_KEY", "")
        or os.getenv("LABEL_STUDIO_ACCESS_TOKEN", "")
    )
    if "localhost" in hostname:
        logger.warning(
            f"Using `localhost` ({hostname}) in LABEL_STUDIO_URL, "
            f"`localhost` is not accessible inside of docker containers. "
            f"You can check your IP with utilities like `ifconfig` and set it as LABEL_STUDIO_URL."
        )
    if hostname and not (
        hostname.startswith("http://") or hostname.startswith("https://")
    ):
        raise ValueError(
            f"Invalid hostname in LABEL_STUDIO_URL: {hostname}. "
            "Please provide full URL starting with protocol (http:// or https://)."
        )

    # fix file upload url
    if url.startswith("upload") or url.startswith("/upload"):
        url = "/data" + ("" if url.startswith("/") else "/") + url

    is_uploaded_file = url.startswith("/data/upload")
    is_local_storage_file = url.startswith("/data/") and "?d=" in url
    is_cloud_storage_file = (
        url.startswith("s3:") or url.startswith("gs:") or url.startswith("azure-blob:")
    )
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    storage_filepath = query_params.get("filepath", [None])[0]
    is_storage_data_file = parsed_url.path.startswith("/storage-data/uploaded") or parsed_url.path.startswith(
        "storage-data/uploaded"
    )

    # Local storage file: try to load locally
    if is_local_storage_file:
        filepath = url.split("?d=")[1]
        filepath = safe_build_path(LOCAL_FILES_DOCUMENT_ROOT, filepath)
        if os.path.exists(filepath):
            logger.debug(
                f"Local Storage file path exists locally, read content directly: {filepath}"
            )
            with open(filepath, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")

    # Upload, Local Storage, Storage Proxy or Cloud Storage file
    if is_uploaded_file or is_local_storage_file or is_cloud_storage_file or is_storage_data_file:
        # hostname check
        if not hostname:
            raise FileNotFoundError(
                f"Can't resolve url, hostname not provided: {url}. "
                "You can set LABEL_STUDIO_URL environment variable to use it as a hostname."
            )
        # uploaded and local storage file
        elif is_uploaded_file or is_local_storage_file:
            url = concat_urls(hostname, url)
            logger.info("Resolving url using hostname [" + hostname + "]: " + url)
        # s3, gs, azure-blob file
        elif is_cloud_storage_file:
            if task_id is None:
                raise Exception(
                    "Label Studio Task ID is required for cloud storage files"
                )
            url = concat_urls(hostname, f"/tasks/{task_id}/presign/?fileuri={url}")
            logger.info(
                "Cloud storage file: Resolving url using hostname ["
                + hostname
                + "]: "
                + url
            )
        elif is_storage_data_file:
            resolved_path = parsed_url.path or "/storage-data/uploaded/"
            url = concat_urls(hostname, resolved_path)
            if parsed_url.query:
                url = url + "?" + parsed_url.query
            logger.info(
                "Storage proxy file: Resolving url using hostname ["
                + hostname
                + "]: "
                + url
            )

        # check access token
        if not access_token:
            raise FileNotFoundError(
                "To access uploaded and local storage files you have to "
                "set LABEL_STUDIO_API_KEY environment variable."
            )

    # Download the content but don't save to filesystem
    headers = _build_headers(url, hostname, access_token)

    fallback_upload_url = None
    if is_storage_data_file and storage_filepath:
        upload_path = storage_filepath
        if upload_path.startswith("data/"):
            upload_path = upload_path[len("data/") :]
        fallback_path = "/data/" + upload_path if not upload_path.startswith("data/") else "/" + upload_path
        if hostname:
            fallback_upload_url = concat_urls(hostname, fallback_path)

    try:
        r = requests.get(url, headers=headers, verify=VERIFY_SSL)
        r.raise_for_status()
        return base64.b64encode(r.content).decode("utf-8")
    except requests.exceptions.SSLError as e:
        logger.error(
            f"SSL error during requests.get('{url}'): {e}\n"
            f"Try to set VERIFY_SSL=False in environment variables to bypass SSL verification."
        )
        raise e
    except requests.exceptions.HTTPError as e:
        if fallback_upload_url:
            logger.info(
                "Download failed for proxy URL, retrying legacy upload path for base64: %s",
                fallback_upload_url,
            )
            fb_headers = _build_headers(fallback_upload_url, hostname, access_token)
            try:
                r = requests.get(fallback_upload_url, headers=fb_headers, verify=VERIFY_SSL)
                r.raise_for_status()
                return base64.b64encode(r.content).decode("utf-8")
            except Exception:
                raise e
        raise e