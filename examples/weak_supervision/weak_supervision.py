"""
**Note:** This code utilizes functions from an older version of the Label Studio SDK (v0.0.34).
The newer versions v1.0 and above still support the functionalities of the old version, but you will need to specify
[`label_studio_sdk._legacy`](../../README.md) in your script.
"""

import os
import random
import re

import pandas as pd

from label_studio_sdk.client import LabelStudio

ls = LabelStudio(base_url=os.getenv('LABEL_STUDIO_URL', 'http://localhost:8080'), api_key=os.getenv('LABEL_STUDIO_API_KEY'))

project = ls.projects.create(
    title="Weak Supervision example with SDK",
    label_config="""
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
    """,
)


tasks = pd.read_csv("data/amazon_cells_labelled.tsv", sep="\t").to_dict("records")
tasks_ids = [
    ls.tasks.create(project=project.id, data=task).id
    for task in tasks
]


# Noisy programmatic labelers
label_ops = {
    r".*\b(good|excellent|great|cool)": "Positive",
    r".*\bi\s+like": "Positive",
    r".*\bnot": "Negative",
    r".*\bdisappointed": "Negative",
    r".*\bjunk": "Negative",
}

# Pre-annotations in Label Studio JSON format
predictions = []
for label_regex, label in label_ops.items():
    model_version = label_regex
    for task, task_id in zip(tasks, tasks_ids):
        text = task["text"].lower()
        if re.match(label_regex, text):
            predictions.append(
                {
                    "task": task_id,
                    "result": [
                        {
                            "from_name": "sentiment",
                            "to_name": "text",
                            "type": "choices",
                            "value": {"choices": [label]},
                        }
                    ],
                    "score": random.random(),
                    "model_version": model_version,
                }
            )

for pr in predictions:
    ls.predictions.create(
        task=pr["task"],
        result=pr["result"],
        score=float(pr["score"]),
        model_version=pr["model_version"],
    )


model_versions = ls.projects.get(id=project.id).model_version

# Predictions coverage helpers are not exposed in v2 SDK. Skipping.


# Auto-creating annotations from predictions isn't supported in OSS SDK v2.
# Blocker: requires enterprise workflow endpoints. Skipping.
