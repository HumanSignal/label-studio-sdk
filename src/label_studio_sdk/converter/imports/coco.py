import os
import json  # better to use "imports ujson as json" for the best performance
import uuid
import logging
from PIL import Image

from label_studio_sdk.converter.utils import ExpandFullPath
from label_studio_sdk.converter.imports.label_config import generate_label_config

logger = logging.getLogger("root")


def new_task(out_type, root_url, file_name):
    """Create a new Label Studio task structure.
    
    Args:
        out_type (str): Type of output - either 'annotations' or 'predictions'
        root_url (str): Root URL path where images will be hosted
        file_name (str): Name of the image file
        
    Returns:
        dict: Label Studio task structure with image data and empty result array
    """
    return {
        "data": {"image": os.path.join(root_url, file_name)},
        # 'annotations' or 'predictions'
        out_type: [
            {
                "result": [],
                "ground_truth": False,
            }
        ],
    }


def create_bbox(annotation, categories, from_name, image_height, image_width, to_name):
    """Convert COCO bounding box annotation to Label Studio format.
    
    COCO bbox format: [x, y, width, height] where (x,y) is top-left corner
    Label Studio format: percentages relative to image dimensions
    
    Args:
        annotation (dict): COCO annotation containing bbox and category_id
        categories (dict): Mapping of category_id to category name
        from_name (str): Control tag name from Label Studio labeling config
        image_height (int): Height of the source image in pixels
        image_width (int): Width of the source image in pixels
        to_name (str): Object name from Label Studio labeling config
        
    Returns:
        dict: Label Studio rectangle annotation item
    """
    label = categories[int(annotation["category_id"])]
    x, y, width, height = annotation["bbox"]
    x, y, width, height = float(x), float(y), float(width), float(height)
    
    # Convert absolute coordinates to percentages
    item = {
        "id": uuid.uuid4().hex[0:10],
        "type": "rectanglelabels",
        "value": {
            "x": x / image_width * 100.0,
            "y": y / image_height * 100.0,
            "width": width / image_width * 100.0,
            "height": height / image_height * 100.0,
            "rotation": 0,
            "rectanglelabels": [label],
        },
        "to_name": to_name,
        "from_name": from_name,
        "image_rotation": 0,
        "original_width": image_width,
        "original_height": image_height,
    }
    return item


def create_segmentation(
    category_id, segmentation, categories, from_name, image_height, image_width, to_name
):
    """Convert COCO segmentation annotation to Label Studio polygon format.
    
    COCO segmentation format: flat array of [x1,y1,x2,y2,...] coordinates
    Label Studio format: array of [x,y] points as percentages
    
    Args:
        category_id (int): COCO category ID for this segmentation
        segmentation (list): Flat list of polygon coordinates [x1,y1,x2,y2,...]
        categories (dict): Mapping of category_id to category name
        from_name (str): Control tag name from Label Studio labeling config
        image_height (int): Height of the source image in pixels
        image_width (int): Width of the source image in pixels
        to_name (str): Object name from Label Studio labeling config
        
    Returns:
        dict: Label Studio polygon annotation item
    """
    label = categories[int(category_id)]
    # Convert flat array [x1,y1,x2,y2,...] to array of points [[x1,y1],[x2,y2],...]
    points = [list(x) for x in zip(*[iter(segmentation)] * 2)]

    # Convert absolute coordinates to percentages
    for i in range(len(points)):
        points[i][0] = points[i][0] / image_width * 100.0
        points[i][1] = points[i][1] / image_height * 100.0

    item = {
        "id": uuid.uuid4().hex[0:10],
        "type": "polygonlabels",
        "value": {"points": points, "polygonlabels": [label]},
        "to_name": to_name,
        "from_name": from_name,
        "image_rotation": 0,
        "original_width": image_width,
        "original_height": image_height,
    }
    return item


