import logging
from label_studio_sdk.converter.utils import convert_annotation_to_yolo, convert_annotation_to_yolo_obb

logger = logging.getLogger(__name__)


def process_keypoints_for_yolo(labels, label_path, category_name_to_id, categories, is_obb):
    class_map = {category['name']: category['id'] for category in categories}

    # Map rectangle IDs to their data
    rectangles = {}
    for result in labels:
        if result['type'].lower() == 'rectanglelabels':
            bbox = result
            bbox_id = bbox['id']
            bbox_label = bbox['rectanglelabels'][0]
            class_idx = class_map.get(bbox_label)
            if class_idx is None:
                continue  # Skip unknown classes

            x = bbox['x'] / 100
            y = bbox['y'] / 100
            width = bbox['original_width'] / 100
            height = bbox['original_height'] / 100
            # Convert from top-left corner to center coordinates
            x_center = x + width / 2
            y_center = y + height / 2

            rectangles[bbox_id] = {
                'class_idx': class_idx,
                'x_center': x_center,
                'y_center': y_center,
                'width': width,
                'height': height,
                'keypoints': []
            }

    # Collect keypoints associated with each rectangle
    for kp_result in labels:
        if kp_result['type'].lower() == 'keypointlabels':
            parent_id = kp_result.get('parentID')
            if parent_id in rectangles:
                kp_x = kp_result['x'] / 100
                kp_y = kp_result['y'] / 100
                visibility = 2  # Assuming keypoints are visible
                rectangles[parent_id]['keypoints'].extend([kp_x, kp_y, visibility])

    # Prepare YOLO formatted lines
    lines = []
    for rect in rectangles.values():
        obj = [
            rect['class_idx'],
            rect['x_center'],
            rect['y_center'],
            rect['width'],
            rect['height']
        ] + rect['keypoints']
        line = ' '.join(map(str, obj))
        lines.append(line)

    # Write to YOLO format file
    with open(label_path, 'w') as f:
        for line in lines:
            f.write(line + '\n')



def process_and_save_yolo_annotations(labels, label_path, category_name_to_id, categories, is_obb, is_keypoints):
    if is_keypoints:
        process_keypoints_for_yolo(labels, label_path, category_name_to_id, categories, is_obb)
        return categories, category_name_to_id

    annotations = []
    for label in labels:
        category_name = None
        category_names = []  # considering multi-label
        for key in ["rectanglelabels", "polygonlabels", "labels"]:
            if key in label and len(label[key]) > 0:
                # change to save multi-label
                for category_name in label[key]:
                    category_names.append(category_name)

        if len(category_names) == 0:
            logger.debug(
                "Unknown label type or labels are empty: " + str(label)
            )
            continue

        for category_name in category_names:
            if category_name not in category_name_to_id:
                category_id = len(categories)
                category_name_to_id[category_name] = category_id
                categories.append({"id": category_id, "name": category_name})
            category_id = category_name_to_id[category_name]

            if (
                "rectanglelabels" in label
                or "rectangle" in label
                or "labels" in label
            ):
                # yolo obb
                if is_obb:
                    obb_annotation = convert_annotation_to_yolo_obb(label)
                    if obb_annotation is None:
                        continue

                    top_left, top_right, bottom_right, bottom_left = (
                        obb_annotation
                    )
                    x1, y1 = top_left
                    x2, y2 = top_right
                    x3, y3 = bottom_right
                    x4, y4 = bottom_left
                    annotations.append(
                        [category_id, x1, y1, x2, y2, x3, y3, x4, y4]
                    )

                # simple yolo
                else:
                    annotation = convert_annotation_to_yolo(label)
                    if annotation is None:
                        continue

                    (
                        x,
                        y,
                        w,
                        h,
                    ) = annotation
                    annotations.append([category_id, x, y, w, h])

            elif "polygonlabels" in label or "polygon" in label:
                if not ('points' in label):
                    continue
                points_abs = [(x / 100, y / 100) for x, y in label["points"]]
                annotations.append(
                    [category_id]
                    + [coord for point in points_abs for coord in point]
                )
            else:
                raise ValueError(f"Unknown label type {label}")
    with open(label_path, "w") as f:
        for annotation in annotations:
            for idx, l in enumerate(annotation):
                if idx == len(annotation) - 1:
                    f.write(f"{l}\n")
                else:
                    f.write(f"{l} ")

    return categories, category_name_to_id
