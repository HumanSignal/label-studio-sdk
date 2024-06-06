from unittest.mock import Mock

import requests_mock

from label_studio_sdk import Client
from label_studio_sdk.data_manager import Filters, Operator, Type, Column


def test_client_headers():
    mock_session = Mock(spec=["request"])
    mock_session.request.return_value = Mock(status_code=200)
    client = Client(
        url="http://fake.url",
        api_key="fake_key",
        session=mock_session,
        versions={"label-studio": "1.0.0"},
        extra_headers={"Proxy-Authorization": "Bearer fake_bearer"},
    )

    client.check_connection()
    args, kwargs = mock_session.request.call_args
    assert kwargs["headers"] == {
        "Authorization": f"Token fake_key",
        "Proxy-Authorization": "Bearer fake_bearer",
    }


def test_client_no_extra_headers():
    mock_session = Mock(spec=["request"])
    mock_session.request.return_value = Mock(status_code=200)
    client = Client(
        url="http://fake.url",
        api_key="fake_key",
        session=mock_session,
        versions={"label-studio": "1.0.0"},
    )

    client.check_connection()
    args, kwargs = mock_session.request.call_args
    assert kwargs["headers"] == {"Authorization": f"Token fake_key"}


def test_project_export_with_filters():
    with requests_mock.Mocker() as m:
        m.get(
            'http://fake.url/api/version',
            json={"version": "1.0.0"},
            status_code=200,
        )
        m.get(
            'http://fake.url/api/projects/1',
            json={"id": 1, "title": "fake_project"},
            status_code=200,
        )
        m.post(
            'http://fake.url/api/projects/1/exports',
            json={"id": 1, "title": "fake_project"},
            status_code=200,
        )
        m.post(
            'http://fake.url/api/dm/views',
            json={"id": 1, "title": "fake_project"},
            status_code=200,
        )
        m.post(
            'http://fake.url/api/projects/1/exports',
            json={"id": 1, "title": "fake_project"},
            status_code=200,
        )
        m.get(
            'http://fake.url/api/projects/1/exports/1',
            json={"id": 1, "title": "fake_project", "status": "completed"},
            status_code=200,
        )
        m.get(
            'http://fake.url/api/projects/1/exports/1/download?exportType=JSON',
            headers={"Content-Disposition": "attachment; filename=fake_project.json"},
            status_code=200,
        )
        m.delete(
            'http://fake.url/api/dm/views/1',
            status_code=200,
        )

        filters = Filters.create(
            Filters.AND,
            [
                Filters.item(
                    Column.inner_id,
                    Operator.GREATER_OR_EQUAL,
                    Type.Number,
                    Filters.value(1),
                ),
                Filters.item(
                    Column.inner_id,
                    Operator.LESS,
                    Type.Number,
                    Filters.value(100),
                ),
            ],
        )

        ls = Client(url='http://fake.url', api_key='fake_key')
        project = ls.get_project(1)
        project.export(filters=filters)
