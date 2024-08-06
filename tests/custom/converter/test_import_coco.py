import json
import os
from typing import Any, Dict, List

import lxml.etree as ET
from label_studio_sdk.converter.imports import coco as import_coco


def test_import_coco_base():
    input_data_dir = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "data", "test_import_coco"
    )

    output_dir = "/tmp/lsc-pytest"
    input_json_file = os.path.join(input_data_dir, "coco_import_input.json")
    out_json_file = os.path.join(output_dir, "coco_import_output.json")

    import_coco.convert_coco_to_ls(input_file=input_json_file, out_file=out_json_file)
    # list files in output dir
    print(os.listdir(output_dir))

    out_config_file = os.path.join(output_dir, "coco_import_output.label_config.xml")

    assert os.path.exists(out_config_file), f"> {out_config_file} is not generated"
    assert os.path.exists(out_json_file), f"> {out_json_file} is not generated"

    input_labels: List[str]
    input_images: List[Dict[str, Any]]
    with open(input_json_file, "r") as f:
        input_coco_data = json.loads(f.read())
        input_labels = [x["name"] for x in input_coco_data["categories"]]
        input_images = input_coco_data["images"]

    label_element = ET.parse(out_config_file).getroot()[2]
    labels_generated = [x.attrib["value"] for x in label_element.getchildren()]
    assert set(input_labels) == set(
        labels_generated
    ), "> generated class labels do not match original labels"

    with open(out_json_file, "r") as f:
        output_data = json.loads(f.read())
    assert len(output_data) == len(input_images), "> some file imports did not succeed!"
