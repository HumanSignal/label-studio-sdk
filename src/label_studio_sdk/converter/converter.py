import io
import logging
import math
import os
import re
import xml.dom
import xml.dom.minidom
from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from enum import Enum
from glob import glob
from shutil import copy2
from typing import Optional, List, Tuple

import ijson
import ujson as json
from PIL import Image
from label_studio_sdk.converter import brush
from label_studio_sdk.converter.audio import convert_to_asr_json_manifest
from label_studio_sdk.converter.keypoints import process_keypoints_for_coco, build_kp_order, update_categories_for_keypoints, keypoints_in_label_config, get_yolo_categories_for_keypoints
from label_studio_sdk.converter.exports import csv2
from label_studio_sdk.converter.utils import (
    parse_config,
    create_tokens_and_tags,
    download,
    get_image_size_and_channels,
    ensure_dir,
    get_polygon_area,
    get_polygon_bounding_box,
    get_annotator,
    get_json_root_type,
    prettify_result,
    convert_annotation_to_yolo,
    convert_annotation_to_yolo_obb,
)
from label_studio_sdk._extensions.label_studio_tools.core.utils.io import get_local_path
from label_studio_sdk.converter.exports.yolo import process_and_save_yolo_annotations

logger = logging.getLogger(__name__)


class FormatNotSupportedError(NotImplementedError):
    pass


class Format(Enum):
    JSON = 1
    JSON_MIN = 2
    CSV = 3
    TSV = 4
    CONLL2003 = 5
    COCO = 6
    VOC = 7
    BRUSH_TO_NUMPY = 8
    BRUSH_TO_PNG = 9
    ASR_MANIFEST = 10
    YOLO = 11
    YOLO_OBB = 12
    CSV_OLD = 13
    YOLO_WITH_IMAGES = 14
    COCO_WITH_IMAGES = 15
    YOLO_OBB_WITH_IMAGES = 16
    BRUSH_TO_COCO = 17 

    def __str__(self):
        return self.name

    @classmethod
    def from_string(cls, s):
        try:
            return Format[s]
        except KeyError:
            raise ValueError()


