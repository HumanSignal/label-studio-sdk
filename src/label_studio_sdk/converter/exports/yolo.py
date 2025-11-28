import logging
import os
from label_studio_sdk.converter.utils import convert_annotation_to_yolo, convert_annotation_to_yolo_obb
from label_studio_sdk.converter.keypoints import build_kp_order

logger = logging.getLogger(__name__)

def process_keypoints_for_yolo(labels, label_path,
                               category_name_to_id, categories,
                               is_obb, kp_order):
    class_map = {c['name']: c['id'] for c in categories}

    rectangles = {}
    for item in labels:
        if item['type'].lower() == 'rectanglelabels':
            bbox_id = item['id']
            # Skip if there are no labels
            rect_labels = item.get('rectanglelabels') or []
            if not rect_labels:
                continue
            cls_name = rect_labels[0]
            cls_idx = class_map.get(cls_name)
            if cls_idx is None:
                continue

            x      = item['x'] / 100.0
            y      = item['y'] / 100.0
            width  = item['width']  / 100.0
            height = item['height'] / 100.0
            x_c    = x + width  / 2.0
            y_c    = y + height / 2.0

            rectangles[bbox_id] = {
                'class_idx': cls_idx,
                'x_center':  x_c,
                'y_center':  y_c,
                'width':     width,
                'height':    height,
                'kp_dict':   {}
            }

    for item in labels:
        if item['type'].lower() == 'keypointlabels':
            parent_id = item.get('parentID')
            if parent_id not in rectangles:
                continue
            kp_labels = item.get('keypointlabels') or []
            if not kp_labels:
                continue
            label_name = kp_labels[0]
            kp_x = item['x'] / 100.0
            kp_y = item['y'] / 100.0
            rectangles[parent_id]['kp_dict'][label_name] = (kp_x, kp_y, 2)  # 2 = visible

    lines = []
    for rect in rectangles.values():
        base = [
            rect['class_idx'],
            rect['x_center'],
            rect['y_center'],
            rect['width'],
            rect['height']
        ]
        keypoints = []
        for k in kp_order:
            keypoints.extend(rect['kp_dict'].get(k, (0.0, 0.0, 0)))
        line = ' '.join(map(str, base + keypoints))
        lines.append(line)

    with open(label_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def process_and_save_yolo_annotations(labels, label_path, category_name_to_id, categories, is_obb, is_keypoints, label_config):
    if is_keypoints:
        kp_order = build_kp_order(label_config)
        process_keypoints_for_yolo(labels, label_path, category_name_to_id, categories, is_obb, kp_order)
        return categories, category_name_to_id

    # Stream annotations directly to a temporary file to avoid
    # accumulating them in memory and to preserve atomic writes.
    tmp_path = f"{label_path}.tmp"

    try:
        with open(tmp_path, "w") as f:
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
                            annotation_values = [category_id, x1, y1, x2, y2, x3, y3, x4, y4]

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
                            annotation_values = [category_id, x, y, w, h]

                    elif "polygonlabels" in label or "polygon" in label:
                        if not ('points' in label):
                            continue
                        points_abs = [(x / 100, y / 100) for x, y in label["points"]]
                        annotation_values = (
                            [category_id]
                            + [coord for point in points_abs for coord in point]
                        )
                    else:
                        raise ValueError(f"Unknown label type {label}")

                    # Write the annotation line immediately
                    for idx, val in enumerate(annotation_values):
                        if idx == len(annotation_values) - 1:
                            f.write(f"{val}\n")
                        else:
                            f.write(f"{val} ")

        # Replace the target file atomically after successful write
        os.replace(tmp_path, label_path)

    finally:
        # Clean up the temp file in case of exceptions before replace
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass

    return categories, category_name_to_id
