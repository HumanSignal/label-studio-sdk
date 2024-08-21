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
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a prediction. To find the prediction ID, use [List predictions](list).
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
client.predictions.delete(
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

<details><summary><code>client.predictions.<a href="src/label_studio_sdk/predictions/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a prediction. To find the prediction ID, use [List predictions](list).

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
client.predictions.update(
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

**id:** `int` — Prediction ID
    
</dd>
</dl>

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

## Projects Exports
<details><summary><code>client.projects.exports.<a href="src/label_studio_sdk/projects/exports/client.py">create_export</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

<Note>If you have a large project it's recommended to use export snapshots, this easy export endpoint might have timeouts.</Note>
Export annotated tasks as a file in a specific format.
For example, to export JSON annotations for a project to a file called `annotations.json`,
run the following from the command line:

```bash
curl -X GET https://localhost:8080/api/projects/{id}/export?exportType=JSON -H 'Authorization: Token abc123' --output 'annotations.json'
```

To export all tasks, including skipped tasks and others without annotations, run the following from the command line:

```bash
curl -X GET https://localhost:8080/api/projects/{id}/export?exportType=JSON&download_all_tasks=true -H 'Authorization: Token abc123' --output 'annotations.json'
```

To export specific tasks with IDs of 123 and 345, run the following from the command line:

```bash
curl -X GET https://localhost:8080/api/projects/{id}/export?ids[]=123\&ids[]=345 -H 'Authorization: Token abc123' --output 'annotations.json'
```

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
client.projects.exports.create_export(
    id=1,
    export_type="string",
    download_all_tasks="string",
    download_resources=True,
    ids=1,
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

**export_type:** `typing.Optional[str]` — Selected export format (JSON by default)
    
</dd>
</dl>

<dl>
<dd>

**download_all_tasks:** `typing.Optional[str]` — If true, download all tasks regardless of status. If false, download only annotated tasks.
    
</dd>
</dl>

<dl>
<dd>

**download_resources:** `typing.Optional[bool]` — If true, download all resource files such as images, audio, and others relevant to the tasks.
    
</dd>
</dl>

<dl>
<dd>

**ids:** `typing.Optional[typing.Union[int, typing.Sequence[int]]]` — Specify a list of task IDs to retrieve only the details for those tasks.
    
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

<details><summary><code>client.projects.exports.<a href="src/label_studio_sdk/projects/exports/client.py">list_formats</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Before exporting annotations, you can check with formats are supported by the specified project. For more information about export formats, see [Export formats supported by Label Studio](https://labelstud.io/guide/export#Export-formats-supported-by-Label-Studio).

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
client.projects.exports.list_formats(
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

<details><summary><code>client.projects.exports.<a href="src/label_studio_sdk/projects/exports/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns a list of export file (snapshots) for a specific project by ID. The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../list).

Included in the response is information about each snapshot, such as who created it and what format it is in.
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
client.projects.exports.list(
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

<details><summary><code>client.projects.exports.<a href="src/label_studio_sdk/projects/exports/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new export request to start a background task and generate an export file (snapshot) for a specific project by ID. The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../list).

A snapshot is a static export of your project's data and annotations at a specific point in time. It captures the current state of your tasks, annotations, and other relevant data, allowing you to download and review them later. Snapshots are particularly useful for large projects as they help avoid timeouts during export operations by processing the data asynchronously.

For more information, see the [Label Studio documentation on exporting annotations](https://labelstud.io/guide/export.html).
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
client.projects.exports.create(
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

**id_:** `int` — A unique integer value identifying this project.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**id:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**created_by:** `typing.Optional[UserSimple]` 
    
</dd>
</dl>

<dl>
<dd>

**created_at:** `typing.Optional[dt.datetime]` — Creation time
    
</dd>
</dl>

<dl>
<dd>

**finished_at:** `typing.Optional[dt.datetime]` — Complete or fail time
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[ExportCreateStatus]` 
    
</dd>
</dl>

<dl>
<dd>

**md5:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**counters:** `typing.Optional[typing.Dict[str, typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**converted_formats:** `typing.Optional[typing.Sequence[ConvertedFormat]]` 
    
</dd>
</dl>

<dl>
<dd>

**task_filter_options:** `typing.Optional[TaskFilterOptions]` 
    
</dd>
</dl>

<dl>
<dd>

**annotation_filter_options:** `typing.Optional[AnnotationFilterOptions]` 
    
</dd>
</dl>

<dl>
<dd>

**serialization_options:** `typing.Optional[SerializationOptions]` 
    
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

<details><summary><code>client.projects.exports.<a href="src/label_studio_sdk/projects/exports/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve information about a specific export file (snapshot).

You will need the export ID. You can find this in the response when you [create the snapshot via the API](create) or using [List all export snapshots](list).

You will also need the project ID. This can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../list).
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
client.projects.exports.get(
    id=1,
    export_pk="export_pk",
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

**export_pk:** `str` — Primary key identifying the export file.
    
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

<details><summary><code>client.projects.exports.<a href="src/label_studio_sdk/projects/exports/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete an export file by specified export ID.

You will need the export ID. You can find this in the response when you [create the snapshot via the API](create) or using [List all export snapshots](list).
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
client.projects.exports.delete(
    id=1,
    export_pk="export_pk",
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

**export_pk:** `str` — Primary key identifying the export file.
    
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

<details><summary><code>client.projects.exports.<a href="src/label_studio_sdk/projects/exports/client.py">convert</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

You can use this to convert an export snapshot into the selected format.

To see what formats are supported, you can use [Get export formats](list-formats) or see [Export formats supported by Label Studio](https://labelstud.io/guide/export#Export-formats-supported-by-Label-Studio).

You will need to provide the project ID and export ID (`export_pk`). The export ID is returned when you create the export or you can use [List all export snapshots](list).

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../list).
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
client.projects.exports.convert(
    id=1,
    export_pk="export_pk",
    export_type="export_type",
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

**export_pk:** `str` — Primary key identifying the export file.
    
</dd>
</dl>

<dl>
<dd>

**export_type:** `str` — Export file format.
    
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

<details><summary><code>client.projects.exports.<a href="src/label_studio_sdk/projects/exports/client.py">download</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Download an export snapshot as a file in a specified format. To see what formats are supported, you can use [Get export formats](list-formats) or see [Export formats supported by Label Studio](https://labelstud.io/guide/export#Export-formats-supported-by-Label-Studio).

You will need to provide the project ID and export ID (`export_pk`). The export ID is returned when you create the export or you can use [List all export snapshots](list).

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../list).
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
client.projects.exports.download(
    id=1,
    export_pk="export_pk",
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

**export_pk:** `str` — Primary key identifying the export file.
    
</dd>
</dl>

<dl>
<dd>

**export_type:** `typing.Optional[str]` — Selected export format
    
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

## Tasks
<details><summary><code>client.tasks.<a href="src/label_studio_sdk/tasks/client.py">create_many_status</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get information about an async project import operation. This can be especially useful to monitor status, as large import jobs can take time.

You will need the project ID and the unique ID of the import operation.

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list).

The import ID is returned as part of the response when you call [Import tasks](import-tasks).
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
client.tasks.create_many_status(
    id=1,
    import_pk="import_pk",
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

**id:** `int` — The project ID.
    
</dd>
</dl>

<dl>
<dd>

**import_pk:** `str` 
    
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

<details><summary><code>client.tasks.<a href="src/label_studio_sdk/tasks/client.py">delete_all_tasks</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete all tasks from a specific project.

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list).
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
client.tasks.delete_all_tasks(
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

<details><summary><code>client.tasks.<a href="src/label_studio_sdk/tasks/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a list of tasks.

You can use the query parameters to filter the list by project and/or view (a tab within the Data Manager). You can also optionally add pagination to make the response easier to parse.

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list). The view ID can be found using [List views](../views/list).
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
response = client.tasks.list()
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

**view:** `typing.Optional[int]` — View ID
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**resolve_uri:** `typing.Optional[bool]` — Resolve task data URIs using Cloud Storage
    
</dd>
</dl>

<dl>
<dd>

**fields:** `typing.Optional[TasksListRequestFields]` — Set to "all" if you want to include annotations and predictions in the response
    
</dd>
</dl>

<dl>
<dd>

**review:** `typing.Optional[bool]` — Get tasks for review
    
</dd>
</dl>

<dl>
<dd>

**include:** `typing.Optional[str]` — Specify which fields to include in the response
    
</dd>
</dl>

<dl>
<dd>

**query:** `typing.Optional[str]` 

Additional query to filter tasks. It must be JSON encoded string of dict containing one of the following parameters: `{"filters": ..., "selectedItems": ..., "ordering": ...}`. Check [Data Manager > Create View > see `data` field](#tag/Data-Manager/operation/api_dm_views_create) for more details about filters, selectedItems and ordering.

- **filters**: dict with `"conjunction"` string (`"or"` or `"and"`) and list of filters in `"items"` array. Each filter is a dictionary with keys: `"filter"`, `"operator"`, `"type"`, `"value"`. [Read more about available filters](https://labelstud.io/sdk/data_manager.html)<br/> Example: `{"conjunction": "or", "items": [{"filter": "filter:tasks:completed_at", "operator": "greater", "type": "Datetime", "value": "2021-01-01T00:00:00.000Z"}]}`
- **selectedItems**: dictionary with keys: `"all"`, `"included"`, `"excluded"`. If "all" is `false`, `"included"` must be used. If "all" is `true`, `"excluded"` must be used.<br/> Examples: `{"all": false, "included": [1, 2, 3]}` or `{"all": true, "excluded": [4, 5]}`
- **ordering**: list of fields to order by. Currently, ordering is supported by only one parameter. <br/>
  Example: `["completed_at"]`
    
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

<details><summary><code>client.tasks.<a href="src/label_studio_sdk/tasks/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new labeling task in Label Studio.

The data you provide depends on your labeling config and data type.

You will also need to provide a project ID. The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list).
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
client.tasks.create(
    data={"image": "https://example.com/image.jpg", "text": "Hello, world!"},
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

**data:** `typing.Optional[typing.Dict[str, typing.Any]]` — Task data dictionary with arbitrary keys and values
    
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

<details><summary><code>client.tasks.<a href="src/label_studio_sdk/tasks/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get task data, metadata, annotations and other attributes for a specific labeling task by task ID.
The task ID is available from the Label Studio URL when viewing the task, or you can retrieve it programmatically with [Get task list](list).
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
client.tasks.get(
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

**id:** `str` — Task ID
    
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

<details><summary><code>client.tasks.<a href="src/label_studio_sdk/tasks/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a task in Label Studio.

You will need the task ID. This is available from the Label Studio URL when viewing the task, or you can retrieve it programmatically with [Get task list](list).

<Warning>This action cannot be undone.</Warning>
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
client.tasks.delete(
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

**id:** `str` — Task ID
    
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

<details><summary><code>client.tasks.<a href="src/label_studio_sdk/tasks/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update the attributes of an existing labeling task.

You will need the task ID. This is available from the Label Studio URL when viewing the task, or you can retrieve it programmatically with [Get task list](list).
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
client.tasks.update(
    id="id",
    data={"image": "https://example.com/image.jpg", "text": "Hello, world!"},
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

**id:** `str` — Task ID
    
</dd>
</dl>

<dl>
<dd>

**data:** `typing.Optional[typing.Dict[str, typing.Any]]` — Task data dictionary with arbitrary keys and values
    
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

## ImportStorage
<details><summary><code>client.import_storage.<a href="src/label_studio_sdk/import_storage/client.py">list_types</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a list of the import storages types.
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
client.import_storage.list_types()

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

## ImportStorage Azure
<details><summary><code>client.import_storage.azure.<a href="src/label_studio_sdk/import_storage/azure/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

You can connect your Microsoft Azure Blob storage container to Label Studio as a source storage or target storage. Use this API request to get a list of all Azure import (source) storage connections for a specific project.

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.import_storage.azure.list()

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

<details><summary><code>client.import_storage.azure.<a href="src/label_studio_sdk/import_storage/azure/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new source storage connection to Microsoft Azure Blob storage.

For information about the required fields and prerequisites, see [Microsoft Azure Blob storage](https://labelstud.io/guide/storage#Microsoft-Azure-Blob-storage) in the Label Studio documentation.

<Info>Ensure you configure CORS before adding cloud storage. This ensures you will be able to see the content of the data rather than just a link.</Info>

<Tip>After you add the storage, you should validate the connection before attempting to sync your data. Your data will not be imported until you [sync your connection](sync).</Tip>
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
client.import_storage.azure.create()

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

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects. You must specify it otherwise no objects will be imported.
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your bucket contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
</dd>
</dl>

<dl>
<dd>

**presign:** `typing.Optional[bool]` — Presign URLs for direct download
    
</dd>
</dl>

<dl>
<dd>

**presign_ttl:** `typing.Optional[int]` — Presign TTL in minutes
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**container:** `typing.Optional[str]` — Azure blob container
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — Azure blob prefix name
    
</dd>
</dl>

<dl>
<dd>

**account_name:** `typing.Optional[str]` — Azure Blob account name
    
</dd>
</dl>

<dl>
<dd>

**account_key:** `typing.Optional[str]` — Azure Blob account key
    
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

<details><summary><code>client.import_storage.azure.<a href="src/label_studio_sdk/import_storage/azure/client.py">validate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Validate a specific Azure import storage connection. This is useful to ensure that the storage configuration settings are correct and operational before attempting to import data.
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
client.import_storage.azure.validate()

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

**id:** `typing.Optional[int]` — Storage ID. If set, storage with specified ID will be updated
    
</dd>
</dl>

<dl>
<dd>

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects. You must specify it otherwise no objects will be imported.
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your bucket contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
</dd>
</dl>

<dl>
<dd>

**presign:** `typing.Optional[bool]` — Presign URLs for direct download
    
</dd>
</dl>

<dl>
<dd>

**presign_ttl:** `typing.Optional[int]` — Presign TTL in minutes
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**container:** `typing.Optional[str]` — Azure blob container
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — Azure blob prefix name
    
</dd>
</dl>

<dl>
<dd>

**account_name:** `typing.Optional[str]` — Azure Blob account name
    
</dd>
</dl>

<dl>
<dd>

**account_key:** `typing.Optional[str]` — Azure Blob account key
    
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

<details><summary><code>client.import_storage.azure.<a href="src/label_studio_sdk/import_storage/azure/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific Azure import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.import_storage.azure.get(
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

**id:** `int` — A unique integer value identifying this azure blob import storage.
    
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

<details><summary><code>client.import_storage.azure.<a href="src/label_studio_sdk/import_storage/azure/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific Azure import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

Deleting a source storage connection does not affect tasks with synced data in Label Studio. The sync process is designed to import new or updated tasks from the connected storage into the project, but it does not track deletions of files from the storage. Therefore, if you remove the external storage connection, the tasks that were created from that storage will remain in the project.

If you want to remove the tasks that were synced from the external storage, you will need to delete them manually from within the Label Studio UI or use the [Delete tasks](../../tasks/delete-all-tasks) API.
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
client.import_storage.azure.delete(
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

**id:** `int` — A unique integer value identifying this azure blob import storage.
    
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

<details><summary><code>client.import_storage.azure.<a href="src/label_studio_sdk/import_storage/azure/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific Azure import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.import_storage.azure.update(
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

**id:** `int` — A unique integer value identifying this azure blob import storage.
    
</dd>
</dl>

<dl>
<dd>

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects. You must specify it otherwise no objects will be imported.
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your bucket contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
</dd>
</dl>

<dl>
<dd>

**presign:** `typing.Optional[bool]` — Presign URLs for direct download
    
</dd>
</dl>

<dl>
<dd>

**presign_ttl:** `typing.Optional[int]` — Presign TTL in minutes
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**container:** `typing.Optional[str]` — Azure blob container
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — Azure blob prefix name
    
</dd>
</dl>

<dl>
<dd>

**account_name:** `typing.Optional[str]` — Azure Blob account name
    
</dd>
</dl>

<dl>
<dd>

**account_key:** `typing.Optional[str]` — Azure Blob account key
    
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

<details><summary><code>client.import_storage.azure.<a href="src/label_studio_sdk/import_storage/azure/client.py">sync</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Sync tasks from an Azure import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

Sync operations with external containers only go one way. They either create tasks from objects in the container (source/import storage) or push annotations to the output container (export/target storage). Changing something on the Microsoft side doesn’t guarantee consistency in results.

<Note>Before proceeding, you should review [How sync operations work - Source storage](https://labelstud.io/guide/storage#Source-storage) to ensure that your data remains secure and private.</Note>
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
client.import_storage.azure.sync(
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

**id:** `int` — Storage ID
    
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

## ExportStorage
<details><summary><code>client.export_storage.<a href="src/label_studio_sdk/export_storage/client.py">list_types</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a list of the export storages types.
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
client.export_storage.list_types()

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

## ExportStorage Azure
<details><summary><code>client.export_storage.azure.<a href="src/label_studio_sdk/export_storage/azure/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

You can connect your Microsoft Azure Blob storage container to Label Studio as a source storage or target storage. Use this API request to get a list of all Azure export (target) storage connections for a specific project.

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.export_storage.azure.list()

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

<details><summary><code>client.export_storage.azure.<a href="src/label_studio_sdk/export_storage/azure/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new target storage connection to Microsoft Azure Blob storage.

For information about the required fields and prerequisites, see [Microsoft Azure Blob storage](https://labelstud.io/guide/storage#Microsoft-Azure-Blob-storage) in the Label Studio documentation.

<Tip>After you add the storage, you should validate the connection before attempting to sync your data. Your data will not be exported until you [sync your connection](sync).</Tip>
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
client.export_storage.azure.create()

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

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**container:** `typing.Optional[str]` — Azure blob container
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — Azure blob prefix name
    
</dd>
</dl>

<dl>
<dd>

**account_name:** `typing.Optional[str]` — Azure Blob account name
    
</dd>
</dl>

<dl>
<dd>

**account_key:** `typing.Optional[str]` — Azure Blob account key
    
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

<details><summary><code>client.export_storage.azure.<a href="src/label_studio_sdk/export_storage/azure/client.py">validate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Validate a specific Azure export storage connection. This is useful to ensure that the storage configuration settings are correct and operational before attempting to export data.
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
client.export_storage.azure.validate()

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

**id:** `typing.Optional[int]` — Storage ID. If set, storage with specified ID will be updated
    
</dd>
</dl>

<dl>
<dd>

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**container:** `typing.Optional[str]` — Azure blob container
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — Azure blob prefix name
    
</dd>
</dl>

<dl>
<dd>

**account_name:** `typing.Optional[str]` — Azure Blob account name
    
</dd>
</dl>

<dl>
<dd>

**account_key:** `typing.Optional[str]` — Azure Blob account key
    
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

<details><summary><code>client.export_storage.azure.<a href="src/label_studio_sdk/export_storage/azure/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific Azure export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.export_storage.azure.get(
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

**id:** `int` — A unique integer value identifying this azure blob export storage.
    
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

<details><summary><code>client.export_storage.azure.<a href="src/label_studio_sdk/export_storage/azure/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific Azure export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

Deleting an export/target storage connection does not affect tasks with synced data in Label Studio. If you want to remove the tasks that were synced from the external storage, you will need to delete them manually from within the Label Studio UI or use the [Delete tasks](../../tasks/delete-all-tasks) API.
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
client.export_storage.azure.delete(
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

**id:** `int` — A unique integer value identifying this azure blob export storage.
    
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

<details><summary><code>client.export_storage.azure.<a href="src/label_studio_sdk/export_storage/azure/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific Azure export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.export_storage.azure.update(
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

**id:** `int` — A unique integer value identifying this azure blob export storage.
    
</dd>
</dl>

<dl>
<dd>

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**container:** `typing.Optional[str]` — Azure blob container
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — Azure blob prefix name
    
</dd>
</dl>

<dl>
<dd>

**account_name:** `typing.Optional[str]` — Azure Blob account name
    
</dd>
</dl>

<dl>
<dd>

**account_key:** `typing.Optional[str]` — Azure Blob account key
    
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

<details><summary><code>client.export_storage.azure.<a href="src/label_studio_sdk/export_storage/azure/client.py">sync</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Sync tasks to an Azure export/target storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

Sync operations with external containers only go one way. They either create tasks from objects in the container (source/import storage) or push annotations to the output container (export/target storage). Changing something on the Microsoft side doesn’t guarantee consistency in results.

<Note>Before proceeding, you should review [How sync operations work - Source storage](https://labelstud.io/guide/storage#Source-storage) to ensure that your data remains secure and private.</Note>
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
client.export_storage.azure.sync(
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

## ExportStorage Gcs
<details><summary><code>client.export_storage.gcs.<a href="src/label_studio_sdk/export_storage/gcs/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

You can connect your Google Cloud Storage bucket to Label Studio as a source storage or target storage. Use this API request to get a list of all GCS export (target) storage connections for a specific project.

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.export_storage.gcs.list()

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

<details><summary><code>client.export_storage.gcs.<a href="src/label_studio_sdk/export_storage/gcs/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new target storage connection to Google Cloud Storage.

For information about the required fields and prerequisites, see [Google Cloud Storage](https://labelstud.io/guide/storage#Google-Cloud-Storage) in the Label Studio documentation.

<Tip>After you add the storage, you should validate the connection before attempting to sync your data. Your data will not be exported until you [sync your connection](sync).</Tip>
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
client.export_storage.gcs.create()

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

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — GCS bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — GCS bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**google_application_credentials:** `typing.Optional[str]` — The content of GOOGLE_APPLICATION_CREDENTIALS json file. Check official Google Cloud Authentication documentation for more details.
    
</dd>
</dl>

<dl>
<dd>

**google_project_id:** `typing.Optional[str]` — Google project ID
    
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

<details><summary><code>client.export_storage.gcs.<a href="src/label_studio_sdk/export_storage/gcs/client.py">validate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Validate a specific GCS export storage connection. This is useful to ensure that the storage configuration settings are correct and operational before attempting to export data.
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
client.export_storage.gcs.validate()

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

**id:** `typing.Optional[int]` — Storage ID. If set, storage with specified ID will be updated
    
</dd>
</dl>

<dl>
<dd>

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — GCS bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — GCS bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**google_application_credentials:** `typing.Optional[str]` — The content of GOOGLE_APPLICATION_CREDENTIALS json file. Check official Google Cloud Authentication documentation for more details.
    
</dd>
</dl>

<dl>
<dd>

**google_project_id:** `typing.Optional[str]` — Google project ID
    
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

<details><summary><code>client.export_storage.gcs.<a href="src/label_studio_sdk/export_storage/gcs/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific GCS export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.export_storage.gcs.get(
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

**id:** `int` — A unique integer value identifying this gcs export storage.
    
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

<details><summary><code>client.export_storage.gcs.<a href="src/label_studio_sdk/export_storage/gcs/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific GCS export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

Deleting an export/target storage connection does not affect tasks with synced data in Label Studio. If you want to remove the tasks that were synced from the external storage, you will need to delete them manually from within the Label Studio UI or use the [Delete tasks](../../tasks/delete-all-tasks) API.
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
client.export_storage.gcs.delete(
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

**id:** `int` — A unique integer value identifying this gcs export storage.
    
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

<details><summary><code>client.export_storage.gcs.<a href="src/label_studio_sdk/export_storage/gcs/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific GCS export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.export_storage.gcs.update(
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

**id:** `int` — A unique integer value identifying this gcs export storage.
    
</dd>
</dl>

<dl>
<dd>

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — GCS bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — GCS bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**google_application_credentials:** `typing.Optional[str]` — The content of GOOGLE_APPLICATION_CREDENTIALS json file. Check official Google Cloud Authentication documentation for more details.
    
</dd>
</dl>

<dl>
<dd>

**google_project_id:** `typing.Optional[str]` — Google project ID
    
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

<details><summary><code>client.export_storage.gcs.<a href="src/label_studio_sdk/export_storage/gcs/client.py">sync</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Sync tasks to a GCS export/target storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

Sync operations with external buckets only go one way. They either create tasks from objects in the bucket (source/import storage) or push annotations to the output bucket (export/target storage). Changing something on the bucket side doesn’t guarantee consistency in results.

<Note>Before proceeding, you should review [How sync operations work - Source storage](https://labelstud.io/guide/storage#Source-storage) to ensure that your data remains secure and private.</Note>
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
client.export_storage.gcs.sync(
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

## ExportStorage Local
<details><summary><code>client.export_storage.local.<a href="src/label_studio_sdk/export_storage/local/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

You can connect a local file directory to Label Studio as a source storage or target storage. Use this API request to get a list of all local file export (target) storage connections for a specific project.

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.export_storage.local.list()

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

<details><summary><code>client.export_storage.local.<a href="src/label_studio_sdk/export_storage/local/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new target storage connection to a local file directory.

For information about the required fields and prerequisites, see [Local storage](https://labelstud.io/guide/storage#Local-storage) in the Label Studio documentation.

<Tip>After you add the storage, you should validate the connection before attempting to sync your data. Your data will not be exported until you [sync your connection](sync).</Tip>
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
client.export_storage.local.create()

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

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**path:** `typing.Optional[str]` — Path to local directory
    
</dd>
</dl>

<dl>
<dd>

**regex_filter:** `typing.Optional[str]` — Regex for filtering objects
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your directory contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
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

<details><summary><code>client.export_storage.local.<a href="src/label_studio_sdk/export_storage/local/client.py">validate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Validate a specific local file export storage connection. This is useful to ensure that the storage configuration settings are correct and operational before attempting to export data.
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
client.export_storage.local.validate()

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

**id:** `typing.Optional[int]` — Storage ID. If set, storage with specified ID will be updated
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**path:** `typing.Optional[str]` — Path to local directory
    
</dd>
</dl>

<dl>
<dd>

**regex_filter:** `typing.Optional[str]` — Regex for filtering objects
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your directory contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
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

<details><summary><code>client.export_storage.local.<a href="src/label_studio_sdk/export_storage/local/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific local file export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.export_storage.local.get(
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

**id:** `int` — A unique integer value identifying this local files export storage.
    
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

<details><summary><code>client.export_storage.local.<a href="src/label_studio_sdk/export_storage/local/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific local file export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

Deleting an export/target storage connection does not affect tasks with synced data in Label Studio. If you want to remove the tasks that were synced from the external storage, you will need to delete them manually from within the Label Studio UI or use the [Delete tasks](../../tasks/delete-all-tasks) API.
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
client.export_storage.local.delete(
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

**id:** `int` — A unique integer value identifying this local files export storage.
    
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

<details><summary><code>client.export_storage.local.<a href="src/label_studio_sdk/export_storage/local/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific local file export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.export_storage.local.update(
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

**id:** `int` — A unique integer value identifying this local files export storage.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**path:** `typing.Optional[str]` — Path to local directory
    
</dd>
</dl>

<dl>
<dd>

**regex_filter:** `typing.Optional[str]` — Regex for filtering objects
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your directory contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
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

<details><summary><code>client.export_storage.local.<a href="src/label_studio_sdk/export_storage/local/client.py">sync</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Sync tasks to an local file export/target storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

Sync operations with external local file directories only go one way. They either create tasks from objects in the directory (source/import storage) or push annotations to the output directory (export/target storage). Changing something on the local file side doesn’t guarantee consistency in results.

<Note>Before proceeding, you should review [How sync operations work - Source storage](https://labelstud.io/guide/storage#Source-storage) to ensure that your data remains secure and private.</Note>
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
client.export_storage.local.sync(
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

## ExportStorage Redis
<details><summary><code>client.export_storage.redis.<a href="src/label_studio_sdk/export_storage/redis/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

You can connect your Redis database to Label Studio as a source storage or target storage. Use this API request to get a list of all Redis export (target) storage connections for a specific project.

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.export_storage.redis.list()

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

<details><summary><code>client.export_storage.redis.<a href="src/label_studio_sdk/export_storage/redis/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new target storage connection to Redis.

For information about the required fields and prerequisites, see [Redis database](https://labelstud.io/guide/storage#Redis-database) in the Label Studio documentation.

<Tip>After you add the storage, you should validate the connection before attempting to sync your data. Your data will not be exported until you [sync your connection](sync).</Tip>
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
client.export_storage.redis.create()

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

**db:** `typing.Optional[int]` — Database ID of database to use
    
</dd>
</dl>

<dl>
<dd>

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**path:** `typing.Optional[str]` — Storage prefix (optional)
    
</dd>
</dl>

<dl>
<dd>

**host:** `typing.Optional[str]` — Server Host IP (optional)
    
</dd>
</dl>

<dl>
<dd>

**port:** `typing.Optional[str]` — Server Port (optional)
    
</dd>
</dl>

<dl>
<dd>

**password:** `typing.Optional[str]` — Server Password (optional)
    
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

<details><summary><code>client.export_storage.redis.<a href="src/label_studio_sdk/export_storage/redis/client.py">validate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Validate a specific Redis export storage connection. This is useful to ensure that the storage configuration settings are correct and operational before attempting to export data.
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
client.export_storage.redis.validate()

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

**id:** `typing.Optional[int]` — Storage ID. If set, storage with specified ID will be updated
    
</dd>
</dl>

<dl>
<dd>

**db:** `typing.Optional[int]` — Database ID of database to use
    
</dd>
</dl>

<dl>
<dd>

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**path:** `typing.Optional[str]` — Storage prefix (optional)
    
</dd>
</dl>

<dl>
<dd>

**host:** `typing.Optional[str]` — Server Host IP (optional)
    
</dd>
</dl>

<dl>
<dd>

**port:** `typing.Optional[str]` — Server Port (optional)
    
</dd>
</dl>

<dl>
<dd>

**password:** `typing.Optional[str]` — Server Password (optional)
    
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

<details><summary><code>client.export_storage.redis.<a href="src/label_studio_sdk/export_storage/redis/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific Redis export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.export_storage.redis.get(
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

**id:** `int` — A unique integer value identifying this redis export storage.
    
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

<details><summary><code>client.export_storage.redis.<a href="src/label_studio_sdk/export_storage/redis/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific Redis export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

Deleting an export/target storage connection does not affect tasks with synced data in Label Studio. If you want to remove the tasks that were synced from the external storage, you will need to delete them manually from within the Label Studio UI or use the [Delete tasks](../../tasks/delete-all-tasks) API.
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
client.export_storage.redis.delete(
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

**id:** `int` — A unique integer value identifying this redis export storage.
    
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

<details><summary><code>client.export_storage.redis.<a href="src/label_studio_sdk/export_storage/redis/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific Redis export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.export_storage.redis.update(
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

**id:** `int` — A unique integer value identifying this redis export storage.
    
</dd>
</dl>

<dl>
<dd>

**db:** `typing.Optional[int]` — Database ID of database to use
    
</dd>
</dl>

<dl>
<dd>

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**path:** `typing.Optional[str]` — Storage prefix (optional)
    
</dd>
</dl>

<dl>
<dd>

**host:** `typing.Optional[str]` — Server Host IP (optional)
    
</dd>
</dl>

<dl>
<dd>

**port:** `typing.Optional[str]` — Server Port (optional)
    
</dd>
</dl>

<dl>
<dd>

**password:** `typing.Optional[str]` — Server Password (optional)
    
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

<details><summary><code>client.export_storage.redis.<a href="src/label_studio_sdk/export_storage/redis/client.py">sync</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Sync tasks to an Redis export/target storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

Sync operations with external databases only go one way. They either create tasks from objects in the database (source/import storage) or push annotations to the output database (export/target storage). Changing something on the database side doesn’t guarantee consistency in results.

<Note>Before proceeding, you should review [How sync operations work - Source storage](https://labelstud.io/guide/storage#Source-storage) to ensure that your data remains secure and private.</Note>
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
client.export_storage.redis.sync(
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

## ExportStorage S3
<details><summary><code>client.export_storage.s3.<a href="src/label_studio_sdk/export_storage/s3/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

You can connect your S3 bucket to Label Studio as a source storage or target storage. Use this API request to get a list of all S3 export (target) storage connections for a specific project.

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.export_storage.s3.list()

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

<details><summary><code>client.export_storage.s3.<a href="src/label_studio_sdk/export_storage/s3/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new target storage connection to S3 storage.

For information about the required fields and prerequisites, see [Amazon S3](https://labelstud.io/guide/storage#Amazon-S3) in the Label Studio documentation.

<Tip>After you add the storage, you should validate the connection before attempting to sync your data. Your data will not be exported until you [sync your connection](sync).</Tip>
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
client.export_storage.s3.create()

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

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — S3 bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — S3 bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**aws_access_key_id:** `typing.Optional[str]` — AWS_ACCESS_KEY_ID
    
</dd>
</dl>

<dl>
<dd>

**aws_secret_access_key:** `typing.Optional[str]` — AWS_SECRET_ACCESS_KEY
    
</dd>
</dl>

<dl>
<dd>

**aws_session_token:** `typing.Optional[str]` — AWS_SESSION_TOKEN
    
</dd>
</dl>

<dl>
<dd>

**aws_sse_kms_key_id:** `typing.Optional[str]` — AWS SSE KMS Key ID
    
</dd>
</dl>

<dl>
<dd>

**region_name:** `typing.Optional[str]` — AWS Region
    
</dd>
</dl>

<dl>
<dd>

**s3endpoint:** `typing.Optional[str]` — S3 Endpoint
    
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

<details><summary><code>client.export_storage.s3.<a href="src/label_studio_sdk/export_storage/s3/client.py">validate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Validate a specific S3 export storage connection. This is useful to ensure that the storage configuration settings are correct and operational before attempting to export data.
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
client.export_storage.s3.validate()

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

**id:** `typing.Optional[int]` — Storage ID. If set, storage with specified ID will be updated
    
</dd>
</dl>

<dl>
<dd>

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — S3 bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — S3 bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**aws_access_key_id:** `typing.Optional[str]` — AWS_ACCESS_KEY_ID
    
</dd>
</dl>

<dl>
<dd>

**aws_secret_access_key:** `typing.Optional[str]` — AWS_SECRET_ACCESS_KEY
    
</dd>
</dl>

<dl>
<dd>

**aws_session_token:** `typing.Optional[str]` — AWS_SESSION_TOKEN
    
</dd>
</dl>

<dl>
<dd>

**aws_sse_kms_key_id:** `typing.Optional[str]` — AWS SSE KMS Key ID
    
</dd>
</dl>

<dl>
<dd>

**region_name:** `typing.Optional[str]` — AWS Region
    
</dd>
</dl>

<dl>
<dd>

**s3endpoint:** `typing.Optional[str]` — S3 Endpoint
    
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

<details><summary><code>client.export_storage.s3.<a href="src/label_studio_sdk/export_storage/s3/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific S3 export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.export_storage.s3.get(
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

**id:** `int` — A unique integer value identifying this s3 export storage.
    
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

<details><summary><code>client.export_storage.s3.<a href="src/label_studio_sdk/export_storage/s3/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific S3 export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

Deleting an export/target storage connection does not affect tasks with synced data in Label Studio. If you want to remove the tasks that were synced from the external storage, you will need to delete them manually from within the Label Studio UI or use the [Delete tasks](../../tasks/delete-all-tasks) API.
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
client.export_storage.s3.delete(
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

**id:** `int` — A unique integer value identifying this s3 export storage.
    
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

<details><summary><code>client.export_storage.s3.<a href="src/label_studio_sdk/export_storage/s3/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific S3 export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.export_storage.s3.update(
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

**id:** `int` — A unique integer value identifying this s3 export storage.
    
</dd>
</dl>

<dl>
<dd>

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — S3 bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — S3 bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**aws_access_key_id:** `typing.Optional[str]` — AWS_ACCESS_KEY_ID
    
</dd>
</dl>

<dl>
<dd>

**aws_secret_access_key:** `typing.Optional[str]` — AWS_SECRET_ACCESS_KEY
    
</dd>
</dl>

<dl>
<dd>

**aws_session_token:** `typing.Optional[str]` — AWS_SESSION_TOKEN
    
</dd>
</dl>

<dl>
<dd>

**aws_sse_kms_key_id:** `typing.Optional[str]` — AWS SSE KMS Key ID
    
</dd>
</dl>

<dl>
<dd>

**region_name:** `typing.Optional[str]` — AWS Region
    
</dd>
</dl>

<dl>
<dd>

**s3endpoint:** `typing.Optional[str]` — S3 Endpoint
    
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

<details><summary><code>client.export_storage.s3.<a href="src/label_studio_sdk/export_storage/s3/client.py">sync</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Sync tasks to an S3 export/target storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).

Sync operations with external buckets only go one way. They either create tasks from objects in the bucket (source/import storage) or push annotations to the output bucket (export/target storage). Changing something on the bucket side doesn’t guarantee consistency in results.

<Note>Before proceeding, you should review [How sync operations work - Source storage](https://labelstud.io/guide/storage#Source-storage) to ensure that your data remains secure and private.</Note>
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
client.export_storage.s3.sync(
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

## ImportStorage Gcs
<details><summary><code>client.import_storage.gcs.<a href="src/label_studio_sdk/import_storage/gcs/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

You can connect your Google Cloud Storage bucket to Label Studio as a source storage or target storage. Use this API request to get a list of all Google import (source) storage connections for a specific project.

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.import_storage.gcs.list()

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

<details><summary><code>client.import_storage.gcs.<a href="src/label_studio_sdk/import_storage/gcs/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new source storage connection to a Google Cloud Storage bucket.

For information about the required fields and prerequisites, see [Google Cloud Storage](https://labelstud.io/guide/storage#Google-Cloud-Storage) in the Label Studio documentation.

<Info>Ensure you configure CORS before adding cloud storage. This ensures you will be able to see the content of the data rather than just a link.</Info>

<Tip>After you add the storage, you should validate the connection before attempting to sync your data. Your data will not be imported until you [sync your connection](sync).</Tip>
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
client.import_storage.gcs.create()

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

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects. You must specify it otherwise no objects will be imported.
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your bucket contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
</dd>
</dl>

<dl>
<dd>

**presign:** `typing.Optional[bool]` — Presign URLs for direct download
    
</dd>
</dl>

<dl>
<dd>

**presign_ttl:** `typing.Optional[int]` — Presign TTL in minutes
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — GCS bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — GCS bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**google_application_credentials:** `typing.Optional[str]` — The content of GOOGLE_APPLICATION_CREDENTIALS json file. Check official Google Cloud Authentication documentation for more details.
    
</dd>
</dl>

<dl>
<dd>

**google_project_id:** `typing.Optional[str]` — Google project ID
    
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

<details><summary><code>client.import_storage.gcs.<a href="src/label_studio_sdk/import_storage/gcs/client.py">validate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Validate a specific GCS import storage connection. This is useful to ensure that the storage configuration settings are correct and operational before attempting to import data.
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
client.import_storage.gcs.validate()

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

**id:** `typing.Optional[int]` — Storage ID. If set, storage with specified ID will be updated
    
</dd>
</dl>

<dl>
<dd>

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects. You must specify it otherwise no objects will be imported.
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your bucket contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
</dd>
</dl>

<dl>
<dd>

**presign:** `typing.Optional[bool]` — Presign URLs for direct download
    
</dd>
</dl>

<dl>
<dd>

**presign_ttl:** `typing.Optional[int]` — Presign TTL in minutes
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — GCS bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — GCS bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**google_application_credentials:** `typing.Optional[str]` — The content of GOOGLE_APPLICATION_CREDENTIALS json file. Check official Google Cloud Authentication documentation for more details.
    
</dd>
</dl>

<dl>
<dd>

**google_project_id:** `typing.Optional[str]` — Google project ID
    
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

<details><summary><code>client.import_storage.gcs.<a href="src/label_studio_sdk/import_storage/gcs/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific GCS import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.import_storage.gcs.get(
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

**id:** `int` — A unique integer value identifying this gcs import storage.
    
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

<details><summary><code>client.import_storage.gcs.<a href="src/label_studio_sdk/import_storage/gcs/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific GCS import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

Deleting a source storage connection does not affect tasks with synced data in Label Studio. The sync process is designed to import new or updated tasks from the connected storage into the project, but it does not track deletions of files from the storage. Therefore, if you remove the external storage connection, the tasks that were created from that storage will remain in the project.

If you want to remove the tasks that were synced from the external storage, you will need to delete them manually from within the Label Studio UI or use the [Delete tasks](../../tasks/delete-all-tasks) API.
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
client.import_storage.gcs.delete(
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

**id:** `int` — A unique integer value identifying this gcs import storage.
    
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

<details><summary><code>client.import_storage.gcs.<a href="src/label_studio_sdk/import_storage/gcs/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific GCS import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.import_storage.gcs.update(
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

**id:** `int` — A unique integer value identifying this gcs import storage.
    
</dd>
</dl>

<dl>
<dd>

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects. You must specify it otherwise no objects will be imported.
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your bucket contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
</dd>
</dl>

<dl>
<dd>

**presign:** `typing.Optional[bool]` — Presign URLs for direct download
    
</dd>
</dl>

<dl>
<dd>

**presign_ttl:** `typing.Optional[int]` — Presign TTL in minutes
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — GCS bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — GCS bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**google_application_credentials:** `typing.Optional[str]` — The content of GOOGLE_APPLICATION_CREDENTIALS json file. Check official Google Cloud Authentication documentation for more details.
    
</dd>
</dl>

<dl>
<dd>

**google_project_id:** `typing.Optional[str]` — Google project ID
    
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

<details><summary><code>client.import_storage.gcs.<a href="src/label_studio_sdk/import_storage/gcs/client.py">sync</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Sync tasks from a GCS import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

Sync operations with external buckets only go one way. They either create tasks from objects in the bucket (source/import storage) or push annotations to the output bucket (export/target storage). Changing something on the bucket side doesn’t guarantee consistency in results.

<Note>Before proceeding, you should review [How sync operations work - Source storage](https://labelstud.io/guide/storage#Source-storage) to ensure that your data remains secure and private.</Note>
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
client.import_storage.gcs.sync(
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

**id:** `int` — Storage ID
    
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

## ImportStorage Local
<details><summary><code>client.import_storage.local.<a href="src/label_studio_sdk/import_storage/local/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

If you have local files that you want to add to Label Studio from a specific directory, you can set up a specific local directory on the machine where LS is running as source or target storage. Use this API request to get a list of all local file import (source) storage connections for a specific project.

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.import_storage.local.list()

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

<details><summary><code>client.import_storage.local.<a href="src/label_studio_sdk/import_storage/local/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new source storage connection to a local file directory.

For information about the required fields and prerequisites, see [Local storage](https://labelstud.io/guide/storage#Local-storage) in the Label Studio documentation.

<Tip>After you add the storage, you should validate the connection before attempting to sync your data. Your data will not be imported until you [sync your connection](sync).</Tip>
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
client.import_storage.local.create()

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

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**path:** `typing.Optional[str]` — Path to local directory
    
</dd>
</dl>

<dl>
<dd>

**regex_filter:** `typing.Optional[str]` — Regex for filtering objects
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your directory contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
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

<details><summary><code>client.import_storage.local.<a href="src/label_studio_sdk/import_storage/local/client.py">validate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Validate a specific local file import storage connection. This is useful to ensure that the storage configuration settings are correct and operational before attempting to import data.
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
client.import_storage.local.validate()

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

**id:** `typing.Optional[int]` — Storage ID. If set, storage with specified ID will be updated
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**path:** `typing.Optional[str]` — Path to local directory
    
</dd>
</dl>

<dl>
<dd>

**regex_filter:** `typing.Optional[str]` — Regex for filtering objects
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your directory contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
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

<details><summary><code>client.import_storage.local.<a href="src/label_studio_sdk/import_storage/local/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific local file import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.import_storage.local.get(
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

**id:** `int` — A unique integer value identifying this local files import storage.
    
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

<details><summary><code>client.import_storage.local.<a href="src/label_studio_sdk/import_storage/local/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific local import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

Deleting a source storage connection does not affect tasks with synced data in Label Studio. The sync process is designed to import new or updated tasks from the connected storage into the project, but it does not track deletions of files from the storage. Therefore, if you remove the external storage connection, the tasks that were created from that storage will remain in the project.

If you want to remove the tasks that were synced from the external storage, you will need to delete them manually from within the Label Studio UI or use the [Delete tasks](../../tasks/delete-all-tasks) API.
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
client.import_storage.local.delete(
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

**id:** `int` — A unique integer value identifying this local files import storage.
    
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

<details><summary><code>client.import_storage.local.<a href="src/label_studio_sdk/import_storage/local/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific local import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.import_storage.local.update(
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

**id:** `int` — A unique integer value identifying this local files import storage.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**path:** `typing.Optional[str]` — Path to local directory
    
</dd>
</dl>

<dl>
<dd>

**regex_filter:** `typing.Optional[str]` — Regex for filtering objects
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your directory contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
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

<details><summary><code>client.import_storage.local.<a href="src/label_studio_sdk/import_storage/local/client.py">sync</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Sync tasks from a local import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

Sync operations with external sources only go one way. They either create tasks from objects in the source directory (source/import storage) or push annotations to the output directory (export/target storage). Changing something on the local file side doesn’t guarantee consistency in results.

<Note>Before proceeding, you should review [How sync operations work - Source storage](https://labelstud.io/guide/storage#Source-storage) to ensure that your data remains secure and private.</Note>
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
client.import_storage.local.sync(
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

**id:** `int` — Storage ID
    
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

## ImportStorage Redis
<details><summary><code>client.import_storage.redis.<a href="src/label_studio_sdk/import_storage/redis/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

You can connect your Redis database to Label Studio as a source storage or target storage. Use this API request to get a list of all Redis import (source) storage connections for a specific project.

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.import_storage.redis.list()

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

<details><summary><code>client.import_storage.redis.<a href="src/label_studio_sdk/import_storage/redis/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new source storage connection to a Redis database.

For information about the required fields and prerequisites, see [Redis database](https://labelstud.io/guide/storage#Redis-database) in the Label Studio documentation.

<Tip>After you add the storage, you should validate the connection before attempting to sync your data. Your data will not be imported until you [sync your connection](sync).</Tip>
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
client.import_storage.redis.create()

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

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects. You must specify it otherwise no objects will be imported.
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your bucket contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**path:** `typing.Optional[str]` — Storage prefix (optional)
    
</dd>
</dl>

<dl>
<dd>

**host:** `typing.Optional[str]` — Server Host IP (optional)
    
</dd>
</dl>

<dl>
<dd>

**port:** `typing.Optional[str]` — Server Port (optional)
    
</dd>
</dl>

<dl>
<dd>

**password:** `typing.Optional[str]` — Server Password (optional)
    
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

<details><summary><code>client.import_storage.redis.<a href="src/label_studio_sdk/import_storage/redis/client.py">validate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Validate a specific Redis import storage connection. This is useful to ensure that the storage configuration settings are correct and operational before attempting to import data.
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
client.import_storage.redis.validate()

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

**id:** `typing.Optional[int]` — Storage ID. If set, storage with specified ID will be updated
    
</dd>
</dl>

<dl>
<dd>

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects. You must specify it otherwise no objects will be imported.
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your bucket contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**path:** `typing.Optional[str]` — Storage prefix (optional)
    
</dd>
</dl>

<dl>
<dd>

**host:** `typing.Optional[str]` — Server Host IP (optional)
    
</dd>
</dl>

<dl>
<dd>

**port:** `typing.Optional[str]` — Server Port (optional)
    
</dd>
</dl>

<dl>
<dd>

**password:** `typing.Optional[str]` — Server Password (optional)
    
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

<details><summary><code>client.import_storage.redis.<a href="src/label_studio_sdk/import_storage/redis/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific Redis import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.import_storage.redis.get(
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

**id:** `int` — A unique integer value identifying this redis import storage.
    
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

<details><summary><code>client.import_storage.redis.<a href="src/label_studio_sdk/import_storage/redis/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific Redis import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

Deleting a source storage connection does not affect tasks with synced data in Label Studio. The sync process is designed to import new or updated tasks from the connected storage into the project, but it does not track deletions of files from the storage. Therefore, if you remove the external storage connection, the tasks that were created from that storage will remain in the project.

If you want to remove the tasks that were synced from the external storage, you will need to delete them manually from within the Label Studio UI or use the [Delete tasks](../../tasks/delete-all-tasks) API.
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
client.import_storage.redis.delete(
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

**id:** `int` — A unique integer value identifying this redis import storage.
    
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

<details><summary><code>client.import_storage.redis.<a href="src/label_studio_sdk/import_storage/redis/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific Redis import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.import_storage.redis.update(
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

**id:** `int` — A unique integer value identifying this redis import storage.
    
</dd>
</dl>

<dl>
<dd>

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects. You must specify it otherwise no objects will be imported.
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your bucket contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**path:** `typing.Optional[str]` — Storage prefix (optional)
    
</dd>
</dl>

<dl>
<dd>

**host:** `typing.Optional[str]` — Server Host IP (optional)
    
</dd>
</dl>

<dl>
<dd>

**port:** `typing.Optional[str]` — Server Port (optional)
    
</dd>
</dl>

<dl>
<dd>

**password:** `typing.Optional[str]` — Server Password (optional)
    
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

<details><summary><code>client.import_storage.redis.<a href="src/label_studio_sdk/import_storage/redis/client.py">sync</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Sync tasks from a Redis import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

Sync operations with external databases only go one way. They either create tasks from objects in the database (source/import storage) or push annotations to the output database (export/target storage). Changing something on the database side doesn’t guarantee consistency in results.

<Note>Before proceeding, you should review [How sync operations work - Source storage](https://labelstud.io/guide/storage#Source-storage) to ensure that your data remains secure and private.</Note>
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
client.import_storage.redis.sync(
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

**id:** `int` — Storage ID
    
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

## ImportStorage S3
<details><summary><code>client.import_storage.s3.<a href="src/label_studio_sdk/import_storage/s3/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

You can connect your S3 bucket to Label Studio as a source storage or target storage. Use this API request to get a list of all Google import (source) storage connections for a specific project.

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.import_storage.s3.list()

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

<details><summary><code>client.import_storage.s3.<a href="src/label_studio_sdk/import_storage/s3/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new source storage connection to a S3 bucket.

For information about the required fields and prerequisites, see [Amazon S3](https://labelstud.io/guide/storage#Amazon-S3) in the Label Studio documentation.

<Info>Ensure you configure CORS before adding cloud storage. This ensures you will be able to see the content of the data rather than just a link.</Info>

<Tip>After you add the storage, you should validate the connection before attempting to sync your data. Your data will not be imported until you [sync your connection](sync).</Tip>
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
client.import_storage.s3.create()

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

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects. You must specify it otherwise no objects will be imported.
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your bucket contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
</dd>
</dl>

<dl>
<dd>

**presign:** `typing.Optional[bool]` — Presign URLs for download
    
</dd>
</dl>

<dl>
<dd>

**presign_ttl:** `typing.Optional[int]` — Presign TTL in minutes
    
</dd>
</dl>

<dl>
<dd>

**recursive_scan:** `typing.Optional[bool]` — Scan recursively
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — S3 bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — S3 bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**aws_access_key_id:** `typing.Optional[str]` — AWS_ACCESS_KEY_ID
    
</dd>
</dl>

<dl>
<dd>

**aws_secret_access_key:** `typing.Optional[str]` — AWS_SECRET_ACCESS_KEY
    
</dd>
</dl>

<dl>
<dd>

**aws_session_token:** `typing.Optional[str]` — AWS_SESSION_TOKEN
    
</dd>
</dl>

<dl>
<dd>

**aws_sse_kms_key_id:** `typing.Optional[str]` — AWS SSE KMS Key ID
    
</dd>
</dl>

<dl>
<dd>

**region_name:** `typing.Optional[str]` — AWS Region
    
</dd>
</dl>

<dl>
<dd>

**s3endpoint:** `typing.Optional[str]` — S3 Endpoint
    
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

<details><summary><code>client.import_storage.s3.<a href="src/label_studio_sdk/import_storage/s3/client.py">validate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Validate a specific S3 import storage connection. This is useful to ensure that the storage configuration settings are correct and operational before attempting to import data.
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
client.import_storage.s3.validate()

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

**id:** `typing.Optional[int]` — Storage ID. If set, storage with specified ID will be updated
    
</dd>
</dl>

<dl>
<dd>

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects. You must specify it otherwise no objects will be imported.
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your bucket contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
</dd>
</dl>

<dl>
<dd>

**presign:** `typing.Optional[bool]` — Presign URLs for download
    
</dd>
</dl>

<dl>
<dd>

**presign_ttl:** `typing.Optional[int]` — Presign TTL in minutes
    
</dd>
</dl>

<dl>
<dd>

**recursive_scan:** `typing.Optional[bool]` — Scan recursively
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — S3 bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — S3 bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**aws_access_key_id:** `typing.Optional[str]` — AWS_ACCESS_KEY_ID
    
</dd>
</dl>

<dl>
<dd>

**aws_secret_access_key:** `typing.Optional[str]` — AWS_SECRET_ACCESS_KEY
    
</dd>
</dl>

<dl>
<dd>

**aws_session_token:** `typing.Optional[str]` — AWS_SESSION_TOKEN
    
</dd>
</dl>

<dl>
<dd>

**aws_sse_kms_key_id:** `typing.Optional[str]` — AWS SSE KMS Key ID
    
</dd>
</dl>

<dl>
<dd>

**region_name:** `typing.Optional[str]` — AWS Region
    
</dd>
</dl>

<dl>
<dd>

**s3endpoint:** `typing.Optional[str]` — S3 Endpoint
    
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

<details><summary><code>client.import_storage.s3.<a href="src/label_studio_sdk/import_storage/s3/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific S3 import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.import_storage.s3.get(
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

**id:** `int` — A unique integer value identifying this s3 import storage.
    
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

<details><summary><code>client.import_storage.s3.<a href="src/label_studio_sdk/import_storage/s3/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific S3 import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

Deleting a source storage connection does not affect tasks with synced data in Label Studio. The sync process is designed to import new or updated tasks from the connected storage into the project, but it does not track deletions of files from the storage. Therefore, if you remove the external storage connection, the tasks that were created from that storage will remain in the project.

If you want to remove the tasks that were synced from the external storage, you will need to delete them manually from within the Label Studio UI or use the [Delete tasks](../../tasks/delete-all-tasks) API.
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
client.import_storage.s3.delete(
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

**id:** `int` — A unique integer value identifying this s3 import storage.
    
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

<details><summary><code>client.import_storage.s3.<a href="src/label_studio_sdk/import_storage/s3/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific S3 import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.import_storage.s3.update(
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

**id:** `int` — A unique integer value identifying this s3 import storage.
    
</dd>
</dl>

<dl>
<dd>

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects. You must specify it otherwise no objects will be imported.
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your bucket contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
</dd>
</dl>

<dl>
<dd>

**presign:** `typing.Optional[bool]` — Presign URLs for download
    
</dd>
</dl>

<dl>
<dd>

**presign_ttl:** `typing.Optional[int]` — Presign TTL in minutes
    
</dd>
</dl>

<dl>
<dd>

**recursive_scan:** `typing.Optional[bool]` — Scan recursively
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — S3 bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — S3 bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**aws_access_key_id:** `typing.Optional[str]` — AWS_ACCESS_KEY_ID
    
</dd>
</dl>

<dl>
<dd>

**aws_secret_access_key:** `typing.Optional[str]` — AWS_SECRET_ACCESS_KEY
    
</dd>
</dl>

<dl>
<dd>

**aws_session_token:** `typing.Optional[str]` — AWS_SESSION_TOKEN
    
</dd>
</dl>

<dl>
<dd>

**aws_sse_kms_key_id:** `typing.Optional[str]` — AWS SSE KMS Key ID
    
</dd>
</dl>

<dl>
<dd>

**region_name:** `typing.Optional[str]` — AWS Region
    
</dd>
</dl>

<dl>
<dd>

**s3endpoint:** `typing.Optional[str]` — S3 Endpoint
    
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

<details><summary><code>client.import_storage.s3.<a href="src/label_studio_sdk/import_storage/s3/client.py">sync</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Sync tasks from an S3 import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

Sync operations with external buckets only go one way. They either create tasks from objects in the bucket (source/import storage) or push annotations to the output bucket (export/target storage). Changing something on the bucket side doesn’t guarantee consistency in results.

<Note>Before proceeding, you should review [How sync operations work - Source storage](https://labelstud.io/guide/storage#Source-storage) to ensure that your data remains secure and private.</Note>
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
client.import_storage.s3.sync(
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

**id:** `int` — Storage ID
    
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

## Webhooks
<details><summary><code>client.webhooks.<a href="src/label_studio_sdk/webhooks/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all webhooks set up for your organization.

Webhooks in Label Studio let you set up integrations that subscribe to certain events that occur inside Label Studio. When an event is triggered, Label Studio sends an HTTP POST request to the configured webhook URL.

For more information, see [Set up webhooks in Label Studio](https://labelstud.io/guide/webhooks).
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
client.webhooks.list()

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

**project:** `typing.Optional[str]` — Project ID
    
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

<details><summary><code>client.webhooks.<a href="src/label_studio_sdk/webhooks/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a webhook.
Label Studio provides several out-of-the box webhook events, which you can find listed here: [Available Label Studio webhooks](https://labelstud.io/guide/webhooks#Available-Label-Studio-webhooks).

If you want to create your own custom webhook, refer to [Create custom events for webhooks in Label Studio](https://labelstud.io/guide/webhook_create).

<Note>Label Studio makes two main types of events available to integrate with webhooks: project-level task events and organization events. If you want to use organization-level webhook events, you will need to set `LABEL_STUDIO_ALLOW_ORGANIZATION_WEBHOOKS=true`. </Note>
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
client.webhooks.create(
    url="url",
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

**url:** `str` — URL of webhook
    
</dd>
</dl>

<dl>
<dd>

**id:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**organization:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**send_payload:** `typing.Optional[bool]` — If value is False send only action
    
</dd>
</dl>

<dl>
<dd>

**send_for_all_actions:** `typing.Optional[bool]` — If value is False - used only for actions from WebhookAction
    
</dd>
</dl>

<dl>
<dd>

**headers:** `typing.Optional[typing.Dict[str, typing.Any]]` — Key Value Json of headers
    
</dd>
</dl>

<dl>
<dd>

**is_active:** `typing.Optional[bool]` — If value is False the webhook is disabled
    
</dd>
</dl>

<dl>
<dd>

**actions:** `typing.Optional[typing.Sequence[WebhookActionsItem]]` 
    
</dd>
</dl>

<dl>
<dd>

**created_at:** `typing.Optional[dt.datetime]` — Creation time
    
</dd>
</dl>

<dl>
<dd>

**updated_at:** `typing.Optional[dt.datetime]` — Last update time
    
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

<details><summary><code>client.webhooks.<a href="src/label_studio_sdk/webhooks/client.py">info</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get descriptions of all available webhook actions to set up webhooks. For more information, see the [Webhook event reference](https://labelstud.io/guide/webhook_reference).
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
client.webhooks.info()

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

**organization_only:** `typing.Optional[bool]` — organization-only or not
    
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

<details><summary><code>client.webhooks.<a href="src/label_studio_sdk/webhooks/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get information about a specific webhook. You will need to provide the webhook ID. You can get this from [List all webhooks](list).

For more information about webhooks, see [Set up webhooks in Label Studio](https://labelstud.io/guide/webhooks) and the [Webhook event reference](https://labelstud.io/guide/webhook_reference).
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
client.webhooks.get(
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

**id:** `int` — A unique integer value identifying this webhook.
    
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

<details><summary><code>client.webhooks.<a href="src/label_studio_sdk/webhooks/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a webhook. You will need to provide the webhook ID. You can get this from [List all webhooks](list).

For more information about webhooks, see [Set up webhooks in Label Studio](https://labelstud.io/guide/webhooks) and the [Webhook event reference](https://labelstud.io/guide/webhook_reference).
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
client.webhooks.delete(
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

**id:** `int` — A unique integer value identifying this webhook.
    
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

<details><summary><code>client.webhooks.<a href="src/label_studio_sdk/webhooks/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a webhook. You will need to provide the webhook ID. You can get this from [List all webhooks](list).

For more information about webhooks, see [Set up webhooks in Label Studio](https://labelstud.io/guide/webhooks) and the [Webhook event reference](https://labelstud.io/guide/webhook_reference).
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
client.webhooks.update(
    id_=1,
    url="url",
    webhook_serializer_for_update_url="url",
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

**id_:** `int` — A unique integer value identifying this webhook.
    
</dd>
</dl>

<dl>
<dd>

**url:** `str` — URL of webhook
    
</dd>
</dl>

<dl>
<dd>

**webhook_serializer_for_update_url:** `str` — URL of webhook
    
</dd>
</dl>

<dl>
<dd>

**send_payload:** `typing.Optional[bool]` — If value is False send only action
    
</dd>
</dl>

<dl>
<dd>

**send_for_all_actions:** `typing.Optional[bool]` — If value is False - used only for actions from WebhookAction
    
</dd>
</dl>

<dl>
<dd>

**headers:** `typing.Optional[str]` — Key Value Json of headers
    
</dd>
</dl>

<dl>
<dd>

**is_active:** `typing.Optional[bool]` — If value is False the webhook is disabled
    
</dd>
</dl>

<dl>
<dd>

**actions:** `typing.Optional[
    typing.Union[
        WebhooksUpdateRequestActionsItem,
        typing.Sequence[WebhooksUpdateRequestActionsItem],
    ]
]` 
    
</dd>
</dl>

<dl>
<dd>

**id:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**organization:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**webhook_serializer_for_update_send_payload:** `typing.Optional[bool]` — If value is False send only action
    
</dd>
</dl>

<dl>
<dd>

**webhook_serializer_for_update_send_for_all_actions:** `typing.Optional[bool]` — If value is False - used only for actions from WebhookAction
    
</dd>
</dl>

<dl>
<dd>

**webhook_serializer_for_update_headers:** `typing.Optional[typing.Dict[str, typing.Any]]` — Key Value Json of headers
    
</dd>
</dl>

<dl>
<dd>

**webhook_serializer_for_update_is_active:** `typing.Optional[bool]` — If value is False the webhook is disabled
    
</dd>
</dl>

<dl>
<dd>

**webhook_serializer_for_update_actions:** `typing.Optional[typing.Sequence[WebhookSerializerForUpdateActionsItem]]` 
    
</dd>
</dl>

<dl>
<dd>

**created_at:** `typing.Optional[dt.datetime]` — Creation time
    
</dd>
</dl>

<dl>
<dd>

**updated_at:** `typing.Optional[dt.datetime]` — Last update time
    
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

## Prompts
<details><summary><code>client.prompts.<a href="src/label_studio_sdk/prompts/client.py">list</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a list of prompts.
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
client.prompts.list()

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

<details><summary><code>client.prompts.<a href="src/label_studio_sdk/prompts/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new prompt.
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
client.prompts.create(
    title="title",
    input_fields=["input_fields"],
    output_classes=["output_classes"],
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

**title:** `str` — Title of the prompt
    
</dd>
</dl>

<dl>
<dd>

**input_fields:** `typing.Sequence[str]` — List of input fields
    
</dd>
</dl>

<dl>
<dd>

**output_classes:** `typing.Sequence[str]` — List of output classes
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Description of the prompt
    
</dd>
</dl>

<dl>
<dd>

**created_by:** `typing.Optional[PromptCreatedBy]` — User ID of the creator of the prompt
    
</dd>
</dl>

<dl>
<dd>

**created_at:** `typing.Optional[dt.datetime]` — Date and time the prompt was created
    
</dd>
</dl>

<dl>
<dd>

**updated_at:** `typing.Optional[dt.datetime]` — Date and time the prompt was last updated
    
</dd>
</dl>

<dl>
<dd>

**organization:** `typing.Optional[PromptOrganization]` — Organization ID of the prompt
    
</dd>
</dl>

<dl>
<dd>

**associated_projects:** `typing.Optional[typing.Sequence[int]]` — List of associated projects IDs
    
</dd>
</dl>

<dl>
<dd>

**skill_name:** `typing.Optional[str]` — Name of the skill
    
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

<details><summary><code>client.prompts.<a href="src/label_studio_sdk/prompts/client.py">batch_predictions</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new batch prediction.
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
client.prompts.batch_predictions()

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

**modelrun_id:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**results:** `typing.Optional[typing.Sequence[typing.Dict[str, typing.Any]]]` 
    
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

## Prompts Versions
<details><summary><code>client.prompts.versions.<a href="src/label_studio_sdk/prompts/versions/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new version of a prompt.
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
client.prompts.versions.create(
    id=1,
    title="title",
    prompt="prompt",
    provider="OpenAI",
    provider_model_id="provider_model_id",
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

**id:** `int` — Prompt ID
    
</dd>
</dl>

<dl>
<dd>

**title:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**prompt:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**provider:** `PromptVersionProvider` 
    
</dd>
</dl>

<dl>
<dd>

**provider_model_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**parent_model:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**created_by:** `typing.Optional[PromptVersionCreatedBy]` 
    
</dd>
</dl>

<dl>
<dd>

**created_at:** `typing.Optional[dt.datetime]` 
    
</dd>
</dl>

<dl>
<dd>

**updated_at:** `typing.Optional[dt.datetime]` 
    
</dd>
</dl>

<dl>
<dd>

**organization:** `typing.Optional[PromptVersionOrganization]` 
    
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

<details><summary><code>client.prompts.versions.<a href="src/label_studio_sdk/prompts/versions/client.py">create_run</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Run a prompt inference.
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
client.prompts.versions.create_run(
    id=1,
    version_id=1,
    project=1,
    project_subset="All",
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

**id:** `int` — Prompt ID
    
</dd>
</dl>

<dl>
<dd>

**version_id:** `int` — Prompt Version ID
    
</dd>
</dl>

<dl>
<dd>

**project:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**project_subset:** `InferenceRunProjectSubset` 
    
</dd>
</dl>

<dl>
<dd>

**organization:** `typing.Optional[InferenceRunOrganization]` 
    
</dd>
</dl>

<dl>
<dd>

**model_version:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**created_by:** `typing.Optional[InferenceRunCreatedBy]` 
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[InferenceRunStatus]` 
    
</dd>
</dl>

<dl>
<dd>

**job_id:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**total_predictions:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**total_correct_predictions:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**total_tasks:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**created_at:** `typing.Optional[dt.datetime]` 
    
</dd>
</dl>

<dl>
<dd>

**triggered_at:** `typing.Optional[dt.datetime]` 
    
</dd>
</dl>

<dl>
<dd>

**predictions_updated_at:** `typing.Optional[dt.datetime]` 
    
</dd>
</dl>

<dl>
<dd>

**completed_at:** `typing.Optional[dt.datetime]` 
    
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

## ModelProviders
<details><summary><code>client.model_providers.<a href="src/label_studio_sdk/model_providers/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new model provider connection.
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
client.model_providers.create(
    provider="OpenAI",
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

**provider:** `ModelProviderConnectionProvider` 
    
</dd>
</dl>

<dl>
<dd>

**api_key:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**deployment_name:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**endpoint:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**scope:** `typing.Optional[ModelProviderConnectionScope]` 
    
</dd>
</dl>

<dl>
<dd>

**organization:** `typing.Optional[ModelProviderConnectionOrganization]` 
    
</dd>
</dl>

<dl>
<dd>

**created_by:** `typing.Optional[ModelProviderConnectionCreatedBy]` 
    
</dd>
</dl>

<dl>
<dd>

**created_at:** `typing.Optional[dt.datetime]` 
    
</dd>
</dl>

<dl>
<dd>

**updated_at:** `typing.Optional[dt.datetime]` 
    
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

## Comments
<details><summary><code>client.comments.<a href="src/label_studio_sdk/comments/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a list of comments for a specific project.
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
client.comments.list()

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

**expand_created_by:** `typing.Optional[bool]` — Expand the created_by field with object instead of ID
    
</dd>
</dl>

<dl>
<dd>

**annotation:** `typing.Optional[int]` — Annotation ID
    
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

<details><summary><code>client.comments.<a href="src/label_studio_sdk/comments/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new comment.
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
client.comments.create()

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

**annotation:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**text:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**is_resolved:** `typing.Optional[bool]` 
    
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

<details><summary><code>client.comments.<a href="src/label_studio_sdk/comments/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific comment.
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
client.comments.get(
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

**id:** `int` — Comment ID
    
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

<details><summary><code>client.comments.<a href="src/label_studio_sdk/comments/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific comment.
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
client.comments.delete(
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

**id:** `int` — Comment ID
    
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

<details><summary><code>client.comments.<a href="src/label_studio_sdk/comments/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific comment.
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
client.comments.update(
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

**id:** `int` — Comment ID
    
</dd>
</dl>

<dl>
<dd>

**annotation:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**text:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**is_resolved:** `typing.Optional[bool]` 
    
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

## ImportStorage S3S
<details><summary><code>client.import_storage.s3s.<a href="src/label_studio_sdk/import_storage/s3s/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

You can connect your S3 bucket to Label Studio as a source storage or target storage. Use this API request to get a list of all Google import (source) storage connections for a specific project.

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.import_storage.s3s.list()

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

<details><summary><code>client.import_storage.s3s.<a href="src/label_studio_sdk/import_storage/s3s/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new source storage connection to a S3 bucket.

For information about the required fields and prerequisites, see [Amazon S3](https://labelstud.io/guide/storage#Amazon-S3) in the Label Studio documentation.

<Info>Ensure you configure CORS before adding cloud storage. This ensures you will be able to see the content of the data rather than just a link.</Info>

<Tip>After you add the storage, you should validate the connection before attempting to sync your data. Your data will not be imported until you [sync your connection](sync).</Tip>
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
client.import_storage.s3s.create()

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

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects. You must specify it otherwise no objects will be imported.
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your bucket contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
</dd>
</dl>

<dl>
<dd>

**presign:** `typing.Optional[bool]` — Presign URLs for download
    
</dd>
</dl>

<dl>
<dd>

**presign_ttl:** `typing.Optional[int]` — Presign TTL in minutes
    
</dd>
</dl>

<dl>
<dd>

**recursive_scan:** `typing.Optional[bool]` — Scan recursively
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — S3 bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — S3 bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**external_id:** `typing.Optional[str]` — AWS External ID
    
</dd>
</dl>

<dl>
<dd>

**role_arn:** `typing.Optional[str]` — AWS Role ARN
    
</dd>
</dl>

<dl>
<dd>

**region_name:** `typing.Optional[str]` — AWS Region
    
</dd>
</dl>

<dl>
<dd>

**s3endpoint:** `typing.Optional[str]` — S3 Endpoint
    
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

<details><summary><code>client.import_storage.s3s.<a href="src/label_studio_sdk/import_storage/s3s/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific S3 import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).
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
client.import_storage.s3s.get(
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

**id:** `int` — Import storage ID
    
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

<details><summary><code>client.import_storage.s3s.<a href="src/label_studio_sdk/import_storage/s3s/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific S3 import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

Deleting a source storage connection does not affect tasks with synced data in Label Studio. The sync process is designed to import new or updated tasks from the connected storage into the project, but it does not track deletions of files from the storage. Therefore, if you remove the external storage connection, the tasks that were created from that storage will remain in the project.

If you want to remove the tasks that were synced from the external storage, you will need to delete them manually from within the Label Studio UI or use the [Delete tasks](../../tasks/delete-all-tasks) API.
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
client.import_storage.s3s.delete(
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

**id:** `int` — Import storage ID
    
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

<details><summary><code>client.import_storage.s3s.<a href="src/label_studio_sdk/import_storage/s3s/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific S3 import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.import_storage.s3s.update(
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

**id:** `int` — Import storage ID
    
</dd>
</dl>

<dl>
<dd>

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects. You must specify it otherwise no objects will be imported.
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your bucket contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
</dd>
</dl>

<dl>
<dd>

**presign:** `typing.Optional[bool]` — Presign URLs for download
    
</dd>
</dl>

<dl>
<dd>

**presign_ttl:** `typing.Optional[int]` — Presign TTL in minutes
    
</dd>
</dl>

<dl>
<dd>

**recursive_scan:** `typing.Optional[bool]` — Scan recursively
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — S3 bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — S3 bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**external_id:** `typing.Optional[str]` — AWS External ID
    
</dd>
</dl>

<dl>
<dd>

**role_arn:** `typing.Optional[str]` — AWS Role ARN
    
</dd>
</dl>

<dl>
<dd>

**region_name:** `typing.Optional[str]` — AWS Region
    
</dd>
</dl>

<dl>
<dd>

**s3endpoint:** `typing.Optional[str]` — S3 Endpoint
    
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

<details><summary><code>client.import_storage.s3s.<a href="src/label_studio_sdk/import_storage/s3s/client.py">validate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Validate a specific S3 import storage connection. This is useful to ensure that the storage configuration settings are correct and operational before attempting to import data.
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
client.import_storage.s3s.validate()

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

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects. You must specify it otherwise no objects will be imported.
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs. For example, if your bucket contains images, you can use this option to generate URLs for these images. If set to False, it will read the content of the file and load it into Label Studio.
    
</dd>
</dl>

<dl>
<dd>

**presign:** `typing.Optional[bool]` — Presign URLs for download
    
</dd>
</dl>

<dl>
<dd>

**presign_ttl:** `typing.Optional[int]` — Presign TTL in minutes
    
</dd>
</dl>

<dl>
<dd>

**recursive_scan:** `typing.Optional[bool]` — Scan recursively
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — S3 bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — S3 bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**external_id:** `typing.Optional[str]` — AWS External ID
    
</dd>
</dl>

<dl>
<dd>

**role_arn:** `typing.Optional[str]` — AWS Role ARN
    
</dd>
</dl>

<dl>
<dd>

**region_name:** `typing.Optional[str]` — AWS Region
    
</dd>
</dl>

<dl>
<dd>

**s3endpoint:** `typing.Optional[str]` — S3 Endpoint
    
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

<details><summary><code>client.import_storage.s3s.<a href="src/label_studio_sdk/import_storage/s3s/client.py">sync</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Sync tasks from an S3 import storage connection. You will need to provide the import storage ID. You can find this using [List import storages](list).
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
client.import_storage.s3s.sync(
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

**id:** `int` — Storage ID
    
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

## ExportStorage S3S
<details><summary><code>client.export_storage.s3s.<a href="src/label_studio_sdk/export_storage/s3s/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

You can connect your S3 bucket to Label Studio as a source storage or target storage. Use this API request to get a list of all S3 export (target) storage connections for a specific project.

The project ID can be found in the URL when viewing the project in Label Studio, or you can retrieve all project IDs using [List all projects](../projects/list).

For more information about working with external storage, see [Sync data from external storage](https://labelstud.io/guide/storage).
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
client.export_storage.s3s.list()

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

<details><summary><code>client.export_storage.s3s.<a href="src/label_studio_sdk/export_storage/s3s/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new target storage connection to a S3 bucket with IAM role access.

For information about the required fields and prerequisites, see [Amazon S3](https://docs.humansignal.com/guide/storage#Set-up-an-S3-connection-with-IAM-role-access) in the Label Studio documentation.
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
client.export_storage.s3s.create()

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

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — S3 bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — S3 bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**external_id:** `typing.Optional[str]` — AWS External ID
    
</dd>
</dl>

<dl>
<dd>

**role_arn:** `typing.Optional[str]` — AWS Role ARN
    
</dd>
</dl>

<dl>
<dd>

**region_name:** `typing.Optional[str]` — AWS Region
    
</dd>
</dl>

<dl>
<dd>

**s3endpoint:** `typing.Optional[str]` — S3 Endpoint
    
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

<details><summary><code>client.export_storage.s3s.<a href="src/label_studio_sdk/export_storage/s3s/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific S3 export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).
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
client.export_storage.s3s.get(
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

**id:** `int` — Export storage ID
    
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

<details><summary><code>client.export_storage.s3s.<a href="src/label_studio_sdk/export_storage/s3s/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific S3 export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).
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
client.export_storage.s3s.delete(
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

**id:** `int` — Export storage ID
    
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

<details><summary><code>client.export_storage.s3s.<a href="src/label_studio_sdk/export_storage/s3s/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific S3 export storage connection. You will need to provide the export storage ID. You can find this using [List export storages](list).
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
client.export_storage.s3s.update(
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

**id:** `int` — Export storage ID
    
</dd>
</dl>

<dl>
<dd>

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — S3 bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — S3 bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**external_id:** `typing.Optional[str]` — AWS External ID
    
</dd>
</dl>

<dl>
<dd>

**role_arn:** `typing.Optional[str]` — AWS Role ARN
    
</dd>
</dl>

<dl>
<dd>

**region_name:** `typing.Optional[str]` — AWS Region
    
</dd>
</dl>

<dl>
<dd>

**s3endpoint:** `typing.Optional[str]` — S3 Endpoint
    
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

<details><summary><code>client.export_storage.s3s.<a href="src/label_studio_sdk/export_storage/s3s/client.py">validate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Validate a specific S3 export storage connection. This is useful to ensure that the storage configuration settings are correct and operational before attempting to export data.
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
client.export_storage.s3s.validate()

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

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled.
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Storage description
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**bucket:** `typing.Optional[str]` — S3 bucket name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — S3 bucket prefix
    
</dd>
</dl>

<dl>
<dd>

**external_id:** `typing.Optional[str]` — AWS External ID
    
</dd>
</dl>

<dl>
<dd>

**role_arn:** `typing.Optional[str]` — AWS Role ARN
    
</dd>
</dl>

<dl>
<dd>

**region_name:** `typing.Optional[str]` — AWS Region
    
</dd>
</dl>

<dl>
<dd>

**s3endpoint:** `typing.Optional[str]` — S3 Endpoint
    
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

## Workspaces
<details><summary><code>client.workspaces.<a href="src/label_studio_sdk/workspaces/client.py">list</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all workspaces for your organization.

Workspaces in Label Studio let you organize your projects and users into separate spaces. This is useful for managing different teams, departments, or projects within your organization.

For more information, see [Workspaces in Label Studio](https://docs.humansignal.com/guide/workspaces).
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
client.workspaces.list()

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

<details><summary><code>client.workspaces.<a href="src/label_studio_sdk/workspaces/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new workspace.

Workspaces in Label Studio let you organize your projects and users into separate spaces. This is useful for managing different teams, departments, or projects within your organization.

For more information, see [Workspaces in Label Studio](https://docs.humansignal.com/guide/workspaces).
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
client.workspaces.create()

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

**title:** `typing.Optional[str]` — Workspace title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Workspace description
    
</dd>
</dl>

<dl>
<dd>

**is_public:** `typing.Optional[bool]` — Is workspace public
    
</dd>
</dl>

<dl>
<dd>

**is_personal:** `typing.Optional[bool]` — Is workspace personal
    
</dd>
</dl>

<dl>
<dd>

**color:** `typing.Optional[str]` — Workspace color in HEX format
    
</dd>
</dl>

<dl>
<dd>

**is_archived:** `typing.Optional[bool]` — Is workspace archived
    
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

<details><summary><code>client.workspaces.<a href="src/label_studio_sdk/workspaces/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get information about a specific workspace. You will need to provide the workspace ID. You can find this using [List workspaces](list).
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
client.workspaces.get(
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

**id:** `int` — Workspace ID
    
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

<details><summary><code>client.workspaces.<a href="src/label_studio_sdk/workspaces/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific workspace. You will need to provide the workspace ID. You can find this using [List workspaces](list).
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
client.workspaces.delete(
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

**id:** `int` — Workspace ID
    
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

<details><summary><code>client.workspaces.<a href="src/label_studio_sdk/workspaces/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific workspace. You will need to provide the workspace ID. You can find this using [List workspaces](list).
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
client.workspaces.update(
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

**id:** `int` — Workspace ID
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Workspace title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Workspace description
    
</dd>
</dl>

<dl>
<dd>

**is_public:** `typing.Optional[bool]` — Is workspace public
    
</dd>
</dl>

<dl>
<dd>

**is_personal:** `typing.Optional[bool]` — Is workspace personal
    
</dd>
</dl>

<dl>
<dd>

**color:** `typing.Optional[str]` — Workspace color in HEX format
    
</dd>
</dl>

<dl>
<dd>

**is_archived:** `typing.Optional[bool]` — Is workspace archived
    
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

## Workspaces Members
<details><summary><code>client.workspaces.members.<a href="src/label_studio_sdk/workspaces/members/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all workspace memberships for a specific workspace. You will need to provide the workspace ID. You can find this using [List workspaces](list).
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
client.workspaces.members.list(
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

**id:** `int` — Workspace ID
    
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

<details><summary><code>client.workspaces.members.<a href="src/label_studio_sdk/workspaces/members/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new workspace membership. You will need to provide the workspace ID. You can find this using [List workspaces](list).
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
client.workspaces.members.create(
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

**id:** `int` — Workspace ID
    
</dd>
</dl>

<dl>
<dd>

**user:** `typing.Optional[int]` — User ID of the workspace member
    
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

<details><summary><code>client.workspaces.members.<a href="src/label_studio_sdk/workspaces/members/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific workspace membership. You will need to provide the workspace ID and the user ID. You can find this using [List workspace memberships](list).
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
client.workspaces.members.delete(
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

**id:** `int` — Workspace ID
    
</dd>
</dl>

<dl>
<dd>

**user:** `typing.Optional[int]` — User ID of the workspace member
    
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

