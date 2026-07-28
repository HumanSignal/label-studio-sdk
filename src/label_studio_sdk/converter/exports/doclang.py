"""DocLang (.dclx) exporter.

Finds DocLang XML in standard Label Studio, ReactCode, and custom Interface
results, then packages it according to the DocLang archive specification:
https://github.com/doclang-project/doclang/blob/main/spec.md#doclang-archive-format.
"""

import io
import json
import logging
import mimetypes
import os
import posixpath
import shutil
import tempfile
from glob import glob
from pathlib import Path
from typing import Iterable, Iterator, Optional
from urllib.parse import parse_qsl, urlparse

import ijson
from doclang import pack
from lxml import etree

from label_studio_sdk.converter.utils import download, ensure_dir, get_json_root_type

logger = logging.getLogger(__name__)

_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
_ASSET_EXTS = _IMAGE_EXTS | {".svg"}
_DOCLANG_NAMESPACE_PREFIX = "https://www.doclang.ai/ns/"
_MAX_VALUE_DEPTH = 32
_MAX_VALUE_NODES = 10_000

# These built-in result types have well-defined non-document payloads. Custom
# Interfaces that use a custom type fall through to content-based detection.
_STANDARD_NON_DOCUMENT_RESULT_TYPES = {
    "bitmask",
    "bitmasklabels",
    "brush",
    "brushlabels",
    "chatmessage",
    "choices",
    "datetime",
    "ellipse",
    "ellipselabels",
    "hypertextlabels",
    "keypoint",
    "keypointlabels",
    "labels",
    "magicwand",
    "number",
    "ocrlabels",
    "pairwise",
    "paragraphlabels",
    "polygon",
    "polygonlabels",
    "ranker",
    "rating",
    "rectangle",
    "rectanglelabels",
    "relation",
    "taxonomy",
    "timelinelabels",
    "timeserieslabels",
    "vector",
    "vectorlabels",
    "videorectangle",
    "videovector",
    "videovectorlabels",
}


def _iter_raw_tasks(input_data: str, is_dir: bool) -> Iterator[dict]:
    """Yield raw task dicts.

    The default Converter pipeline filters annotation results by the parsed
    label config schema, which strips DocLang textarea regions when the project
    uses a Custom Interface with an empty XML config. We stream raw tasks here
    to preserve those regions.
    """
    if is_dir:
        for json_file in glob(os.path.join(input_data, "*.json")):
            yield from _iter_raw_tasks(json_file, is_dir=False)
        return

    root = get_json_root_type(input_data)
    if root == "dict":
        with open(input_data, "r", encoding="utf-8") as f:
            yield json.load(f)
    else:
        with io.open(input_data, "rb") as f:
            for task in ijson.items(f, "item", use_float=True):
                yield task


def _candidate_payload(result: dict):
    result_type = result.get("type")
    value = result.get("value")

    if result_type == "textarea":
        return value.get("text") if isinstance(value, dict) else None
    if result_type == "reactcode":
        return value.get("reactcode") if isinstance(value, dict) else None
    if result_type in _STANDARD_NON_DOCUMENT_RESULT_TYPES:
        return None
    return value


def _iter_string_values(value) -> Iterator[str]:
    """Iterate strings in a JSON value without unbounded Python recursion."""
    stack = [iter(((value, 0),))]
    visited = 0

    while stack and visited < _MAX_VALUE_NODES:
        try:
            current, depth = next(stack[-1])
        except StopIteration:
            stack.pop()
            continue

        visited += 1

        if isinstance(current, str):
            yield current
        elif depth < _MAX_VALUE_DEPTH:
            if isinstance(current, dict):
                stack.append(((child, depth + 1) for child in current.values()))
            elif isinstance(current, list):
                stack.append(((child, depth + 1) for child in current))


