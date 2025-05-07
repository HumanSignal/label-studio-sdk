import logging
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
            cls_name = item['rectanglelabels'][0]
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
            label_name = item['keypointlabels'][0]
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
