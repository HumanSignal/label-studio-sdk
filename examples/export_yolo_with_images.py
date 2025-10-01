"""
This is a Python script that exports labeled data from a Label Studio project 
and converts it into the YOLO format, including downloading associated images.

## 1. What It Does and How
The script performs the following steps:

1. **Connects to Label Studio:** It uses the Label Studio SDK to connect 
to a Label Studio instance using the provided URL and API key.
2. **Retrieves the Project:** Fetches the specified project by its ID.
3. **Creates an Export Snapshot:** Generates a snapshot of the project's annotations for export.
4. **Downloads Annotations:** Downloads the annotations in JSON format.
5. **Converts Annotations to YOLO Format:** Utilizes the Label Studio Converter 
to transform the annotations into the YOLO format suitable for object detection tasks.
6. **Downloads Associated Images:** Iterates over the exported tasks and downloads the corresponding images, 
implementing retry logic with exponential backoff to handle rate limits or transient network issues.

## 2. How to Use It

1. **Install Dependencies:** Ensure you have Python installed along with the required packages:
   ```bash
   pip install git+https://github.com/heartexlabs/label-studio-sdk.git tqdm
   ```

2. **Set Up Credentials:** Provide your LABEL_STUDIO_URL, LABEL_STUDIO_API_KEY, and PROJECT_ID either 
by modifying the script variables or via command-line arguments.

3. **Run the Script:** Execute the script from the terminal:
   ```bash
   python script.py --url 'https://app.humansignal.com' --api-key 'your-api-key' --project-id 12345
   ```
   Replace `'your-api-key'` and `12345` with your actual API key and project ID.

4. **Output:** The script will create an `output_yolo` directory containing:
   - YOLO-formatted annotation files.
   - An `images` subdirectory with all the downloaded images.

## 3. When to Use It
Use this script when you need to prepare labeled datasets from Label Studio for training YOLO object detection models. 
It's particularly useful for converting annotations into the required YOLO format and ensuring all associated images 
are downloaded and organized locally for your machine learning pipeline.
"""

import argparse
import os
import time
import json
import shutil
import logging

from tqdm import tqdm
from label_studio_sdk.client import LabelStudio
import os
from label_studio_sdk.converter import Converter
from label_studio_sdk._extensions.label_studio_tools.core.utils.io import get_local_path


LABEL_STUDIO_URL = os.getenv('LABEL_STUDIO_URL', 'http://localhost:8080')
LABEL_STUDIO_API_KEY = os.getenv('LABEL_STUDIO_API_KEY')
PROJECT_ID = int(os.getenv('PROJECT_ID', '1'))

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [%(module)s] - %(message)s')


def prepare_export(ls: LabelStudio, project_id: int, view_id: int | None = None):
    logger.info("Creating export snapshot for project.")
    create_kwargs = {"title": "YOLO Export Snapshot"}
    if view_id is not None:
        create_kwargs["task_filter_options"] = {"view": view_id}

    export = ls.projects.exports.create(project_id, **create_kwargs)
    while export.status == 'in_progress':
        time.sleep(3)
        export = ls.projects.exports.get(id=project_id, export_pk=export.id)
    data_iter = ls.projects.exports.download(id=project_id, export_pk=export.id, export_type='JSON')

    snapshot_path = os.path.abspath(f"project_{project_id}_yolo_export.json")
    with open(snapshot_path, "wb") as f:
        for data in data_iter:
            f.write(data)
    with open(snapshot_path) as f:
        exported_tasks = json.load(f)
    logger.info(f"Export snapshot saved to {snapshot_path}.")
    return snapshot_path, exported_tasks


def run(url: str, api_key: str, project_id: int):
    logger.info("Connecting to Label Studio.")
    ls = LabelStudio(base_url=url, api_key=api_key)
    logger.info("Connected to Label Studio successfully.")

    logger.info(f"Retrieving project with ID: {project_id}.")
    project = ls.projects.get(id=project_id)

    logger.info("Downloading export snapshot and loading exported tasks.")
    views = ls.views.list(project=project_id)
    view_id = views[0].id if views else None
    snapshot_path, exported_tasks = prepare_export(ls, project_id, view_id)

    logger.info("Initializing Converter with labeling config.")
    label_config = project.label_config
    converter = Converter(config=label_config, project_dir=os.path.dirname(snapshot_path), download_resources=False)

    logger.info("Converting to YOLO format.")
    output_dir = 'output_yolo'
    converter.convert_to_yolo(input_data=snapshot_path, output_dir=output_dir, is_dir=False)

    logger.info("Creating directory for YOLO images.")
    yolo_images_dir = os.path.join(output_dir, 'images')
    os.makedirs(yolo_images_dir, exist_ok=True)

    logger.info("Downloading images for exported tasks.")
    for task in tqdm(exported_tasks):
        image_url = next(iter(task['data'].values()))
        if image_url:
            max_retries = 100
            retry_delay = 1  # initial delay in seconds
            for attempt in range(1, max_retries + 1):
                try:
                    local_image_path = get_local_path(
                        url=image_url,
                        hostname=url,
                        access_token=api_key,
                        task_id=task['id'],
                        download_resources=True
                    )
                    name = os.path.basename(local_image_path).split('__', 1)[-1]
                    destination_path = os.path.join(yolo_images_dir, name)
                    shutil.copy2(local_image_path, destination_path)
                    logger.info(f"Copied image {local_image_path} to {destination_path}")
                    break  # Break the retry loop if download is successful
                except Exception as e:
                    logger.error(f"Error downloading image for task {task['id']}: {e}")
                    if attempt < max_retries:
                        sleep_time = retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                        logger.info(f"Retrying in {sleep_time} seconds... (Attempt {attempt}/{max_retries})")
                        time.sleep(sleep_time)
                    else:
                        logger.error(f"Failed to download image for task {task['id']} after {max_retries} attempts.")
        else:
            logger.warning(f"No image URL found for task {task['id']}")
    logger.info("YOLO export with images completed successfully.")

    return True

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='YOLO Export Script for Label Studio'
    )
    parser.add_argument(
        '--url',
        type=str,
        default=os.getenv('LABEL_STUDIO_URL', LABEL_STUDIO_URL),
        help='Label Studio URL',
    )
    parser.add_argument(
        '--api-key',
        type=str,
        default=os.getenv('LABEL_STUDIO_API_KEY', LABEL_STUDIO_API_KEY),
        help='Label Studio API Key',
    )
    parser.add_argument(
        '--project-id',
        type=int,
        default=int(os.getenv('PROJECT_ID', PROJECT_ID)),
        help='Label Studio Project ID',
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    run(args.url, args.api_key, args.project_id)
