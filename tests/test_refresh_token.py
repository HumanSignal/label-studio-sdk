import asyncio
import datetime
import json
import threading
import time
from datetime import timezone
from unittest.mock import patch

import httpx
import jwt
import pytest
from label_studio_sdk import LabelStudio
from label_studio_sdk.client import AsyncLabelStudio
from label_studio_sdk.core.api_error import ApiError
from label_studio_sdk.projects.types.projects_list_response import \
    ProjectsListResponse
from label_studio_sdk.types.token_refresh_response import TokenRefreshResponse
from label_studio_sdk.tokens.client_ext import TokensClientExt

NOW = int(datetime.datetime.now(timezone.utc).timestamp())
ONE_HOUR_AGO = NOW - 3600
IN_ONE_HOUR = NOW + 3600
BASE_URL = "https://mocked.test"


@pytest.mark.respx(base_url=BASE_URL)
def test_refresh_token_auth(respx_mock):
    """Test basic refresh token authentication."""
    refresh_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    access_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    refresh_route = respx_mock.post("/api/token/refresh/").mock(
        return_value=httpx.Response(200, json={"access": access_token})
    )
    projects_route = respx_mock.get("/api/projects/").mock(
        return_value=httpx.Response(200, json=ProjectsListResponse(count=0, results=[]).dict())
    )

    client = LabelStudio(
        base_url=BASE_URL,
        api_key=refresh_token
    )
    client.projects.list()

    assert refresh_route.called
    assert json.loads(refresh_route.calls.last.request.content.decode()) == {"refresh": refresh_token}
    assert projects_route.calls.last.response.status_code == 200


@pytest.mark.respx(base_url=BASE_URL)
def test_initial_request_triggers_token_refresh(respx_mock):
    """Test that the initial request with no access token triggers a token refresh."""
    refresh_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    access_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    refresh_route = respx_mock.post("/api/token/refresh/").mock(
        return_value=httpx.Response(200, json={"access": access_token})
    )
    projects_route = respx_mock.get("/api/projects/").mock(
        return_value=httpx.Response(200, json=ProjectsListResponse(count=0, results=[]).dict())
    )

    client = LabelStudio(
        base_url=BASE_URL,
        api_key=refresh_token
    )
    client.projects.list()

    assert projects_route.calls.last.response.status_code == 200
    assert refresh_route.called


@pytest.mark.respx(base_url=BASE_URL)
def test_expired_token_triggers_refresh(respx_mock):
    """Test that a request with an expired access token triggers a token refresh."""
    refresh_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    expired_access_token = jwt.encode({"exp": ONE_HOUR_AGO}, "secret")
    valid_access_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    refresh_route = respx_mock.post("/api/token/refresh/").mock(
        return_value=httpx.Response(200, json={"access": valid_access_token})
    )
    projects_route = respx_mock.get("/api/projects/").mock(
        return_value=httpx.Response(200, json=ProjectsListResponse(count=0, results=[]).dict())
    )

    client = LabelStudio(
        base_url=BASE_URL,
        api_key=refresh_token
    )
    client._client_wrapper._tokens_client._set_access_token(expired_access_token)
    client.projects.list()

    assert projects_route.calls.last.response.status_code == 200
    assert refresh_route.called


@pytest.mark.respx(base_url=BASE_URL, assert_all_called=False)
def test_valid_token_skips_refresh(respx_mock):
    """Test that a request with a valid access token does not trigger a token refresh."""
    refresh_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    access_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")

    refresh_route = respx_mock.post("/api/token/refresh/").mock(
        return_value=httpx.Response(200, json={"access": access_token})
    )
    projects_route = respx_mock.get("/api/projects/").mock(
        return_value=httpx.Response(200, json=ProjectsListResponse(count=0, results=[]).dict())
    )

    client = LabelStudio(
        base_url=BASE_URL,
        api_key=refresh_token
    )
    client._client_wrapper._tokens_client._set_access_token(access_token)
    client.projects.list()

    assert projects_route.calls.last.response.status_code == 200
    assert not refresh_route.called


@pytest.mark.respx(base_url=BASE_URL)
def test_legacy_token_detection(respx_mock):
    """Test that a non-JWT token is automatically detected as a legacy token."""
    legacy_token = "some-legacy-token-123"
    projects_route = respx_mock.get("/api/projects/").mock(
        return_value=httpx.Response(200, json=ProjectsListResponse(count=0, results=[]).dict())
    )

    client = LabelStudio(
        base_url=BASE_URL,
        api_key=legacy_token
    )
    client.projects.list()

    assert projects_route.calls.last.response.status_code == 200
    assert projects_route.calls.last.request.headers["Authorization"] == f"Token {legacy_token}"


