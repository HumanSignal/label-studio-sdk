import time
import json
from datetime import datetime, timedelta, timezone
import numpy as np
import rasterio
from shapely.geometry import Polygon
from label_studio_sdk.client import LabelStudio
from label_studio_sdk import Client, Project
from label_studio_sdk.data_manager import Filters, Column, Operator, Type


def _filter_tasks(last_poll_time: datetime):
    """
    Build filters for client to poll for tasks
    """
    filters = Filters.create(
        "and",  # need 'and' instead of 'or' evfen if we had only 1 filter
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


def poll_for_completed_tasks_new(
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
            # can't use fields='all' because of maybe-nonexistent task fields
            fields="all",
            # fields=['image', 'annotations'],
        )
        yield from tasks
        time.sleep(freq_seconds)


def poll_for_completed_tasks_old(project: Project, freq_seconds: int) -> list:
    """
    Every n seconds, yield all tasks that have been updated since the last poll.
    Uses label_studio_sdk < 1.0.0
    """
    while True:
        print("polling")
        last_poll_time = datetime.now(timezone.utc) - timedelta(seconds=freq_seconds)
        filters = _filter_tasks(last_poll_time)
        tasks = project.get_tasks(filters=filters)
        yield from tasks
        time.sleep(freq_seconds)


def calculate_distances(source_img_path, annot):
    """
    Calculate properties of the polygon annotation in geographic coordinates given by the georeferenced TIFF source image the polygon was drawn on.
    """
    try:
        width = annot["result"][0]["original_width"]
        height = annot["result"][0]["original_height"]
        points = annot["result"][0]["value"]["points"]

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


def _bugfix_task_columns_old(project):
    """
    Using the old SDK client, due to our workaround providing extra task columns and uploading single images instead of full task objects, PATCH /api/tasks/<id> requests will not complete correctly until the task has those columns populated.
    """
    # look for tasks with missing values
    old_tasks = project.get_tasks()
    default_values = {
        "perimeter_m": 0,
        "area_m2": 0,
        "major_axis_m": 0,
        "minor_axis_m": 0,
    }
    tasks_to_recreate = []
    for task in old_tasks:
        for k in default_values:
            if k not in task["data"]:
                tasks_to_recreate.append(task)
                break
    # instead of updating tasks, need to delete and recreate tasks
    if tasks_to_recreate:
        _ = project.delete_tasks(task_ids=[task["id"] for task in tasks_to_recreate])
        new_task_data = [
            {
                "data": {
                    **default_values,
                    "image": task["data"]["image"],
                }
            }
            for task in tasks_to_recreate
        ]
        _ = project.import_tasks(new_task_data)


if __name__ == "__main__":
    url = "http://localhost:8080"
    api_key = "cca56ca8fc0d511a87bbc63f5857b9a7a8f14c23"
    project_id = 5

    # poll frequency
    freq_seconds = 1

    # new sdk is waiting on: https://github.com/HumanSignal/label-studio/pull/6012
    use_new_sdk = False

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

    if use_new_sdk:
        # new SDK client (version >= 1.0.0)
        ls = LabelStudio(base_url=url, api_key=api_key)
        for task in poll_for_completed_tasks_new(ls, project_id, freq_seconds):
            # assume that the most recent annotation is the one that was updated
            # can check annot['updated_at'] and annot['created_at'] to confirm
            annot = task.annotations[0]
            source_image_path = _lookup_source_image_path(task.data["image"])
            distances = calculate_distances(source_image_path, annot)
            new_data = task.data
            new_data.update(distances)
            ls.tasks.update(id=task.id, data=new_data)
            print("updated task", task.id)
    else:
        # old SDK client (version < 1.0.0)
        client = Client(url=url, api_key=api_key)
        client.check_connection()
        project = client.get_project(project_id)

        _bugfix_task_columns_old(project)

        for task in poll_for_completed_tasks_old(project, freq_seconds):
            # assume that the most recent annotation is the one that was updated
            # can check annot['updated_at'] and annot['created_at'] to confirm
            annot = task["annotations"][0]
            source_image_path = _lookup_source_image_path(task["data"]["image"])
            distances = calculate_distances(source_image_path, annot)
            new_data = task["data"]
            new_data.update(distances)
            project.update_task(task_id=task["id"], data=new_data)
            print("updated task", task["id"])
