"""
Note: This code utilizes functions from an older version of the Label Studio SDK (v0.0.34).
The newer versions v1.0 and above still support the functionalities of the old version, but you will need to specify
[`label_studio_sdk._legacy`](../../README.md) in your script.
"""

import os

from google.cloud import storage as google_storage

from label_studio_sdk.client import LabelStudio
import os

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


LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080")
API_KEY = os.getenv("LABEL_STUDIO_API_KEY")

ls = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=API_KEY)


project = ls.projects.create(
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


"""
BLOCKER: For v2, connecting GCS import storage should be done via
ls.import_storage.gcs.create(project=project.id, bucket=..., google_application_credentials=..., regex_filter=...)
However, this script requires valid GCS credentials and a real bucket.
Without these, we cannot create or sync storage. Leaving instructions only.
"""
# Example (uncomment with real credentials):
# ls.import_storage.gcs.create(
#     project=project.id,
#     bucket=BUCKET_NAME,
#     google_application_credentials=open(GOOGLE_APPLICATION_CREDENTIALS, 'r').read(),
#     use_blob_urls=True,
#     presign=True,
#     presign_ttl=15,
#     title="GCS storage",
#     regex_filter=".*",
# )


# Importing via tasks list still works without storage
for t in tasks:
    ls.tasks.create(project=project.id, data=t)