@pytest.mark.respx(base_url=BASE_URL)
@pytest.mark.asyncio
async def test_async_legacy_token_detection(respx_mock):
    """Test that a non-JWT token is automatically detected as a legacy token in async client."""
    legacy_token = "some-legacy-token-123"
    projects_route = respx_mock.get("/api/projects/").mock(
        return_value=httpx.Response(200, json=ProjectsListResponse(count=0, results=[]).dict())
    )

    client = AsyncLabelStudio(
        base_url=BASE_URL,
        api_key=legacy_token
    )
    await client.projects.list()

    assert projects_route.calls.last.response.status_code == 200
    assert projects_route.calls.last.request.headers["Authorization"] == f"Token {legacy_token}"


@pytest.mark.respx(base_url=BASE_URL)
@pytest.mark.asyncio
async def test_async_jwt_refresh_token(respx_mock):
    """Test that a JWT token is automatically detected and uses the JWT mechanism in async client."""
    jwt_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    refresh_route = respx_mock.post("/api/token/refresh/").mock(
        return_value=httpx.Response(200, json={"access": jwt_token})
    )
    projects_route = respx_mock.get("/api/projects/").mock(
        return_value=httpx.Response(200, json=ProjectsListResponse(count=0, results=[]).dict())
    )

    async with httpx.AsyncClient() as http_client:
        client = AsyncLabelStudio(
            base_url=BASE_URL,
            api_key=jwt_token,
            httpx_client=http_client
        )
        # Force token refresh by setting expired token
        client._client_wrapper._tokens_client._access_token = jwt.encode({"exp": ONE_HOUR_AGO}, "secret")
        client._client_wrapper._tokens_client._access_token_expiration = ONE_HOUR_AGO

        # Ensure we refresh the token before making the request
        client._client_wrapper._tokens_client.refresh()

        await client.projects.list()

    assert refresh_route.called
    assert projects_route.called
    assert projects_route.calls.last.request.headers["Authorization"].startswith("Bearer ")



def test_expired_api_key_detection():
    """Test that an expired API key is detected and raises an appropriate error."""
    expired_token = jwt.encode({"exp": ONE_HOUR_AGO}, "secret")

    with pytest.raises(ApiError) as exc:
        LabelStudio(
            base_url=BASE_URL,
            api_key=expired_token
        )
    assert "API key has expired" in str(exc.value)


def test_concurrent_refresh_single_request():
    """Test that multiple concurrent refresh attempts result in only one API call"""
    refresh_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    expired_access_token = jwt.encode({"exp": ONE_HOUR_AGO}, "secret")
    valid_access_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    mock_response = TokenRefreshResponse(access=valid_access_token)
    
    refresh_count = 0
    refresh_called = threading.Event()
    
    def mock_refresh(*args, **kwargs):
        nonlocal refresh_count
        refresh_count += 1
        # let requests pile up
        time.sleep(0.1)
        refresh_called.set()
        return mock_response

    with patch('label_studio_sdk.tokens.client_ext.TokensClientExt.refresh', side_effect=mock_refresh):
        client = LabelStudio(api_key=refresh_token, base_url=BASE_URL)
        client._client_wrapper._tokens_client._set_access_token(expired_access_token)

        # Spam refresh on multiple threads
        threads = []
        for _ in range(5):
            t = threading.Thread(target=lambda: client._client_wrapper._tokens_client.api_key)
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
        refresh_called.wait(timeout=1.0)
        
    assert refresh_count == 1, "Expected exactly one refresh call"
    assert client._client_wrapper._tokens_client.api_key == mock_response.access

@pytest.mark.asyncio
async def test_async_concurrent_refresh_single_request():
    """Test that multiple async refresh attempts result in only one API call"""
    refresh_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    expired_access_token = jwt.encode({"exp": ONE_HOUR_AGO}, "secret")
    valid_access_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    mock_response = TokenRefreshResponse(access=valid_access_token)

    refresh_count = 0
    refresh_called = asyncio.Event()

    def mock_refresh(self):
        nonlocal refresh_count
        refresh_count += 1
        refresh_called.set()
        # let requests pile up
        time.sleep(0.1)
        self._set_access_token(valid_access_token)
        return mock_response

    async with httpx.AsyncClient() as http_client:
        with patch('label_studio_sdk.tokens.client_ext.TokensClientExt.refresh',
                   mock_refresh):
            client = AsyncLabelStudio(api_key=refresh_token, base_url=BASE_URL, httpx_client=http_client)
            client._client_wrapper._tokens_client._set_access_token(expired_access_token)

            # simple async wrapper for getting the api_key
            async def refresh_task():
                return client._client_wrapper._tokens_client.api_key

            tasks = [asyncio.create_task(refresh_task())] * 5
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                assert not isinstance(result, Exception), f"Task raised an exception: {result}"

    assert refresh_count == 1, "Expected exactly one refresh call"
    assert client._client_wrapper._tokens_client.api_key == valid_access_token