class Converter(object):
    _FORMAT_INFO = {
        Format.JSON: {
            "title": "JSON",
            "description": "List of items in raw JSON format stored in one JSON file. Use to export both the data "
            "and the annotations for a dataset. It's Label Studio Common Format",
            "link": "https://labelstud.io/guide/export.html#JSON",
        },
        Format.JSON_MIN: {
            "title": "JSON-MIN",
            "description": 'List of items where only "from_name", "to_name" values from the raw JSON format are '
            "exported. Use to export only the annotations for a dataset.",
            "link": "https://labelstud.io/guide/export.html#JSON-MIN",
        },
        Format.CSV: {
            "title": "CSV",
            "description": "Results are stored as comma-separated values with the column names specified by the "
            'values of the "from_name" and "to_name" fields.',
            "link": "https://labelstud.io/guide/export.html#CSV",
        },
        Format.TSV: {
            "title": "TSV",
            "description": "Results are stored in tab-separated tabular file with column names specified by "
            '"from_name" "to_name" values',
            "link": "https://labelstud.io/guide/export.html#TSV",
        },
        Format.CONLL2003: {
            "title": "CONLL2003",
            "description": "Popular format used for the CoNLL-2003 named entity recognition challenge.",
            "link": "https://labelstud.io/guide/export.html#CONLL2003",
            "tags": ["sequence labeling", "text tagging", "named entity recognition"],
        },
        Format.COCO: {
            "title": "COCO",
            "description": "Popular machine learning format used by the COCO dataset for object detection and image "
            "segmentation tasks with polygons and rectangles.",
            "link": "https://labelstud.io/guide/export.html#COCO",
            "tags": ["image segmentation", "object detection", "keypoints"],
        },
        Format.COCO_WITH_IMAGES: {
            "title": "COCO with Images",
            "description": "COCO format with images downloaded.",
            "link": "https://labelstud.io/guide/export.html#COCO",
            "tags": ["image segmentation", "object detection", "keypoints"],
        },
        Format.VOC: {
            "title": "Pascal VOC XML",
            "description": "Popular XML format used for object detection and polygon image segmentation tasks.",
            "link": "https://labelstud.io/guide/export.html#Pascal-VOC-XML",
            "tags": ["image segmentation", "object detection"],
        },
        Format.YOLO: {
            "title": "YOLO",
            "description": "Popular TXT format is created for each image file. Each txt file contains annotations for "
            "the corresponding image file, that is object class, object coordinates, height & width.",
            "link": "https://labelstud.io/guide/export.html#YOLO",
            "tags": ["image segmentation", "object detection", "keypoints"],
        },
        Format.YOLO_WITH_IMAGES: {
            "title": "YOLO with Images",
            "description": "YOLO format with images downloaded.",
            "link": "https://labelstud.io/guide/export.html#YOLO",
            "tags": ["image segmentation", "object detection", "keypoints"],
        },
        Format.YOLO_OBB: {
            "title": "YOLOv8 OBB",
            "description": "Popular TXT format is created for each image file. Each txt file contains annotations for "
            "the corresponding image file. The YOLO OBB format designates bounding boxes by their four corner points "
            "with coordinates normalized between 0 and 1, so it is possible to export rotated objects.",
            "link": "https://labelstud.io/guide/export.html#YOLO",
            "tags": ["image segmentation", "object detection"],
        },
        Format.YOLO_OBB_WITH_IMAGES: {
            "title": "YOLOv8 OBB with Images",
            "description": "YOLOv8 OBB format with images downloaded.",
            "link": "https://labelstud.io/guide/export.html#YOLO",
            "tags": ["image segmentation", "object detection"],
        },
        Format.BRUSH_TO_NUMPY: {
            "title": "Brush labels to NumPy",
            "description": "Export your brush labels as NumPy 2d arrays. Each label outputs as one image.",
            "link": "https://labelstud.io/guide/export.html#Brush-labels-to-NumPy-amp-PNG",
            "tags": ["image segmentation"],
        },
        Format.BRUSH_TO_PNG: {
            "title": "Brush labels to PNG",
            "description": "Export your brush labels as PNG images. Each label outputs as one image.",
            "link": "https://labelstud.io/guide/export.html#Brush-labels-to-NumPy-amp-PNG",
            "tags": ["image segmentation"],
        },
        Format.ASR_MANIFEST: {
            "title": "ASR Manifest",
            "description": "Export audio transcription labels for automatic speech recognition as the JSON manifest "
            "format expected by NVIDIA NeMo models.",
            "link": "https://labelstud.io/guide/export.html#ASR-MANIFEST",
            "tags": ["speech recognition"],
        },   
        Format.BRUSH_TO_COCO: {

            "title": "Brush labels to COCO",
            "description": "Export your brush labels as COCO format for segmentation tasks. Converts RLE encoded masks to COCO polygons.",
            "link": "https://labelstud.io/guide/export.html#COCO",
            "tags": ["image segmentation", "brush annotations"],
        },
    }

    def all_formats(self):
        return self._FORMAT_INFO

    def __init__(
        self,
        config,
        project_dir,
        output_tags=None,
        upload_dir=None,
        download_resources=True,
        access_token=None,
        hostname=None,
    ):
        """Initialize Label Studio Converter for Exports

        :param config: string or dict: XML string with Label studio labeling config or path to this file or parsed_config
        :param project_dir: upload root directory for images, audio and other labeling files
        :param output_tags: it will be calculated automatically, contains label names
        :param upload_dir: upload root directory with files that were imported using LS GUI
        :param download_resources: if True, LS will try to download images, audio, etc and include them to export
        """
        self.project_dir = project_dir
        self.upload_dir = upload_dir
        self.download_resources = download_resources
        self._schema = None
        self.access_token = access_token
        self.hostname = hostname
        self.is_keypoints = None

        if isinstance(config, dict):
            self._schema = config
        elif isinstance(config, str):
            if os.path.isfile(config):
                with io.open(config) as f:
                    config_string = f.read()
            else:
                config_string = config
            self._schema = parse_config(config_string)

        if self._schema is None:
            logger.warning(
                "Label config or schema for Converter is not provided, "
                "it might be critical for some export formats, now set schema to empty dict"
            )
            self._schema = {}

        self._data_keys, self._output_tags = self._get_data_keys_and_output_tags(
            output_tags
        )
        self._supported_formats = self._get_supported_formats()

    def convert(self, input_data, output_data, format, is_dir=True, **kwargs):
        if isinstance(format, str):
            format = Format.from_string(format)

        if format == Format.JSON:
            self.convert_to_json(input_data, output_data, is_dir=is_dir)
        elif format == Format.JSON_MIN:
            self.convert_to_json_min(input_data, output_data, is_dir=is_dir)
        elif format == Format.CSV:
            header = kwargs.get("csv_header", True)
            sep = kwargs.get("csv_separator", ",")
            self.convert_to_csv(
                input_data, output_data, sep=sep, header=header, is_dir=is_dir
            )
        elif format == Format.TSV:
            header = kwargs.get("csv_header", True)
            sep = kwargs.get("csv_separator", "\t")
            self.convert_to_csv(
                input_data, output_data, sep=sep, header=header, is_dir=is_dir
            )
        elif format == Format.CONLL2003:
            self.convert_to_conll2003(input_data, output_data, is_dir=is_dir)
        elif format in [Format.COCO, Format.COCO_WITH_IMAGES]:
            image_dir = kwargs.get("image_dir")
            self.download_resources = format == Format.COCO_WITH_IMAGES
            self.convert_to_coco(
                input_data, output_data, output_image_dir=image_dir, is_dir=is_dir
            )
        elif format in [Format.YOLO, Format.YOLO_OBB, Format.YOLO_OBB_WITH_IMAGES, Format.YOLO_WITH_IMAGES]:
            image_dir = kwargs.get("image_dir")
            label_dir = kwargs.get("label_dir")
            self.download_resources = format in [Format.YOLO_WITH_IMAGES, Format.YOLO_OBB_WITH_IMAGES]
            self.convert_to_yolo(
                input_data,
                output_data,
                output_image_dir=image_dir,
                output_label_dir=label_dir,
                is_dir=is_dir,
                is_obb=(format in [Format.YOLO_OBB, Format.YOLO_OBB_WITH_IMAGES]),
            )
        elif format == Format.VOC:
            image_dir = kwargs.get("image_dir")
            self.convert_to_voc(
                input_data, output_data, output_image_dir=image_dir, is_dir=is_dir
            )
        elif format == Format.BRUSH_TO_NUMPY:
            items = (
                self.iter_from_dir(input_data)
                if is_dir
                else self.iter_from_json_file(input_data)
            )
            brush.convert_task_dir(items, output_data, out_format="numpy")
        elif format == Format.BRUSH_TO_PNG:
            items = (
                self.iter_from_dir(input_data)
                if is_dir
                else self.iter_from_json_file(input_data)
            )
            brush.convert_task_dir(items, output_data, out_format="png")
        elif format == Format.ASR_MANIFEST:
            items = (
                self.iter_from_dir(input_data)
                if is_dir
                else self.iter_from_json_file(input_data)
            )
            convert_to_asr_json_manifest(
                items,
                output_data,
                data_key=self._data_keys[0],
                project_dir=self.project_dir,
                upload_dir=self.upload_dir,
                download_resources=self.download_resources,
            )
        elif format == Format.BRUSH_TO_COCO:
            items = (
                self.iter_from_dir(input_data)
                if is_dir
                else self.iter_from_json_file(input_data)
            )
            from label_studio_sdk.converter.exports.brush_to_coco import convert_to_coco
            image_dir = kwargs.get("image_dir")
            convert_to_coco(
                items, 
                output_data, 
                output_image_dir=image_dir
            )

    def _get_data_keys_and_output_tags(self, output_tags=None):
        data_keys = set()
        output_tag_names = []
        if output_tags is not None:
            for tag in output_tags:
                if tag not in self._schema:
                    logger.debug(
                        'Specified tag "{tag}" not found in config schema: '
                        "available options are {schema_keys}".format(
                            tag=tag, schema_keys=str(list(self._schema.keys()))
                        )
                    )
        for name, info in self._schema.items():
            if output_tags is not None and name not in output_tags:
                continue
            for input_tag in info["inputs"]:
                for value_key_name in ["value", "valueList"]:
                    if value_key_name in input_tag:
                        data_keys.add(input_tag[value_key_name])
            output_tag_names.append(name)

        return list(data_keys), output_tag_names

    def _get_supported_formats(self):
        is_mig = False
        if len(self._data_keys) > 1:
            return [
                Format.JSON.name,
                Format.JSON_MIN.name,
                Format.CSV.name,
                Format.TSV.name,
            ]
        output_tag_types = set()
        input_tag_types = set()
        for info in self._schema.values():
            output_tag_types.add(info["type"])
            for input_tag in info["inputs"]:
                if input_tag.get("valueList"):
                    is_mig = True
                if input_tag["type"] == "Text" and input_tag.get("valueType") == "url":
                    logger.error('valueType="url" are not supported for text inputs')
                    continue
                input_tag_types.add(input_tag["type"])

        all_formats = [f.name for f in Format]

        # Check if KeyPointLabels exists without RectangleLabels
        has_keypoint_labels = "KeyPointLabels" in output_tag_types
        has_rectangle_labels = "RectangleLabels" in output_tag_types

        # If config has KeyPointLabels but no RectangleLabels, exclude COCO and YOLO formats
        # RectangleLabels are required for COCO and YOLO formats for category mapping
        if has_keypoint_labels and not has_rectangle_labels:
            if Format.COCO.name in all_formats:
                all_formats.remove(Format.COCO.name)
            if Format.COCO_WITH_IMAGES.name in all_formats:
                all_formats.remove(Format.COCO_WITH_IMAGES.name)
            if Format.YOLO.name in all_formats:
                all_formats.remove(Format.YOLO.name)
            if Format.YOLO_WITH_IMAGES.name in all_formats:
                all_formats.remove(Format.YOLO_WITH_IMAGES.name)

        if not ("Text" in input_tag_types and "Labels" in output_tag_types):
            all_formats.remove(Format.CONLL2003.name)
        if is_mig or not (
            "Image" in input_tag_types
            and (
                "RectangleLabels" in output_tag_types
                or "Rectangle" in output_tag_types
                and "Labels" in output_tag_types
            )
        ):
            all_formats.remove(Format.VOC.name)
        if is_mig or not (
            "Image" in input_tag_types
            and (
                "RectangleLabels" in output_tag_types
                or "PolygonLabels" in output_tag_types
                or "KeyPointLabels" in output_tag_types
            )
            or "Rectangle" in output_tag_types
            and "Labels" in output_tag_types
            or "PolygonLabels" in output_tag_types
            and "Labels" in output_tag_types
            or "KeyPointLabels" in output_tag_types
            and "Labels" in output_tag_types
        ):
            all_formats.remove(Format.COCO.name)
            all_formats.remove(Format.COCO_WITH_IMAGES.name)
            all_formats.remove(Format.YOLO.name)
            all_formats.remove(Format.YOLO_WITH_IMAGES.name)
        if not (
            "Image" in input_tag_types
            and (
                "BrushLabels" in output_tag_types
                or "brushlabels" in output_tag_types
                or "Brush" in output_tag_types
                and "Labels" in output_tag_types
            )
        ):
            all_formats.remove(Format.BRUSH_TO_NUMPY.name)
            all_formats.remove(Format.BRUSH_TO_PNG.name)
            all_formats.remove(Format.BRUSH_TO_COCO.name) 
        if not (
            ("Audio" in input_tag_types or "AudioPlus" in input_tag_types)
            and "TextArea" in output_tag_types
        ):
            all_formats.remove(Format.ASR_MANIFEST.name)
        if is_mig or ('Video' in input_tag_types and 'TimelineLabels' in output_tag_types):
            all_formats.remove(Format.YOLO_OBB.name)
            all_formats.remove(Format.YOLO_OBB_WITH_IMAGES.name)

        return all_formats

    @property
    def supported_formats(self):
        return self._supported_formats

    def iter_from_dir(self, input_dir):
        if not os.path.exists(input_dir):
            raise FileNotFoundError(
                "{input_dir} doesn't exist".format(input_dir=input_dir)
            )
        for json_file in glob(os.path.join(input_dir, "*.json")):
            for item in self.iter_from_json_file(json_file):
                if item:
                    yield item

    def iter_from_json_file(self, json_file):
        """Extract annotation results from json file

        param json_file: path to task list or dict with annotations
        """
        data_type = get_json_root_type(json_file)

        # one task
        if data_type == "dict":
            with open(json_file, "r") as json_file:
                data = json.load(json_file)
            for item in self.annotation_result_from_task(data):
                yield item

        # many tasks
        elif data_type == "list":
            with io.open(json_file, "rb") as f:
                logger.debug(f"ijson backend in use: {ijson.backend}")
                data = ijson.items(
                    f, "item", use_float=True
                )  # 'item' means to read array of dicts
                for task in data:
                    for item in self.annotation_result_from_task(task):
                        if item is not None:
                            yield item

    def _maybe_matching_tag_from_schema(self, from_name: str) -> Optional[str]:
        """If the from name exactly matches an output tag from the schema, return that tag.

        Otherwise, certain tags (like those from Repeater) contain
        placeholders like {{idx}}. Such placeholders are mapped to a regex in self._schema.
        For example, if "my_output_tag_{{idx}}" is a tag in the schema,
        then the from_name "my_output_tag_0" should match it, and we should return "my_output_tag_{{idx}}".
        """

        best_match = None
        best_match_len = 0

        for tag_name, tag_info in self._schema.items():
            if tag_name == from_name:
                return tag_name

            if not tag_info.get("regex"):
                continue

            tag_name_pattern = tag_name
            for variable, regex in tag_info["regex"].items():
                tag_name_pattern = tag_name_pattern.replace(variable, regex)

            # In some cases there are tags with same prefix - we need to find the best or longest matching pattern
            if r := re.compile(tag_name_pattern).match(from_name):
                if match_len := len(tag_name_pattern) > best_match_len:
                    best_match = tag_name
                    best_match_len = len(tag_name_pattern)

        return best_match if best_match else None

    def annotation_result_from_task(self, task):
        has_annotations = "completions" in task or "annotations" in task
        if not has_annotations:
            logger.warning(
                'Each task dict item should contain "annotations" or "completions" [deprecated], '
                "where value is list of dicts"
            )
            return None

        # get last not skipped completion and make result from it
        annotations = (
            task["annotations"] if "annotations" in task else task["completions"]
        )

        # return task with empty annotations
        if not annotations:
            data = Converter.get_data(task, {}, {})
            yield data

        # skip cancelled annotations
        cancelled = lambda x: not (
            x.get("skipped", False) or x.get("was_cancelled", False)
        )
        annotations = list(filter(cancelled, annotations))
        if not annotations:
            return None

        # sort by creation time
        annotations = sorted(
            annotations, key=lambda x: x.get("created_at", 0), reverse=True
        )

        for annotation in annotations:
            result = annotation["result"]
            outputs = defaultdict(list)

            # get results only as output
            for r in result:
                if "from_name" in r and (
                    tag_name := self._maybe_matching_tag_from_schema(r["from_name"])
                ):
                    v = deepcopy(r["value"])
                    v["type"] = self._schema[tag_name]["type"]
                    if "original_width" in r:
                        v["original_width"] = r["original_width"]
                    if "original_height" in r:
                        v["original_height"] = r["original_height"]
                    outputs[r["from_name"]].append(v)
                    if self.is_keypoints:
                        v['id'] = r.get('id')
                        v['parentID'] = r.get('parentID')

            data = Converter.get_data(task, outputs, annotation)
            if "agreement" in task:
                data["agreement"] = task["agreement"]
            yield data

    @staticmethod
    def get_data(task, outputs, annotation):
        return {
            "id": task["id"],
            "input": task["data"],
            "output": outputs or {},
            "completed_by": annotation.get("completed_by", {}),
            "annotation_id": annotation.get("id"),
            "created_at": annotation.get("created_at"),
            "updated_at": annotation.get("updated_at"),
            "lead_time": annotation.get("lead_time"),
            "history": annotation.get("history"),
            "was_cancelled": annotation.get("was_cancelled"),
        }

    def _check_format(self, fmt):
        pass

    def convert_to_json(self, input_data, output_dir, is_dir=True):
        self._check_format(Format.JSON)
        ensure_dir(output_dir)
        output_file = os.path.join(output_dir, "result.json")

        if is_dir:
            # Memory-optimized: stream JSON writing instead of accumulating in memory
            with io.open(output_file, mode="w", encoding="utf8") as fout:
                fout.write("[\n")
                first_record = True

                for json_file in glob(os.path.join(input_data, "*.json")):
                    with io.open(json_file, encoding="utf8") as f:
                        record = json.load(f)

                        if not first_record:
                            fout.write(",\n")
                        json.dump(record, fout, indent=2, ensure_ascii=False)
                        first_record = False

                        # Free memory immediately
                        del record

                fout.write("\n]")
        else:
            copy2(input_data, output_file)

    def convert_to_json_min(self, input_data, output_dir, is_dir=True):
        self._check_format(Format.JSON_MIN)
        ensure_dir(output_dir)
        output_file = os.path.join(output_dir, "result.json")
        item_iterator = self.iter_from_dir if is_dir else self.iter_from_json_file

        with io.open(output_file, mode="w", encoding="utf8") as fout:
            fout.write("[\n")
            first_record = True

            for item in item_iterator(input_data):
                # SAFE memory optimization: use json serialization/deserialization
                # This avoids deepcopy but ensures complete isolation of objects
                record = json.loads(json.dumps(item["input"]))

                if item.get("id") is not None:
                    record["id"] = item["id"]
                for name, value in item["output"].items():
                    record[name] = prettify_result(value)
                record["annotator"] = get_annotator(item, int_id=True)
                record["annotation_id"] = item["annotation_id"]
                record["created_at"] = item["created_at"]
                record["updated_at"] = item["updated_at"]
                record["lead_time"] = item["lead_time"]
                if "agreement" in item:
                    record["agreement"] = item["agreement"]

                # Write record to file immediately
                if not first_record:
                    fout.write(",\n")
                json.dump(record, fout, indent=2, ensure_ascii=False)
                first_record = False

                # Explicitly delete record to free memory
                del record

            fout.write("\n]")

    def convert_to_csv(self, input_data, output_dir, is_dir=True, **kwargs):
        self._check_format(Format.CSV)
        item_iterator = self.iter_from_dir if is_dir else self.iter_from_json_file
        return csv2.convert(item_iterator, input_data, output_dir, **kwargs)

    def convert_to_conll2003(self, input_data, output_dir, is_dir=True):
        self._check_format(Format.CONLL2003)
        ensure_dir(output_dir)
        output_file = os.path.join(output_dir, "result.conll")
        data_key = self._data_keys[0]
        with io.open(output_file, "w", encoding="utf8") as fout:
            fout.write("-DOCSTART- -X- O\n")
            item_iterator = self.iter_from_dir if is_dir else self.iter_from_json_file

            for item in item_iterator(input_data):
                filtered_output = list(
                    filter(
                        lambda x: x[0]["type"].lower() == "labels",
                        item["output"].values(),
                    )
                )
                tokens, tags = create_tokens_and_tags(
                    text=item["input"][data_key],
                    spans=next(iter(filtered_output), None),
                )
                for token, tag in zip(tokens, tags):
                    fout.write("{token} -X- _ {tag}\n".format(token=token, tag=tag))
                fout.write("\n")

    def convert_to_coco(
        self, input_data, output_dir, output_image_dir=None, is_dir=True
    ):
        def add_image(images, width, height, image_id, image_path):
            images.append(
                {
                    "width": width,
                    "height": height,
                    "id": image_id,
                    "file_name": image_path,
                }
            )
            return images

        self._check_format(Format.COCO)
        ensure_dir(output_dir)
        output_file = os.path.join(output_dir, "result.json")
        if output_image_dir is not None:
            ensure_dir(output_image_dir)
        else:
            output_image_dir = os.path.join(output_dir, "images")
            os.makedirs(output_image_dir, exist_ok=True)
        images, categories, annotations = [], [], []
        categories, category_name_to_id = self._get_labels()
        categories, category_name_to_id = update_categories_for_keypoints(categories, category_name_to_id, self._schema)
        data_key = self._data_keys[0]
        item_iterator = (
            self.iter_from_dir(input_data)
            if is_dir
            else self.iter_from_json_file(input_data)
        )
        for item_idx, item in enumerate(item_iterator):
            image_path = item["input"][data_key]
            task_id = item["id"]
            image_id = len(images)
            width = None
            height = None
            # download all images of the dataset, including the ones without annotations
            if not os.path.exists(image_path):
                try:
                    image_path = get_local_path(
                        url=image_path,
                        hostname=self.hostname,
                        project_dir=self.project_dir,
                        image_dir=self.upload_dir,
                        cache_dir=output_image_dir,
                        download_resources=self.download_resources,
                        access_token=self.access_token,
                        task_id=task_id,
                    )
                    # make path relative to output_image_dir
                    image_path = os.path.relpath(image_path, output_dir)
                except:
                    logger.info(
                        "Unable to download {image_path}. The image of {item} will be skipped".format(
                            image_path=image_path, item=item
                        ),
                        exc_info=True,
                    )
            # add image to final images list
            try:
                with Image.open(os.path.join(output_dir, image_path)) as img:
                    width, height = img.size
                images = add_image(images, width, height, image_id, image_path)
            except:
                logger.info(
                    "Unable to open {image_path}, can't extract width and height for COCO export".format(
                        image_path=image_path, item=item
                    ),
                    exc_info=True,
                )

            # skip tasks without annotations
            if not item["output"]:
                # image wasn't load and there are no labels
                if not width:
                    images = add_image(images, width, height, image_id, image_path)

                logger.warning("No annotations found for item #" + str(item_idx))
                continue

            # concatenate results over all tag names
            labels = []
            for key in item["output"]:
                labels += item["output"][key]

            if len(labels) == 0:
                logger.debug(f'Empty bboxes for {item["output"]}')
                continue

            keypoint_labels = []
            for label in labels:
                category_name = None
                for key in ["rectanglelabels", "polygonlabels", "keypointlabels", "labels"]:
                    if key in label and len(label[key]) > 0:
                        category_name = label[key][0]
                        break

                if category_name is None:
                    logger.warning("Unknown label type or labels are empty")
                    continue

                if not height or not width:
                    if "original_width" not in label or "original_height" not in label:
                        logger.debug(
                            f"original_width or original_height not found in {image_path}"
                        )
                        continue

                    width, height = label["original_width"], label["original_height"]
                    images = add_image(images, width, height, image_id, image_path)

                if category_name not in category_name_to_id:
                    category_id = len(categories)
                    category_name_to_id[category_name] = category_id
                    categories.append({"id": category_id, "name": category_name})
                category_id = category_name_to_id[category_name]

                annotation_id = len(annotations)

                if "rectanglelabels" in label or "labels" in label:
                    xywh = self.rotated_rectangle(label)
                    if xywh is None:
                        continue

                    x, y, w, h = xywh
                    x = x * label["original_width"] / 100
                    y = y * label["original_height"] / 100
                    w = w * label["original_width"] / 100
                    h = h * label["original_height"] / 100

                    annotations.append(
                        {
                            "id": annotation_id,
                            "image_id": image_id,
                            "category_id": category_id,
                            "segmentation": [],
                            "bbox": [x, y, w, h],
                            "ignore": 0,
                            "iscrowd": 0,
                            "area": w * h,
                        }
                    )
                elif "polygonlabels" in label:
                    points_abs = [
                        (x / 100 * width, y / 100 * height) for x, y in label["points"]
                    ]
                    x, y = zip(*points_abs)

                    annotations.append(
                        {
                            "id": annotation_id,
                            "image_id": image_id,
                            "category_id": category_id,
                            "segmentation": [
                                [coord for point in points_abs for coord in point]
                            ],
                            "bbox": get_polygon_bounding_box(x, y),
                            "ignore": 0,
                            "iscrowd": 0,
                            "area": get_polygon_area(x, y),
                        }
                    )
                elif "keypointlabels" in label:
                    keypoint_labels.append(label)
                else:
                    raise ValueError("Unknown label type")

                if os.getenv("LABEL_STUDIO_FORCE_ANNOTATOR_EXPORT"):
                    annotations[-1].update({"annotator": get_annotator(item)})
            if keypoint_labels:
                kp_order = build_kp_order(self._schema)
                annotations.append(process_keypoints_for_coco(
                    keypoint_labels,
                    kp_order,
                    annotation_id=len(annotations),
                    image_id=image_id,
                    category_name_to_id=category_name_to_id,
                ))

        with io.open(output_file, mode="w", encoding="utf8") as fout:
            json.dump(
                {
                    "images": images,
                    "categories": categories,
                    "annotations": annotations,
                    "info": {
                        "year": datetime.now().year,
                        "version": "1.0",
                        "description": "",
                        "contributor": "Label Studio",
                        "url": "",
                        "date_created": str(datetime.now()),
                    },
                },
                fout,
                indent=2,
            )

    def convert_to_yolo(
        self,
        input_data,
        output_dir,
        output_image_dir=None,
        output_label_dir=None,
        is_dir=True,
        split_labelers=False,
        is_obb=False,
    ):
        """Convert data in a specific format to the YOLO format.

        Parameters
        ----------
        input_data : str
            The input data, either a directory or a JSON file.
        output_dir : str
            The directory to store the output files in.
        output_image_dir : str, optional
            The directory to store the image files in. If not provided, it will default to a subdirectory called 'images' in output_dir.
        output_label_dir : str, optional
            The directory to store the label files in. If not provided, it will default to a subdirectory called 'labels' in output_dir.
        is_dir : bool, optional
            A boolean indicating whether `input_data` is a directory (True) or a JSON file (False).
        split_labelers : bool, optional
            A boolean indicating whether to create a dedicated subfolder for each labeler in the output label directory.
        obb : bool, optional
            A boolean indicating whether to convert to Oriented Bounding Box (OBB) format.
        """
        if is_obb:
            self._check_format(Format.YOLO_OBB)
        else:
            self._check_format(Format.YOLO)
        ensure_dir(output_dir)
        notes_file = os.path.join(output_dir, "notes.json")
        class_file = os.path.join(output_dir, "classes.txt")
        if output_image_dir is not None:
            ensure_dir(output_image_dir)
        else:
            output_image_dir = os.path.join(output_dir, "images")
            os.makedirs(output_image_dir, exist_ok=True)
        if output_label_dir is not None:
            ensure_dir(output_label_dir)
        else:
            output_label_dir = os.path.join(output_dir, "labels")
            os.makedirs(output_label_dir, exist_ok=True)
        is_keypoints = keypoints_in_label_config(self._schema)

        if is_keypoints:
            # we use this attribute to add id and parentID to annotation data
            self.is_keypoints = True
            categories, category_name_to_id = get_yolo_categories_for_keypoints(self._schema)
        else:
            categories, category_name_to_id = self._get_labels()
        data_key = self._data_keys[0]
        item_iterator = (
            self.iter_from_dir(input_data)
            if is_dir
            else self.iter_from_json_file(input_data)
        )
        for item_idx, item in enumerate(item_iterator):
            # get image path(s) and label file path
            image_paths = item["input"][data_key]
            image_paths = [image_paths] if isinstance(image_paths, str) else image_paths
            # download image(s)
            image_path = None
            task_id = item["id"]
            # TODO: for multi-page annotation, this code won't produce correct relationships between page and annotated shapes
            # fixing the issue in RND-84
            for image_path in reversed(image_paths):
                if not os.path.exists(image_path):
                    try:
                        image_path = get_local_path(
                            url=image_path,
                            hostname=self.hostname,
                            project_dir=self.project_dir,
                            image_dir=self.upload_dir,
                            cache_dir=output_image_dir,
                            download_resources=self.download_resources,
                            access_token=self.access_token,
                            task_id=task_id,
                        )
                        # make path relative to output_image_dir
                        image_path = os.path.relpath(image_path, output_dir)
                    except:
                        logger.info(
                            "Unable to download {image_path}. The item {item} will be skipped".format(
                                image_path=image_path, item=item
                            ),
                            exc_info=True,
                        )
            if not image_path:
                logger.error(f"No image path found for item #{item_idx}")
                continue

            # create dedicated subfolder for each labeler if split_labelers=True
            labeler_subfolder = str(item["completed_by"]) if split_labelers else ""
            os.makedirs(
                os.path.join(output_label_dir, labeler_subfolder), exist_ok=True
            )

            # identify label file path
            filename = os.path.splitext(os.path.basename(image_path))[0]
            filename = filename[
                0 : 255 - 4
            ]  # urls might be too long, use 255 bytes (-4 for .txt) limit for filenames
            label_path = os.path.join(
                output_label_dir, labeler_subfolder, filename + ".txt"
            )

            # Skip tasks without annotations
            if not item["output"]:
                logger.warning("No completions found for item #" + str(item_idx))
                if not os.path.exists(label_path):
                    with open(label_path, "x"):
                        pass
                continue

            # concatenate results over all tag names
            labels = []
            for key in item["output"]:
                labels += item["output"][key]

            if len(labels) == 0:
                logger.warning(f'Empty bboxes for {item["output"]}')
                if not os.path.exists(label_path):
                    with open(label_path, "x"):
                        pass
                continue

            categories, category_name_to_id = process_and_save_yolo_annotations(labels, label_path, category_name_to_id, categories, is_obb, is_keypoints, self._schema)
        with open(class_file, "w", encoding="utf8") as f:
            for c in categories:
                f.write(c["name"] + "\n")
        with io.open(notes_file, mode="w", encoding="utf8") as fout:
            json.dump(
                {
                    "categories": categories,
                    "info": {
                        "year": datetime.now().year,
                        "version": "1.0",
                        "contributor": "Label Studio",
                    },
                },
                fout,
                indent=2,
            )

    @staticmethod
    def rotated_rectangle(label):
        if not (
            "x" in label and "y" in label and "width" in label and "height" in label
        ):
            return None

        label_x, label_y, label_w, label_h, label_r = (
            label["x"],
            label["y"],
            label["width"],
            label["height"],
            label["rotation"] if "rotation" in label else 0.0,
        )

        if abs(label_r) > 0:
            alpha = math.atan(label_h / label_w)
            beta = math.pi * (
                label_r / 180
            )  # Label studio defines the angle towards the vertical axis

            radius = math.sqrt((label_w / 2) ** 2 + (label_h / 2) ** 2)

            # Label studio saves the position of top left corner after rotation
            x_0 = (
                label_x
                - radius
                * (math.cos(math.pi - alpha - beta) - math.cos(math.pi - alpha))
                + label_w / 2
            )
            y_0 = (
                label_y
                + radius
                * (math.sin(math.pi - alpha - beta) - math.sin(math.pi - alpha))
                + label_h / 2
            )

            theta_1 = alpha + beta
            theta_2 = math.pi - alpha + beta
            theta_3 = math.pi + alpha + beta
            theta_4 = 2 * math.pi - alpha + beta

            x_coord = [
                x_0 + radius * math.cos(theta_1),
                x_0 + radius * math.cos(theta_2),
                x_0 + radius * math.cos(theta_3),
                x_0 + radius * math.cos(theta_4),
            ]
            y_coord = [
                y_0 + radius * math.sin(theta_1),
                y_0 + radius * math.sin(theta_2),
                y_0 + radius * math.sin(theta_3),
                y_0 + radius * math.sin(theta_4),
            ]

            label_x = min(x_coord)
            label_y = min(y_coord)
            label_w = max(x_coord) - label_x
            label_h = max(y_coord) - label_y

        return label_x, label_y, label_w, label_h

    def convert_to_voc(
        self, input_data, output_dir, output_image_dir=None, is_dir=True
    ):
        ensure_dir(output_dir)
        if output_image_dir is not None:
            ensure_dir(output_image_dir)
            output_image_dir_rel = output_image_dir
        else:
            output_image_dir = os.path.join(output_dir, "images")
            os.makedirs(output_image_dir, exist_ok=True)
            output_image_dir_rel = "images"

        def create_child_node(doc, tag, attr, parent_node):
            child_node = doc.createElement(tag)
            text_node = doc.createTextNode(attr)
            child_node.appendChild(text_node)
            parent_node.appendChild(child_node)

        data_key = self._data_keys[0]
        item_iterator = (
            self.iter_from_dir(input_data)
            if is_dir
            else self.iter_from_json_file(input_data)
        )
        for item_idx, item in enumerate(item_iterator):
            image_path = item["input"][data_key]
            annotations_dir = os.path.join(output_dir, "Annotations")
            if not os.path.exists(annotations_dir):
                os.makedirs(annotations_dir)
            # Download image
            channels = 3
            if not os.path.exists(image_path):
                try:
                    image_path = download(
                        image_path,
                        output_image_dir,
                        project_dir=self.project_dir,
                        upload_dir=self.upload_dir,
                        return_relative_path=True,
                        download_resources=self.download_resources,
                    )
                except:
                    logger.info(
                        "Unable to download {image_path}. The item {item} will be skipped".format(
                            image_path=image_path, item=item
                        ),
                        exc_info=True,
                    )
                else:
                    full_image_path = os.path.join(
                        output_image_dir, os.path.basename(image_path)
                    )
                    # retrieve number of channels from downloaded image
                    try:
                        _, _, channels = get_image_size_and_channels(full_image_path)
                    except:
                        logger.warning(f"Can't read channels from image")

            # skip tasks without annotations
            if not item["output"]:
                logger.warning("No annotations found for item #" + str(item_idx))
                continue

            image_name = os.path.basename(image_path)
            xml_name = os.path.splitext(image_name)[0] + ".xml"

            # concatenate results over all tag names
            bboxes = []
            for key in item["output"]:
                bboxes += item["output"][key]

            if len(bboxes) == 0:
                logger.debug(f'Empty bboxes for {item["output"]}')
                continue

            if "original_width" not in bboxes[0] or "original_height" not in bboxes[0]:
                logger.debug(
                    f"original_width or original_height not found in {image_name}"
                )
                continue

            width, height = bboxes[0]["original_width"], bboxes[0]["original_height"]
            xml_filepath = os.path.join(annotations_dir, xml_name)

            my_dom = xml.dom.getDOMImplementation()
            doc = my_dom.createDocument(None, "annotation", None)
            root_node = doc.documentElement
            create_child_node(doc, "folder", output_image_dir_rel, root_node)
            create_child_node(doc, "filename", image_name, root_node)

            source_node = doc.createElement("source")
            create_child_node(doc, "database", "MyDatabase", source_node)
            create_child_node(doc, "annotation", "COCO2017", source_node)
            create_child_node(doc, "image", "flickr", source_node)
            create_child_node(doc, "flickrid", "NULL", source_node)
            create_child_node(doc, "annotator", get_annotator(item, ""), source_node)
            root_node.appendChild(source_node)

            owner_node = doc.createElement("owner")
            create_child_node(doc, "flickrid", "NULL", owner_node)
            create_child_node(doc, "name", "Label Studio", owner_node)
            root_node.appendChild(owner_node)
            size_node = doc.createElement("size")
            create_child_node(doc, "width", str(width), size_node)
            create_child_node(doc, "height", str(height), size_node)
            create_child_node(doc, "depth", str(channels), size_node)
            root_node.appendChild(size_node)
            create_child_node(doc, "segmented", "0", root_node)

            for bbox in bboxes:
                key = (
                    "rectanglelabels"
                    if "rectanglelabels" in bbox
                    else ("labels" if "labels" in bbox else None)
                )
                if key is None or len(bbox[key]) == 0:
                    continue

                name = bbox[key][0]
                x = int(bbox["x"] / 100 * width)
                y = int(bbox["y"] / 100 * height)
                w = int(bbox["width"] / 100 * width)
                h = int(bbox["height"] / 100 * height)

                object_node = doc.createElement("object")
                create_child_node(doc, "name", name, object_node)
                create_child_node(doc, "pose", "Unspecified", object_node)
                create_child_node(doc, "truncated", "0", object_node)
                create_child_node(doc, "difficult", "0", object_node)
                bndbox_node = doc.createElement("bndbox")
                create_child_node(doc, "xmin", str(x), bndbox_node)
                create_child_node(doc, "ymin", str(y), bndbox_node)
                create_child_node(doc, "xmax", str(x + w), bndbox_node)
                create_child_node(doc, "ymax", str(y + h), bndbox_node)

                object_node.appendChild(bndbox_node)
                root_node.appendChild(object_node)

            with io.open(xml_filepath, mode="w", encoding="utf8") as fout:
                doc.writexml(fout, addindent="" * 4, newl="\n", encoding="utf-8")

    def _get_labels(self):
        labels = set()
        categories = list()
        category_name_to_id = dict()

        for name, info in self._schema.items():
            labels |= set(info["labels"])
            attrs = info["labels_attrs"]
            for label in attrs:
                if attrs[label].get("category"):
                    categories.append(
                        {"id": attrs[label].get("category"), "name": label}
                    )
                    category_name_to_id[label] = attrs[label].get("category")
        labels_to_add = set(labels) - set(list(category_name_to_id.keys()))
        labels_to_add = sorted(list(labels_to_add))
        idx = 0
        while idx in list(category_name_to_id.values()):
            idx += 1
        for label in labels_to_add:
            categories.append({"id": idx, "name": label})
            category_name_to_id[label] = idx
            idx += 1
            while idx in list(category_name_to_id.values()):
                idx += 1
        return categories, category_name_to_id
