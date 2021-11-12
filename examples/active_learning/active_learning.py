import random

from label_studio_sdk import Client
from label_studio_sdk.project import ProjectSampling
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

LABEL_STUDIO_URL = 'http://localhost:8000'
API_KEY = '91b3b61589784ed069b138eae3d5a5fe1e909f57'


ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
ls.check_connection()


project = ls.start_project(
    title='AL Project Created from SDK',
    label_config='''
    <View>
    <Text name="text" value="$text"/>
    <Choices name="sentiment" toName="text" choice="single" showInLine="true">
        <Choice value="Positive"/>
        <Choice value="Negative"/>
        <Choice value="Neutral"/>
    </Choices>
    </View>
    ''',
)


project.set_sampling(ProjectSampling.UNCERTAINTY)


labels_map = {'Positive': 0, 'Negative': 1, 'Neutral': 2}
inv_labels_map = {idx: label for label, idx in labels_map.items()}


def get_model():
    # Initialize model with random weights
    return make_pipeline(TfidfVectorizer(), LogisticRegression(C=10, verbose=True))


def train_model(model, input_texts, output_labels):
    # Train the model, given a list of input texts and output labels
    model.fit(input_texts, [labels_map[label] for label in output_labels])


def get_model_predictions(model, input_texts):
    # Make model inference and return predicted labels and associated prediction scores
    probabilities = model.predict_proba(input_texts)
    predicted_label_indices = np.argmax(probabilities, axis=1)
    predicted_scores = probabilities[np.arange(len(predicted_label_indices)), predicted_label_indices]
    return [inv_labels_map[i] for i in predicted_label_indices], predicted_scores


labeled_tasks = project.get_labeled_tasks()
texts, labels = [], []
for labeled_task in labeled_tasks:
    texts.append(labeled_task['data']['text'])
    labels.append(labeled_task['annotations'][0]['result'][0]['value']['choices'][0])


model = get_model()
train_model(model, texts, labels)


unlabeled_tasks_ids = project.get_unlabeled_tasks_ids()
batch_ids = random.sample(unlabeled_tasks_ids, 10)
unlabeled_tasks = project.get_tasks(selected_ids=batch_ids)


texts = [task['data']['text'] for task in unlabeled_tasks]
pred_labels, pred_scores = get_model_predictions(model, texts)


model_version = f'model_{len(labeled_tasks)}'


predictions = []
for task, pred_label, pred_score in zip(unlabeled_tasks, pred_labels, pred_scores):
    project.create_prediction(
        task_id=task['id'],
        # alternatively you can use a simple form here:
        # result=pred_label,
        result=[{'from_name': 'sentiment', 'to_name': 'text', 'type': 'choices', 'value': {'choices': [pred_label]}}],
        score=pred_score,
        model_version=model_version,
    )


project.set_model_version(model_version)
