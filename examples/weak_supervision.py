import random
import pandas as pd
import re

from label_studio_sdk import Client

LABEL_STUDIO_URL = 'http://localhost:8080'
API_KEY = '681842051079710a6b0ebce5ec56f746e3400c98'

# LABEL_STUDIO_URL = 'http://localhost:8000'
# API_KEY = 'd6f8a2622d39e9d89ff0dfef1a80ad877f4ee9e3'

ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
ls.check_connection()

project = ls.start_project(
    title='Project Created from SDK 111',
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
    '''
)

tasks = pd.read_csv('amazon_cells_labelled.tsv', sep='\t').to_dict('records')
tasks_ids = project.import_tasks(tasks)

label_ops = {
    r'.*\b(good|excellent|great|cool)': 'Positive',
    r'.*\bi\s+like': 'Positive',
    r'.*\bnot': 'Negative',
    r'.*\bdisappointed': 'Negative',
    r'.*\bjunk': 'Negative'
}

predictions = []
for label_regex, label in label_ops.items():
    model_version = label_regex
    for task, task_id in zip(tasks, tasks_ids):
        text = task['text'].lower()
        if re.match(label_regex, text):
            predictions.append({
                'task': task_id,
                'result': label,
                'score': random.random(),
                'model_version': model_version
            })

project.create_predictions(predictions)

model_versions = project.get_model_versions()

# check model version stats
# project.predictions_coverage(model_versions)
# project.predictions_agreement(model_versions)
# then select specific model versions

print(project.create_annotations_from_predictions(model_versions=model_versions))
