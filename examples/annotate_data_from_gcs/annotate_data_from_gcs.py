"""
Note: This code utilizes functions from an older version of the Label Studio SDK (v0.0.34).
While the newer versions v1.0 and above still support the functionalities of the old version
(see `label_studio_sdk._legacy` for reference), we recommend using the latest Label Studio SDK v1.0 or higher.
"""

import os

from google.cloud import storage as google_storage

from label_studio_sdk import Client

BUCKET_NAME = "my-bucket"  # specify your bucket name here
GOOGLE_APPLICATION_CREDENTIALS = (
    "my-service-account-credentials.json"  # specify your GCS credentials
)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

google_client = google_storage.Client()
bucket = google_client.get_bucket(BUCKET_NAME)
tasks = []
for filename in bucket.list_blobs():
    tasks.append({"image": f"gs://{BUCKET_NAME}/{filename}"})


LABEL_STUDIO_URL = "http://localhost:8080"
API_KEY = "91b3b61589784ed069b138eae3d5a5fe1e909f57"

ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
ls.check_connection()


project = ls.start_project(
    title="Image Annotation Project from SDK",
    label_config="""
    <View>
        <Image name="image" value="$image"/>
        <RectangleLabels name="objects" toName="image">
            <Choice value="Airplane"/>
            <Choice value="Car"/>
        </RectangleLabels>
    </View>
    """,
)


project.connect_google_import_storage(
    bucket=BUCKET_NAME, google_application_credentials=GOOGLE_APPLICATION_CREDENTIALS
)


project.import_tasks(tasks)
