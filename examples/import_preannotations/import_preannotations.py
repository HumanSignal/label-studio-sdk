from evalme.metrics import get_agreement  # run first `pip install label-studio-evalme` to use this package
from label_studio_sdk import Client
import pandas as pd

LABEL_STUDIO_URL = 'http://localhost:8080'
API_KEY = '91b3b61589784ed069b138eae3d5a5fe1e909f57'

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
    ''',
)


project.import_tasks(
    [
        {
            'data': {'image': 'https://data.heartex.net/open-images/train_0/mini/0045dd96bf73936c.jpg'},
            'predictions': [
                {
                    'result': [
                        {
                            'from_name': 'image_class',
                            'to_name': 'image',
                            'type': 'choices',
                            'value': {'choices': ['Dog']},
                        }
                    ],
                    'score': 0.87,
                }
            ],
        },
        {
            'data': {'image': 'https://data.heartex.net/open-images/train_0/mini/0083d02f6ad18b38.jpg'},
            'predictions': [
                {
                    'result': [
                        {
                            'from_name': 'image_class',
                            'to_name': 'image',
                            'type': 'choices',
                            'value': {'choices': ['Cat']},
                        }
                    ],
                    'score': 0.65,
                }
            ],
        },
    ]
)


project.import_tasks(
    [
        {'image': f'https://data.heartex.net/open-images/train_0/mini/0045dd96bf73936c.jpg', 'pet': 'Dog'},
        {'image': f'https://data.heartex.net/open-images/train_0/mini/0083d02f6ad18b38.jpg', 'pet': 'Cat'},
    ],
    preannotated_from_fields=['pet'],
)


pd.read_csv('data/images.csv')

project.import_tasks('data/images.csv', preannotated_from_fields=['pet'])


tasks_ids = project.get_tasks_ids()
project.create_prediction(tasks_ids[0], result='Dog', model_version='1')


predictions = [
    {"task": tasks_ids[0], "result": "Dog", "score": 0.9},
    {"task": tasks_ids[1], "result": "Cat", "score": 0.8},
]
project.create_predictions(predictions)

print('Pre-annotation agreement scores:')

total_score = 0
n = 0
for task in project.tasks:
    score = get_agreement(task['annotations'][0], task['predictions'][0])
    print(f'{task["id"]} ==> {score}')
    total_score += score
    n += 1

print(f'Pre-annotation accuracy: {100 * total_score / n: .0f}%')

