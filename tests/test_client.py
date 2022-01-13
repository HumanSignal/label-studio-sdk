from unittest.mock import patch

from label_studio_sdk.client import Client


def test_client_headers():
    client = Client(url='http://fake.url', api_key='fake_key',
                    extra_headers={'Proxy-Authorization': 'Bearer fake_bearer'})
    with patch('requests.Session.request') as mocked_get:
        mocked_get.return_value.status_code = 200
        client.check_connection()
        args, kwargs = mocked_get.call_args
        assert kwargs['headers'] == {'Authorization': f'Token fake_key', 'Proxy-Authorization': 'Bearer fake_bearer'}


def test_client_no_extra_headers():
    client = Client(url='http://fake.url', api_key='fake_key')
    with patch('requests.Session.request') as mocked_get:
        mocked_get.return_value.status_code = 200
        client.check_connection()
        args, kwargs = mocked_get.call_args
        assert kwargs['headers'] == {'Authorization': f'Token fake_key'}
