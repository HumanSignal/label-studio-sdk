# HumansignalOrg Python Library

[![fern shield](https://img.shields.io/badge/%F0%9F%8C%BF-SDK%20generated%20by%20Fern-brightgreen)](https://github.com/fern-api/fern)
[![pypi](https://img.shields.io/pypi/v/label-studio-sdk)](https://pypi.python.org/pypi/label-studio-sdk)

The HumansignalOrg Python library provides convenient access to the HumansignalOrg API from Python.

## Create a new project

```python
from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk.label_interface.create import labels

project = ls.projects.create(
    name="Project name",
    description="Project description",
    label_config=LabelInterface.create({
      "image": "Image",
      "bbox": labels(["cat", "dog"], tag_type="RectangleLabels")
    })
)
```

## Create a new task
    
```python
task = ls.tasks.create(
    project=project.id,
    data={"image": "https://example.com/image.jpg"}
)
```
Now you can open the project `PROJECT_ID` in the Label Studio UI and create annotations for the task.

## Export annotations

```python
annotations = [
    task.annotations
    for task in ls.tasks.list(project=project.id, fields='all')
    if task.annotations
]
```


## Installation

```sh
pip install label-studio-sdk
```

## Usage

Instantiate and use the client with the following:

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.annotations.create(
    id=1,
    result=[
        {
            "original_width": 1920,
            "original_height": 1080,
            "image_rotation": 0,
            "from_name": "bboxes",
            "to_name": "image",
            "type": "rectanglelabels",
            "value": {
                "x": 20,
                "y": 30,
                "width": 50,
                "height": 60,
                "rotation": 0,
                "values": {"rectanglelabels": ["Person"]},
            },
        }
    ],
    was_cancelled=False,
    ground_truth=True,
)
```

## Async Client

The SDK also exports an `async` client so that you can make non-blocking calls to our API.

```python
from label_studio_sdk.client import AsyncLabelStudio

client = AsyncLabelStudio(
    api_key="YOUR_API_KEY",
)
await client.annotations.create(
    id=1,
    result=[
        {
            "original_width": 1920,
            "original_height": 1080,
            "image_rotation": 0,
            "from_name": "bboxes",
            "to_name": "image",
            "type": "rectanglelabels",
            "value": {
                "x": 20,
                "y": 30,
                "width": 50,
                "height": 60,
                "rotation": 0,
                "values": {"rectanglelabels": ["Person"]},
            },
        }
    ],
    was_cancelled=False,
    ground_truth=True,
)
```

## Pagination

Paginated requests will return a `SyncPager` or `AsyncPager`, which can be used as generators for the underlying object.

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
response = client.projects.list()
for item in response:
    yield item
# alternatively, you can paginate page-by-page
for page in response.iter_pages():
    yield page
```

## Advanced

### Timeouts
By default, requests time out after 60 seconds. You can configure this with a 
timeout option at the client or request level.

```python
from label_studio_sdk.client import LabelStudio

ls = LabelStudio(
    # All timeouts set to 20 seconds
    timeout=20.0
)

ls.projects.create(..., {
    # Override timeout for a specific method
    timeout=20.0
})
```

### Custom HTTP client
You can override the httpx client to customize it for your use-case. Some common use-cases 
include support for proxies and transports.

```python
import httpx

from label_studio_sdk.client import LabelStudio

ls = LabelStudio(
    http_client=httpx.Client(
        proxies="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

## Contributing

While we value open-source contributions to this SDK, this library is generated programmatically.
Additions made directly to this library would have to be moved over to our generation code,
otherwise they would be overwritten upon the next generated release. Feel free to open a PR as
a proof of concept, but know that we will not be able to merge it as-is. We suggest opening
an issue first to discuss with us!

On the other hand, contributions to the README are always very welcome!
