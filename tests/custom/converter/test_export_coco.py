import json
import shutil
import tempfile
from pathlib import Path

import pytest
from label_studio_sdk.converter import Converter
from label_studio_sdk.converter.keypoints import process_keypoints_for_coco


TEST_DATA_DIR = Path(__file__).resolve().parent / "data" / "test_export_coco"
LABEL_CONFIG_PATH = TEST_DATA_DIR / "label_config.xml"
INPUT_JSON_PATH = TEST_DATA_DIR / "data.json"
PROJECT_DIR = "."  # images are referenced relatively


@pytest.fixture
def temp_out_dir():
    tmpdir = Path(tempfile.mkdtemp())
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


def test_convert_to_coco_integration(temp_out_dir):
    out_images_dir = temp_out_dir / "images"

    conv = Converter(
        config=str(LABEL_CONFIG_PATH),
        project_dir=PROJECT_DIR,
        download_resources=False,
    )

    conv.convert_to_coco(
        str(INPUT_JSON_PATH),
        str(temp_out_dir),
        output_image_dir=str(out_images_dir),
        is_dir=False,
    )

    with INPUT_JSON_PATH.open() as fp:
        ls_tasks = json.load(fp)

    coco_files = list(temp_out_dir.glob("*.json"))
    assert len(coco_files) == 1, "expected exactly one COCO file"

    coco_path = coco_files[0]
    with coco_path.open() as fp:
        coco = json.load(fp)

    for key in ("images", "annotations", "categories"):
        assert key in coco, f"missing '{key}' section"


def test_convert_to_coco_contents(temp_out_dir):
    converter = Converter(
        config=str(LABEL_CONFIG_PATH),
        project_dir=PROJECT_DIR,
        download_resources=False,
    )

    converter.convert_to_coco(
        str(INPUT_JSON_PATH),
        str(temp_out_dir),
        output_image_dir=str(temp_out_dir / "images"),
        is_dir=False,
    )

    coco_path = next(temp_out_dir.glob("*.json"))
    coco = json.loads(coco_path.read_text())

    category_names = {cat["name"] for cat in coco["categories"]}
    assert {"rectangle_label", "polygon_label"} <= category_names

    rect_ann = next(a for a in coco["annotations"] if not a["segmentation"])
    poly_ann = next(
        a for a in coco["annotations"] if a["segmentation"] and "keypoints" not in a
    )

    exp_bbox = [
        31.941923774954628 / 100 * 500,      # x_px
        4.113475177304964 / 100 * 320,       # y_px
        6.352087114337568 / 100 * 500,       # w_px
        9.929078014184398 / 100 * 320,       # h_px
    ]
    assert rect_ann["bbox"] == pytest.approx(exp_bbox, rel=1e-6)

    seg = poly_ann["segmentation"][0]
    assert len(seg) == 6
    assert poly_ann["area"] > 0
    _, _, w, h = poly_ann["bbox"]
    assert w > 0 and h > 0

    assert len(coco["annotations"]) == 3


def _run_converter(out_dir: Path):
    conv = Converter(
        config=str(LABEL_CONFIG_PATH),
        project_dir=PROJECT_DIR,
        download_resources=False,
    )
    images_dir = out_dir / "images"
    conv.convert_to_coco(
        str(INPUT_JSON_PATH),
        str(out_dir),
        output_image_dir=str(images_dir),
        is_dir=False,
    )
    coco_path = next(out_dir.glob("*.json"))
    return json.loads(coco_path.read_text())


def test_convert_to_coco_rectangle_and_polygon(temp_out_dir: Path):
    coco = _run_converter(temp_out_dir)

    # basic structure
    assert set(coco.keys()).issuperset({"images", "annotations", "categories"})
    assert len(coco["images"]) >= 1  # at least one image expected

    cats = {c["name"] for c in coco["categories"]}
    assert {"rectangle_label", "polygon_label"}.issubset(cats)

    rect_anns = [a for a in coco["annotations"] if not a.get("segmentation")]
    assert rect_anns, "No rectangle annotations found"
    rect = rect_anns[0]
    assert rect["bbox"][2] > 0 and rect["bbox"][3] > 0

    poly_anns = [a for a in coco["annotations"] if a.get("segmentation") and not a.get("keypoints")]
    assert poly_anns, "No polygon annotations found"
    poly = poly_anns[0]
    assert len(poly["segmentation"][0]) % 2 == 0


