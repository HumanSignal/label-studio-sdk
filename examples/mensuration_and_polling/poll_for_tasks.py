import time
import json
from datetime import datetime, timedelta, timezone
import rasterio
from shapely.geometry import Polygon
from label_studio_sdk.client import LabelStudio
from label_studio_sdk import Client, Project
from label_studio_sdk.data_manager import Filters, Column, Operator, Type


def poll_for_completed_tasks_new(
    ls: LabelStudio, project_id: int, freq_sec: int
) -> list:
    while True:
        last_poll_time = datetime.now(timezone.utc) - timedelta(seconds=freq_sec)
        filters = Filters.create(
            "and",  # need 'and' instead of 'or', even though this is only one filter
            [
                Filters.item(
                    Column.updated_at,
                    Operator.GREATER_OR_EQUAL,
                    Type.Datetime,
                    Filters.value(last_poll_time),
                )
            ],
        )
        tasks = ls.tasks.list(
            project=project_id,
            query=json.dumps({"filters": filters}),
            fields="all",
        )
        yield from tasks
        time.sleep(freq_seconds)


def poll_for_completed_tasks_old(project: Project, freq_seconds: int) -> list:
    while True:
        print("polling")
        last_poll_time = datetime.now(timezone.utc) - timedelta(seconds=freq_seconds)
        filters = Filters.create(
            "and",  # need 'and' instead of 'or', even though this is only one filter
            [
                Filters.item(
                    Column.updated_at,
                    Operator.GREATER_OR_EQUAL,
                    Type.Datetime,
                    Filters.value(last_poll_time),
                )
            ],
        )
        tasks = project.get_tasks(filters=filters)
        yield from tasks
        time.sleep(freq_seconds)


def perimeter_and_area(source_img_path, annot):
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
    area_m = poly.area

    perimeter_km = perimeter_m / 1e3
    area_km = area_m / 1e6

    return perimeter_km, area_km


if __name__ == "__main__":
    url = "http://localhost:8080"
    api_key = "cca56ca8fc0d511a87bbc63f5857b9a7a8f14c23"
    project_id = 4
    freq_seconds = 1
    use_new_sdk = True
    if use_new_sdk:
        # new SDK client (version >= 1.0.0)
        ls = LabelStudio(base_url=url, api_key=api_key)
        for task in poll_for_completed_tasks_new(ls, project_id, freq_seconds):
            # assume that the most recent annotation is the one that was updated
            # can check annot['updated_at'] to confirm
            annot = task.annotations[0]
            # currently, we only have one source image, but in general need to build a mapping between the task image (PNG) and the source image (TIFF)
            perimeter, area = perimeter_and_area(
                "data/e9b9661bcbd97b67f45364aafd82f9d6/response.tiff", annot
            )
            ls.tasks.update(
                id=task.id,
                data={**task.data, "label_perimeter": perimeter, "label_area": area},
            )
            print("updated task", task.id)
    else:
        # old SDK client (version < 1.0.0)
        client = Client(url=url, api_key=api_key)
        client.check_connection()
        project = client.get_project(project_id)
        for task in poll_for_completed_tasks_old(project, freq_seconds):
            # assume that the most recent annotation is the one that was updated
            # can check annot['updated_at'] to confirm
            annot = task["annotations"][0]
            # currently, we only have one source image, but in general need to build a mapping between the task image (PNG) and the source image (TIFF)
            perimeter, area = perimeter_and_area(
                "data/e9b9661bcbd97b67f45364aafd82f9d6/response.tiff", annot
            )
            project.update_task(
                task_id=task["id"],
                data={**task["data"], "label_perimeter": perimeter, "label_area": area},
            )
            print("updated task", task["id"])
