import random
import re

from label_studio_sdk import Client
import pandas as pd

ls = Client(url='http://localhost:8080', api_key='d6f8a2622d39e9d89ff0dfef1a80ad877f4ee9e3')
ls.check_connection()


project = ls.start_project(
    title='Weak Supervision example with SDK',
    label_config='''
    <View>
    <Text name="text" value="$text"/>
    <View style="box-shadow: 2px 2px 5px #999; padding: 20px; margin-top: 2em; border-radius: 5px;">
        <Header value="Choose text sentiment"/>
        <Choices name="sentiment" toName="text" choice="single" showInLine="true">
            <Choice value="Positive"/>
            <Choice value="Negative"/>
            <Choice value="Neutral"/>
        </Choices>
    </View>
    </View>
    ''',
)


tasks = pd.read_csv('data/amazon_cells_labelled.tsv', sep='\t').to_dict('records')
tasks_ids = project.import_tasks(tasks)


# Noisy programmatic labelers
label_ops = {
    r'.*\b(good|excellent|great|cool)': 'Positive',
    r'.*\bi\s+like': 'Positive',
    r'.*\bnot': 'Negative',
    r'.*\bdisappointed': 'Negative',
    r'.*\bjunk': 'Negative',
}

# Pre-annotations in Label Studio JSON format
predictions = []
for label_regex, label in label_ops.items():
    model_version = label_regex
    for task, task_id in zip(tasks, tasks_ids):
        text = task['text'].lower()
        if re.match(label_regex, text):
            predictions.append(
                {
                    'task': task_id,
                    'result': [
                        {'from_name': 'sentiment', 'to_name': 'text', 'type': 'choices', 'value': {'choices': [label]}}
                    ],
                    'score': random.random(),
                    'model_version': model_version,
                }
            )

project.create_predictions(predictions)


model_versions = project.get_model_versions()

# check model version stats
pd.Series(project.get_predictions_coverage(), name='Coverage')


print(project.create_annotations_from_predictions(model_versions=list(model_versions)))