def test_convert_to_coco_keypoints(temp_out_dir: Path):
    coco = _run_converter(temp_out_dir)

    kp_anns = [a for a in coco["annotations"] if "keypoints" in a and a["num_keypoints"] > 0]
    assert kp_anns, "No keypoint annotations were exported"

    ann = kp_anns[0]

    # length consistency: 3 numbers per keypoint (x, y, v)
    assert len(ann["keypoints"]) == ann["num_keypoints"] * 3

    # visibility flags must be 0, 1 or 2
    vis_flags = ann["keypoints"][2::3]
    assert all(v in (0, 1, 2) for v in vis_flags)

    xs = ann["keypoints"][0::3]
    ys = ann["keypoints"][1::3]
    x0, y0, w, h = ann["bbox"]

    assert x0 <= min(xs) <= x0 + w
    assert x0 <= max(xs) <= x0 + w
    assert y0 <= min(ys) <= y0 + h
    assert y0 <= max(ys) <= y0 + h

    kp_cats = [c for c in coco["categories"] if "keypoints" in c]
    assert kp_cats, "No keypoint category present in categories section"
    cat = kp_cats[0]

    assert cat["name"] == "default"


def test_convert_to_coco_preserves_explicit_category_ids(temp_out_dir: Path):
    """COCO export should keep explicit `category` ids from the labeling config."""
    config = """
    <View>
      <Image name="image" value="$image"/>
      <RectangleLabels name="label" toName="image">
        <Label value="car" category="10"/>
        <Label value="person" category="2"/>
        <Label value="truck" category="7"/>
      </RectangleLabels>
    </View>
    """.strip()
    input_payload = [
        {
            "id": 1,
            "data": {"image": "not-downloaded.jpg"},
            "annotations": [
                {
                    "id": 1,
                    "result": [
                        {
                            "id": "r1",
                            "type": "rectanglelabels",
                            "value": {
                                "x": 10,
                                "y": 10,
                                "width": 20,
                                "height": 20,
                                "rotation": 0,
                                "rectanglelabels": ["car"],
                            },
                            "to_name": "image",
                            "from_name": "label",
                            "original_width": 1000,
                            "original_height": 500,
                        },
                        {
                            "id": "r2",
                            "type": "rectanglelabels",
                            "value": {
                                "x": 30,
                                "y": 30,
                                "width": 10,
                                "height": 10,
                                "rotation": 0,
                                "rectanglelabels": ["truck"],
                            },
                            "to_name": "image",
                            "from_name": "label",
                            "original_width": 1000,
                            "original_height": 500,
                        },
                    ],
                }
            ],
        }
    ]
    input_path = temp_out_dir / "input.json"
    input_path.write_text(json.dumps(input_payload))

    converter = Converter(config=config, project_dir=PROJECT_DIR, download_resources=False)
    converter.convert_to_coco(str(input_path), str(temp_out_dir), output_image_dir=str(temp_out_dir / "images"), is_dir=False)

    coco_path = temp_out_dir / "result.json"
    coco = json.loads(coco_path.read_text())

    category_id_by_name = {cat["name"]: cat["id"] for cat in coco["categories"]}
    assert category_id_by_name["car"] == 10
    assert category_id_by_name["person"] == 2
    assert category_id_by_name["truck"] == 7
    assert all(isinstance(cat["id"], int) for cat in coco["categories"])

    annotation_category_ids = {ann["category_id"] for ann in coco["annotations"]}
    assert annotation_category_ids == {10, 7}


SAM2_GHOST_CONFIG = """
<View>
  <Image name="image" value="$image"/>
  <BrushLabels name="tag" toName="image">
    <Label value="defect"/>
  </BrushLabels>
  <KeyPointLabels name="tag2" toName="image" smart="true">
    <Label value="defect" model_index="0"/>
  </KeyPointLabels>
  <RectangleLabels name="tag3" toName="image" smart="true">
    <Label value="defect"/>
  </RectangleLabels>
</View>
""".strip()

SAM2_GHOST_CONFIG_NO_MODEL_INDEX = SAM2_GHOST_CONFIG.replace(' model_index="0"', "")


