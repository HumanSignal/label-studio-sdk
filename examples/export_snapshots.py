"""
**Note:** This code utilizes functions from an older version of the Label Studio SDK (v0.0.34).
While the newer versions v1.0 and above still support the functionalities of the old version
(see `label_studio_sdk._legacy` for reference), we recommend using the latest Label Studio SDK v1.0 or higher.
"""

import os
import time

from label_studio_sdk import Client

LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", default="http://localhost:8080")
API_KEY = os.getenv("LABEL_STUDIO_API_KEY")
PROJECT_ID = int(os.getenv("LABEL_STUDIO_PROJECT_ID"))

# connect to Label Studio
ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
ls.check_connection()

# init new project
"""project = ls.start_project(
    title='Export SDK Snapshot test',
    label_config='''
    <View>
        <Image name="image" value="$image"/>
        <RectangleLabels name="objects" toName="image">
            <Choice value="Airplane"/>
            <Choice value="Car"/>
        </RectangleLabels>
    </View>
    ''',
)"""
# get existing project
project = ls.get_project(PROJECT_ID)

# get the first tab
views = project.get_views()
task_filter_options = {"view": views[0]["id"]} if views else {}

# create new export snapshot
export_result = project.export_snapshot_create(
    title="Export SDK Snapshot", task_filter_options=task_filter_options
)
assert "id" in export_result
export_id = export_result["id"]

# wait until snapshot is ready
while project.export_snapshot_status(export_id).is_in_progress():
    time.sleep(1.0)

# download snapshot file
status, file_name = project.export_snapshot_download(export_id, export_type="JSON")
assert status == 200
assert file_name is not None
print(f"Status of the export is {status}.\nFile name is {file_name}")
