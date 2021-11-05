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

project.import_tasks(
    [{
        'data': {'image': 'https://data.heartex.net/open-images/train_0/mini/0045dd96bf73936c.jpg'},
        'predictions': [{
            'result': [{
                'from_name': 'image_class',
                'to_name': 'image',
                'type': 'choices',
                'value': {
                    'choices': ['Dog']
                }
            }],
            'score': 0.87
        }]
    }, {
        'data': {'image': 'https://data.heartex.net/open-images/train_0/mini/0083d02f6ad18b38.jpg'},
        'predictions': [{
            'result': [{
                'from_name': 'image_class',
                'to_name': 'image',
                'type': 'choices',
                'value': {
                    'choices': ['Cat']
                }
            }],
            'score': 0.65
        }]
    }]
)

project.import_tasks(
    [{'image': f'https://data.heartex.net/open-images/train_0/mini/0045dd96bf73936c.jpg', 'pet': 'Dog'},
    {'image': f'https://data.heartex.net/open-images/train_0/mini/0083d02f6ad18b38.jpg', 'pet': 'Cat'}],
    preannotated_from_fields=['pet']
)

import pandas as pd
pd.read_csv('images.csv')

# alternative we can import data from file images.csv:
# image,pet
# gs://url,Cat
# project.import_tasks('images.csv', preannotated_from_fields=['pet'])

# Now review your preannotations in Label Studio
# ...


# If you have evalme package installed, you can compute preannotation agreement with real annotations,
# and sum up this to overall preannotation accuracy
# from evalme import get_agreement
#
#
# print('Preannotation agreement scores:')
#
# total_score = 0
# n = 0
# for task in project.tasks:
#     score = get_agreement(task['annotations'][0], task['predictions'][0])
#     print(f'{task["id"]} ==> {score}')
#     total_score += score
#     n += 1
#
# print(f'Preannotation accuracy: {100 * total_score / n: .0f}%')