def _doclang_xml_bytes(value: str) -> Optional[bytes]:
    try:
        encoded = value.encode("utf-8")
    except UnicodeEncodeError:
        return None

    parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False, recover=False, huge_tree=True)
    try:
        root = etree.fromstring(encoded, parser=parser)
        qname = etree.QName(root)
    except (ValueError, etree.XMLSyntaxError):
        return None

    namespace_version = (
        qname.namespace.removeprefix(_DOCLANG_NAMESPACE_PREFIX)
        if qname.namespace and qname.namespace.startswith(_DOCLANG_NAMESPACE_PREFIX)
        else None
    )
    has_doclang_namespace = not qname.namespace or (
        namespace_version is not None
        and namespace_version.startswith("v")
        and namespace_version.removeprefix("v").isdigit()
    )
    is_doclang = qname.localname == "doclang" and has_doclang_namespace and not root.getroottree().docinfo.doctype
    if not is_doclang:
        return None

    return encoded


def _extract_doclang_bytes(annotation: dict) -> Optional[bytes]:
    for result in annotation.get("result", []) or []:
        if not isinstance(result, dict):
            continue
        for value in _iter_string_values(_candidate_payload(result)):
            document = _doclang_xml_bytes(value)
            if document is not None:
                return document
    return None


def _extract_image_url(task: dict, image_key: str) -> Optional[str]:
    data = task.get("data") or {}
    raw = data.get(image_key)
    if isinstance(raw, dict):
        raw = raw.get("url")
    if isinstance(raw, str) and raw:
        return raw
    return None


def _image_extension(url: str) -> str:
    parsed = urlparse(url)
    _, ext = posixpath.splitext(parsed.path)
    ext = ext.lower()
    if ext == ".jpe":
        ext = ".jpg"
    if ext in _IMAGE_EXTS:
        return ext
    guess = mimetypes.guess_extension(mimetypes.guess_type(parsed.path)[0] or "") or ""
    return guess.lower() if guess.lower() in _IMAGE_EXTS else ".png"


def _fetch_page_image(
    url: str,
    destination_dir: str,
    project_dir: Optional[str],
    upload_dir: Optional[str],
) -> Optional[str]:
    try:
        local_path = download(
            url,
            destination_dir,
            project_dir=project_dir,
            upload_dir=upload_dir,
            download_resources=True,
        )
        if not local_path or not os.path.exists(local_path):
            logger.warning("Downloaded image not found on disk for %s", url)
            return None

        staged_path = os.path.join(destination_dir, os.path.basename(local_path))
        if not os.path.exists(staged_path):
            shutil.copy2(local_path, staged_path)

        page_path = os.path.join(destination_dir, f"1{_image_extension(staged_path)}")
        if os.path.abspath(staged_path) != os.path.abspath(page_path):
            os.replace(staged_path, page_path)
        return page_path
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to fetch page image %s: %s", url, exc)
        return None


def _asset_uri_path(uri: str) -> str:
    parsed = urlparse(uri)
    candidate_paths = [parsed.path]
    candidate_paths.extend(value for key, value in parse_qsl(parsed.query) if key == "d")
    return next((path for path in candidate_paths if posixpath.splitext(path)[1]), parsed.path)


def _asset_extension(uri: str) -> str:
    path = _asset_uri_path(uri)
    _, ext = posixpath.splitext(path)
    ext = ext.lower()
    if ext == ".jpe":
        ext = ".jpg"
    if ext in _ASSET_EXTS:
        return ext
    if ext:
        return ""
    guess = mimetypes.guess_extension(mimetypes.guess_type(path)[0] or "") or ""
    return guess.lower() if guess.lower() in _ASSET_EXTS else ".png"


def _archive_asset_path(uri: str, used_paths: set[str]) -> Optional[str]:
    ext = _asset_extension(uri)
    if not ext:
        return None

    stem = Path(posixpath.basename(_asset_uri_path(uri))).stem or "image"
    candidate = f"assets/{stem}{ext}"
    index = 2
    while candidate in used_paths:
        candidate = f"assets/{stem}-{index}{ext}"
        index += 1
    used_paths.add(candidate)
    return candidate


