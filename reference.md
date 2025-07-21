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

Retrieve a specific annotation for a task using the annotation result ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Delete an annotation. This action can't be undone!
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Update existing attributes on an annotation.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**result:** `typing.Optional[typing.Sequence[typing.Dict[str, typing.Optional[typing.Any]]]]` — Labeling result in JSON format. Read more about the format in [the Label Studio documentation.](https://labelstud.io/guide/task_format)
    
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

<details><summary><code>client.annotations.<a href="src/label_studio_sdk/annotations/client.py">create_bulk</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create multiple annotations at once
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.annotations.create_bulk()

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

**result:** `typing.Optional[typing.Sequence[typing.Dict[str, typing.Optional[typing.Any]]]]` — List of annotation results for the task
    
</dd>
</dl>

<dl>
<dd>

**completed_by:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**unique_id:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**tasks:** `typing.Optional[typing.Sequence[int]]` 
    
</dd>
</dl>

<dl>
<dd>

**selected_items:** `typing.Optional[SelectedItemsRequest]` 
    
</dd>
</dl>

<dl>
<dd>

**was_cancelled:** `typing.Optional[bool]` — User skipped the task
    
</dd>
</dl>

<dl>
<dd>

**ground_truth:** `typing.Optional[bool]` — This annotation is a Ground Truth (ground_truth)
    
</dd>
</dl>

<dl>
<dd>

**draft_created_at:** `typing.Optional[dt.datetime]` — Draft creation time
    
</dd>
</dl>

<dl>
<dd>

**lead_time:** `typing.Optional[float]` — How much time it took to annotate the task
    
</dd>
</dl>

<dl>
<dd>

**import_id:** `typing.Optional[int]` — Original annotation ID that was at the import step or NULL if this annotation wasn't imported
    
</dd>
</dl>

<dl>
<dd>

**last_action:** `typing.Optional[AnnotationBulkSerializerWithSelectedItemsRequestLastAction]` 

Action which was performed in the last annotation history item

* `prediction` - Created from prediction
* `propagated_annotation` - Created from another annotation
* `imported` - Imported
* `submitted` - Submitted
* `updated` - Updated
* `skipped` - Skipped
* `accepted` - Accepted
* `rejected` - Rejected
* `fixed_and_accepted` - Fixed and accepted
* `deleted_review` - Deleted review
    
</dd>
</dl>

<dl>
<dd>

**bulk_created:** `typing.Optional[bool]` — Annotation was created in bulk mode
    
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

**updated_by:** `typing.Optional[int]` — Last user who updated this annotation
    
</dd>
</dl>

<dl>
<dd>

**parent_prediction:** `typing.Optional[int]` — Points to the prediction from which this annotation was created
    
</dd>
</dl>

<dl>
<dd>

**parent_annotation:** `typing.Optional[int]` — Points to the parent annotation from which this annotation was created
    
</dd>
</dl>

<dl>
<dd>

**last_created_by:** `typing.Optional[int]` — User who created the last annotation history item
    
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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


        Add annotations to a task like an annotator does. The content of the result field depends on your 
        labeling configuration. For example, send the following data as part of your POST 
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**result:** `typing.Optional[typing.Sequence[typing.Dict[str, typing.Optional[typing.Any]]]]` — Labeling result in JSON format. Read more about the format in [the Label Studio documentation.](https://labelstud.io/guide/task_format)
    
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

## Comments
<details><summary><code>client.comments.<a href="src/label_studio_sdk/comments/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all comments for a specific annotation ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.comments.list(
    classifications="classifications",
    region_ref="region_ref",
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

**classifications:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**region_ref:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**annotation:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**annotators:** `typing.Optional[typing.Union[int, typing.Sequence[int]]]` 
    
</dd>
</dl>

<dl>
<dd>

**draft:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**expand_created_by:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
</dd>
</dl>

<dl>
<dd>

**projects:** `typing.Optional[typing.Union[int, typing.Sequence[int]]]` 
    
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

Create a comment for a specific annotation ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**expand_created_by:** `typing.Optional[bool]` — Expand the created_by field
    
</dd>
</dl>

<dl>
<dd>

**region_ref:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**classifications:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**text:** `typing.Optional[str]` — Reviewer or annotator comment
    
</dd>
</dl>

<dl>
<dd>

**is_resolved:** `typing.Optional[bool]` — True if the comment is resolved
    
</dd>
</dl>

<dl>
<dd>

**draft:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**annotation:** `typing.Optional[int]` 
    
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

Retrieve a specific comment by ID for an annotation.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.comments.get(
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

**expand_created_by:** `typing.Optional[bool]` — Expand the created_by field
    
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

Delete a comment by ID
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.comments.delete(
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

**expand_created_by:** `typing.Optional[bool]` — Expand the created_by field
    
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

Update a specific comment by ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.comments.update(
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

**expand_created_by:** `typing.Optional[bool]` — Expand the created_by field
    
</dd>
</dl>

<dl>
<dd>

**region_ref:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**classifications:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**text:** `typing.Optional[str]` — Reviewer or annotator comment
    
</dd>
</dl>

<dl>
<dd>

**is_resolved:** `typing.Optional[bool]` — True if the comment is resolved
    
</dd>
</dl>

<dl>
<dd>

**draft:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**annotation:** `typing.Optional[int]` 
    
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
<details><summary><code>client.users.<a href="src/label_studio_sdk/users/client.py">get_current_user</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get info about the currently authenticated user.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.users.get_current_user()

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

<details><summary><code>client.users.<a href="src/label_studio_sdk/users/client.py">update_current_user</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update details for the currently authenticated user.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.users.update_current_user()

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

**first_name:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**last_name:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**username:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**custom_hotkeys:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**phone:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**active_organization:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**allow_newsletters:** `typing.Optional[bool]` — Allow sending newsletters to user
    
</dd>
</dl>

<dl>
<dd>

**date_joined:** `typing.Optional[dt.datetime]` 
    
</dd>
</dl>

<dl>
<dd>

**password:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**onboarding_state:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**is_email_verified:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**email_notification_settings:** `typing.Optional[typing.Optional[typing.Any]]` 
    
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

<details><summary><code>client.users.<a href="src/label_studio_sdk/users/client.py">get_hotkeys</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve the custom hotkeys configuration for the current user.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.users.get_hotkeys()

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

<details><summary><code>client.users.<a href="src/label_studio_sdk/users/client.py">update_hotkeys</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update the custom hotkeys configuration for the current user.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.users.update_hotkeys()

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

**custom_hotkeys:** `typing.Optional[typing.Dict[str, typing.Optional[typing.Any]]]` 
    
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

<details><summary><code>client.users.<a href="src/label_studio_sdk/users/client.py">reset_token</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Reset the user token for the current user.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

Get a user token to authenticate to the API as the current user.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

Retrieve details of the account that you are using to access the API.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.users.<a href="src/label_studio_sdk/users/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List the users that exist on the Label Studio server.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

Get info about a specific Label Studio user, based on the user ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

Delete a specific Label Studio user. Only available in community edition.

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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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


        Update details for a specific user, such as their name or contact information, in Label Studio.
        
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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
from label_studio_sdk import LabelStudio
from label_studio_sdk.actions import (
    ActionsCreateRequestFilters,
    ActionsCreateRequestFiltersItemsItem,
    ActionsCreateRequestSelectedItemsExcluded,
)

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.actions.create(
    id="delete_annotators",
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

List all views for a specific project.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

Create a view for a specific project.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.views.<a href="src/label_studio_sdk/views/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get the details about a specific view in the data manager
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

Delete a specific view by ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

Update view data with additional filters and other information for a specific project.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.views.<a href="src/label_studio_sdk/views/client.py">update_order</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update the order field of views based on the provided list of view IDs
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.views.update_order(
    project=1,
    ids=[1],
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

**ids:** `typing.Sequence[int]` — A list of view IDs in the desired order.
    
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

<details><summary><code>client.views.<a href="src/label_studio_sdk/views/client.py">delete_all</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete all views for a specific project. Request body example: `{"project": 1}`.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.views.delete_all()

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

## Files
<details><summary><code>client.files.<a href="src/label_studio_sdk/files/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve details about a specific uploaded file.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Delete a specific uploaded file.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Update a specific uploaded file.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.files.update(
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**file:** `from __future__ import annotations

typing.Optional[core.File]` — See core.File for more documentation
    
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


        Retrieve the list of uploaded files used to create labeling tasks for a specific project.
        
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**all_:** `typing.Optional[bool]` — Set to "true" if you want to retrieve all file uploads
    
</dd>
</dl>

<dl>
<dd>

**ids:** `typing.Optional[typing.Union[str, typing.Sequence[str]]]` — Specify the list of file upload IDs to retrieve, e.g. ids=[1,2,3]
    
</dd>
</dl>

<dl>
<dd>

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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


        Delete uploaded files for a specific project.
        
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Download a specific uploaded file.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

## Organizations
<details><summary><code>client.organizations.<a href="src/label_studio_sdk/organizations/client.py">reset_token</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Reset the token used in the invitation link to invite someone to an organization.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.organizations.reset_token()

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

<details><summary><code>client.organizations.<a href="src/label_studio_sdk/organizations/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>


        Return a list of the organizations you've created or that you have access to.
        
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.organizations.list()

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

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.organizations.<a href="src/label_studio_sdk/organizations/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve the settings for a specific organization by ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.organizations.get(
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

**id:** `int` 
    
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

## JwtSettings
<details><summary><code>client.jwt_settings.<a href="src/label_studio_sdk/jwt_settings/client.py">get</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve JWT settings for the currently active organization.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.jwt_settings.get()

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

<details><summary><code>client.jwt_settings.<a href="src/label_studio_sdk/jwt_settings/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update JWT settings for the currently active organization.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.jwt_settings.update()

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

**api_tokens_enabled:** `typing.Optional[bool]` — Enable JWT API token authentication for this organization
    
</dd>
</dl>

<dl>
<dd>

**legacy_api_tokens_enabled:** `typing.Optional[bool]` — Enable legacy API token authentication for this organization
    
</dd>
</dl>

<dl>
<dd>

**api_token_ttl_days:** `typing.Optional[int]` — Number of days before JWT API tokens expire
    
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


    List all configured ML backends for a specific project by ID.
    Use the following cURL command:
    ```bash
    curl http://localhost:8000/api/ml?project={project_id} -H 'Authorization: Token abc123'
    
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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


    Add an ML backend to a project using the Label Studio UI or by sending a POST request using the following cURL 
    command:
    ```bash
    curl -X POST -H 'Content-type: application/json' http://localhost:8000/api/ml -H 'Authorization: Token abc123'\
    --data '{"url": "http://localhost:9090", "project": {project_id}}' 
    
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**extra_params:** `typing.Optional[typing.Dict[str, typing.Optional[typing.Any]]]` — Extra parameters
    
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


    Get details about a specific ML backend connection by ID. For example, make a GET request using the
    following cURL command:
    ```bash
    curl http://localhost:8000/api/ml/{ml_backend_ID} -H 'Authorization: Token abc123'
    
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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


    Remove an existing ML backend connection by ID. For example, use the
    following cURL command:
    ```bash
    curl -X DELETE http://localhost:8000/api/ml/{ml_backend_ID} -H 'Authorization: Token abc123'
    
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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


    Update ML backend parameters using the Label Studio UI or by sending a PATCH request using the following cURL command:
    ```bash
    curl -X PATCH -H 'Content-type: application/json' http://localhost:8000/api/ml/{ml_backend_ID} -H 'Authorization: Token abc123'\
    --data '{"url": "http://localhost:9091"}' 
    
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

**extra_params:** `typing.Optional[typing.Dict[str, typing.Optional[typing.Any]]]` — Extra parameters
    
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


        Send a request to the machine learning backend set up to be used for interactive preannotations to retrieve a
        predicted region based on annotator input. 
        See [set up machine learning](https://labelstud.io/guide/ml.html#Get-interactive-preannotations) for more.
        
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**context:** `typing.Optional[typing.Optional[typing.Any]]` 
    
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


        After you add an ML backend, call this API with the ML backend ID to start training with 
        already-labeled tasks. 
        
        Get the ML backend ID by [listing the ML backends for a project](https://labelstud.io/api/#operation/api_ml_list).
        
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

Get available versions of the model.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.ml.list_model_versions(
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

**id:** `int` 
    
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
<details><summary><code>client.model_providers.<a href="src/label_studio_sdk/model_providers/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all model provider connections.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.model_providers.list()

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

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.model_providers.create()

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

**provider:** `typing.Optional[ProviderEnum]` 
    
</dd>
</dl>

<dl>
<dd>

**api_key:** `typing.Optional[str]` — Model provider API key
    
</dd>
</dl>

<dl>
<dd>

**auth_token:** `typing.Optional[str]` — Model provider Auth token
    
</dd>
</dl>

<dl>
<dd>

**deployment_name:** `typing.Optional[str]` — Azure OpenAI deployment name
    
</dd>
</dl>

<dl>
<dd>

**endpoint:** `typing.Optional[str]` — Azure OpenAI endpoint
    
</dd>
</dl>

<dl>
<dd>

**google_application_credentials:** `typing.Optional[str]` — The content of GOOGLE_APPLICATION_CREDENTIALS json file
    
</dd>
</dl>

<dl>
<dd>

**google_project_id:** `typing.Optional[str]` — Google project ID
    
</dd>
</dl>

<dl>
<dd>

**google_location:** `typing.Optional[str]` — Google project location
    
</dd>
</dl>

<dl>
<dd>

**cached_available_models:** `typing.Optional[str]` — List of available models from the provider
    
</dd>
</dl>

<dl>
<dd>

**scope:** `typing.Optional[ScopeEnum]` 
    
</dd>
</dl>

<dl>
<dd>

**is_internal:** `typing.Optional[bool]` — Whether the model provider connection is internal, not visible to the user
    
</dd>
</dl>

<dl>
<dd>

**budget_alert_threshold:** `typing.Optional[float]` — Budget alert threshold for the given provider connection
    
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

<details><summary><code>client.model_providers.<a href="src/label_studio_sdk/model_providers/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a specific model provider connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.model_providers.get(
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

<details><summary><code>client.model_providers.<a href="src/label_studio_sdk/model_providers/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a model provider connection by ID
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.model_providers.delete(
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

<details><summary><code>client.model_providers.<a href="src/label_studio_sdk/model_providers/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific model provider connection by ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.model_providers.update(
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

**provider:** `typing.Optional[ProviderEnum]` 
    
</dd>
</dl>

<dl>
<dd>

**api_key:** `typing.Optional[str]` — Model provider API key
    
</dd>
</dl>

<dl>
<dd>

**auth_token:** `typing.Optional[str]` — Model provider Auth token
    
</dd>
</dl>

<dl>
<dd>

**deployment_name:** `typing.Optional[str]` — Azure OpenAI deployment name
    
</dd>
</dl>

<dl>
<dd>

**endpoint:** `typing.Optional[str]` — Azure OpenAI endpoint
    
</dd>
</dl>

<dl>
<dd>

**google_application_credentials:** `typing.Optional[str]` — The content of GOOGLE_APPLICATION_CREDENTIALS json file
    
</dd>
</dl>

<dl>
<dd>

**google_project_id:** `typing.Optional[str]` — Google project ID
    
</dd>
</dl>

<dl>
<dd>

**google_location:** `typing.Optional[str]` — Google project location
    
</dd>
</dl>

<dl>
<dd>

**cached_available_models:** `typing.Optional[str]` — List of available models from the provider
    
</dd>
</dl>

<dl>
<dd>

**scope:** `typing.Optional[ScopeEnum]` 
    
</dd>
</dl>

<dl>
<dd>

**is_internal:** `typing.Optional[bool]` — Whether the model provider connection is internal, not visible to the user
    
</dd>
</dl>

<dl>
<dd>

**budget_alert_threshold:** `typing.Optional[float]` — Budget alert threshold for the given provider connection
    
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

<details><summary><code>client.model_providers.<a href="src/label_studio_sdk/model_providers/client.py">list_model_provider_choices</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all possible model provider choices
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.model_providers.list_model_provider_choices()

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

## Prompts
<details><summary><code>client.prompts.<a href="src/label_studio_sdk/prompts/client.py">create_batch_failed_predictions</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new batch of failed predictions.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.create_batch_failed_predictions(
    job_id="job_id",
    failed_predictions=[],
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

**job_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**failed_predictions:** `typing.Sequence[typing.Optional[typing.Any]]` 
    
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

<details><summary><code>client.prompts.<a href="src/label_studio_sdk/prompts/client.py">create_batch_predictions</a>(...)</code></summary>
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.create_batch_predictions(
    job_id="job_id",
    results=[],
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

**job_id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**results:** `typing.Sequence[typing.Optional[typing.Any]]` 
    
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

<details><summary><code>client.prompts.<a href="src/label_studio_sdk/prompts/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all prompts.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.create(
    title="title",
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

**title:** `str` — Model name
    
</dd>
</dl>

<dl>
<dd>

**created_by:** `typing.Optional[UserSimpleRequest]` — User who created Dataset
    
</dd>
</dl>

<dl>
<dd>

**skill_name:** `typing.Optional[SkillNameEnum]` 
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Model description
    
</dd>
</dl>

<dl>
<dd>

**input_fields:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**output_classes:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**organization:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**associated_projects:** `typing.Optional[typing.Sequence[int]]` 
    
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

<details><summary><code>client.prompts.<a href="src/label_studio_sdk/prompts/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a specific prompt.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.get(
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

<details><summary><code>client.prompts.<a href="src/label_studio_sdk/prompts/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a prompt by ID
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.delete(
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

<details><summary><code>client.prompts.<a href="src/label_studio_sdk/prompts/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific prompt by ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.update(
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

**created_by:** `typing.Optional[UserSimpleRequest]` — User who created Dataset
    
</dd>
</dl>

<dl>
<dd>

**skill_name:** `typing.Optional[SkillNameEnum]` 
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Model name
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Model description
    
</dd>
</dl>

<dl>
<dd>

**input_fields:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**output_classes:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**organization:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**associated_projects:** `typing.Optional[typing.Sequence[int]]` 
    
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

<details><summary><code>client.prompts.<a href="src/label_studio_sdk/prompts/client.py">compatible_projects</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a list of compatible project for prompt.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.compatible_projects()

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

**project_type:** `typing.Optional[PromptsCompatibleProjectsRequestProjectType]` — Skill to filter by
    
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

List all predictions and their IDs.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**project:** `typing.Optional[int]` — Filter predictions by project ID
    
</dd>
</dl>

<dl>
<dd>

**task:** `typing.Optional[int]` — Filter predictions by task ID
    
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

Create a prediction for a specific task.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**result:** `typing.Optional[typing.Sequence[typing.Dict[str, typing.Optional[typing.Any]]]]` — Prediction result in JSON format. Read more about the format in [the Label Studio documentation.](https://labelstud.io/guide/predictions)
    
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

Get details about a specific prediction by its ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

Delete a prediction by prediction ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

Update prediction data by prediction ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**result:** `typing.Optional[typing.Sequence[typing.Dict[str, typing.Optional[typing.Any]]]]` — Prediction result in JSON format. Read more about the format in [the Label Studio documentation.](https://labelstud.io/guide/predictions)
    
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

## Projects
<details><summary><code>client.projects.<a href="src/label_studio_sdk/projects/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a list of projects.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**filter:** `typing.Optional[ProjectsListRequestFilter]` — Filter projects by pinned status. Use 'pinned_only' to return only pinned projects, 'exclude_pinned' to return only non-pinned projects, or 'all' to return all projects.
    
</dd>
</dl>

<dl>
<dd>

**ids:** `typing.Optional[str]` — ids
    
</dd>
</dl>

<dl>
<dd>

**include:** `typing.Optional[str]` — Comma-separated list of count fields to include in the response to optimize performance. Available fields: task_number, finished_task_number, total_predictions_number, total_annotations_number, num_tasks_with_annotations, useful_annotation_number, ground_truth_number, skipped_annotations_number. If not specified, all count fields are included.
    
</dd>
</dl>

<dl>
<dd>

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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

**title:** `typing.Optional[str]` — title
    
</dd>
</dl>

<dl>
<dd>

**workspaces:** `typing.Optional[int]` — workspaces
    
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

Create a project for a specific organization.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**title:** `typing.Optional[str]` — Project name. Must be between 3 and 50 characters long.
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Project description
    
</dd>
</dl>

<dl>
<dd>

**label_config:** `typing.Optional[str]` — Label config in XML format. See more about it in documentation
    
</dd>
</dl>

<dl>
<dd>

**expert_instruction:** `typing.Optional[str]` — Labeling instructions in HTML format
    
</dd>
</dl>

<dl>
<dd>

**show_instruction:** `typing.Optional[bool]` — Show instructions to the annotator before they start
    
</dd>
</dl>

<dl>
<dd>

**show_skip_button:** `typing.Optional[bool]` — Show a skip button in interface and allow annotators to skip the task
    
</dd>
</dl>

<dl>
<dd>

**enable_empty_annotation:** `typing.Optional[bool]` — Allow annotators to submit empty annotations
    
</dd>
</dl>

<dl>
<dd>

**show_annotation_history:** `typing.Optional[bool]` — Show annotation history to annotator
    
</dd>
</dl>

<dl>
<dd>

**organization:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**color:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**maximum_annotations:** `typing.Optional[int]` — Maximum number of annotations for one task. If the number of annotations per task is equal or greater to this value, the task is completed (is_labeled=True)
    
</dd>
</dl>

<dl>
<dd>

**is_published:** `typing.Optional[bool]` — Whether or not the project is published to annotators
    
</dd>
</dl>

<dl>
<dd>

**model_version:** `typing.Optional[str]` — Machine learning model version
    
</dd>
</dl>

<dl>
<dd>

**is_draft:** `typing.Optional[bool]` — Whether or not the project is in the middle of being created
    
</dd>
</dl>

<dl>
<dd>

**created_by:** `typing.Optional[UserSimpleRequest]` — Project owner
    
</dd>
</dl>

<dl>
<dd>

**min_annotations_to_start_training:** `typing.Optional[int]` — Minimum number of completed tasks after which model training is started
    
</dd>
</dl>

<dl>
<dd>

**show_collab_predictions:** `typing.Optional[bool]` — If set, the annotator can view model predictions
    
</dd>
</dl>

<dl>
<dd>

**sampling:** `typing.Optional[LseProjectCreateRequestSampling]` 
    
</dd>
</dl>

<dl>
<dd>

**show_ground_truth_first:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**show_overlap_first:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**overlap_cohort_percentage:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**task_data_login:** `typing.Optional[str]` — Task data credentials: login
    
</dd>
</dl>

<dl>
<dd>

**task_data_password:** `typing.Optional[str]` — Task data credentials: password
    
</dd>
</dl>

<dl>
<dd>

**control_weights:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**evaluate_predictions_automatically:** `typing.Optional[bool]` — Retrieve and display predictions when loading a task
    
</dd>
</dl>

<dl>
<dd>

**skip_queue:** `typing.Optional[LseProjectCreateRequestSkipQueue]` 
    
</dd>
</dl>

<dl>
<dd>

**reveal_preannotations_interactively:** `typing.Optional[bool]` — Reveal pre-annotations interactively
    
</dd>
</dl>

<dl>
<dd>

**pinned_at:** `typing.Optional[dt.datetime]` — Pinned date and time
    
</dd>
</dl>

<dl>
<dd>

**workspace:** `typing.Optional[int]` 
    
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

Retrieve information about a project by project ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Delete a project by specified project ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Update the details of a specific project.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Project name. Must be between 3 and 50 characters long.
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Project description
    
</dd>
</dl>

<dl>
<dd>

**label_config:** `typing.Optional[str]` — Label config in XML format. See more about it in documentation
    
</dd>
</dl>

<dl>
<dd>

**expert_instruction:** `typing.Optional[str]` — Labeling instructions in HTML format
    
</dd>
</dl>

<dl>
<dd>

**show_instruction:** `typing.Optional[bool]` — Show instructions to the annotator before they start
    
</dd>
</dl>

<dl>
<dd>

**show_skip_button:** `typing.Optional[bool]` — Show a skip button in interface and allow annotators to skip the task
    
</dd>
</dl>

<dl>
<dd>

**enable_empty_annotation:** `typing.Optional[bool]` — Allow annotators to submit empty annotations
    
</dd>
</dl>

<dl>
<dd>

**show_annotation_history:** `typing.Optional[bool]` — Show annotation history to annotator
    
</dd>
</dl>

<dl>
<dd>

**organization:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**color:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**maximum_annotations:** `typing.Optional[int]` — Maximum number of annotations for one task. If the number of annotations per task is equal or greater to this value, the task is completed (is_labeled=True)
    
</dd>
</dl>

<dl>
<dd>

**is_published:** `typing.Optional[bool]` — Whether or not the project is published to annotators
    
</dd>
</dl>

<dl>
<dd>

**model_version:** `typing.Optional[str]` — Machine learning model version
    
</dd>
</dl>

<dl>
<dd>

**is_draft:** `typing.Optional[bool]` — Whether or not the project is in the middle of being created
    
</dd>
</dl>

<dl>
<dd>

**created_by:** `typing.Optional[UserSimpleRequest]` — Project owner
    
</dd>
</dl>

<dl>
<dd>

**min_annotations_to_start_training:** `typing.Optional[int]` — Minimum number of completed tasks after which model training is started
    
</dd>
</dl>

<dl>
<dd>

**show_collab_predictions:** `typing.Optional[bool]` — If set, the annotator can view model predictions
    
</dd>
</dl>

<dl>
<dd>

**sampling:** `typing.Optional[PatchedLseProjectRequestSampling]` 
    
</dd>
</dl>

<dl>
<dd>

**show_ground_truth_first:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**show_overlap_first:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**overlap_cohort_percentage:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**task_data_login:** `typing.Optional[str]` — Task data credentials: login
    
</dd>
</dl>

<dl>
<dd>

**task_data_password:** `typing.Optional[str]` — Task data credentials: password
    
</dd>
</dl>

<dl>
<dd>

**control_weights:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**evaluate_predictions_automatically:** `typing.Optional[bool]` — Retrieve and display predictions when loading a task
    
</dd>
</dl>

<dl>
<dd>

**skip_queue:** `typing.Optional[PatchedLseProjectRequestSkipQueue]` 
    
</dd>
</dl>

<dl>
<dd>

**reveal_preannotations_interactively:** `typing.Optional[bool]` — Reveal pre-annotations interactively
    
</dd>
</dl>

<dl>
<dd>

**pinned_at:** `typing.Optional[dt.datetime]` — Pinned date and time
    
</dd>
</dl>

<dl>
<dd>

**review_settings:** `typing.Optional[ReviewSettingsRequest]` 
    
</dd>
</dl>

<dl>
<dd>

**assignment_settings:** `typing.Optional[AssignmentSettingsRequest]` 
    
</dd>
</dl>

<dl>
<dd>

**custom_script:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**comment_classification_config:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**duplication_done:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**require_comment_on_skip:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**custom_task_lock_ttl:** `typing.Optional[int]` — TTL in seconds for task reservations, on new and existing tasks
    
</dd>
</dl>

<dl>
<dd>

**annotation_limit_count:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**annotation_limit_percent:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**pause_on_failed_annotator_evaluation:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**annotator_evaluation_minimum_score:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**annotator_evaluation_minimum_tasks:** `typing.Optional[int]` 
    
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

<details><summary><code>client.projects.<a href="src/label_studio_sdk/projects/client.py">duplicate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Make a copy of project.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.projects.duplicate(
    id=1,
    mode="settings",
    workspace=1,
    title="title",
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**mode:** `ModeEnum` 

Data that you want to duplicate: settings only, with tasks, with annotations

* `settings` - Only settings
* `settings,data` - Settings and tasks
    
</dd>
</dl>

<dl>
<dd>

**workspace:** `int` — Workspace, where to place duplicated project
    
</dd>
</dl>

<dl>
<dd>

**title:** `str` — Title of duplicated project
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Description of duplicated project
    
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


            Import data as labeling tasks in bulk using this API endpoint. You can use this API endpoint to import multiple tasks.
            One POST request is limited at 250K tasks and 200 MB.

            **Note:** Imported data is verified against a project *label_config* and must
            include all variables that were used in the *label_config*. For example,
            if the label configuration has a *$text* variable, then each item in a data object
            must include a "text" field.
            <br>

            ## POST requests
            <hr style="opacity:0.3">

            There are three possible ways to import tasks with this endpoint:

            ### 1. **POST with data**
            Send JSON tasks as POST data. Only JSON is supported for POSTing files directly.
            Update this example to specify your authorization token and Label Studio instance host, then run the following from
            the command line.

            ```bash
            curl -H 'Content-Type: application/json' -H 'Authorization: Token abc123' \
            -X POST 'http://localhost:8000/api/projects/1/import' --data '[{"text": "Some text 1"}, {"text": "Some text 2"}]'
            ```

            ### 2. **POST with files**
            Send tasks as files. You can attach multiple files with different names.

            - **JSON**: text files in JavaScript object notation format
            - **CSV**: text files with tables in Comma Separated Values format
            - **TSV**: text files with tables in Tab Separated Value format
            - **TXT**: simple text files are similar to CSV with one column and no header, supported for projects with one source only

            Update this example to specify your authorization token, Label Studio instance host, and file name and path,
            then run the following from the command line:

            ```bash
            curl -H 'Authorization: Token abc123' \
            -X POST 'http://localhost:8000/api/projects/1/import' -F 'file=@path/to/my_file.csv'
            ```

            ### 3. **POST with URL**
            You can also provide a URL to a file with labeling tasks. Supported file formats are the same as in option 2.

            ```bash
            curl -H 'Content-Type: application/json' -H 'Authorization: Token abc123' \
            -X POST 'http://localhost:8000/api/projects/1/import' \
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.projects.import_tasks(
    id=1,
    request=[],
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

**request:** `typing.Sequence[ImportApiRequest]` 
    
</dd>
</dl>

<dl>
<dd>

**commit_to_project:** `typing.Optional[bool]` — Set to "true" to immediately commit tasks to the project.
    
</dd>
</dl>

<dl>
<dd>

**preannotated_from_fields:** `typing.Optional[typing.Union[str, typing.Sequence[str]]]` — List of fields to preannotate from the task data. For example, if you provide a list of `{"text": "text", "prediction": "label"}` items in the request, the system will create a task with the `text` field and a prediction with the `label` field when `preannoted_from_fields=["prediction"]`.
    
</dd>
</dl>

<dl>
<dd>

**return_task_ids:** `typing.Optional[bool]` — Set to "true" to return task IDs in the response.
    
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

<details><summary><code>client.projects.<a href="src/label_studio_sdk/projects/client.py">validate_label_config</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Determine whether the label configuration for a specific project is valid.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.projects.validate_label_config(
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

## Tasks
<details><summary><code>client.tasks.<a href="src/label_studio_sdk/tasks/client.py">create_many_status</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Return data related to async project import operation
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.tasks.create_many_status(
    id=1,
    import_pk=1,
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

**id:** `int` — A unique integer value identifying this project import.
    
</dd>
</dl>

<dl>
<dd>

**import_pk:** `int` 
    
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

Retrieve a paginated list of tasks. The response format varies based on the user's role in the organization:
- **Admin/Owner**: Full task details with all annotations, reviews, and metadata
- **Reviewer**: Task details optimized for review workflow
- **Annotator**: Task details filtered to show only user's own annotations and assignments
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**fields:** `typing.Optional[TasksListRequestFields]` — Set to "all" if you want to include annotations and predictions in the response. Defaults to task_only
    
</dd>
</dl>

<dl>
<dd>

**include:** `typing.Optional[str]` — Specify which fields to include in the response
    
</dd>
</dl>

<dl>
<dd>

**only_annotated:** `typing.Optional[bool]` — Filter to show only tasks that have annotations
    
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

**project:** `typing.Optional[int]` — Project ID
    
</dd>
</dl>

<dl>
<dd>

**query:** `typing.Optional[str]` 

Additional query to filter tasks. It must be JSON encoded string of dict containing one of the following parameters: {"filters": ..., "selectedItems": ..., "ordering": ...}. Check Data Manager > Create View > see data field for more details about filters, selectedItems and ordering.

filters: dict with "conjunction" string ("or" or "and") and list of filters in "items" array. Each filter is a dictionary with keys: "filter", "operator", "type", "value". Read more about available filters
Example: {"conjunction": "or", "items": [{"filter": "filter:tasks:completed_at", "operator": "greater", "type": "Datetime", "value": "2021-01-01T00:00:00.000Z"}]}
selectedItems: dictionary with keys: "all", "included", "excluded". If "all" is false, "included" must be used. If "all" is true, "excluded" must be used.
Examples: {"all": false, "included": [1, 2, 3]} or {"all": true, "excluded": [4, 5]}
ordering: list of fields to order by. Currently, ordering is supported by only one parameter.
Example: ["completed_at"]
    
</dd>
</dl>

<dl>
<dd>

**resolve_uri:** `typing.Optional[bool]` — Resolve task data URIs using Cloud Storage
    
</dd>
</dl>

<dl>
<dd>

**review:** `typing.Optional[bool]` — Get tasks for review
    
</dd>
</dl>

<dl>
<dd>

**selected_items:** `typing.Optional[str]` — JSON string of selected task IDs for review workflow
    
</dd>
</dl>

<dl>
<dd>

**view:** `typing.Optional[int]` — View ID
    
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

Create a new task
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.tasks.create(
    data={"key": "value"},
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

**data:** `typing.Optional[typing.Any]` 
    
</dd>
</dl>

<dl>
<dd>

**meta:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**is_labeled:** `typing.Optional[bool]` — True if the number of annotations for this task is greater than or equal to the number of maximum_completions for the project
    
</dd>
</dl>

<dl>
<dd>

**overlap:** `typing.Optional[int]` — Number of distinct annotators that processed the current task
    
</dd>
</dl>

<dl>
<dd>

**inner_id:** `typing.Optional[int]` — Internal task ID in the project, starts with 1
    
</dd>
</dl>

<dl>
<dd>

**total_annotations:** `typing.Optional[int]` — Number of total annotations for the current task except cancelled annotations
    
</dd>
</dl>

<dl>
<dd>

**cancelled_annotations:** `typing.Optional[int]` — Number of total cancelled annotations for the current task
    
</dd>
</dl>

<dl>
<dd>

**total_predictions:** `typing.Optional[int]` — Number of total predictions for the current task
    
</dd>
</dl>

<dl>
<dd>

**comment_count:** `typing.Optional[int]` — Number of comments in the task including all annotations
    
</dd>
</dl>

<dl>
<dd>

**unresolved_comment_count:** `typing.Optional[int]` — Number of unresolved comments in the task including all annotations
    
</dd>
</dl>

<dl>
<dd>

**last_comment_updated_at:** `typing.Optional[dt.datetime]` — When the last comment was updated
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID for this task
    
</dd>
</dl>

<dl>
<dd>

**updated_by:** `typing.Optional[int]` — Last annotator or reviewer who updated this task
    
</dd>
</dl>

<dl>
<dd>

**file_upload:** `typing.Optional[int]` — Uploaded file used as data source for this task
    
</dd>
</dl>

<dl>
<dd>

**comment_authors:** `typing.Optional[typing.Sequence[int]]` — Users who wrote comments
    
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

Delete a task in Label Studio. This action cannot be undone!
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.tasks.update(
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

**inner_id:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**cancelled_annotations:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**total_annotations:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**total_predictions:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**completed_at:** `typing.Optional[dt.datetime]` 
    
</dd>
</dl>

<dl>
<dd>

**predictions_score:** `typing.Optional[float]` 
    
</dd>
</dl>

<dl>
<dd>

**avg_lead_time:** `typing.Optional[float]` 
    
</dd>
</dl>

<dl>
<dd>

**draft_exists:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**reviewed:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**reviews_accepted:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**reviews_rejected:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**ground_truth:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**data:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**meta:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**is_labeled:** `typing.Optional[bool]` — True if the number of annotations for this task is greater than or equal to the number of maximum_completions for the project
    
</dd>
</dl>

<dl>
<dd>

**overlap:** `typing.Optional[int]` — Number of distinct annotators that processed the current task
    
</dd>
</dl>

<dl>
<dd>

**comment_count:** `typing.Optional[int]` — Number of comments in the task including all annotations
    
</dd>
</dl>

<dl>
<dd>

**unresolved_comment_count:** `typing.Optional[int]` — Number of unresolved comments in the task including all annotations
    
</dd>
</dl>

<dl>
<dd>

**last_comment_updated_at:** `typing.Optional[dt.datetime]` — When the last comment was updated
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — Project ID for this task
    
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

## Tokens
<details><summary><code>client.tokens.<a href="src/label_studio_sdk/tokens/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all API tokens for the current user.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.tokens.list()

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

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.tokens.<a href="src/label_studio_sdk/tokens/client.py">create</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new API token for the current user.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.tokens.create()

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

<details><summary><code>client.tokens.<a href="src/label_studio_sdk/tokens/client.py">blacklist</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Adds a JWT refresh token to the blacklist, preventing it from being used to obtain new access tokens.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.tokens.blacklist(
    refresh="refresh",
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

**refresh:** `str` 
    
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

<details><summary><code>client.tokens.<a href="src/label_studio_sdk/tokens/client.py">refresh</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a new access token, using a refresh token.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.tokens.refresh(
    refresh="refresh",
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

**refresh:** `str` 
    
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

<details><summary><code>client.tokens.<a href="src/label_studio_sdk/tokens/client.py">rotate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a new JWT refresh token and blacklists the current one.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.tokens.rotate(
    refresh="refresh",
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

**refresh:** `str` 
    
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

## Versions
<details><summary><code>client.versions.<a href="src/label_studio_sdk/versions/client.py">get</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get version information about the Label Studio instance.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.versions.get()

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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

Create a webhook for your organization.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**headers:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**is_active:** `typing.Optional[bool]` — If value is False the webhook is disabled
    
</dd>
</dl>

<dl>
<dd>

**actions:** `typing.Optional[typing.Sequence[ActionsEnum]]` 
    
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

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.webhooks.update(
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**url:** `typing.Optional[str]` — URL of webhook
    
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

**headers:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**is_active:** `typing.Optional[bool]` — If value is False the webhook is disabled
    
</dd>
</dl>

<dl>
<dd>

**actions:** `typing.Optional[typing.Sequence[ActionsEnum]]` 
    
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

Get descriptions of all available webhook actions to set up webhooks.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

## Workspaces
<details><summary><code>client.workspaces.<a href="src/label_studio_sdk/workspaces/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all workspaces for your organization. Workspaces in Label Studio let you organize your projects and users into separate spaces. This is useful for managing different teams, departments, or projects within your organization. For more information, see the [Workspaces documentation](https://docs.humansignal.com/workspaces).
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**is_personal:** `typing.Optional[bool]` — Workspace is a personal user workspace.
    
</dd>
</dl>

<dl>
<dd>

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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

<details><summary><code>client.workspaces.<a href="src/label_studio_sdk/workspaces/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new workspace. Workspaces in Label Studio let you organize your projects and users into separate spaces. This is useful for managing different teams, departments, or projects within your organization. For more information, see the [Workspaces documentation](https://docs.humansignal.com/workspaces).
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.workspaces.create(
    title="title",
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

**title:** `str` — Workspace name
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Workspace description
    
</dd>
</dl>

<dl>
<dd>

**color:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**is_personal:** `typing.Optional[bool]` — Workspace is a personal user workspace
    
</dd>
</dl>

<dl>
<dd>

**is_archived:** `typing.Optional[bool]` — Workspace is archived
    
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

Retrieve details for a specific workspace by ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Delete a specific workspace by ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Update settings for a specific workspace by ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Workspace name
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Workspace description
    
</dd>
</dl>

<dl>
<dd>

**color:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**is_personal:** `typing.Optional[bool]` — Workspace is a personal user workspace
    
</dd>
</dl>

<dl>
<dd>

**is_archived:** `typing.Optional[bool]` — Workspace is archived
    
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

## ExportStorage Azure
<details><summary><code>client.export_storage.azure.<a href="src/label_studio_sdk/export_storage/azure/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a list of all Azure export storage connections.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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

<details><summary><code>client.export_storage.azure.<a href="src/label_studio_sdk/export_storage/azure/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new Azure export storage connection to store annotations.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.export_storage.azure.<a href="src/label_studio_sdk/export_storage/azure/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific Azure export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Delete a specific Azure export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Update a specific Azure export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Sync tasks from an Azure export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.export_storage.azure.sync(
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

**id:** `int` 
    
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

Validate a specific Azure export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

## ExportStorage Gcs
<details><summary><code>client.export_storage.gcs.<a href="src/label_studio_sdk/export_storage/gcs/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a list of all GCS export storage connections.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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

<details><summary><code>client.export_storage.gcs.<a href="src/label_studio_sdk/export_storage/gcs/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new GCS export storage connection to store annotations.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.export_storage.gcs.<a href="src/label_studio_sdk/export_storage/gcs/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific GCS export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Delete a specific GCS export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Update a specific GCS export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Sync tasks from an GCS export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.export_storage.gcs.sync(
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

**id:** `int` 
    
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

Validate a specific GCS export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

## ExportStorage Local
<details><summary><code>client.export_storage.local.<a href="src/label_studio_sdk/export_storage/local/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a list of all local file export storage connections.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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

<details><summary><code>client.export_storage.local.<a href="src/label_studio_sdk/export_storage/local/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new local file export storage connection to store annotations.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.export_storage.local.<a href="src/label_studio_sdk/export_storage/local/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific local file export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Delete a specific local file export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Update a specific local file export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Sync tasks from a local file export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.export_storage.local.sync(
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

**id:** `int` 
    
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

Validate a specific local file export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

## ExportStorage Redis
<details><summary><code>client.export_storage.redis.<a href="src/label_studio_sdk/export_storage/redis/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a list of all Redis export storage connections.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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

<details><summary><code>client.export_storage.redis.<a href="src/label_studio_sdk/export_storage/redis/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new Redis export storage connection to store annotations.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.export_storage.redis.<a href="src/label_studio_sdk/export_storage/redis/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific Redis export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Delete a specific Redis export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Update a specific Redis export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Sync tasks from a Redis export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.export_storage.redis.sync(
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

**id:** `int` 
    
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

Validate a specific Redis export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

## ExportStorage S3
<details><summary><code>client.export_storage.s3.<a href="src/label_studio_sdk/export_storage/s3/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a list of all S3 export storage connections.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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

<details><summary><code>client.export_storage.s3.<a href="src/label_studio_sdk/export_storage/s3/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new S3 export storage connection to store annotations.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.export_storage.s3.<a href="src/label_studio_sdk/export_storage/s3/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific S3 export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Delete a specific S3 export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Update a specific S3 export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Sync tasks from an S3 export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.export_storage.s3.sync(
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

**id:** `int` 
    
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

Validate a specific S3 export storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

## ExportStorage S3S
<details><summary><code>client.export_storage.s3s.<a href="src/label_studio_sdk/export_storage/s3s/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a list of all S3 export storage connections that were set up with IAM role access.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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

Create an S3 export storage connection with IAM role access to store annotations.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.export_storage.s3s.create(
    role_arn="role_arn",
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

**role_arn:** `str` — AWS RoleArn
    
</dd>
</dl>

<dl>
<dd>

**project:** `int` — A unique integer value identifying this project.
    
</dd>
</dl>

<dl>
<dd>

**synchronizable:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**last_sync:** `typing.Optional[dt.datetime]` — Last sync finished time
    
</dd>
</dl>

<dl>
<dd>

**last_sync_count:** `typing.Optional[int]` — Count of tasks synced last time
    
</dd>
</dl>

<dl>
<dd>

**last_sync_job:** `typing.Optional[str]` — Last sync job ID
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[StatusD14Enum]` 
    
</dd>
</dl>

<dl>
<dd>

**traceback:** `typing.Optional[str]` — Traceback report for the last failed sync
    
</dd>
</dl>

<dl>
<dd>

**meta:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Cloud storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Cloud storage description
    
</dd>
</dl>

<dl>
<dd>

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled
    
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

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs
    
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

**external_id:** `typing.Optional[str]` — AWS ExternalId
    
</dd>
</dl>

<dl>
<dd>

**legacy_auth:** `typing.Optional[bool]` 
    
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

Get a specific S3 export storage connection that was set up with IAM role access.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Delete a specific S3 export storage connection that was set up with IAM role access.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Update a specific S3 export storage connection that was set up with IAM role access.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**synchronizable:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**last_sync:** `typing.Optional[dt.datetime]` — Last sync finished time
    
</dd>
</dl>

<dl>
<dd>

**last_sync_count:** `typing.Optional[int]` — Count of tasks synced last time
    
</dd>
</dl>

<dl>
<dd>

**last_sync_job:** `typing.Optional[str]` — Last sync job ID
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[StatusD14Enum]` 
    
</dd>
</dl>

<dl>
<dd>

**traceback:** `typing.Optional[str]` — Traceback report for the last failed sync
    
</dd>
</dl>

<dl>
<dd>

**meta:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Cloud storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Cloud storage description
    
</dd>
</dl>

<dl>
<dd>

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled
    
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

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs
    
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

**external_id:** `typing.Optional[str]` — AWS ExternalId
    
</dd>
</dl>

<dl>
<dd>

**role_arn:** `typing.Optional[str]` — AWS RoleArn
    
</dd>
</dl>

<dl>
<dd>

**legacy_auth:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — A unique integer value identifying this project.
    
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

<details><summary><code>client.export_storage.s3s.<a href="src/label_studio_sdk/export_storage/s3s/client.py">sync</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Sync tasks from an S3 export storage.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.export_storage.s3s.sync(
    id=1,
    role_arn="role_arn",
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**role_arn:** `str` — AWS RoleArn
    
</dd>
</dl>

<dl>
<dd>

**project:** `int` — A unique integer value identifying this project.
    
</dd>
</dl>

<dl>
<dd>

**synchronizable:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**last_sync:** `typing.Optional[dt.datetime]` — Last sync finished time
    
</dd>
</dl>

<dl>
<dd>

**last_sync_count:** `typing.Optional[int]` — Count of tasks synced last time
    
</dd>
</dl>

<dl>
<dd>

**last_sync_job:** `typing.Optional[str]` — Last sync job ID
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[StatusD14Enum]` 
    
</dd>
</dl>

<dl>
<dd>

**traceback:** `typing.Optional[str]` — Traceback report for the last failed sync
    
</dd>
</dl>

<dl>
<dd>

**meta:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Cloud storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Cloud storage description
    
</dd>
</dl>

<dl>
<dd>

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled
    
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

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs
    
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

**external_id:** `typing.Optional[str]` — AWS ExternalId
    
</dd>
</dl>

<dl>
<dd>

**legacy_auth:** `typing.Optional[bool]` 
    
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

Validate a specific S3 export storage connection that was set up with IAM role access.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.export_storage.s3s.validate(
    role_arn="role_arn",
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

**role_arn:** `str` — AWS RoleArn
    
</dd>
</dl>

<dl>
<dd>

**project:** `int` — A unique integer value identifying this project.
    
</dd>
</dl>

<dl>
<dd>

**synchronizable:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**last_sync:** `typing.Optional[dt.datetime]` — Last sync finished time
    
</dd>
</dl>

<dl>
<dd>

**last_sync_count:** `typing.Optional[int]` — Count of tasks synced last time
    
</dd>
</dl>

<dl>
<dd>

**last_sync_job:** `typing.Optional[str]` — Last sync job ID
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[StatusD14Enum]` 
    
</dd>
</dl>

<dl>
<dd>

**traceback:** `typing.Optional[str]` — Traceback report for the last failed sync
    
</dd>
</dl>

<dl>
<dd>

**meta:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Cloud storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Cloud storage description
    
</dd>
</dl>

<dl>
<dd>

**can_delete_objects:** `typing.Optional[bool]` — Deletion from storage enabled
    
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

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs
    
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

**external_id:** `typing.Optional[str]` — AWS ExternalId
    
</dd>
</dl>

<dl>
<dd>

**legacy_auth:** `typing.Optional[bool]` 
    
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

## ImportStorage Azure
<details><summary><code>client.import_storage.azure.<a href="src/label_studio_sdk/import_storage/azure/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get list of all Azure import storage connections.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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

<details><summary><code>client.import_storage.azure.<a href="src/label_studio_sdk/import_storage/azure/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create new Azure import storage
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.import_storage.azure.<a href="src/label_studio_sdk/import_storage/azure/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific Azure import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Delete a specific Azure import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Update a specific Azure import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Sync tasks from an Azure import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.import_storage.azure.<a href="src/label_studio_sdk/import_storage/azure/client.py">validate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Validate a specific Azure import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

## ImportStorage Gcs
<details><summary><code>client.import_storage.gcs.<a href="src/label_studio_sdk/import_storage/gcs/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a list of all GCS import storage connections.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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

<details><summary><code>client.import_storage.gcs.<a href="src/label_studio_sdk/import_storage/gcs/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new GCS import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.import_storage.gcs.<a href="src/label_studio_sdk/import_storage/gcs/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific GCS import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Delete a specific GCS import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Update a specific GCS import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Sync tasks from a GCS import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.import_storage.gcs.<a href="src/label_studio_sdk/import_storage/gcs/client.py">validate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Validate a specific GCS import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

## ImportStorage Local
<details><summary><code>client.import_storage.local.<a href="src/label_studio_sdk/import_storage/local/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a list of all local file import storage connections.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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

<details><summary><code>client.import_storage.local.<a href="src/label_studio_sdk/import_storage/local/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new local file import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.import_storage.local.<a href="src/label_studio_sdk/import_storage/local/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific local file import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Delete a specific local file import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Update a specific local file import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Sync tasks from a local file import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.import_storage.local.<a href="src/label_studio_sdk/import_storage/local/client.py">validate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Validate a specific local file import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

## ImportStorage Redis
<details><summary><code>client.import_storage.redis.<a href="src/label_studio_sdk/import_storage/redis/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a list of all Redis import storage connections.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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

<details><summary><code>client.import_storage.redis.<a href="src/label_studio_sdk/import_storage/redis/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new Redis import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.import_storage.redis.<a href="src/label_studio_sdk/import_storage/redis/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific Redis import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Delete a specific Redis import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Update a specific Redis import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Sync tasks from a Redis import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.import_storage.redis.<a href="src/label_studio_sdk/import_storage/redis/client.py">validate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Validate a specific Redis import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

## ImportStorage S3
<details><summary><code>client.import_storage.s3.<a href="src/label_studio_sdk/import_storage/s3/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a list of all S3 import storage connections.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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

<details><summary><code>client.import_storage.s3.<a href="src/label_studio_sdk/import_storage/s3/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create new S3 import storage
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.import_storage.s3.<a href="src/label_studio_sdk/import_storage/s3/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific S3 import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Delete a specific S3 import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Update a specific S3 import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Sync tasks from an S3 import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

<details><summary><code>client.import_storage.s3.<a href="src/label_studio_sdk/import_storage/s3/client.py">validate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Validate a specific S3 import storage connection.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

## ImportStorage S3S
<details><summary><code>client.import_storage.s3s.<a href="src/label_studio_sdk/import_storage/s3s/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get list of all S3 import storage connections set up with IAM role access.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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

Create S3 import storage with IAM role access.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.import_storage.s3s.create(
    role_arn="role_arn",
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

**role_arn:** `str` — AWS RoleArn
    
</dd>
</dl>

<dl>
<dd>

**project:** `int` — A unique integer value identifying this project.
    
</dd>
</dl>

<dl>
<dd>

**synchronizable:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**presign:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**last_sync:** `typing.Optional[dt.datetime]` — Last sync finished time
    
</dd>
</dl>

<dl>
<dd>

**last_sync_count:** `typing.Optional[int]` — Count of tasks synced last time
    
</dd>
</dl>

<dl>
<dd>

**last_sync_job:** `typing.Optional[str]` — Last sync job ID
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[StatusD14Enum]` 
    
</dd>
</dl>

<dl>
<dd>

**traceback:** `typing.Optional[str]` — Traceback report for the last failed sync
    
</dd>
</dl>

<dl>
<dd>

**meta:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Cloud storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Cloud storage description
    
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

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs
    
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

**external_id:** `typing.Optional[str]` — AWS ExternalId
    
</dd>
</dl>

<dl>
<dd>

**legacy_auth:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**presign_ttl:** `typing.Optional[int]` — Presigned URLs TTL (in minutes)
    
</dd>
</dl>

<dl>
<dd>

**recursive_scan:** `typing.Optional[bool]` — Perform recursive scan over the bucket content
    
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

Get a specific S3 import storage connection that was set up with IAM role access.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Delete a specific S3 import storage connection that was set up with IAM role access.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Update a specific S3 import storage connection that was set up with IAM role access.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**synchronizable:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**presign:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**last_sync:** `typing.Optional[dt.datetime]` — Last sync finished time
    
</dd>
</dl>

<dl>
<dd>

**last_sync_count:** `typing.Optional[int]` — Count of tasks synced last time
    
</dd>
</dl>

<dl>
<dd>

**last_sync_job:** `typing.Optional[str]` — Last sync job ID
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[StatusD14Enum]` 
    
</dd>
</dl>

<dl>
<dd>

**traceback:** `typing.Optional[str]` — Traceback report for the last failed sync
    
</dd>
</dl>

<dl>
<dd>

**meta:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Cloud storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Cloud storage description
    
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

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs
    
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

**external_id:** `typing.Optional[str]` — AWS ExternalId
    
</dd>
</dl>

<dl>
<dd>

**role_arn:** `typing.Optional[str]` — AWS RoleArn
    
</dd>
</dl>

<dl>
<dd>

**legacy_auth:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**presign_ttl:** `typing.Optional[int]` — Presigned URLs TTL (in minutes)
    
</dd>
</dl>

<dl>
<dd>

**recursive_scan:** `typing.Optional[bool]` — Perform recursive scan over the bucket content
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — A unique integer value identifying this project.
    
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

Sync tasks from an S3 import storage connection that was set up with IAM role access.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.import_storage.s3s.sync(
    id=1,
    role_arn="role_arn",
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**role_arn:** `str` — AWS RoleArn
    
</dd>
</dl>

<dl>
<dd>

**project:** `int` — A unique integer value identifying this project.
    
</dd>
</dl>

<dl>
<dd>

**synchronizable:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**presign:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**last_sync:** `typing.Optional[dt.datetime]` — Last sync finished time
    
</dd>
</dl>

<dl>
<dd>

**last_sync_count:** `typing.Optional[int]` — Count of tasks synced last time
    
</dd>
</dl>

<dl>
<dd>

**last_sync_job:** `typing.Optional[str]` — Last sync job ID
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[StatusD14Enum]` 
    
</dd>
</dl>

<dl>
<dd>

**traceback:** `typing.Optional[str]` — Traceback report for the last failed sync
    
</dd>
</dl>

<dl>
<dd>

**meta:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Cloud storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Cloud storage description
    
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

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs
    
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

**external_id:** `typing.Optional[str]` — AWS ExternalId
    
</dd>
</dl>

<dl>
<dd>

**legacy_auth:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**presign_ttl:** `typing.Optional[int]` — Presigned URLs TTL (in minutes)
    
</dd>
</dl>

<dl>
<dd>

**recursive_scan:** `typing.Optional[bool]` — Perform recursive scan over the bucket content
    
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

Validate a specific S3 import storage connection that was set up with IAM role access.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.import_storage.s3s.validate(
    role_arn="role_arn",
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

**role_arn:** `str` — AWS RoleArn
    
</dd>
</dl>

<dl>
<dd>

**project:** `int` — A unique integer value identifying this project.
    
</dd>
</dl>

<dl>
<dd>

**synchronizable:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**presign:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**last_sync:** `typing.Optional[dt.datetime]` — Last sync finished time
    
</dd>
</dl>

<dl>
<dd>

**last_sync_count:** `typing.Optional[int]` — Count of tasks synced last time
    
</dd>
</dl>

<dl>
<dd>

**last_sync_job:** `typing.Optional[str]` — Last sync job ID
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[StatusD14Enum]` 
    
</dd>
</dl>

<dl>
<dd>

**traceback:** `typing.Optional[str]` — Traceback report for the last failed sync
    
</dd>
</dl>

<dl>
<dd>

**meta:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Cloud storage title
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Cloud storage description
    
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

**regex_filter:** `typing.Optional[str]` — Cloud storage regex for filtering objects
    
</dd>
</dl>

<dl>
<dd>

**use_blob_urls:** `typing.Optional[bool]` — Interpret objects as BLOBs and generate URLs
    
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

**external_id:** `typing.Optional[str]` — AWS ExternalId
    
</dd>
</dl>

<dl>
<dd>

**legacy_auth:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**presign_ttl:** `typing.Optional[int]` — Presigned URLs TTL (in minutes)
    
</dd>
</dl>

<dl>
<dd>

**recursive_scan:** `typing.Optional[bool]` — Perform recursive scan over the bucket content
    
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

## Organizations Members
<details><summary><code>client.organizations.members.<a href="src/label_studio_sdk/organizations/members/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get organization member details by user ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.organizations.members.get(
    id=1,
    user_pk=1,
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**user_pk:** `int` — A unique integer value identifying the user to get organization details for.
    
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

<details><summary><code>client.organizations.members.<a href="src/label_studio_sdk/organizations/members/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Soft delete a member from the organization.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.organizations.members.delete(
    id=1,
    user_pk=1,
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**user_pk:** `int` — A unique integer value identifying the user to be deleted from the organization.
    
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
<details><summary><code>client.projects.exports.<a href="src/label_studio_sdk/projects/exports/client.py">list_formats</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve the available export formats for the current project by ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

Returns a list of exported files for a specific project by ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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

Create a new export request to start a background task and generate an export file for a specific project by ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.projects.exports.create(
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

**title:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**created_by:** `typing.Optional[UserSimpleRequest]` 
    
</dd>
</dl>

<dl>
<dd>

**finished_at:** `typing.Optional[dt.datetime]` — Complete or fail time
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[Status7BfEnum]` 
    
</dd>
</dl>

<dl>
<dd>

**md5:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**counters:** `typing.Optional[typing.Optional[typing.Any]]` 
    
</dd>
</dl>

<dl>
<dd>

**converted_formats:** `typing.Optional[typing.Sequence[ConvertedFormatRequest]]` 
    
</dd>
</dl>

<dl>
<dd>

**task_filter_options:** `typing.Optional[LseTaskFilterOptionsRequest]` 
    
</dd>
</dl>

<dl>
<dd>

**annotation_filter_options:** `typing.Optional[LseAnnotationFilterOptionsRequest]` 
    
</dd>
</dl>

<dl>
<dd>

**serialization_options:** `typing.Optional[SerializationOptionsRequest]` 
    
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

Retrieve information about an export file by export ID for a specific project.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.projects.exports.get(
    export_pk="export_pk",
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

**export_pk:** `str` — Primary key identifying the export file.
    
</dd>
</dl>

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

<details><summary><code>client.projects.exports.<a href="src/label_studio_sdk/projects/exports/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete an export file by specified export ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.projects.exports.delete(
    export_pk="export_pk",
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

**export_pk:** `str` — Primary key identifying the export file.
    
</dd>
</dl>

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

<details><summary><code>client.projects.exports.<a href="src/label_studio_sdk/projects/exports/client.py">convert</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Convert export snapshot to selected format
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.projects.exports.convert(
    export_pk="export_pk",
    id=1,
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

**export_pk:** `str` — Primary key identifying the export file.
    
</dd>
</dl>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this project.
    
</dd>
</dl>

<dl>
<dd>

**export_type:** `str` — Export file format.
    
</dd>
</dl>

<dl>
<dd>

**download_resources:** `typing.Optional[bool]` — Download resources in converter.
    
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


        Download an export file in the specified format for a specific project. Specify the project ID with the `id`
        parameter in the path and the ID of the export file you want to download using the `export_pk` parameter
        in the path.

        Get the `export_pk` from the response of the request to [Create new export](/api#operation/api_projects_exports_create)
        or after [listing export files](/api#operation/api_projects_exports_list).
        
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.projects.exports.download(
    export_pk="export_pk",
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

**export_pk:** `str` — Primary key identifying the export file.
    
</dd>
</dl>

<dl>
<dd>

**id:** `int` — A unique integer value identifying this project.
    
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

## Projects Pauses
<details><summary><code>client.projects.pauses.<a href="src/label_studio_sdk/projects/pauses/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a list of all pauses.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.projects.pauses.list(
    project_pk=1,
    user_pk=1,
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

**project_pk:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**user_pk:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**include_deleted:** `typing.Optional[bool]` — Include deleted pauses.
    
</dd>
</dl>

<dl>
<dd>

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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

<details><summary><code>client.projects.pauses.<a href="src/label_studio_sdk/projects/pauses/client.py">create</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new pause entry.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.projects.pauses.create(
    project_pk=1,
    user_pk=1,
    reason="MANUAL",
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

**project_pk:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**user_pk:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**reason:** `ReasonEnum` 

Reason for pausing

* `MANUAL` - Manual
* `BEHAVIOR_BASED` - Behavior-based
* `ANNOTATOR_EVALUATION` - Annotator evaluation
* `ANNOTATION_LIMIT` - Annotation limit
* `CUSTOM_SCRIPT` - Custom script
    
</dd>
</dl>

<dl>
<dd>

**verbose_reason:** `typing.Optional[str]` — Detailed description of why the project is paused, will be readable by paused annotators
    
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

<details><summary><code>client.projects.pauses.<a href="src/label_studio_sdk/projects/pauses/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a specific pause by ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.projects.pauses.get(
    id="id",
    project_pk=1,
    user_pk=1,
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

**project_pk:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**user_pk:** `int` 
    
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

<details><summary><code>client.projects.pauses.<a href="src/label_studio_sdk/projects/pauses/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific pause by ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.projects.pauses.delete(
    id="id",
    project_pk=1,
    user_pk=1,
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

**project_pk:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**user_pk:** `int` 
    
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

<details><summary><code>client.projects.pauses.<a href="src/label_studio_sdk/projects/pauses/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Partially update a pause entry by ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.projects.pauses.update(
    id="id",
    project_pk=1,
    user_pk=1,
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

**project_pk:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**user_pk:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**reason:** `typing.Optional[ReasonEnum]` 

Reason for pausing

* `MANUAL` - Manual
* `BEHAVIOR_BASED` - Behavior-based
* `ANNOTATOR_EVALUATION` - Annotator evaluation
* `ANNOTATION_LIMIT` - Annotation limit
* `CUSTOM_SCRIPT` - Custom script
    
</dd>
</dl>

<dl>
<dd>

**verbose_reason:** `typing.Optional[str]` — Detailed description of why the project is paused, will be readable by paused annotators
    
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

## Prompts Indicators
<details><summary><code>client.prompts.indicators.<a href="src/label_studio_sdk/prompts/indicators/client.py">get_key_indicators</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get key indicators for the Prompt dashboard.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.indicators.get_key_indicators(
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

**id:** `int` 
    
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

<details><summary><code>client.prompts.indicators.<a href="src/label_studio_sdk/prompts/indicators/client.py">get_key_indicator</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a specific key indicator for the Prompt dashboard.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.indicators.get_key_indicator(
    id=1,
    indicator_key="indicator_key",
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**indicator_key:** `str` 
    
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
<details><summary><code>client.prompts.versions.<a href="src/label_studio_sdk/prompts/versions/client.py">get_default_version_name</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get default prompt version name
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.versions.get_default_version_name(
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

**id:** `int` 
    
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

<details><summary><code>client.prompts.versions.<a href="src/label_studio_sdk/prompts/versions/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all versions of a prompt.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.versions.list(
    prompt_id_=1,
    prompt_id=1,
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

**prompt_id_:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**prompt_id:** `int` — A unique integer value identifying the model ID to list versions for.
    
</dd>
</dl>

<dl>
<dd>

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.versions.create(
    prompt_id=1,
    title="title",
    prompt="prompt",
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

**prompt_id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**title:** `str` — Model name
    
</dd>
</dl>

<dl>
<dd>

**prompt:** `str` — Prompt to execute
    
</dd>
</dl>

<dl>
<dd>

**provider_model_id:** `str` — The model ID to use within the given provider, e.g. gpt-3.5
    
</dd>
</dl>

<dl>
<dd>

**parent_model:** `typing.Optional[int]` — Parent model interface ID
    
</dd>
</dl>

<dl>
<dd>

**provider:** `typing.Optional[ProviderEnum]` 

The model provider to use e.g. OpenAI

* `OpenAI` - OpenAI
* `AzureOpenAI` - AzureOpenAI
* `AzureAIFoundry` - AzureAIFoundry
* `VertexAI` - VertexAI
* `Gemini` - Gemini
* `Anthropic` - Anthropic
* `Custom` - Custom
    
</dd>
</dl>

<dl>
<dd>

**model_provider_connection:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**organization:** `typing.Optional[int]` 
    
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

<details><summary><code>client.prompts.versions.<a href="src/label_studio_sdk/prompts/versions/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a specific prompt of a model.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.versions.get(
    id=1,
    prompt_id=1,
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**prompt_id:** `int` 
    
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

<details><summary><code>client.prompts.versions.<a href="src/label_studio_sdk/prompts/versions/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a prompt version by ID
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.versions.delete(
    id=1,
    prompt_id=1,
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**prompt_id:** `int` 
    
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

<details><summary><code>client.prompts.versions.<a href="src/label_studio_sdk/prompts/versions/client.py">update</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update a specific prompt version by ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.versions.update(
    id=1,
    prompt_id=1,
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**prompt_id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**parent_model:** `typing.Optional[int]` — Parent model interface ID
    
</dd>
</dl>

<dl>
<dd>

**title:** `typing.Optional[str]` — Model name
    
</dd>
</dl>

<dl>
<dd>

**prompt:** `typing.Optional[str]` — Prompt to execute
    
</dd>
</dl>

<dl>
<dd>

**provider:** `typing.Optional[ProviderEnum]` 

The model provider to use e.g. OpenAI

* `OpenAI` - OpenAI
* `AzureOpenAI` - AzureOpenAI
* `AzureAIFoundry` - AzureAIFoundry
* `VertexAI` - VertexAI
* `Gemini` - Gemini
* `Anthropic` - Anthropic
* `Custom` - Custom
    
</dd>
</dl>

<dl>
<dd>

**provider_model_id:** `typing.Optional[str]` — The model ID to use within the given provider, e.g. gpt-3.5
    
</dd>
</dl>

<dl>
<dd>

**model_provider_connection:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**organization:** `typing.Optional[int]` 
    
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

<details><summary><code>client.prompts.versions.<a href="src/label_studio_sdk/prompts/versions/client.py">get_cost_estimate</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get an estimate of the cost for making an inference run on the selected Prompt Version and Project/ProjectSubset
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.versions.get_cost_estimate(
    prompt_id=1,
    version_id=1,
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

**prompt_id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**version_id:** `int` 
    
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

<details><summary><code>client.prompts.versions.<a href="src/label_studio_sdk/prompts/versions/client.py">get_refinement_status</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get the refined prompt based on the `refinement_job_id`.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.versions.get_refinement_status(
    prompt_id=1,
    version_id=1,
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

**prompt_id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**version_id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**refinement_job_id:** `typing.Optional[str]` — Refinement Job ID acquired from the `POST /api/prompts/{prompt_id}/versions/{version_id}/refine` endpoint
    
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

<details><summary><code>client.prompts.versions.<a href="src/label_studio_sdk/prompts/versions/client.py">refine</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Refine a prompt version using a teacher model and save the refined prompt as a new version.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.versions.refine(
    prompt_id=1,
    version_id=1,
    teacher_model_provider_connection_id=1,
    teacher_model_name="teacher_model_name",
    project_id=1,
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

**prompt_id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**version_id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**teacher_model_provider_connection_id:** `int` — Model Provider Connection ID to use to refine the prompt
    
</dd>
</dl>

<dl>
<dd>

**teacher_model_name:** `str` — Name of the model to use to refine the prompt
    
</dd>
</dl>

<dl>
<dd>

**project_id:** `int` — Project ID to target the refined prompt for
    
</dd>
</dl>

<dl>
<dd>

**async_:** `typing.Optional[bool]` — Whether to run the refinement asynchronously
    
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

## Prompts Runs
<details><summary><code>client.prompts.runs.<a href="src/label_studio_sdk/prompts/runs/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get information (status, metadata, etc) about an existing inference run
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.runs.list(
    prompt_id=1,
    version_id=1,
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

**prompt_id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**version_id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**ordering:** `typing.Optional[str]` — Which field to use when ordering the results.
    
</dd>
</dl>

<dl>
<dd>

**parent_model:** `typing.Optional[int]` — The ID of the parent model for this Inference Run
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[int]` — The ID of the project this Inference Run makes predictions on
    
</dd>
</dl>

<dl>
<dd>

**project_subset:** `typing.Optional[RunsListRequestProjectSubset]` — Defines which tasks are operated on (e.g. HasGT will only operate on tasks with a ground truth annotation, but All will operate on all records)
    
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

<details><summary><code>client.prompts.runs.<a href="src/label_studio_sdk/prompts/runs/client.py">create</a>(...)</code></summary>
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.prompts.runs.create(
    prompt_id=1,
    version_id=1,
    project=1,
    model_version=1,
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

**prompt_id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**version_id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**project:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**model_version:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**project_subset:** `typing.Optional[ProjectSubsetEnum]` 
    
</dd>
</dl>

<dl>
<dd>

**job_id:** `typing.Optional[str]` — Job ID for inference job for a ModelRun e.g. Adala job ID
    
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

**predictions_updated_at:** `typing.Optional[dt.datetime]` 
    
</dd>
</dl>

<dl>
<dd>

**organization:** `typing.Optional[int]` 
    
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

Get a list of all members in a specific workspace.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

Add a new workspace member by user ID.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
client.workspaces.members.create(
    id=1,
    user=1,
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

**id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**user:** `int` — User ID
    
</dd>
</dl>

<dl>
<dd>

**workspace:** `typing.Optional[int]` — Workspace ID
    
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

Remove a specific member by ID from a workspace. This endpoint expects an object like `{"user_id": 123}`.
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
from label_studio_sdk import LabelStudio

client = LabelStudio(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
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

**id:** `int` 
    
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

