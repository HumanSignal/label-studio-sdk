""" Export tasks filtered by inner_id range using SDK 2.0+

For OSS, export snapshots with filters require a saved view. As a portable alternative,
we paginate tasks with a filters query and save them as JSON.
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

print('Export started ...')
ls = LabelStudio(base_url=host, api_key=api_key)

# Paginate tasks with filters
paged = ls.tasks.list(project=project_id, fields='all', query=json.dumps({'filters': filters}))
tasks = [t.model_dump(mode="json") for t in paged]

out_dir = Path('exported')
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / f'project_{project_id}_inner_id_{start_id}_{end_id}.json'
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(tasks, f)

print(f"Export file saved as: {out_file}")
