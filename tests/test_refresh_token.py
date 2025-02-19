import datetime
import json
from datetime import timezone

import httpx
import jwt
import pytest
from label_studio_sdk import LabelStudio
from label_studio_sdk.projects.types.projects_list_response import \
    ProjectsListResponse

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
    # the request should use the Bearer token format
    assert projects_route.calls.last.request.headers["Authorization"] == f"Bearer {legacy_token}"


@pytest.mark.respx(base_url=BASE_URL)
def test_force_legacy_token(respx_mock):
    """Test that JWT tokens can be forced to use legacy token mechanism."""
    now = int(datetime.datetime.now(timezone.utc).timestamp())
    jwt_looking_token = jwt.encode({"exp": IN_ONE_HOUR}, "secret")
    projects_route = respx_mock.get("/api/projects/").mock(
        return_value=httpx.Response(200, json=ProjectsListResponse(count=0, results=[]).dict())
    )

    client = LabelStudio(
        base_url=BASE_URL,
        api_key=jwt_looking_token,
        use_legacy_token=True,
    )
    client.projects.list()

    assert projects_route.calls.last.response.status_code == 200
    # the request should use the Bearer token format
    assert projects_route.calls.last.request.headers["Authorization"] == f"Bearer {jwt_looking_token}"


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
