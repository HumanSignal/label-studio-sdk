from label_studio_sdk import Client

LABEL_STUDIO_URL = 'http://localhost:8080'
API_KEY = '681842051079710a6b0ebce5ec56f746e3400c98'

ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)

project = ls.start_project(
    title='Project Created from SDK: Image Preannotation',
    label_config='''
    <View>
    <Image name="image" value="$image"/>
    <Choices name="image_class" toName="image">
        <Choice value="Cat"/>
        <Choice value="Dog"/>
    </Choices>
    </View>
    '''
)

BUCKET_NAME = ''  # your bucket name goes here
GOOGLE_APPLICATION_CREDENTIALS = '/Users/nik/aqueous-cortex-307813-870df09fe8c2.json'

project.import_tasks(
    [{'image': f'gs://{BUCKET_NAME}/image1.jpg', 'pet': 'Cat'},
    {'image': f'gs://{BUCKET_NAME}/image2.jpg', 'pet': 'Dog'}],
    preannotated_from_fields=['pet']
)

# alternative we can import data from file images.csv:
# image,pet
# gs://url,Cat
project.import_tasks('images.csv', preannotated_from_fields=['pet'])

project.connect_google_source_storage(
    bucket=BUCKET_NAME,
    google_application_credentials=GOOGLE_APPLICATION_CREDENTIALS
)

# Now review your preannotations in Label Studio
# ...


# If you have evalme package installed, you can compute preannotation agreement with real annotations,
# and sum up this to overall preannotation accuracy
from evalme import get_agreement


print('Preannotation agreement scores:')

total_score = 0
n = 0
for task in project.tasks:
    score = get_agreement(task)
    print(f'{task["id"]} ==> {score}')
    total_score += score
    n += 1

print(f'Preannotation accuracy: {100 * total_score / n: .0f}%')
