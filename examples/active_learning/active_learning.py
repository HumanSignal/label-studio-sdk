"""
**Note:** This code utilizes functions from an older version of the Label Studio SDK (v0.0.34). 
The newer versions v1.0 and above still support the functionalities of the old version, but you will need to specify
[`label_studio_sdk._legacy`](../../README.md) in your script.
"""

import random

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from label_studio_sdk.client import LabelStudio
import os

LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080")
API_KEY = os.getenv("LABEL_STUDIO_API_KEY")


ls = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=API_KEY)


# Use existing project if provided, else reuse by title, else create
env_pid = os.getenv("LABEL_STUDIO_PROJECT_ID")
project = None
if env_pid:
    project = ls.projects.get(id=int(env_pid))
else:
    for p in ls.projects.list():
        if getattr(p, "title", "") == "AL Project Created from SDK":
            project = p
            break
    if project is None:
        project = ls.projects.create(
            title="AL Project Created from SDK",
            label_config="""
            <View>
            <Text name="text" value="$text"/>
            <Choices name="sentiment" toName="text" choice="single" showInLine="true">
                <Choice value="Positive"/>
                <Choice value="Negative"/>
                <Choice value="Neutral"/>
            </Choices>
            </View>
            """,
        )


ls.projects.update(id=project.id, sampling="Uncertainty sampling")


labels_map = {"Positive": 0, "Negative": 1, "Neutral": 2}
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
    predicted_scores = probabilities[
        np.arange(len(predicted_label_indices)), predicted_label_indices
    ]
    return [inv_labels_map[i] for i in predicted_label_indices], predicted_scores


# Fetch tasks and filter those with annotations (OSS may ignore only_annotated)
all_tasks_full = list(ls.tasks.list(project=project.id, fields='all'))
labeled_tasks = [t.model_dump() for t in all_tasks_full if getattr(t, "annotations", None)]
if not labeled_tasks:
    print(f'No labeled tasks found in project "{project.title}" (id={project.id}).')
    raise SystemExit(0)
texts, labels = [], []
for labeled_task in labeled_tasks:
    texts.append(labeled_task["data"]["text"])
    labels.append(labeled_task["annotations"][0]["result"][0]["value"]["choices"][0])


model = get_model()
train_model(model, texts, labels)


all_tasks = list(ls.tasks.list(project=project.id, fields='task_only'))
annotated_ids = {t["id"] for t in labeled_tasks}
unlabeled_tasks = [t for t in all_tasks if t.id not in annotated_ids]
batch = random.sample(unlabeled_tasks, min(10, len(unlabeled_tasks)))


texts = [task.data["text"] for task in batch]
pred_labels, pred_scores = get_model_predictions(model, texts)


model_version = f"model_{len(labeled_tasks)}"


for task, pred_label, pred_score in zip(batch, pred_labels, pred_scores):
    ls.predictions.create(
        task=task.id,
        result=[
            {
                "from_name": "sentiment",
                "to_name": "text",
                "type": "choices",
                "value": {"choices": [pred_label]},
            }
        ],
        score=float(pred_score),
        model_version=model_version,
    )


ls.projects.update(id=project.id, model_version=model_version)
