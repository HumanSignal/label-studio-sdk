import os
import json


def keypoints_in_label_config(label_config):
    """
    Check if the label config contains keypoints.
    :param label_config: Label config in JSON format.
    :return: True if keypoints are present, False otherwise.
    """
    for cfg in label_config.values():
        if cfg.get("type") == "KeyPointLabels":
            return True
    return False


def update_categories_for_keypoints(categories, category_name_to_id, label_config):
    keypoint_labels = []
    for cfg in label_config.values():
        if cfg.get("type") == "KeyPointLabels":
            keypoint_labels.extend(cfg.get("labels", []))
    keypoint_labels = list(dict.fromkeys(keypoint_labels))

    non_kp = [cat.copy() for cat in categories if cat["name"] not in keypoint_labels]

    new_categories = []
    new_mapping = {}
    next_id = 0
    for cat in non_kp:
        cat["id"] = next_id
        new_categories.append(cat)
        new_mapping[cat["name"]] = next_id
        next_id += 1

    if keypoint_labels:
        merged_id = next_id
        merged_category = {
            "id": merged_id,
            "name": "default",
            "supercategory": "default",
            "keypoints": keypoint_labels,
            "skeleton": []
        }
        new_categories.append(merged_category)
        for kp_name in keypoint_labels:
            new_mapping[kp_name] = merged_id

    return new_categories, new_mapping


def build_kp_order(label_config):
    kp_block = {}

    for tag in label_config.values():
        if tag.get("type") == "KeyPointLabels":
            kp_block.update(tag.get("labels_attrs", {}))

    pairs, used = [], set()

    for name, attrs in kp_block.items():
        try:
            idx = int(attrs.get("model_index"))
        except (TypeError, ValueError):
            continue
        if idx in used:
            continue
        pairs.append((idx, name))
        used.add(idx)

    pairs.sort(key=lambda p: p[0])
    result = [name for _, name in pairs]
    return result


def get_bbox_coco(keypoints, kp_order):
    xs = [keypoints[3*i] for i in range(len(kp_order)) if keypoints[3*i + 2] > 0]
    ys = [keypoints[3*i + 1] for i in range(len(kp_order)) if keypoints[3*i + 2] > 0]
    if xs and ys:
        x_min = min(xs)
        y_min = min(ys)
        x_max = max(xs)
        y_max = max(ys)
        width = x_max - x_min
        height = y_max - y_min
        bbox = [x_min, y_min, width, height]
    else:
        bbox = [0, 0, 0, 0]
    return bbox


def process_keypoints_for_coco(keypoint_labels, kp_order, annotation_id, image_id, category_name_to_id):
    if not kp_order:
        raise ValueError(
            "No keypoint order found. Please ensure that KeyPointLabels in your label config "
            "have 'model_index' attributes defined. For example:\n"
            "<KeyPointLabels name=\"keypoints\" toName=\"image\">\n"
            "  <Label value=\"eye\" model_index=\"0\"/>\n"
            "  <Label value=\"nose\" model_index=\"1\"/>\n"
            "</KeyPointLabels>"
        )

    keypoints = [0] * (len(kp_order) * 3)

    for kp in keypoint_labels:
        width, height = kp["original_width"], kp["original_height"]
        x, y = kp['x'] / 100 * width, kp['y'] / 100 * height
        labels = kp.get('keypointlabels', [])
        v = 2 if labels else 0
        for label in labels:
            if label in kp_order:
                idx = kp_order.index(label)
                keypoints[3 * idx] = int(round(x))
                keypoints[3 * idx + 1] = int(round(y))
                keypoints[3 * idx + 2] = v

    num_keypoints = sum(1 for i in range(len(kp_order)) if keypoints[3*i + 2] > 0)

    bbox = get_bbox_coco(keypoints, kp_order)

    category_id = category_name_to_id.get(kp_order[0], 0)
    annotation = {
        'id': annotation_id,
        'image_id': image_id,
        'category_id': category_id,
        'keypoints': keypoints,
        'num_keypoints': num_keypoints,
        'bbox': bbox,
        'iscrowd': 0
    }
    return annotation


def get_yolo_categories_for_keypoints(label_config):
    # Get all keypoint labels from the label config
    keypoint_labels = []
    for cfg in label_config.values():
        if cfg.get("type") == "KeyPointLabels":
            keypoint_labels.extend(cfg.get("labels", []))
    keypoint_labels = list(dict.fromkeys(keypoint_labels))  # Remove duplicates

    # Get all rectangle labels from the label config
    rectangle_labels = []
    for cfg in label_config.values():
        if cfg.get("type") == "RectangleLabels":
            rectangle_labels.extend(cfg.get("labels", []))
    rectangle_labels = list(dict.fromkeys(rectangle_labels))  # Remove duplicates

    # Create categories for each rectangle label
    categories = []
    category_name_to_id = {}

    for i, label in enumerate(rectangle_labels):
        categories.append({"id": i, "name": label, "keypoints": keypoint_labels})
        category_name_to_id[label] = i

    return categories, category_name_to_id
