"""DocLang (.dclx) exporter.

Finds DocLang XML in standard Label Studio, ReactCode, and custom Interface
results, then packages it according to the DocLang archive specification:
https://github.com/doclang-project/doclang/blob/main/spec.md#doclang-archive-format.

Document discovery (export sources)
------------------------------------
DocLang archives are written from four task payload sources, in order:

1. **Annotations** — each non-cancelled, non-skipped entry in ``annotations``
   (or legacy ``completions``). One ``.dclx`` per annotation whose ``result``
   contains DocLang XML.

2. **Drafts** — each entry in ``drafts`` whose ``result`` contains DocLang XML.
   When a draft is linked to an annotation via ``annotation`` and that annotation
   already produced a DocLang archive in step 1, the draft is skipped so the
   same labeling session does not emit duplicate documents.

3. **Predictions** — each entry in ``predictions`` whose ``result`` contains
   DocLang XML. Predictions are always exported under their own id; they are
   never deduplicated against annotations or drafts.

4. **Task data fallback** — when steps 1–3 produce no documents, DocLang XML
   embedded under ``doclang`` / ``document`` keys in ``task.data`` is exported as
   ``task-{id}-data.dclx`` (or ``task-{id}-data-{n}.dclx`` when multiple
   distinct documents are found).

Archive filenames use distinct prefixes (``annotation``, ``draft``,
``prediction``, ``data``) plus the source id so outputs from different source
kinds cannot collide.
"""

import base64
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
from typing import Iterable, Iterator, Mapping, NamedTuple, Optional
from urllib.parse import parse_qsl, urlparse

import ijson
from doclang import pack
from lxml import etree

from label_studio_sdk._extensions.label_studio_tools.core.utils.io import get_local_path
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

_TASK_DATA_DOCLANG_KEYS = ("doclang", "document")
# URL fields in task.data pointing at .dclg/.dclx archives are not fetched in v1.


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


def _extract_doclang_bytes_from_data(task: dict) -> list[bytes]:
    """Return distinct DocLang documents found under known keys in task.data."""
    data = task.get("data") or {}
    if not isinstance(data, dict):
        return []

    seen: set[bytes] = set()
    documents: list[bytes] = []
    stack = [(data, 0, False)]
    visited = 0

    while stack and visited < _MAX_VALUE_NODES:
        current, depth, under_doclang_key = stack.pop()
        visited += 1

        if isinstance(current, str):
            if under_doclang_key:
                document = _doclang_xml_bytes(current)
                if document is not None and document not in seen:
                    seen.add(document)
                    documents.append(document)
        elif depth < _MAX_VALUE_DEPTH:
            if isinstance(current, dict):
                stack.extend(
                    (child, depth + 1, under_doclang_key or key in _TASK_DATA_DOCLANG_KEYS)
                    for key, child in reversed(tuple(current.items()))
                )
            elif isinstance(current, list):
                stack.extend((child, depth + 1, under_doclang_key) for child in reversed(current))

    return documents


def resolve_image_data_keys(
    schema: Optional[Mapping] = None,
    config: Optional[str] = None,
) -> tuple[Optional[str], Optional[str]]:
    """Return (single_image_key, list_image_key) from Image tags in a parsed label config."""
    single_key = None
    list_key = None
    if schema:
        for info in schema.values():
            for input_tag in info.get("inputs", []):
                if input_tag.get("type") != "Image":
                    continue
                if input_tag.get("valueList"):
                    list_key = input_tag["valueList"]
                elif input_tag.get("value"):
                    single_key = input_tag["value"]

    if config:
        parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False, recover=False)
        root = etree.fromstring(config.encode("utf-8"), parser=parser)
        for tag in root.iter():
            if not isinstance(tag.tag, str) or etree.QName(tag).localname != "Image":
                continue
            if tag.attrib.get("valueList"):
                list_key = tag.attrib["valueList"].lstrip("$")
            elif tag.attrib.get("value"):
                single_key = tag.attrib["value"].lstrip("$")

    return single_key, list_key


def _normalize_page_source(raw) -> Optional[str]:
    if isinstance(raw, dict):
        raw = raw.get("url")
    if isinstance(raw, str) and raw:
        return raw
    return None