def _sam2_task_with_ghost_keypoint(include_xy=False):
    keypoint_value = {"width": 0.5, "keypointlabels": ["defect"]}
    if include_xy:
        keypoint_value["x"] = 15
        keypoint_value["y"] = 25
    return [
        {
            "id": 1,
            "data": {"image": "not-downloaded.jpg"},
            "annotations": [
                {
                    "id": 1,
                    "result": [
                        {
                            "id": "ghost",
                            "type": "keypointlabels",
                            "value": keypoint_value,
                            "to_name": "image",
                            "from_name": "tag2",
                            "original_width": 100,
                            "original_height": 100,
                        },
                        {
                            "id": "rect",
                            "type": "rectanglelabels",
                            "value": {
                                "x": 10,
                                "y": 10,
                                "width": 20,
                                "height": 20,
                                "rotation": 0,
                                "rectanglelabels": ["defect"],
                            },
                            "to_name": "image",
                            "from_name": "tag3",
                            "original_width": 100,
                            "original_height": 100,
                        },
                    ],
                }
            ],
        }
    ]


def test_process_keypoints_for_coco_skips_keypoints_without_xy():
    """Ghost/SAM2 prompt keypoints without x/y must not abort COCO keypoint packing."""
    ghost = {
        "original_width": 100,
        "original_height": 100,
        "width": 0.5,
        "keypointlabels": ["keypoint_label1"],
    }
    missing_none = {
        "original_width": 100,
        "original_height": 100,
        "x": None,
        "y": None,
        "keypointlabels": ["keypoint_label1"],
    }
    valid = {
        "original_width": 100,
        "original_height": 100,
        "x": 10,
        "y": 20,
        "keypointlabels": ["keypoint_label2"],
    }
    ann = process_keypoints_for_coco(
        [ghost, missing_none, valid],
        kp_order=["keypoint_label1", "keypoint_label2"],
        annotation_id=7,
        image_id=3,
        category_name_to_id={"keypoint_label1": 1, "keypoint_label2": 1},
    )
    assert ann is not None
    assert ann["num_keypoints"] == 1
    assert ann["keypoints"][0:3] == [0, 0, 0]
    assert ann["keypoints"][3:6] == [10, 20, 2]


def test_process_keypoints_for_coco_returns_none_when_all_keypoints_lack_xy():
    ghost = {
        "original_width": 100,
        "original_height": 100,
        "keypointlabels": ["keypoint_label1"],
    }
    assert (
        process_keypoints_for_coco(
            [ghost],
            kp_order=["keypoint_label1"],
            annotation_id=0,
            image_id=0,
            category_name_to_id={"keypoint_label1": 0},
        )
        is None
    )


def test_convert_to_coco_skips_sam2_ghost_keypoints_without_xy(temp_out_dir: Path):
    """SAM2 prompt keypoints with no x/y must not fail COCO export of other regions."""
    input_path = temp_out_dir / "input.json"
    input_path.write_text(json.dumps(_sam2_task_with_ghost_keypoint(include_xy=False)))

    converter = Converter(config=SAM2_GHOST_CONFIG, project_dir=PROJECT_DIR, download_resources=False)
    converter.convert_to_coco(
        str(input_path), str(temp_out_dir), output_image_dir=str(temp_out_dir / "images"), is_dir=False
    )

    coco = json.loads((temp_out_dir / "result.json").read_text())
    assert coco["annotations"], "rectangle annotation should still be exported"
    assert not any("keypoints" in ann for ann in coco["annotations"])
    rect = coco["annotations"][0]
    assert rect["bbox"][2] > 0 and rect["bbox"][3] > 0


def test_convert_to_coco_skips_sam2_keypoints_without_model_index(temp_out_dir: Path):
    """SAM2 KeyPointLabels without model_index must not fail the rest of COCO export."""
    input_path = temp_out_dir / "input.json"
    input_path.write_text(json.dumps(_sam2_task_with_ghost_keypoint(include_xy=True)))

    converter = Converter(
        config=SAM2_GHOST_CONFIG_NO_MODEL_INDEX, project_dir=PROJECT_DIR, download_resources=False
    )
    converter.convert_to_coco(
        str(input_path), str(temp_out_dir), output_image_dir=str(temp_out_dir / "images"), is_dir=False
    )

    coco = json.loads((temp_out_dir / "result.json").read_text())
    assert coco["annotations"], "rectangle annotation should still be exported"
    assert not any("keypoints" in ann for ann in coco["annotations"])
