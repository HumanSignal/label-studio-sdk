import time
import json
from datetime import datetime, timedelta, timezone
import numpy as np
import rasterio
from shapely.geometry import Polygon
from label_studio_sdk.client import LabelStudio
import os
from label_studio_sdk.data_manager import Filters, Column, Operator, Type


def _filter_tasks(last_poll_time: datetime):
    """
    Build filters for client to poll for tasks
    """
    filters = Filters.create(
        "and",  # need 'and' instead of 'or' even if we had only 1 filter
        [
            # task updated since the last poll
            Filters.item(
                Column.updated_at,
                Operator.GREATER_OR_EQUAL,
                Type.Datetime,
                Filters.value(last_poll_time),
            ),
            # task has at least one annotation
            Filters.item(
                Column.total_annotations,
                Operator.GREATER_OR_EQUAL,
                Type.Number,
                Filters.value(1),
            ),
        ],
    )
    return filters


def poll_for_completed_tasks(
    ls: LabelStudio, project_id: int, freq_sec: int
) -> list:
    """
    Every n seconds, yield all tasks that have been updated since the last poll.
    Uses label_studio_sdk >= 1.0.0
    """
    while True:
        print("polling")
        last_poll_time = datetime.now(timezone.utc) - timedelta(seconds=freq_sec)
        filters = _filter_tasks(last_poll_time)
        tasks = ls.tasks.list(
            project=project_id,
            query=json.dumps({"filters": filters}),
            only_annotated=True,
            resolve_uri=False,  # to lookup file name in cloud storage
        )
        yield from tasks
        time.sleep(freq_sec)


def calculate_distances(source_img_path, annot):
    """
    Calculate properties of the polygon annotation in geographic coordinates given by the georeferenced TIFF source image the polygon was drawn on.
    """
    try:
        width = annot.result[0]["original_width"]
        height = annot.result[0]["original_height"]
        points = annot.result[0]["value"]["points"]

        # convert relative coordinates to pixel coordinates
        points_pxl = [(x / 100 * width, y / 100 * height) for x, y in points]

        with rasterio.open(source_img_path) as src:
            # convert pixel coordinates to geographic coordinates
            points_geo = [src.transform * (x, y) for x, y in points_pxl]

        # use Shapely to create a polygon
        poly = Polygon(points_geo)

        # assume the image CRS is in meters
        perimeter_m = poly.length
        area_m2 = poly.area

        oriented_bbox = poly.minimum_rotated_rectangle
        coords = np.array(oriented_bbox.exterior.coords)
        side_lengths = ((coords[1:] - coords[:-1]) ** 2).sum(axis=1) ** 0.5
        major_axis_m = max(side_lengths)
        minor_axis_m = min(side_lengths)

        return {
            "perimeter_m": perimeter_m,
            "area_m2": area_m2,
            "major_axis_m": major_axis_m,
            "minor_axis_m": minor_axis_m,
        }
    # guard against incomplete polygons
    except (ValueError, IndexError):
        print("no valid polygon in annotation")
        return {
            "perimeter_m": 0,
            "area_m2": 0,
            "major_axis_m": 0,
            "minor_axis_m": 0,
        }


if __name__ == "__main__":
    url = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080")
    api_key = os.getenv("LABEL_STUDIO_API_KEY")
    project_id = int(os.getenv("LABEL_STUDIO_PROJECT_ID", "1"))

    # poll frequency
    freq_seconds = 1

    # Use new SDK path only
    use_new_sdk = True

    def _lookup_source_image_path(annotated_image_path: str) -> str:
        """
        In a real project this lookup should be another column in the task. For ease of demoing the project by simply uploading images, it's a hacky function.
        """
        if annotated_image_path.endswith("response.png"):
            return "data/e9b9661bcbd97b67f45364aafd82f9d6/response.tiff"
        elif annotated_image_path.endswith("cropped.png"):
            return "data/oam/666dbadcf1cf8e0001fb2f51_cropped.tif"
        else:
            print("unknown annotated image path ", annotated_image_path)
            return annotated_image_path

    ls = LabelStudio(base_url=url, api_key=api_key)
    for task in poll_for_completed_tasks(ls, project_id, freq_seconds):
        # assume that the most recent annotation is the one that was updated
        # can check annot.updated_at and annot.created_at to confirm
        annot = ls.annotations.list(id=task.id)[0]
        source_image_path = _lookup_source_image_path(task.data["image"])
        distances = calculate_distances(source_image_path, annot)
        new_data = task.data
        new_data.update(distances)
        ls.tasks.update(id=task.id, data=new_data)
        print("updated task", task.id)