def _extract_page_urls(task: dict, image_key: str, image_list_key: Optional[str] = None) -> list[str]:
    data = task.get("data") or {}
    if image_list_key:
        raw_pages = data.get(image_list_key)
        if isinstance(raw_pages, list):
            urls = [_normalize_page_source(item) for item in raw_pages]
            return [url for url in urls if url]

    raw = data.get(image_key)
    url = _normalize_page_source(raw)
    return [url] if url else []


def _image_extension(url: str, local_path: Optional[str] = None) -> str:
    if url.startswith("data:"):
        mime = url[5:].split(";", 1)[0].strip()
        guess = mimetypes.guess_extension(mime) or ""
        if guess == ".jpe":
            guess = ".jpg"
        return guess.lower() if guess.lower() in _IMAGE_EXTS else ".png"

    parsed = urlparse(url)
    _, ext = posixpath.splitext(parsed.path)
    ext = ext.lower()
    if ext == ".jpe":
        ext = ".jpg"
    if ext in _IMAGE_EXTS:
        return ext

    if local_path:
        _, local_ext = posixpath.splitext(local_path)
        local_ext = local_ext.lower()
        if local_ext == ".jpe":
            local_ext = ".jpg"
        if local_ext in _IMAGE_EXTS:
            return local_ext

    guess = mimetypes.guess_extension(mimetypes.guess_type(parsed.path)[0] or "") or ""
    return guess.lower() if guess.lower() in _IMAGE_EXTS else ".png"


def _write_data_url_page(url: str, destination_dir: str, page_number: int) -> Optional[str]:
    if not url.startswith("data:"):
        return None

    try:
        header, _, encoded = url.partition(",")
        if ";base64" not in header.lower() or not encoded:
            logger.warning("Unsupported data URL page raster (expected base64): %s", url[:64])
            return None

        page_path = os.path.join(destination_dir, f"{page_number}{_image_extension(url)}")
        with open(page_path, "wb") as page_file:
            page_file.write(base64.b64decode(encoded))
        return page_path
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to decode data URL page raster: %s", exc)
        return None


def _fetch_page_image(
    url: str,
    destination_dir: str,
    page_number: int,
    project_dir: Optional[str],
    upload_dir: Optional[str],
    hostname: Optional[str],
    access_token: Optional[str],
    task_id: Optional[int],
) -> Optional[str]:
    data_url_path = _write_data_url_page(url, destination_dir, page_number)
    if data_url_path is not None:
        return data_url_path

    try:
        local_path = get_local_path(
            url=url,
            hostname=hostname,
            project_dir=project_dir,
            image_dir=upload_dir,
            cache_dir=destination_dir,
            access_token=access_token,
            download_resources=True,
            task_id=task_id,
        )
        if not local_path or not os.path.exists(local_path):
            logger.warning("Downloaded image not found on disk for %s", url)
            return None

        staged_path = os.path.join(destination_dir, os.path.basename(local_path))
        if not os.path.exists(staged_path):
            shutil.copy2(local_path, staged_path)

        page_path = os.path.join(destination_dir, f"{page_number}{_image_extension(url, local_path)}")
        if os.path.abspath(staged_path) != os.path.abspath(page_path):
            os.replace(staged_path, page_path)
        return page_path
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to fetch page image %s: %s", url, exc)
        return None


def _fetch_page_images(
    urls: list[str],
    destination_dir: str,
    project_dir: Optional[str],
    upload_dir: Optional[str],
    hostname: Optional[str],
    access_token: Optional[str],
    task_id: Optional[int],
) -> dict[int, str]:
    pages: dict[int, str] = {}
    for page_number, url in enumerate(urls, start=1):
        page_path = _fetch_page_image(
            url,
            destination_dir,
            page_number,
            project_dir,
            upload_dir,
            hostname,
            access_token,
            task_id,
        )
        if page_path:
            pages[page_number] = page_path
    return pages


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
        if not isinstance(ann, dict):
            continue
        if ann.get("was_cancelled") or ann.get("skipped"):
            continue
        yield ann


