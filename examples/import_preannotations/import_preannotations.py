# Import tasks with pre-annotations (predictions) using SDK,
# then calculate agreement scores (accuracy) per tasks.

import os
import pandas as pd

from label_studio_sdk.client import LabelStudio

LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080")
API_KEY = os.getenv("LABEL_STUDIO_API_KEY")

ls = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=API_KEY)


project = ls.projects.create(
    title="Project Created from SDK: Image Preannotation",
    label_config="""
    <View>
    <Image name="image" value="$image"/>
    <Choices name="image_class" toName="image">
        <Choice value="Cat"/>
        <Choice value="Dog"/>
    </Choices>
    </View>
    """,
)


# Bulk import with embedded predictions
bulk_with_predictions = [
    {
        "image": "https://data.heartex.net/open-images/train_0/mini/0045dd96bf73936c.jpg",
        "_predictions": [
            {
                "result": [
                    {
                        "from_name": "image_class",
                        "to_name": "image",
                        "type": "choices",
                        "value": {"choices": ["Dog"]},
                    }
                ],
                "score": 0.87,
            }
        ],
    },
    {
        "image": "https://data.heartex.net/open-images/train_0/mini/0083d02f6ad18b38.jpg",
        "_predictions": [
            {
                "result": [
                    {
                        "from_name": "image_class",
                        "to_name": "image",
                        "type": "choices",
                        "value": {"choices": ["Cat"]},
                    }
                ],
                "score": 0.65,
            }
        ],
    },
]
ls.projects.import_tasks(
    id=project.id,
    request=[
        {"data": {"image": r["image"]}, "predictions": r["_predictions"]}
        for r in bulk_with_predictions
    ],
)


bulk_simple = [
    {
        "image": "https://data.heartex.net/open-images/train_0/mini/0045dd96bf73936c.jpg",
        "pet": "Dog",
    },
    {
        "image": "https://data.heartex.net/open-images/train_0/mini/0083d02f6ad18b38.jpg",
        "pet": "Cat",
    },
]
ls.projects.import_tasks(
    id=project.id,
    request=[{"data": row} for row in bulk_simple],
)

# Create predictions for the imported tasks according to the "pet" field
for task in ls.tasks.list(project=project.id, fields="task_only"):
    data = task.data
    if "pet" in data:
        ls.predictions.create(
            task=task.id,
            result=[
                {
                    "from_name": "image_class",
                    "to_name": "image",
                    "type": "choices",
                    "value": {"choices": [data["pet"]]},
                }
            ],
            score=0.5,
            model_version="from_fields",
        )


pd.read_csv("data/images.csv")


task_ids = [t.id for t in ls.tasks.list(project=project.id, fields='task_only')]
ls.predictions.create(
    task=task_ids[0],
    result=[
        {
            "from_name": "image_class",
            "to_name": "image",
            "type": "choices",
            "value": {"choices": ["Dog"]},
        }
    ],
    model_version="1",
)


predictions = [
    {"task": task_ids[0], "label": "Dog", "score": 0.9},
    {"task": task_ids[1], "label": "Cat", "score": 0.8},
]
for pr in predictions:
    ls.predictions.create(
        task=pr["task"],
        result=[
            {
                "from_name": "image_class",
                "to_name": "image",
                "type": "choices",
                "value": {"choices": [pr["label"]]},
            }
        ],
        score=pr["score"],
        model_version="bulk",
    )


try:
    # NOTE: total_agreement available only in LSE
    agreement = ls.projects.stats.total_agreement(id=project.id)
    print(agreement.model_dump(mode="json"))
except Exception as e:
    print(f"Agreement stats unavailable on this edition: {e}")
