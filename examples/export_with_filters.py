""" Export a snapshot with tasks filtered by ID range.

**Note:** at this moment it's not possible to export snapshots with filters,
LS API doesn't support it yet. However, it's achievable by creating a view
with a filter and then exporting a snapshot using this view.
This approach is hidden behind the `project.export()` method.

**Note:** This code utilizes functions from an older version of the Label Studio SDK (v0.0.34). 
The newer versions v1.0 and above still support the functionalities of the old version, but you will need to specify
[`label_studio_sdk._legacy`](../README.md) in your script.
"""

from label_studio_sdk import Client
from label_studio_sdk.data_manager import Filters, Operator, Type, Column


# Usage example
host = 'https://app.heartex.com'
api_key = '<your_api_key>'
project_id = 14528
start_id = 10000
end_id = 20000

# Create a filter for task ID range
filters = Filters.create(
    Filters.AND,
    [
        Filters.item(
            Column.inner_id,
            Operator.GREATER_OR_EQUAL,
            Type.Number,
            Filters.value(start_id),
        ),
        Filters.item(
            Column.inner_id,
            Operator.LESS,
            Type.Number,
            Filters.value(end_id),
        ),
    ],
)

print('Export started ...')
ls = Client(url=host, api_key=api_key)
project = ls.get_project(project_id)
result = project.export(filters=filters, export_type="JSON", output_dir='exported')
print(
    f"Export file saved as: exported/{result['filename']}, status: {result['status']}, export_id: {result['export_id']}"
)