class _DoclangSource(NamedTuple):
    kind: str
    source_id: int | str
    document: bytes


def _archive_filename(task_id, source: _DoclangSource) -> str:
    if source.kind == "data":
        if source.source_id == "":
            return f"task-{task_id}-data.dclx"
        return f"task-{task_id}-data-{source.source_id}.dclx"
    return f"task-{task_id}-{source.kind}-{source.source_id}.dclx"


def _iter_doclang_sources(task: dict) -> Iterable[_DoclangSource]:
    """Yield result sources, falling back to known DocLang fields in task.data."""
    exported_annotation_ids: set[int | str] = set()
    found_result_source = False

    for index, ann in enumerate(_valid_annotations(task)):
        document = _extract_doclang_bytes(ann)
        if document is None:
            continue
        ann_id = ann.get("id", index)
        exported_annotation_ids.add(ann_id)
        found_result_source = True
        yield _DoclangSource("annotation", ann_id, document)

    for index, draft in enumerate(task.get("drafts") or []):
        if not isinstance(draft, dict):
            continue
        linked_annotation = draft.get("annotation")
        if linked_annotation is not None and linked_annotation in exported_annotation_ids:
            continue
        document = _extract_doclang_bytes(draft)
        if document is None:
            continue
        draft_id = draft.get("id", index)
        found_result_source = True
        yield _DoclangSource("draft", draft_id, document)

    for index, prediction in enumerate(task.get("predictions") or []):
        if not isinstance(prediction, dict):
            continue
        document = _extract_doclang_bytes(prediction)
        if document is None:
            continue
        prediction_id = prediction.get("id", index)
        found_result_source = True
        yield _DoclangSource("prediction", prediction_id, document)

    if found_result_source:
        return

    data_documents = _extract_doclang_bytes_from_data(task)
    if len(data_documents) == 1:
        yield _DoclangSource("data", "", data_documents[0])
    else:
        for index, document in enumerate(data_documents, start=1):
            yield _DoclangSource("data", index, document)


def convert_to_doclang(
    input_data: str,
    output_dir: str,
    is_dir: bool = True,
    image_key: str = "image",
    image_list_key: Optional[str] = None,
    download_resources: bool = True,
    project_dir: Optional[str] = None,
    upload_dir: Optional[str] = None,
    hostname: Optional[str] = None,
    access_token: Optional[str] = None,
) -> int:
    """Export annotations to DocLang ``.dclx`` archives.

    One archive is written per annotation, draft, prediction, or task.data
    source that contains a DocLang XML region (see module docstring for
    discovery rules). Returns the number of archives written.
    """
    ensure_dir(output_dir)

    written = 0
    for task in _iter_raw_tasks(input_data, is_dir=is_dir):
        sources = list(_iter_doclang_sources(task))
        if not sources:
            continue

        task_id = task.get("id")
        page_urls = _extract_page_urls(task, image_key, image_list_key)

        with tempfile.TemporaryDirectory() as task_tmp:
            pages = (
                _fetch_page_images(
                    page_urls,
                    task_tmp,
                    project_dir,
                    upload_dir,
                    hostname,
                    access_token,
                    task_id,
                )
                if download_resources and page_urls
                else None
            )

            for source in sources:
                filename = _archive_filename(task_id, source)
                output_path = os.path.join(output_dir, filename)
                with tempfile.TemporaryDirectory() as tmp:
                    document = source.document
                    assets = {}
                    if download_resources:
                        asset_dir = os.path.join(tmp, "assets")
                        ensure_dir(asset_dir)
                        document, assets = _stage_document_assets(document, asset_dir, project_dir, upload_dir)
                    document_path = Path(tmp) / "document.dclg"
                    document_path.write_bytes(document)
                    pack(
                        document_path,
                        output=output_path,
                        pages=pages or None,
                        assets=assets or None,
                        # DocLang 0.x minor releases are intentionally breaking, so full
                        # schema validation is deferred until its compatibility contract stabilizes:
                        # validate=True,
                        validate=False,
                    )
                written += 1

    logger.info("DocLang export: wrote %d archives", written)
    return written
