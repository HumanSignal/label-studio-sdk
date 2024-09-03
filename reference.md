# Reference
## Annotations
<details><summary><code>client.annotations.<a href="src/label_studio_sdk/annotations/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Tasks can have multiple annotations. Use this call to retrieve a specific annotation using its ID.

You can find the ID in the Label Studio UI listed at the top of the annotation in its tab. It is also listed in the History panel when viewing the annotation. Or you can use [Get all task annotations](list) to find all annotation IDs.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.annotations.get(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this annotation.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.annotations.<a href="src/label_studio_sdk/annotations/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete an annotation.

<Warning>This action can't be undone!</Warning>

You will need to supply the annotation's unique ID. You can find the ID in the Label Studio UI listed at the top of the annotation in its tab. It is also listed in the History panel when viewing the annotation. Or you can use [Get all task annotations](list) to find all annotation IDs.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.annotations.delete(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this annotation.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.annotations.<a href="src/label_studio_sdk/annotations/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update attributes for an existing annotation.

You will need to supply the annotation's unique ID. You can find the ID in the Label Studio UI listed at the top of the annotation in its tab. It is also listed in the History panel when viewing the annotation. Or you can use [Get all task annotations](list) to find all annotation IDs.

For information about the JSON format used in the result, see [Label Studio JSON format of annotated tasks](https://labelstud.io/guide/export#Label-Studio-JSON-format-of-annotated-tasks).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.annotations.update(
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
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this annotation.
    
</dd>
</dl>

<dl>
<dd>

**result:** `typing.Optional[typing.Sequence[typing.Dict[str, typing.Any]]]` — Labeling result in JSON format. Read more about the format in [the Label Studio documentation.](https://labelstud.io/guide/task_format)
    
</dd>
</dl>

<dl>
<dd>

**task:** `typing.Optional[int]` — Corresponding task for this annotation
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID for this annotation
    
</dd>
</dl>

<dl>
<dd>

**completed_by:** `typing.Optional[int]` — User ID of the person who created this annotation
    
</dd>
</dl>

<dl>
<dd>

**updated_by:** `typing.Optional[int]` — Last user who updated this annotation
    
</dd>
</dl>

<dl>
<dd>

**was_cancelled:** `typing.Optional[bool]` — User skipped the task
    
</dd>
</dl>

<dl>
<dd>

**ground_truth:** `typing.Optional[bool]` — This annotation is a Ground Truth
    
</dd>
</dl>

<dl>
<dd>

**lead_time:** `typing.Optional[float]` — How much time it took to annotate the task (in seconds)
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.annotations.<a href="src/label_studio_sdk/annotations/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all annotations for a task.

You will need to supply the task ID. You can find this in Label Studio by opening a task and checking the URL. It is also listed at the top of the labeling interface. Or you can use [Get tasks list](../tasks/list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.annotations.list(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — Task ID
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.annotations.<a href="src/label_studio_sdk/annotations/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Add annotations to a task like an annotator does.

You will need to supply the task ID. You can find this in Label Studio by opening a task and checking the URL. It is also listed at the top of the labeling interface. Or you can use [Get tasks list](../tasks/list).

The content of the result field depends on your labeling configuration. For example, send the following data as part of your POST
request to send an empty annotation with the ID of the user who completed the task:

```json
{
"result": {},
"was_cancelled": true,
"ground_truth": true,
"lead_time": 0,
"task": 0
"completed_by": 123
}
```
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

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
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — Task ID
    
</dd>
</dl>

<dl>
<dd>

**result:** `typing.Optional[typing.Sequence[typing.Dict[str, typing.Any]]]` — Labeling result in JSON format. Read more about the format in [the Label Studio documentation.](https://labelstud.io/guide/task_format)
    
</dd>
</dl>

<dl>
<dd>

**task:** `typing.Optional[int]` — Corresponding task for this annotation
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID for this annotation
    
</dd>
</dl>

<dl>
<dd>

**completed_by:** `typing.Optional[int]` — User ID of the person who created this annotation
    
</dd>
</dl>

<dl>
<dd>

**updated_by:** `typing.Optional[int]` — Last user who updated this annotation
    
</dd>
</dl>

<dl>
<dd>

**was_cancelled:** `typing.Optional[bool]` — User skipped the task
    
</dd>
</dl>

<dl>
<dd>

**ground_truth:** `typing.Optional[bool]` — This annotation is a Ground Truth
    
</dd>
</dl>

<dl>
<dd>

**lead_time:** `typing.Optional[float]` — How much time it took to annotate the task (in seconds)
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Users
<details><summary><code>client.users.<a href="src/label_studio_sdk/users/client.py">reset_token</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Reset your access token or API key. When reset, any scripts or automations you have in place will need to be updated with the new key.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.users.reset_token()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.users.<a href="src/label_studio_sdk/users/client.py">get_token</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a access token to authenticate to the API as the current user. To find this in the Label Studio interface, click **Account & Settings** in the upper right. For more information, see [Access Token](https://labelstud.io/guide/user_account#Access-token).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.users.get_token()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.users.<a href="src/label_studio_sdk/users/client.py">whoami</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get information about your user account, such as your username, email, and user ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.users.whoami()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.users.<a href="src/label_studio_sdk/users/client.py">list</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all users in your Label Studio organization.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.users.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.users.<a href="src/label_studio_sdk/users/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a user in Label Studio.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.users.create()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `typing.Optional[int]` — User ID
    
</dd>
</dl>

<dl>
<dd>

**first_name:** `typing.Optional[str]` — First name of the user
    
</dd>
</dl>

<dl>
<dd>

**last_name:** `typing.Optional[str]` — Last name of the user
    
</dd>
</dl>

<dl>
<dd>

**username:** `typing.Optional[str]` — Username of the user
    
</dd>
</dl>

<dl>
<dd>

**email:** `typing.Optional[str]` — Email of the user
    
</dd>
</dl>

<dl>
<dd>

**avatar:** `typing.Optional[str]` — Avatar URL of the user
    
</dd>
</dl>

<dl>
<dd>

**initials:** `typing.Optional[str]` — Initials of the user
    
</dd>
</dl>

<dl>
<dd>

**phone:** `typing.Optional[str]` — Phone number of the user
    
</dd>
</dl>

<dl>
<dd>

**allow_newsletters:** `typing.Optional[bool]` — Whether the user allows newsletters
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.users.<a href="src/label_studio_sdk/users/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get info about a specific Label Studio user.
You will need to provide their user ID. You can find a list of all user IDs using [List users](list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.users.get(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — User ID
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.users.<a href="src/label_studio_sdk/users/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific Label Studio user.

You will need to provide their user ID. You can find a list of all user IDs using [List users](list).

<Warning>Use caution when deleting a user, as this can cause issues such as breaking the "Annotated by" filter or leaving orphaned records.</Warning>
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.users.delete(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — User ID
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.users.<a href="src/label_studio_sdk/users/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update details for a specific Label Studio user, such as their name or contact information.

You will need to provide their user ID. You can find a list of all user IDs using [List users](list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.users.update(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — User ID
    
</dd>
</dl>

<dl>
<dd>

**users_update_request_id:** `typing.Optional[int]` — User ID
    
</dd>
</dl>

<dl>
<dd>

**first_name:** `typing.Optional[str]` — First name of the user
    
</dd>
</dl>

<dl>
<dd>

**last_name:** `typing.Optional[str]` — Last name of the user
    
</dd>
</dl>

<dl>
<dd>

**username:** `typing.Optional[str]` — Username of the user
    
</dd>
</dl>

<dl>
<dd>

**email:** `typing.Optional[str]` — Email of the user
    
</dd>
</dl>

<dl>
<dd>

**avatar:** `typing.Optional[str]` — Avatar URL of the user
    
</dd>
</dl>

<dl>
<dd>

**initials:** `typing.Optional[str]` — Initials of the user
    
</dd>
</dl>

<dl>
<dd>

**phone:** `typing.Optional[str]` — Phone number of the user
    
</dd>
</dl>

<dl>
<dd>

**allow_newsletters:** `typing.Optional[bool]` — Whether the user allows newsletters
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Actions
<details><summary><code>client.actions.<a href="src/label_studio_sdk/actions/client.py">list</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve all the registered actions with descriptions that data manager can use.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.actions.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.actions.<a href="src/label_studio_sdk/actions/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Perform a Data Manager action with the selected tasks and filters. Note: More complex actions require additional parameters in the request body. Call `GET api/actions?project=<id>` to explore them. <br>Example: `GET api/actions?id=delete_tasks&project=1`
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk import (
    ActionsCreateRequestFilters,
    ActionsCreateRequestFiltersItemsItem,
    ActionsCreateRequestSelectedItemsExcluded,
)
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.actions.create(
    id="retrieve_tasks_predictions",
    project=1,
    filters=ActionsCreateRequestFilters(
        conjunction="or",
        items=[
            ActionsCreateRequestFiltersItemsItem(
                filter="filter:tasks:id",
                operator="greater",
                type="Number",
                value=123,
            )
        ],
    ),
    selected_items=ActionsCreateRequestSelectedItemsExcluded(
        all_=True,
        excluded=[124, 125, 126],
    ),
    ordering=["tasks:total_annotations"],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `ActionsCreateRequestId` — Action name ID, see the full list of actions in the `GET api/actions` request
    
</dd>
</dl>

<dl>
<dd>

**project:** `int` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**view:** `typing.Optional[int]` — View ID (optional, it has higher priority than filters, selectedItems and ordering from the request body payload)
    
</dd>
</dl>

<dl>
<dd>

**filters:** `typing.Optional[ActionsCreateRequestFilters]` — Filters to apply on tasks. You can use [the helper class `Filters` from this page](https://labelstud.io/sdk/data_manager.html) to create Data Manager Filters.<br>Example: `{"conjunction": "or", "items": [{"filter": "filter:tasks:completed_at", "operator": "greater", "type": "Datetime", "value": "2021-01-01T00:00:00.000Z"}]}`
    
</dd>
</dl>

<dl>
<dd>

**selected_items:** `typing.Optional[ActionsCreateRequestSelectedItems]` — Task selection by IDs. If filters are applied, the selection will be applied to the filtered tasks.If "all" is `false`, `"included"` must be used. If "all" is `true`, `"excluded"` must be used.<br>Examples: `{"all": false, "included": [1, 2, 3]}` or `{"all": true, "excluded": [4, 5]}`
    
</dd>
</dl>

<dl>
<dd>

**ordering:** `typing.Optional[typing.Sequence[ActionsCreateRequestOrderingItem]]` — List of fields to order by. Fields are similar to filters but without the `filter:` prefix. To reverse the order, add a minus sign before the field name, e.g. `-tasks:created_at`.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Views
<details><summary><code>client.views.<a href="src/label_studio_sdk/views/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all views for a specific project. A view is a tab in the Data Manager where you can set filters and customize which tasks and information appears.

You will need to provide the project ID. You can find this in the URL when viewing the project in Label Studio, or you can use [List all projects](../projects/list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.views.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.views.<a href="src/label_studio_sdk/views/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new Data Manager view for a specific project. A view is a tab in the Data Manager where you can set filters and customize what tasks and information appears.

You will need to provide the project ID. You can find this in the URL when viewing the project in Label Studio, or you can use [List all projects](../projects/list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.views.create()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**data:** `typing.Optional[ViewsCreateRequestData]` — Custom view data
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.views.<a href="src/label_studio_sdk/views/client.py">delete_all</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete all views for a specific project. A view is a tab in the Data Manager where you can set filters and customize what tasks appear.

You will need to provide the project ID. You can find this in the URL when viewing the project in Label Studio, or you can use [List all projects](../projects/list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.views.delete_all(
    project=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**project:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.views.<a href="src/label_studio_sdk/views/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get the details about a specific Data Manager view (tab). You will need to supply the view ID. You can find this using [List views](list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.views.get(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — View ID
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.views.<a href="src/label_studio_sdk/views/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific Data Manager view (tab) by ID. You can find the view using [List views](list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.views.delete(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — View ID
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.views.<a href="src/label_studio_sdk/views/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

You can update a specific Data Manager view (tab) with additional filters and other customizations. You will need to supply the view ID. You can find this using [List views](list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.views.update(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — View ID
    
</dd>
</dl>

<dl>
<dd>

**data:** `typing.Optional[ViewsUpdateRequestData]` — Custom view data
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Files
<details><summary><code>client.files.<a href="src/label_studio_sdk/files/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve details about a specific uploaded file. To get the file upload ID, use [Get files list](list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.files.get(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this file upload.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.files.<a href="src/label_studio_sdk/files/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific uploaded file. To get the file upload ID, use [Get files list](list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.files.delete(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this file upload.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.files.<a href="src/label_studio_sdk/files/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific uploaded file. To get the file upload ID, use [Get files list](list).

You will need to include the file data in the request body. For example:

```bash
curl -H 'Authorization: Token abc123' \ -X POST 'https://localhost:8080/api/import/file-upload/245' -F ‘file=@path/to/my_file.csv’
```
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.files.update(
    id_=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id_:** `int` — A unique integer value identifying this file upload.
    
</dd>
</dl>

<dl>
<dd>

**id:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**file:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.files.<a href="src/label_studio_sdk/files/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve the list of uploaded files used to create labeling tasks for a specific project. These are files that have been uploaded directly to Label Studio.

You must provide a project ID. The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.files.list(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this file upload.
    
</dd>
</dl>

<dl>
<dd>

**all_:** `typing.Optional[bool]` — Set to "true" if you want to retrieve all file uploads
    
</dd>
</dl>

<dl>
<dd>

**ids:** `typing.Optional[typing.Union[int, typing.Sequence[int]]]` — Specify the list of file upload IDs to retrieve, e.g. ids=[1,2,3]
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.files.<a href="src/label_studio_sdk/files/client.py">delete_many</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete uploaded files for a specific project. These are files that have been uploaded directly to Label Studio.

You must provide a project ID. The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.files.delete_many(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this file upload.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.files.<a href="src/label_studio_sdk/files/client.py">download</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Download a specific uploaded file. If you aren't sure of the file name, try [Get files list](list) first.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.files.download(
    filename="filename",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**filename:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Projects
<details><summary><code>client.projects.<a href="src/label_studio_sdk/projects/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Return a list of the projects within your organization.

To perform most tasks with the Label Studio API, you must specify the project ID, sometimes referred to as the `pk`. The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using this API call.

To retrieve a list of your Label Studio projects, update the following command to match your own environment.
Replace the domain name, port, and authorization token, then run the following from the command line:

```bash
curl -X GET https://localhost:8080/api/projects/ -H 'Authorization: Token abc123'
```
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

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
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
</dd>
</dl>

<dl>
<dd>

**ids:** `typing.Optional[str]` — ids
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — title
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — A page number within the paginated result set.
    
</dd>
</dl>

<dl>
<dd>

**page_size:** `typing.Optional[int]` — Number of results to return per page.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.projects.<a href="src/label_studio_sdk/projects/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a project and set up the labeling interface. For more information about setting up projects, see the following:

- [Create and configure projects](https://labelstud.io/guide/setup_project)
- [Configure labeling interface](https://labelstud.io/guide/setup)
- [Project settings](https://labelstud.io/guide/project_settings)

```bash
curl -H Content-Type:application/json -H 'Authorization: Token abc123' -X POST 'https://localhost:8080/api/projects'     --data '{"label_config": "<View>[...]</View>"}'
```
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.projects.create()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**title:** `typing.Optional[str]` — Project title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Project description
    
</dd>
</dl>

<dl>
<dd>

**label_config:** `typing.Optional[str]` — Label config in XML format
    
</dd>
</dl>

<dl>
<dd>

**expert_instruction:** `typing.Optional[str]` — Labeling instructions to show to the user
    
</dd>
</dl>

<dl>
<dd>

**show_instruction:** `typing.Optional[bool]` — Show labeling instructions
    
</dd>
</dl>

<dl>
<dd>

**show_skip_button:** `typing.Optional[bool]` — Show skip button
    
</dd>
</dl>

<dl>
<dd>

**enable_empty_annotation:** `typing.Optional[bool]` — Allow empty annotations
    
</dd>
</dl>

<dl>
<dd>

**show_annotation_history:** `typing.Optional[bool]` — Show annotation history
    
</dd>
</dl>

<dl>
<dd>

**reveal_preannotations_interactively:** `typing.Optional[bool]` — Reveal preannotations interactively. If set to True, predictions will be shown to the user only after selecting the area of interest
    
</dd>
</dl>

<dl>
<dd>

**show_collab_predictions:** `typing.Optional[bool]` — Show predictions to annotators
    
</dd>
</dl>

<dl>
<dd>

**maximum_annotations:** `typing.Optional[int]` — Maximum annotations per task
    
</dd>
</dl>

<dl>
<dd>

**color:** `typing.Optional[str]` — Project color in HEX format
    
</dd>
</dl>

<dl>
<dd>

**control_weights:** `typing.Optional[typing.Dict[str, typing.Any]]` — Dict of weights for each control tag in metric calculation. Each control tag (e.g. label or choice) will have its own key in control weight dict with weight for each label and overall weight. For example, if a bounding box annotation with a control tag named my_bbox should be included with 0.33 weight in agreement calculation, and the first label Car should be twice as important as Airplane, then you need to specify: {'my_bbox': {'type': 'RectangleLabels', 'labels': {'Car': 1.0, 'Airplane': 0.5}, 'overall': 0.33}
    
</dd>
</dl>

<dl>
<dd>

**workspace:** `typing.Optional[int]` — Workspace ID
    
</dd>
</dl>

<dl>
<dd>

**model_version:** `typing.Optional[str]` — Model version
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.projects.<a href="src/label_studio_sdk/projects/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve information about a specific project by project ID. The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.projects.get(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this project.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.projects.<a href="src/label_studio_sdk/projects/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a project by specified project ID. Deleting a project permanently removes all tasks, annotations, and project data from Label Studio.

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.projects.delete(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this project.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.projects.<a href="src/label_studio_sdk/projects/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update the project settings for a specific project. For more information, see the following:

- [Create and configure projects](https://labelstud.io/guide/setup_project)
- [Configure labeling interface](https://labelstud.io/guide/setup)
- [Project settings](https://labelstud.io/guide/project_settings)

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](list).

<Warning>
If you are modifying the labeling config for project that has in-progress work, note the following:
* You cannot remove labels or change the type of labeling being performed unless you delete any existing annotations that are using those labels. 
* If you make changes to the labeling configuration, any tabs that you might have created in the Data Manager are removed.
</Warning>
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.projects.update(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this project.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Project title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Project description
    
</dd>
</dl>

<dl>
<dd>

**label_config:** `typing.Optional[str]` — Label config in XML format
    
</dd>
</dl>

<dl>
<dd>

**expert_instruction:** `typing.Optional[str]` — Labeling instructions to show to the user
    
</dd>
</dl>

<dl>
<dd>

**show_instruction:** `typing.Optional[bool]` — Show labeling instructions
    
</dd>
</dl>

<dl>
<dd>

**show_skip_button:** `typing.Optional[bool]` — Show skip button
    
</dd>
</dl>

<dl>
<dd>

**enable_empty_annotation:** `typing.Optional[bool]` — Allow empty annotations
    
</dd>
</dl>

<dl>
<dd>

**show_annotation_history:** `typing.Optional[bool]` — Show annotation history
    
</dd>
</dl>

<dl>
<dd>

**reveal_preannotations_interactively:** `typing.Optional[bool]` — Reveal preannotations interactively. If set to True, predictions will be shown to the user only after selecting the area of interest
    
</dd>
</dl>

<dl>
<dd>

**show_collab_predictions:** `typing.Optional[bool]` — Show predictions to annotators
    
</dd>
</dl>

<dl>
<dd>

**maximum_annotations:** `typing.Optional[int]` — Maximum annotations per task
    
</dd>
</dl>

<dl>
<dd>

**color:** `typing.Optional[str]` — Project color in HEX format
    
</dd>
</dl>

<dl>
<dd>

**control_weights:** `typing.Optional[typing.Dict[str, typing.Any]]` — Dict of weights for each control tag in metric calculation. Each control tag (e.g. label or choice) will have its own key in control weight dict with weight for each label and overall weight. For example, if a bounding box annotation with a control tag named my_bbox should be included with 0.33 weight in agreement calculation, and the first label Car should be twice as important as Airplane, then you need to specify: {'my_bbox': {'type': 'RectangleLabels', 'labels': {'Car': 1.0, 'Airplane': 0.5}, 'overall': 0.33}
    
</dd>
</dl>

<dl>
<dd>

**workspace:** `typing.Optional[int]` — Workspace ID
    
</dd>
</dl>

<dl>
<dd>

**model_version:** `typing.Optional[str]` — Model version
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.projects.<a href="src/label_studio_sdk/projects/client.py">import_tasks</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Use this API endpoint to import labeling tasks in bulk. Note that each POST request is limited at 250K tasks and 200 MB.
The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list).

<Note>
Imported data is verified against a project *label_config* and must include all variables that were used in the *label_config*.

For example, if the label configuration has a _$text_ variable, then each item in a data object must include a `text` field.
</Note>

There are three possible ways to import tasks with this endpoint:

#### 1\. **POST with data**

Send JSON tasks as POST data. Only JSON is supported for POSTing files directly.

Update this example to specify your authorization token and Label Studio instance host, then run the following from
the command line:

```bash
curl -H 'Content-Type: application/json' -H 'Authorization: Token abc123' \
-X POST 'https://localhost:8080/api/projects/1/import' --data '[{"text": "Some text 1"}, {"text": "Some text 2"}]'
```

#### 2\. **POST with files**

Send tasks as files. You can attach multiple files with different names.

- **JSON**: text files in JavaScript object notation format
- **CSV**: text files with tables in Comma Separated Values format
- **TSV**: text files with tables in Tab Separated Value format
- **TXT**: simple text files are similar to CSV with one column and no header, supported for projects with one source only

Update this example to specify your authorization token, Label Studio instance host, and file name and path,
then run the following from the command line:

```bash
curl -H 'Authorization: Token abc123' \
-X POST 'https://localhost:8080/api/projects/1/import' -F ‘file=@path/to/my_file.csv’
```

#### 3\. **POST with URL**

You can also provide a URL to a file with labeling tasks. Supported file formats are the same as in option 2.

```bash
curl -H 'Content-Type: application/json' -H 'Authorization: Token abc123' \
-X POST 'https://localhost:8080/api/projects/1/import' \
--data '[{"url": "http://example.com/test1.csv"}, {"url": "http://example.com/test2.csv"}]'
```

<br>
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.projects.import_tasks(
    id=1,
    request=[{"key": "value"}],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this project.
    
</dd>
</dl>

<dl>
<dd>

**request:** `typing.Sequence[typing.Dict[str, typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**commit_to_project:** `typing.Optional[bool]` — Set to "true" to immediately commit tasks to the project.
    
</dd>
</dl>

<dl>
<dd>

**return_task_ids:** `typing.Optional[bool]` — Set to "true" to return task IDs in the response.
    
</dd>
</dl>

<dl>
<dd>

**preannotated_from_fields:** `typing.Optional[typing.Union[str, typing.Sequence[str]]]` — List of fields to preannotate from the task data. For example, if you provide a list of `{"text": "text", "prediction": "label"}` items in the request, the system will create a task with the `text` field and a prediction with the `label` field when `preannoted_from_fields=["prediction"]`.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.projects.<a href="src/label_studio_sdk/projects/client.py">validate_config</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Determine whether the label configuration for a specific project is valid. For more information about setting up labeling configs, see [Configure labeling interface](https://labelstud.io/guide/setup) and our [Tags reference](https://labelstud.io/tags/).

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.projects.validate_config(
    id=1,
    label_config="label_config",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this project.
    
</dd>
</dl>

<dl>
<dd>

**label_config:** `str` — Label config in XML format. See more about it in documentation
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Ml
<details><summary><code>client.ml.<a href="src/label_studio_sdk/ml/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all configured Machine Learning (ML) backends for a specific project by ID. For more information about ML backends, see [Machine learning integration](https://labelstud.io/guide/ml).

You will need to provide the project ID. This can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.ml.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.ml.<a href="src/label_studio_sdk/ml/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Add an ML backend to a project. For more information about what you need to configure when adding an ML backend, see [Connect the model to Label studio](https://labelstud.io/guide/ml#Connect-the-model-to-Label-Studio).

<Note>If you are using Docker Compose, you may need to adjust your ML backend URL. See [localhost and Docker containers](https://labelstud.io/guide/ml#localhost-and-Docker-containers).</Note>

<Note>If you are using files that are located in the cloud, local storage, or uploaded to Label Studio, you must configure your environment variables to allow the ML backend to interact with those files. See [Allow the ML backend to access Label Studio](https://labelstud.io/guide/ml#Allow-the-ML-backend-to-access-Label-Studio-data).</Note>
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.ml.create()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**url:** `typing.Optional[str]` — ML backend URL
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**is_interactive:** `typing.Optional[bool]` — Is interactive
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Description
    
</dd>
</dl>

<dl>
<dd>

**auth_method:** `typing.Optional[MlCreateRequestAuthMethod]` — Auth method
    
</dd>
</dl>

<dl>
<dd>

**basic_auth_user:** `typing.Optional[str]` — Basic auth user
    
</dd>
</dl>

<dl>
<dd>

**basic_auth_pass:** `typing.Optional[str]` — Basic auth password
    
</dd>
</dl>

<dl>
<dd>

**extra_params:** `typing.Optional[typing.Dict[str, typing.Any]]` — Extra parameters
    
</dd>
</dl>

<dl>
<dd>

**timeout:** `typing.Optional[int]` — Response model timeout
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.ml.<a href="src/label_studio_sdk/ml/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get details about a specific ML backend. You will need to specify an ID for the backend connection. You can find this using [List ML backends](list).

For more information, see [Machine learning integration](https://labelstud.io/guide/ml).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.ml.get(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this ml backend.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.ml.<a href="src/label_studio_sdk/ml/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Remove an existing ML backend connection. You will need to specify an ID for the backend connection. You can find this using [List ML backends](list).

For more information, see [Machine learning integration](https://labelstud.io/guide/ml).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.ml.delete(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this ml backend.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.ml.<a href="src/label_studio_sdk/ml/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update the ML backend parameters. You will need to specify an ID for the backend connection. You can find this using [List ML backends](list).

For more information, see [Machine learning integration](https://labelstud.io/guide/ml).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.ml.update(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this ml backend.
    
</dd>
</dl>

<dl>
<dd>

**url:** `typing.Optional[str]` — ML backend URL
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**is_interactive:** `typing.Optional[bool]` — Is interactive
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Description
    
</dd>
</dl>

<dl>
<dd>

**auth_method:** `typing.Optional[MlUpdateRequestAuthMethod]` — Auth method
    
</dd>
</dl>

<dl>
<dd>

**basic_auth_user:** `typing.Optional[str]` — Basic auth user
    
</dd>
</dl>

<dl>
<dd>

**basic_auth_pass:** `typing.Optional[str]` — Basic auth password
    
</dd>
</dl>

<dl>
<dd>

**extra_params:** `typing.Optional[typing.Dict[str, typing.Any]]` — Extra parameters
    
</dd>
</dl>

<dl>
<dd>

**timeout:** `typing.Optional[int]` — Response model timeout
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.ml.<a href="src/label_studio_sdk/ml/client.py">predict_interactive</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Enable interactive pre-annotations for a specific task.

ML-assisted labeling with interactive pre-annotations works with image segmentation and object detection tasks using rectangles, ellipses, polygons, brush masks, and keypoints, as well as with HTML and text named entity recognition tasks. Your ML backend must support the type of labeling that you’re performing, recognize the input that you create, and be able to respond with the relevant output for a prediction. For more information, see [Interactive pre-annotations](https://labelstud.io/guide/ml.html#Interactive-pre-annotations).

Before you can use interactive annotations, it must be enabled for you ML backend connection (`"is_interactive": true`).

You will need the task ID and the ML backend connection ID. The task ID is available from the Label Studio URL when viewing the task, or you can retrieve it programmatically with [Get task list](../tasks/list). The ML backend connection ID is available via [List ML backends](list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.ml.predict_interactive(
    id=1,
    task=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this ML backend.
    
</dd>
</dl>

<dl>
<dd>

**task:** `int` — ID of task to annotate
    
</dd>
</dl>

<dl>
<dd>

**context:** `typing.Optional[typing.Dict[str, typing.Any]]` — Context for ML model
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.ml.<a href="src/label_studio_sdk/ml/client.py">train</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

After you connect a model to Label Studio as a machine learning backend and annotate at least one task, you can start training the model. Training logs appear in stdout and the console.

For more information, see [Model training](https://labelstud.io/guide/ml.html#Model-training).

You will need to specify an ID for the backend connection. You can find this using [List ML backends](list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.ml.train(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this ML backend.
    
</dd>
</dl>

<dl>
<dd>

**use_ground_truth:** `typing.Optional[bool]` — Whether to include ground truth annotations in training
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.ml.<a href="src/label_studio_sdk/ml/client.py">list_model_versions</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get available versions of the model. You will need to specify an ID for the backend connection. You can find this using [List ML backends](list).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.ml.list_model_versions(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Predictions
<details><summary><code>client.predictions.<a href="src/label_studio_sdk/predictions/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a list of all predictions. You can optionally filter these by task or by project. If you want to filter, you will need the project ID and/or task ID. Both of these can be found in the Label Studio URL when viewing a task, or you can use [List all projects](../projects/list) and [Get tasks list](../tasks/list).

<Note>The terms "predictions" and pre-annotations" are used interchangeably.</Note>

Predictions can be [imported directly into Label Studio](https://labelstud.io/guide/predictions) or [generated by a connected ML backend](https://labelstud.io/guide/ml.html#Pre-annotations-predictions).

To import predictions via the API, see [Create prediction](create).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.predictions.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**task:** `typing.Optional[int]` — Filter predictions by task ID
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Filter predictions by project ID
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.predictions.<a href="src/label_studio_sdk/predictions/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

If you have predictions generated for your dataset from a model, either as pre-annotated tasks or pre-labeled tasks, you can import the predictions with your dataset into Label Studio for review and correction.

To import predicted labels into Label Studio, you must use the [Basic Label Studio JSON format](https://labelstud.io/guide/tasks#Basic-Label-Studio-JSON-format) and set up your tasks with the predictions JSON key. The Label Studio ML backend also outputs tasks in this format.

#### JSON format for predictions

Label Studio JSON format for pre-annotations must contain two sections:

- A data object which references the source of the data that the pre-annotations apply to. This can be a URL to an audio file, a pre-signed cloud storage link to an image, plain text, a reference to a CSV file stored in Label Studio, or something else.
- A predictions array that contains the pre-annotation results for the different types of labeling. See how to add results to the predictions array.

For more information, see [the JSON format reference in the Label Studio documentation](https://labelstud.io/guide/predictions#JSON-format-for-pre-annotations)
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.predictions.create(
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
    score=0.95,
    model_version="yolo-v8",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**task:** `typing.Optional[int]` — Task ID for which the prediction is created
    
</dd>
</dl>

<dl>
<dd>

**result:** `typing.Optional[typing.Sequence[typing.Dict[str, typing.Any]]]` — Prediction result in JSON format. Read more about the format in [the Label Studio documentation.](https://labelstud.io/guide/predictions)
    
</dd>
</dl>

<dl>
<dd>

**score:** `typing.Optional[float]` — Prediction score. Can be used in Data Manager to sort task by model confidence. Task with the lowest score will be shown first.
    
</dd>
</dl>

<dl>
<dd>

**model_version:** `typing.Optional[str]` — Model version - tag for predictions that can be used to filter tasks in Data Manager, as well as select specific model version for showing preannotations in the labeling interface
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.predictions.<a href="src/label_studio_sdk/predictions/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get details about a specific prediction by its ID. To find the prediction ID, use [List predictions](list).

For information about the prediction format, see [the JSON format reference in the Label Studio documentation](https://labelstud.io/guide/predictions#JSON-format-for-pre-annotations).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk.client import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
)
client.predictions.get(
    id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `int` — Prediction ID
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.predictions.<a href="src/label_studio_sdk/predictions/client.py">delete</a>(...)</code></summary>
