""" Export tasks filtered by inner_id range
"""

import json
import os
from pathlib import Path

from label_studio_sdk.client import LabelStudio
from label_studio_sdk.data_manager import Filters, Operator, Type, Column


# Usage example (override via env vars if needed)
host = os.getenv('LABEL_STUDIO_URL', 'http://localhost:8080')
api_key = os.getenv('LABEL_STUDIO_API_KEY')
project_id = int(os.getenv('LABEL_STUDIO_PROJECT_ID', '1'))
start_id = int(os.getenv('START_INNER_ID', '1'))
end_id = int(os.getenv('END_INNER_ID', '20000'))

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

ls = LabelStudio(base_url=host, api_key=api_key)

# Create a view using this filter

view = ls.views.create(project=project_id, data={'filters': filters})

# Create export snapshot and download JSON
out_dir = Path("exported/")
out_dir.mkdir(parents=True, exist_ok=True)

create_kwargs = {
    "title": "Export SDK Snapshot",
    "task_filter_options": {'view': view.id},
}
print('creating snapshot...')
snapshot = ls.projects.exports.create(
    project_id,
    **create_kwargs,
)

# wait for snapshot to finish
# can also poll it
import time
time.sleep(5)

data_iter = ls.projects.exports.download(export_pk=snapshot.id, id=project_id, export_type='JSON')

out_path = out_dir / f"project_{project_id}_export.json"
with open(out_path, "wb") as f:
    for data in data_iter:
        f.write(data)

print(f"Export completed. File saved to: {out_path}")