def test_no_unnecessary_refresh():
    """Test that if token is refreshed while waiting for lock, second refresh is skipped"""
    refresh_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    expired_access_token = jwt.encode({"exp": ONE_HOUR_AGO}, "secret")
    valid_access_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    mock_response = TokenRefreshResponse(access=valid_access_token)

    refresh_count = 0
    refresh_started = threading.Event()

    def mock_refresh(*args, **kwargs):
        nonlocal refresh_count
        refresh_count += 1
        refresh_started.set()
        time.sleep(0.1)
        return mock_response

    with patch('label_studio_sdk.tokens.client_ext.TokensClientExt.refresh', side_effect=mock_refresh):
        client = LabelStudio(api_key=refresh_token, base_url=BASE_URL)
        client._client_wrapper._tokens_client._set_access_token(expired_access_token)

        def refresh_thread():
            _ = client._client_wrapper._tokens_client.api_key

        # trigger two refreshes, only one should result in a refresh call
        t1 = threading.Thread(target=refresh_thread)
        t1.start()
        refresh_started.wait(timeout=1.0)
        assert refresh_started.is_set(), "First refresh did not start"

        t2 = threading.Thread(target=refresh_thread)
        t2.start()
        
        t1.join(timeout=2.0)
        t2.join(timeout=2.0)

    assert refresh_count == 1, "Expected exactly one refresh call"
    assert client._client_wrapper._tokens_client.api_key == mock_response.access

@pytest.mark.asyncio
async def test_client_params_preserved_during_refresh():
    # Initialize test parameters
    test_params = {
        'auth': httpx.BasicAuth('user', 'pass'),
        'params': {'test': 'param'},
        'headers': {'X-Test': 'header'},  # httpx will convert this to lowercase
        'cookies': {'test': 'cookie'},
        'timeout': httpx.Timeout(10.0),
        'follow_redirects': True,
        'max_redirects': 5,
        'event_hooks': {'request': [lambda r: r]},
        'base_url': 'http://test.com',
        'trust_env': False,
        'default_encoding': 'latin1',
        'verify': False,
        'http1': True,
        'http2': False,
        'limits': httpx.Limits(max_connections=50, max_keepalive_connections=10, keepalive_expiry=10.0)
    }

    # Create AsyncLabelStudio with test parameters
    ls = AsyncLabelStudio(
        base_url="http://localhost:8080",
        api_key="test_key",
        httpx_client=httpx.AsyncClient(**test_params)
    )

    # Get the tokens client
    tokens_client = ls._client_wrapper._tokens_client

    # Get parameters from the new client that would be created during refresh
    new_params = tokens_client._get_client_params(tokens_client._client_wrapper.httpx_client.httpx_client)

    # Verify all parameters are preserved
    for key, value in test_params.items():
        if key == 'limits':
            # Limits objects need special comparison
            assert new_params[key].max_connections == value.max_connections
            assert new_params[key].max_keepalive_connections == value.max_keepalive_connections
            assert new_params[key].keepalive_expiry == value.keepalive_expiry
        elif key == 'params':
            # QueryParams need to be compared as dict
            assert dict(new_params[key]) == value
        elif key == 'headers':
            # Headers need to be compared as dict, but only our custom headers
            new_headers = dict(new_params[key])
            # Remove default httpx headers
            default_headers = {'accept', 'accept-encoding', 'connection', 'user-agent'}
            for header in default_headers:
                new_headers.pop(header, None)
            # Convert test headers to lowercase for comparison
            test_headers = {k.lower(): v for k, v in value.items()}
            assert new_headers == test_headers
        elif key == 'cookies':
            # Cookies need to be compared as dict
            assert dict(new_params[key]) == value
        elif key == 'event_hooks':
            # Only compare request hooks since httpx adds default response hooks
            assert new_params[key]['request'] == value['request']
        else:
            assert new_params[key] == value, f"Parameter {key} was not preserved correctly"
