from unittest.mock import Mock

from label_studio_sdk.client import Client


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