def create_keypoints(
    annotation, categories, from_name, to_name, image_height, image_width, point_width
):
    """Convert COCO keypoints annotation to Label Studio keypoint format.
    
    COCO keypoints format: [x1,y1,v1,x2,y2,v2,...] where v is visibility flag
    v=0: not labeled, v=1: labeled but not visible, v=2: labeled and visible
    
    Args:
        annotation (dict): COCO annotation containing keypoints and category_id
        categories (dict): Mapping of category_id to category name
        from_name (str): Control tag name from Label Studio labeling config
        to_name (str): Object name from Label Studio labeling config
        image_height (int): Height of the source image in pixels
        image_width (int): Width of the source image in pixels
        point_width (float): Width/size of keypoints in Label Studio
        
    Returns:
        list: List of Label Studio keypoint annotation items
    """
    label = categories[int(annotation["category_id"])]
    points = annotation["keypoints"]
    items = []

    # Process keypoints in groups of 3: x, y, visibility
    for i in range(0, len(points), 3):
        x, y, v = points[i : i + 3]  # x, y, visibility
        x, y, v = float(x), float(y), int(v)
        
        # Convert absolute coordinates to percentages
        item = {
            "id": uuid.uuid4().hex[0:10],
            "type": "keypointlabels",
            "value": {
                "x": x / image_width * 100.0,
                "y": y / image_height * 100.0,
                "width": point_width,
                "keypointlabels": [label],
            },
            "to_name": to_name,
            "from_name": from_name,
            "image_rotation": 0,
            "original_width": image_width,
            "original_height": image_height,
        }

        # Handle visibility: if v < 2, the keypoint is hidden
        if v < 2:
            item["value"]["hidden"] = True

        items.append(item)
    return items


def convert_coco_to_ls(
    input_file,
    out_file,
    to_name="image",
    from_name="label",
    out_type="annotations",
    image_root_url="/data/local-files/?d=",
    use_super_categories=False,
    point_width=1.0,
):
    """Convert COCO dataset annotations to Label Studio JSON format.
    
    This function processes a COCO dataset JSON file and converts all annotations
    (bounding boxes, segmentations, keypoints) to Label Studio's format. It supports:
    - Object detection (bounding boxes)
    - Instance segmentation (polygons) 
    - Keypoint detection (pose estimation)
    
    The function automatically generates a Label Studio labeling configuration
    based on the annotation types found in the COCO dataset.

    Args:
        input_file (str): Path to input COCO JSON file
        out_file (str): Path to output Label Studio JSON file
        to_name (str, optional): Object name from Label Studio labeling config. Defaults to "image".
        from_name (str, optional): Control tag name from Label Studio labeling config. Defaults to "label".
        out_type (str, optional): Annotation type - "annotations" or "predictions". Defaults to "annotations".
        image_root_url (str, optional): Root URL path where images will be hosted. 
            Defaults to "/data/local-files/?d=" for local storage.
        use_super_categories (bool, optional): Use super categories from COCO if available. Defaults to False.
        point_width (float, optional): Width/size of keypoints in pixels. Defaults to 1.0.
    
    Example:
        >>> convert_coco_to_ls(
        ...     input_file='annotations/instances_val2017.json',
        ...     out_file='label_studio_tasks.json',
        ...     image_root_url='s3://my-bucket/images/',
        ...     use_super_categories=True
        ... )
        
    Note:
        - The function will create a corresponding .label_config.xml file with the labeling configuration
        - RLE (Run-Length Encoding) segmentations are not yet supported
        - Keypoints are supported without skeleton connections
        - Images must be accessible at the specified image_root_url
    """

    tasks = {}  # image_id => task
    logger.info("Reading COCO notes and categories from %s", input_file)

    # Load and parse COCO JSON file
    with open(input_file, encoding="utf8") as f:
        coco = json.load(f)

    # Build categories => labels dict
    new_categories = {}
    # Convert list to dict: [...] => {category_id: category_item}
    categories = {int(category["id"]): category for category in coco["categories"]}
    ids = sorted(categories.keys())  # Sort labels by their original IDs

    # Build category name mapping, optionally including super categories
    for i in ids:
        name = categories[i]["name"]
        if use_super_categories and "supercategory" in categories[i]:
            name = categories[i]["supercategory"] + ":" + name
        new_categories[i] = name

    # Final mapping: id => category name
    categories = new_categories

    # Create mapping: image id => image metadata
    images = {item["id"]: item for item in coco["images"]}

    logger.info(
        f'Found {len(categories)} categories, {len(images)} images and {len(coco["annotations"])} annotations'
    )

    # Flags for tracking annotation types and generating appropriate labeling config
    segmentation = bbox = keypoints = rle = False
    segmentation_once = bbox_once = keypoints_once = rle_once = False
    
    # Generate appropriate from_name tags for different annotation types
    rectangles_from_name, keypoints_from_name = (
        from_name + "_rectangles",
        from_name + "_keypoints",
    )
    segmentation_from_name = from_name + "polygons"
    tags = {}

    # Create initial tasks for each image
    for image in coco["images"]:
        image_id, image_file_name = image["id"], image["file_name"]
        tasks[image_id] = new_task(out_type, image_root_url, image_file_name)

    # Process all annotations
    for i, annotation in enumerate(coco["annotations"]):
        # Detect which annotation types are present
        segmentation |= "segmentation" in annotation
        bbox |= "bbox" in annotation
        keypoints |= "keypoints" in annotation
        rle |= (
            annotation.get("iscrowd") == 1
        )  # 0 - polygons are in segmentation, otherwise RLE

        # Log warnings and build tag configuration
        if rle and not rle_once:  # RLE not supported yet
            logger.error("RLE in segmentation is not yet supported in COCO")
            rle_once = True
        if keypoints and not keypoints_once:
            logger.warning("Keypoints are partially supported without skeletons")
            tags.update({keypoints_from_name: "KeyPointLabels"})
            keypoints_once = True
        if segmentation and not segmentation_once:  # Experimental support
            logger.warning("Segmentation in COCO is experimental")
            tags.update({segmentation_from_name: "PolygonLabels"})
            segmentation_once = True
        if bbox and not bbox_once:
            tags.update({rectangles_from_name: "RectangleLabels"})
            bbox_once = True

        # Get image metadata for coordinate conversion
        image_id = annotation["image_id"]
        image = images[image_id]
        image_file_name, image_width, image_height = (
            image["file_name"],
            image["width"],
            image["height"],
        )

        task = tasks[image_id]

        # Convert bounding box annotations
        if "bbox" in annotation:
            item = create_bbox(
                annotation,
                categories,
                rectangles_from_name,
                image_height,
                image_width,
                to_name,
            )
            task[out_type][0]["result"].append(item)

        # Convert segmentation annotations (polygons)
        if "segmentation" in annotation and len(annotation["segmentation"]):
            for single_segmentation in annotation["segmentation"]:
                item = create_segmentation(
                    annotation["category_id"],
                    single_segmentation,
                    categories,
                    segmentation_from_name,
                    image_height,
                    image_width,
                    to_name,
                )
                task[out_type][0]["result"].append(item)

        # Convert keypoint annotations
        if "keypoints" in annotation:
            items = create_keypoints(
                annotation,
                categories,
                keypoints_from_name,
                to_name,
                image_height,
                image_width,
                point_width,
            )
            task[out_type][0]["result"] += items

        tasks[image_id] = task

    # Generate and save labeling configuration
    label_config_file = out_file.replace(".json", "") + ".label_config.xml"
    generate_label_config(categories, tags, to_name, from_name, label_config_file)

    # Save converted tasks to output file
    if len(tasks) > 0:
        tasks = [tasks[key] for key in sorted(tasks.keys())]
        logger.info("Saving Label Studio JSON to %s", out_file)
        with open(out_file, "w") as out:
            json.dump(tasks, out)

        # Print helpful instructions for user
        print(
            "\n"
            f"  1. Create a new project in Label Studio\n"
            f'  2. Use Labeling Config from "{label_config_file}"\n'
            f"  3. Setup serving for images [e.g. you can use Local Storage (or others):\n"
            f"     https://labelstud.io/guide/storage.html#Local-storage]\n"
            f'  4. Import "{out_file}" to the project\n'
        )
    else:
        logger.error("No labels converted")