def _download_document_asset(
    uri: str,
    destination_dir: str,
    project_dir: Optional[str],
    upload_dir: Optional[str],
) -> Optional[str]:
    try:
        local_path = download(
            uri,
            destination_dir,
            project_dir=project_dir,
            upload_dir=upload_dir,
            download_resources=True,
        )
        if not local_path or not os.path.exists(local_path):
            logger.warning("Downloaded document asset not found on disk for %s", uri)
            return None

        staged_path = os.path.join(destination_dir, os.path.basename(local_path))
        if not os.path.exists(staged_path):
            shutil.copy2(local_path, staged_path)
        return staged_path
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to fetch document asset %s: %s", uri, exc)
        return None


def _is_downloadable_asset_uri(uri: str) -> bool:
    parsed = urlparse(uri)
    if parsed.scheme == "data":
        return False
    if parsed.scheme:
        is_downloadable = parsed.scheme in {"http", "https"}
    else:
        is_downloadable = uri.startswith("/data/")
    if not is_downloadable:
        return False
    return bool(_asset_extension(uri))


def _stage_document_assets(
    document: bytes,
    destination_dir: str,
    project_dir: Optional[str],
    upload_dir: Optional[str],
) -> tuple[bytes, dict[str, str]]:
    parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False, recover=False, huge_tree=True)
    root = etree.fromstring(document, parser=parser)
    assets = {}
    used_paths = set()
    rewritten = False

    for element in root.iter():
        if not isinstance(element.tag, str):
            continue
        if etree.QName(element).localname != "src":
            continue

        uri = element.get("uri")
        if not uri or not _is_downloadable_asset_uri(uri):
            continue

        archive_path = _archive_asset_path(uri, used_paths)
        if not archive_path:
            continue

        local_path = _download_document_asset(uri, destination_dir, project_dir, upload_dir)
        if not local_path:
            continue

        assets[archive_path.removeprefix("assets/")] = local_path
        element.set("uri", archive_path)
        rewritten = True

    if not rewritten:
        return document, {}

    return etree.tostring(root, encoding="utf-8"), assets


def _valid_annotations(task: dict) -> Iterable[dict]:
    annotations = task.get("annotations") or task.get("completions") or []
    for ann in annotations:
        if ann.get("was_cancelled") or ann.get("skipped"):
            continue
        yield ann


def convert_to_doclang(
    input_data: str,
    output_dir: str,
    is_dir: bool = True,
    image_key: str = "image",
    download_resources: bool = True,
    project_dir: Optional[str] = None,
    upload_dir: Optional[str] = None,
) -> int:
    """Export annotations to DocLang ``.dclx`` archives.

    One archive is written per non-cancelled annotation that contains a DocLang
    XML region. Returns the number of archives written.
    """
    ensure_dir(output_dir)

    written = 0
    skipped_no_xml = 0
    for task in _iter_raw_tasks(input_data, is_dir=is_dir):
        task_id = task.get("id")
        image_url = _extract_image_url(task, image_key)

        for ann in _valid_annotations(task):
            document = _extract_doclang_bytes(ann)
            if document is None:
                skipped_no_xml += 1
                continue

            filename = f"task-{task_id}-annotation-{ann.get('id')}.dclx"
            output_path = os.path.join(output_dir, filename)
            with tempfile.TemporaryDirectory() as tmp:
                assets = {}
                if download_resources:
                    asset_dir = os.path.join(tmp, "assets")
                    ensure_dir(asset_dir)
                    document, assets = _stage_document_assets(document, asset_dir, project_dir, upload_dir)
                document_path = Path(tmp) / "document.dclg"
                document_path.write_bytes(document)
                page_path = (
                    _fetch_page_image(image_url, tmp, project_dir, upload_dir)
                    if download_resources and image_url
                    else None
                )
                pack(
                    document_path,
                    output=output_path,
                    pages={1: page_path} if page_path else None,
                    assets=assets or None,
                    # DocLang 0.x minor releases are intentionally breaking, so full
                    # schema validation is deferred until the format stabilizes:
                    # validate=True,
                    validate=False,
                )
            written += 1

    logger.info(
        "DocLang export: wrote %d archives (skipped %d annotations with no DocLang XML)",
        written,
        skipped_no_xml,
    )
    return written
