"""
**Note:** This code utilizes functions from an older version of the Label Studio SDK (v0.0.34).
The newer versions v1.0 and above still support the functionalities of the old version, but you will need to specify
[`label_studio_sdk._legacy`](../../README.md) in your script.
"""

# Create a new project with several tasks and brush preannotations
# Contributed by https://github.com/berombau:
# https://github.com/heartexlabs/label-studio-sdk/issues/19#issuecomment-992327281

import numpy as np

import label_studio_sdk.converter.brush as brush
from label_studio_sdk import Client

LABEL_STUDIO_URL = "http://localhost:8080"
LABEL_STUDIO_API_KEY = "<your-token>"
LABEL = "Mitochondria"

ls = Client(url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_API_KEY)
ls.check_connection()

project = ls.start_project(
    title=LABEL,
    label_config=f"""
    <View>
    <Image name="image" value="$image" zoom="true"/>
    <BrushLabels name="brush_labels_tag" toName="image">
        <Label value="{LABEL}" background="#8ff0a4"/>
    </BrushLabels>
    </View>
    """,
)

ids = project.import_tasks(
    [{"image": f"http://example.com/data_{i:04}.png"} for i in range(64)]
)

mask = (np.random.random([512, 512]) * 255).astype(np.uint8)  # just a random 2D mask
mask = (mask > 128).astype(
    np.uint8
) * 255  # better to threshold, it reduces output annotation size
rle = brush.mask2rle(mask)  # mask image in RLE format

project.create_prediction(
    task_id=ids[0],
    model_version=None,
    result=[
        {
            "from_name": "brush_labels_tag",
            "to_name": "image",
            "type": "brushlabels",
            "value": {"format": "rle", "rle": rle, "brushlabels": [LABEL]},
        }
    ],
)
