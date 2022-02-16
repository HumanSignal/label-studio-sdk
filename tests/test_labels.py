import requests_mock

from label_studio_sdk.client import Client

LS_URL = 'http://fake.url'

LABELS_RESPONSE = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [
        {
            "id": 3,
            "from_name": "test",
            "project": 37,
            "label": {
                "id": 2,
                "created_at": "2022-01-31T13:27:06.270857Z",
                "updated_at": "2022-01-31T13:27:06.270880Z",
                "value": {"a": 1},
                "label_config_tags": None,
                "title": "Test",
                "description": None,
                "approved": False,
                "created_by": 1,
                "approved_by": None,
                "organization": 1,
            },
        }
    ],
}


def test_get_label_links():
    client = Client(url=LS_URL, api_key='fake_key')
    with requests_mock.Mocker() as m:
        m.get(f'{LS_URL}/api/label_links', json=LABELS_RESPONSE)
        label_link = client.get_label_links()[0]
        assert label_link.from_name == LABELS_RESPONSE['results'][0]['from_name']
        assert label_link.project == LABELS_RESPONSE['results'][0]['project']


def test_create_labels():
    labels_data = [
        {"value": {"test": 1}, "title": "aaa", "from_name": "test", "project": 37},
        {"value": {"test": 2}, "title": "bbb", "from_name": "test", "project": 37},
    ]
    client = Client(url=LS_URL, api_key='fake_key')
    with requests_mock.Mocker() as m:
        m.post(f'{LS_URL}/api/labels', json=labels_data)
        labels = client.create_labels(labels_data)
        assert len(labels) == 2


def test_get_update_label():
    label_id = 2
    label_response = {
        "id": label_id,
        "links": [3],
        "created_at": "2022-01-31T13:27:06.270857Z",
        "updated_at": "2022-01-31T13:27:06.270880Z",
        "value": {"a": 1},
        "label_config_tags": None,
        "title": "Test",
        "description": None,
        "approved": False,
        "created_by": 1,
        "approved_by": None,
        "organization": 1,
        "projects": [37],
    }
    updated_label_response = {
        "id": label_id,
        "links": [3],
        "created_at": "2022-01-31T13:27:06.270857Z",
        "updated_at": "2022-01-31T13:27:06.270880Z",
        "value": {"a": 1},
        "label_config_tags": None,
        "title": "Test",
        "description": None,
        "approved": False,
        "created_by": 1,
        "approved_by": None,
        "organization": 1,
        "projects": [37],
    }
    client = Client(url=LS_URL, api_key='fake_key')
    with requests_mock.Mocker() as m:
        m.get(f'{LS_URL}/api/labels/{label_id}', json=label_response)
        label = client.get_label(label_id)
        m.patch(f'{LS_URL}/api/labels/{label_id}', json=updated_label_response)
        new_title = 'New title'
        label.update(title=new_title)
        assert label.title == new_title


def test_delete_label():
    label_id = 2
    label_response = {
        "id": label_id,
        "links": [3],
        "created_at": "2022-01-31T13:27:06.270857Z",
        "updated_at": "2022-01-31T13:27:06.270880Z",
        "value": {"a": 1},
        "label_config_tags": None,
        "title": "Test",
        "description": None,
        "approved": False,
        "created_by": 1,
        "approved_by": None,
        "organization": 1,
        "projects": [37],
    }
    client = Client(url=LS_URL, api_key='fake_key')
    with requests_mock.Mocker() as m:
        m.get(f'{LS_URL}/api/labels/{label_id}', json=label_response)
        label = client.get_label(label_id)
        m.delete(f'{LS_URL}/api/labels/{label.id}')
        label.delete()

def test_bulk_update_labels():
    client = Client(url=LS_URL, api_key='fake_key')
    with requests_mock.Mocker() as m:
        m.post(f'{LS_URL}/api/labels/bulk', json={'annotations_updated': 1})
        annotations_updated = client.bulk_update_labels(old_label=['Positive'], new_label=['Negative'], project=1)
        assert annotations_updated == 1
