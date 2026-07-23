import os
import csv
import time
import logging
import ujson as json

from copy import deepcopy, copy

from label_studio_sdk.converter.utils import ensure_dir, get_annotator, prettify_result


logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


def convert(item_iterator, input_data, output_dir, **kwargs):
    start_time = time.time()
    logger.debug("Convert CSV started")
    if str(output_dir).endswith(".csv"):
        output_file = output_dir
        parent_dir = os.path.dirname(str(output_file))
        if parent_dir:
            ensure_dir(parent_dir)
    else:
        ensure_dir(output_dir)
        output_file = os.path.join(output_dir, "result.csv")

    # these keys are always presented
    keys = {"annotator", "annotation_id", "created_at", "updated_at", "lead_time"}

    # Discover colliding keys across the whole export so every row uses the same columns.
    input_keys = set()
    output_keys = set()
    logger.debug("Discover global input/output keys for CSV ...")
    for item in item_iterator(input_data):
        input_keys.update(item["input"].keys())
        output_keys.update(item["output"].keys())
    colliding_keys = input_keys & output_keys

    # First pass: column names (requires headers before writing rows).
    logger.debug("Prepare column names for CSV ...")
    for item in item_iterator(input_data):
        record = prepare_annotation_keys(item, colliding_keys)
        keys.update(record)

    # Second pass: write records to csv.
    logger.debug(
        f"Prepare done in {time.time()-start_time:0.2f} sec. Write CSV rows now ..."
    )
    with open(output_file, "w", encoding="utf8") as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=sorted(list(keys)),
            quoting=csv.QUOTE_NONNUMERIC,
            delimiter=kwargs["sep"],
        )
        writer.writeheader()

        for item in item_iterator(input_data):
            record = prepare_annotation(item, colliding_keys)
            writer.writerow(record)

    logger.debug(f"CSV conversion finished in {time.time()-start_time:0.2f} sec")


def generate_chat_transcript(pretty_value):
    """Generate a human-readable transcript from Chat messages.
    
    Args:
        pretty_value: List of message objects, each containing 'role' and 'content' keys.
    
    Returns:
        str: Newline-separated transcript with format "role: content" for each message.
    """
    transcript_lines = []
    if isinstance(pretty_value, list):
        for message in pretty_value:
            if not isinstance(message, dict):
                continue
            role = str(message.get("role", ""))
            content = str(message.get("content", ""))
            if role:
                transcript_lines.append(
                    f"{role}: {content}" if content else f"{role}:"
                )
            else:
                transcript_lines.append(content)
    return "\n".join(transcript_lines)


def _colliding_keys(item):
    return set(item["input"].keys()) & set(item["output"].keys())


def _input_column_name(name, colliding_keys):
    # Keep annotation columns as the bare control-tag name for backward
    # compatibility; only rename colliding task.data keys.
    if name in colliding_keys:
        return f"_data_{name}"
    return name


def prepare_annotation(item, colliding_keys=None):
    record = {}
    if colliding_keys is None:
        colliding_keys = _colliding_keys(item)
    if item.get("id") is not None:
        record["id"] = item["id"]

    for name, value in item["output"].items():
        # Annotation output keeps the original key (e.g. "text") for BC.
        pretty_value = prettify_result(value)
        record[name] = (
            pretty_value
            if isinstance(pretty_value, str)
            else json.dumps(pretty_value, ensure_ascii=False)
        )

        if any(
            isinstance(result, dict)
            and result.get("type") in ("Chat", "chatmessage")
            for result in value
        ):
            record[f"{name}_transcript"] = generate_chat_transcript(pretty_value)

    for name, value in item["input"].items():
        column_name = _input_column_name(name, colliding_keys)
        if isinstance(value, dict) or isinstance(value, list):
            # flat dicts and arrays from task.data to json strings
            record[column_name] = json.dumps(value, ensure_ascii=False)
        else:
            record[column_name] = value

    record["annotator"] = get_annotator(item)
    record["annotation_id"] = item["annotation_id"]
    record["created_at"] = item["created_at"]
    record["updated_at"] = item["updated_at"]
    record["lead_time"] = item["lead_time"]

    if "agreement" in item:
        record["agreement"] = item["agreement"]

    if "history" in item and item["history"]:
        record["history"] = json.dumps(item["history"], ensure_ascii=False)

    return record


def prepare_annotation_keys(item, colliding_keys=None):
    if colliding_keys is None:
        colliding_keys = _colliding_keys(item)
    record = {_input_column_name(name, colliding_keys) for name in item["input"].keys()}
    if item.get("id") is not None:
        record.add("id")

    for name, value in item["output"].items():
        record.add(name)
        if any(
            isinstance(result, dict)
            and result.get("type") in ("Chat", "chatmessage")
            for result in value
        ):
            record.add(f"{name}_transcript")

    if "agreement" in item:
        record.add("agreement")

    if "history" in item and item["history"]:
        record.add("history")

    return record
