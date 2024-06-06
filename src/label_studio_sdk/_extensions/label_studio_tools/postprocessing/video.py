from copy import deepcopy
from operator import itemgetter

from label_studio_sdk._extensions.label_studio_tools.core.label_config import (
    _VIDEO_TRACKING_TAGS,
)


def extract_key_frames(results):
    """
    Extract frames from key frames from video annotation results
    :param results: Annotation results
    :return: Frames in LS format
    """
    final_results = []
    for result in results:
        temp = deepcopy(result)
        if result["type"].lower() not in _VIDEO_TRACKING_TAGS:
            final_results.append(result)
            continue
        sequence = result["value"]["sequence"]
        if len(sequence) < 1:
            continue
        sequence = sorted(sequence, key=lambda d: d["frame"])
        exclude_first = False
        for i in range(len(sequence)):
            frame_a = sequence[i]
            frame_b = {} if i == len(sequence) - 1 else sequence[i + 1]
            temp["value"]["sequence"].extend(
                _construct_result_from_frames(
                    frame1=frame_a,
                    frame2=frame_b,
                    frameCount=result["value"].get("framesCount", 0),
                    duration=result["value"].get("duration", 0),
                    exclude_first=exclude_first,
                )
            )
            exclude_first = frame_a["enabled"]
        temp["value"]["sequence"] = sorted(
            temp["value"]["sequence"], key=itemgetter("frame")
        )
        final_results.append(temp)
    return final_results


def _construct_result_from_frames(
    frame1, frame2, frameCount=0, duration=0, exclude_first=True
):
    """
    Construct frames between 2 keyframes
    :param frame1: First frame in sequence
    :param frame2: Next frame in sequence
    :param frameCount: Total frame count in the video
    :param duration: Total duration of the video
    :param exclude_first: Exclude first result to deduplicate results
    :return: List of frames
    """
    final_results = []
    if not frame1["enabled"]:
        return []
    if len(frame2) > 0:
        if frame1["frame"] > frame2["frame"]:
            return []
        frame_count = frame2["frame"] - frame1["frame"] + 1
    else:
        frame_count = frameCount - frame1["frame"] + 1
    start_i = 1 if exclude_first else 0
    for i in range(start_i, frame_count):
        frame_number = i + frame1["frame"]
        delta = i / max(1, (frame_count - 1))
        deltas = {}
        for v in ["x", "y", "rotation", "width", "height", "time"]:
            deltas[v] = (
                0
                if (frame1[v] == frame2.get(v) or not frame2)
                else (frame2.get(v, 0) - frame1[v]) * delta
            )
        result = deepcopy(frame1)
        result.update(
            {
                "x": frame1["x"] + deltas["x"],
                "y": frame1["y"] + deltas["y"],
                "width": frame1["width"] + deltas["width"],
                "height": frame1["height"] + deltas["height"],
                "rotation": frame1["rotation"] + deltas["rotation"],
                "frame": frame_number,
                "time": round(frame1["time"] + deltas["time"], 2),
            }
        )
        if frame_number not in [frame1.get("frame"), frame2.get("frame")]:
            result["auto"] = True
            if deltas["time"] == 0 and duration > 0:
                result["time"] = round(
                    frame1["time"] + delta * (duration - frame1["time"]), 2
                )
            final_results.append(result)
    return final_results
