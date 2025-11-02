import os

from google.cloud import storage as google_storage

from label_studio_sdk import LabelStudio

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


ls.import_storage.gcs.create(
    project=project.id,
    bucket=BUCKET_NAME,
    google_application_credentials=open(GOOGLE_APPLICATION_CREDENTIALS, 'r').read(),
    use_blob_urls=True,
    presign=True,
    presign_ttl=15,
    title="GCS storage",
    regex_filter=".*",
)


# Importing via tasks list still works without storage
for t in tasks:
    ls.tasks.create(project=project.id, data=t)
