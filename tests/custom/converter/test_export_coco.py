import json
import shutil
import tempfile
from pathlib import Path

import pytest
from label_studio_sdk.converter import Converter


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

    coco_path = next(temp_out_dir.glob("*.json"))
    coco = json.loads(coco_path.read_text())

    category_id_by_name = {cat["name"]: cat["id"] for cat in coco["categories"]}
    assert category_id_by_name["car"] == 10
    assert category_id_by_name["person"] == 2
    assert category_id_by_name["truck"] == 7
    assert all(isinstance(cat["id"], int) for cat in coco["categories"])

    annotation_category_ids = {ann["category_id"] for ann in coco["annotations"]}
    assert annotation_category_ids == {10, 7}
