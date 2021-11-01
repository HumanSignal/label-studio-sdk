import random

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline


labels_map = {
    'Positive': 0,
    'Negative': 1,
    'Neutral': 2
}
inv_labels_map = {idx: label for label, idx in labels_map.items()}


def get_model():
    return make_pipeline(TfidfVectorizer(), LogisticRegression(C=10, verbose=True))


def train_model(model, input_texts, output_labels):
    model.fit(input_texts, [labels_map[label] for label in output_labels])


def get_model_predictions(model, input_texts):
    probabilities = model.predict_proba(input_texts)
    predicted_label_indices = np.argmax(probabilities, axis=1)
    predicted_scores = probabilities[np.arange(len(predicted_label_indices)), predicted_label_indices]
    return [inv_labels_map[i] for i in predicted_label_indices], predicted_scores


LABEL_STUDIO_URL = 'http://localhost:8000'
API_KEY = 'd6f8a2622d39e9d89ff0dfef1a80ad877f4ee9e3'


from label_studio_sdk import Client

ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
ls.check_connection()


from label_studio_sdk.project import ProjectSampling

# project = ls.start_project(
#     title='AL Project Created from SDK',
#     label_config='''
#     <View>
#     <Text name="text" value="$text"/>
#     <Choices name="sentiment" toName="text" choice="single" showInLine="true">
#         <Choice value="Positive"/>
#         <Choice value="Negative"/>
#         <Choice value="Neutral"/>
#     </Choices>
#     </View>
#     '''
# )
# project.set_sampling(ProjectSampling.UNCERTAINTY)

import pandas as pd

project = ls.get_project(50)
# tasks = pd.read_csv('amazon_cells_labelled.tsv', sep='\t').to_dict('records')
# tasks_ids = project.import_tasks(tasks)

# tasks_ids = project.get_tasks_ids()

model = get_model()

labeled_tasks = project.get_labeled_tasks()
texts, labels = [], []
for labeled_task in labeled_tasks:
    texts.append(labeled_task['data']['text'])
    labels.append(labeled_task['annotations'][0]['result'][0]['value']['choices'][0])

train_model(model, texts, labels)

unlabeled_tasks_ids = project.get_unlabeled_tasks_ids()
batch_ids = random.sample(unlabeled_tasks_ids, 10)
unlabeled_tasks = project.get_tasks(selected_ids=batch_ids)
texts = [task['data']['text'] for task in unlabeled_tasks]
pred_labels, pred_scores = get_model_predictions(model, texts)

predictions = []
for task, pred_label, pred_score in zip(unlabeled_tasks, pred_labels, pred_scores):
    print(project.create_prediction(
        task_id=task['id'],
        result=pred_label,
        score=pred_score,
        model_version=f'model_{len(labeled_tasks)}'
    ))



