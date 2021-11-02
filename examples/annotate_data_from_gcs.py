from google.cloud import storage as google_storage

BUCKET_NAME = ''  # specify your bucket name here
GOOGLE_APPLICATION_CREDENTIALS = '/Users/nik/aqueous-cortex-307813-870df09fe8c2.json'

google_client = google_storage.Client()
bucket = google_client.get_bucket(BUCKET_NAME)
blobs = bucket.list_blobs()


from label_studio_sdk import Client
LABEL_STUDIO_URL = 'http://localhost:8000'
API_KEY = 'd6f8a2622d39e9d89ff0dfef1a80ad877f4ee9e3'

ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
ls.check_connection()

project = ls.start_project(
    title='Image Annotation Project from SDK',
    label_config='''
    <View>
        <Image name="image" value="$image"/>
        <RectangleLabels name="objects" toName="image">
            <Choice value="Airplane"/>
            <Choice value="Car"/>
        </RectangleLabels>
    </View>
    '''
)

project.connect_google_import_storage(
    bucket=BUCKET_NAME,
    google_application_credentials=GOOGLE_APPLICATION_CREDENTIALS
)