def add_parser(subparsers):
    """Add COCO converter arguments to command line parser.
    
    Args:
        subparsers: Argparse subparsers object to add the COCO parser to
    """
    coco = subparsers.add_parser("coco")

    coco.add_argument(
        "-i",
        "--input",
        dest="input",
        required=True,
        help="input COCO json file",
        action=ExpandFullPath,
    )
    coco.add_argument(
        "-o",
        "--output",
        dest="output",
        help="output file with Label Studio JSON tasks",
        default="output.json",
        action=ExpandFullPath,
    )
    coco.add_argument(
        "--to-name",
        dest="to_name",
        help="object name from Label Studio labeling config",
        default="image",
    )
    coco.add_argument(
        "--from-name",
        dest="from_name",
        help="control tag name from Label Studio labeling config",
        default="label",
    )
    coco.add_argument(
        "--out-type",
        dest="out_type",
        help='annotation type - "annotations" or "predictions"',
        default="annotations",
    )
    coco.add_argument(
        "--image-root-url",
        dest="image_root_url",
        help="root URL path where images will be hosted, e.g.: http://example.com/images",
        default="/data/local-files/?d=",
    )
    coco.add_argument(
        "--point-width",
        dest="point_width",
        help="key point width (size)",
        default=1.0,
        type=float,
    )
