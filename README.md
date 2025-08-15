# Label Studio Python Library

[![fern shield](https://img.shields.io/badge/%F0%9F%8C%BF-SDK%20generated%20by%20Fern-brightgreen)](https://github.com/fern-api/fern)
[![pypi](https://img.shields.io/pypi/v/label-studio-sdk.svg)](https://pypi.python.org/pypi/label-studio-sdk)

The Label Studio Python Library provides convenient access to the Label Studio API from applications written in Python.
<!-- End Title  -->

<!-- Outline -->


# Documentation
Explore the Label Studio API documentation [here](https://api.labelstud.io/).


# Installation

```sh
pip install --upgrade label-studio-sdk
# or
poetry add label-studio-sdk
```

# Usage

```python
from label_studio_sdk.client import LabelStudio

ls = LabelStudio(
    base_url='YOUR_LABEL_STUDIO_URL',  
    api_key="YOUR_API_KEY",
)
```

# Versions

## SDK 2.0.0

In August 2025, we released SDK version 2.0.0. 

This version has a number of documentation and functional improvements over SDK 1. 

### Enhancements 

**Enterprise-only**

- Added a new `projects.stats.iaa` endpoint to return stats from the inter-annotator agreement matrix. 
- You can now update tasks that have comments.
- Added support for `sync` to `S3s` (S3 with IAM role) exports.

**Enterprise and open source**

- Expanded support to include all project settings, many of which were missing in SDK 1. For example, in Enterprise environments you can now configure `assignment_settings`, `review_settings`, `annotator_evaluation`, and many more.
- Fixed passing the `project` parameter in `actions.list()` (broken in SDK 1). 
- Relaxed request/response validation reduces pydantic errors in SDK 2.

### Breaking changes

**Enterprise-only**

- `comments.create` no longer accepts a `project` argument.
- In `prompts.indicators`, the `pk` parameter is now `id`.
- In `prompts.runs` and `prompts.versions`, the `id` parameter is now `prompt_id`.
- `workspaces.members.list` responses are now objects instead of dictionaries.

**Enterprise and open source**

- In `projects.exports` calls, the project ID is now passed as `id`, while the export ID is passed as `export_pk`.
- Predictions returned in task responses are now objects instead of dictionaries. 

## SDK 1.0+

SDK 1 was released in June 2024. 

If you use the Label Studio SDK 1 package in any automated pipelines, we strongly recommend pinning your SDK version to `<2.0.0` until you can reconcile the breaking changes. 


## SDK <1

The version of `label-studio-sdk<1` is deprecated and no longer supported. We recommend updating to the latest version.

<details>

<summary> To use SDK <1 </summary>

If you still want to use the deprecated version, you can install it with `pip install "label-studio-sdk<1"`. 

OR You can find the branch with the old version by cloning the repository and checking out the branch as follows:

```sh
git clone https://github.com/HumanSignal/label-studio-sdk.git
cd label-studio-sdk
git fetch origin
git checkout release/0.0.34
```

OR you can change your import statements as follows:
```python
from label_studio_sdk import Client
from label_studio_sdk.data_manager import Filters, Column, Operator, Type
from label_studio_sdk._legacy import Project
```

</details>

# Examples

Check more examples [here](https://api.labelstud.io/).

## Create a new project

```python
from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk.label_interface.create import labels

project = ls.projects.create(
    title="Project name",
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


## Async client

```python
from label_studio_sdk.client import AsyncLabelStudio

client = AsyncLabelStudio(
    api_key="YOUR_API_KEY",
)
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

## Enterprise features

### Create comments
    
```python
comment = ls.comments.create(
    project=project.id,
    annotation=annotation.id,
    text="Comment text"
)
```

<!-- Begin Contributing, generated by Fern  -->
# Contributing

Please follow [this guide to contribute to the SDK](https://github.com/HumanSignal/label-studio-client-generator?tab=readme-ov-file#how-to-contribute)

While we value open-source contributions to this SDK, this library is generated programmatically. 
Additions made directly to this library would have to be moved over to our generation code, 
otherwise they would be overwritten upon the next generated release. Feel free to open a PR as
 a proof of concept, but know that we will not be able to merge it as-is. We suggest opening 
an issue first to discuss with us!

On the other hand, contributions to the README are always very welcome!
<!-- End Contributing  -->

