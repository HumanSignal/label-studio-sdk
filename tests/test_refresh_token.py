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
from label_studio_sdk.core.api_error import ApiError
from label_studio_sdk.projects.types.projects_list_response import \
    ProjectsListResponse
from label_studio_sdk.types.access_token_response import AccessTokenResponse

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
    client._client_wrapper._set_access_token(expired_access_token)
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
    client._client_wrapper._set_access_token(access_token)
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
    assert projects_route.calls.last.request.headers["Authorization"] == f"Bearer {legacy_token}"


@pytest.mark.respx(base_url=BASE_URL)
def test_jwt_token_detection(respx_mock):
    """Test that a JWT token is automatically detected and uses the JWT mechanism."""
    now = int(datetime.datetime.now(timezone.utc).timestamp())
    jwt_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    refresh_route = respx_mock.post("/api/token/refresh/").mock(
        return_value=httpx.Response(200, json={"access": jwt_token})
    )
    projects_route = respx_mock.get("/api/projects/").mock(
        return_value=httpx.Response(200, json=ProjectsListResponse(count=0, results=[]).dict())
    )

    client = LabelStudio(
        base_url=BASE_URL,
        api_key=jwt_token
    )
    client.projects.list()

    assert refresh_route.called
    assert projects_route.calls.last.response.status_code == 200
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
    mock_response = AccessTokenResponse(access=valid_access_token)
    
    refresh_count = 0
    refresh_called = threading.Event()
    
    def mock_refresh(*args, **kwargs):
        nonlocal refresh_count
        refresh_count += 1
        # let requests pile up
        time.sleep(0.1)
        refresh_called.set()
        return mock_response

    with patch('label_studio_sdk.tokens.client.TokensClient.refresh', side_effect=mock_refresh):
        client = LabelStudio(api_key=refresh_token, base_url=BASE_URL)
        client._client_wrapper._set_access_token(expired_access_token)

        # Spam refresh on multiple threads
        threads = []
        for _ in range(5):
            t = threading.Thread(target=lambda: client._client_wrapper.api_key)
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
        refresh_called.wait(timeout=1.0)
        
        assert refresh_count == 1, "Expected exactly one refresh call"
        assert client._client_wrapper.api_key == mock_response.access


def test_concurrent_refresh_error_handling():
    """Test that if refresh fails, subsequent attempts are allowed"""
    refresh_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    expired_access_token = jwt.encode({"exp": ONE_HOUR_AGO}, "secret")
    valid_access_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    mock_response = AccessTokenResponse(access=valid_access_token)

    fail_first = True
    refresh_count = 0
    

    def mock_refresh(*args, **kwargs):
        nonlocal fail_first, refresh_count
        refresh_count += 1
        if fail_first:
            fail_first = False
            raise Exception("Simulated API error")
        return mock_response

    with patch('label_studio_sdk.tokens.client.TokensClient.refresh', side_effect=mock_refresh):
        client = LabelStudio(api_key=refresh_token, base_url=BASE_URL)
        client._client_wrapper._set_access_token(expired_access_token)

        # First attempt should fail
        with pytest.raises(ApiError):
            _ = client._client_wrapper.api_key
            
        # Second attempt should succeed
        assert client._client_wrapper.api_key == mock_response.access
        
        # Verify we attempted refresh twice
        assert refresh_count == 2, "Expected exactly two refresh attempts"


def test_no_unnecessary_refresh():
    """Test that if token is refreshed while waiting for lock, second refresh is skipped"""
    refresh_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    expired_access_token = jwt.encode({"exp": ONE_HOUR_AGO}, "secret")
    valid_access_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    mock_response = AccessTokenResponse(access=valid_access_token)

    refresh_count = 0
    refresh_started = threading.Event()

    def mock_refresh(*args, **kwargs):
        nonlocal refresh_count
        refresh_count += 1
        refresh_started.set()
        time.sleep(0.1)
        return mock_response

    with patch('label_studio_sdk.tokens.client.TokensClient.refresh', side_effect=mock_refresh):
        client = LabelStudio(api_key=refresh_token, base_url=BASE_URL)
        client._client_wrapper._set_access_token(expired_access_token)

        def refresh_thread():
            _ = client._client_wrapper.api_key

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
        assert client._client_wrapper.api_key == mock_response.access
