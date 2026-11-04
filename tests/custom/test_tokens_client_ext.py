from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, PropertyMock, patch

import jwt
import pytest

from label_studio_sdk.tokens.client_ext import TokensClientExt
from label_studio_sdk.types.token_refresh_response import TokenRefreshResponse


def _jwt(token_type: str, exp_days: int = 1, *, jti: str = "1") -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=exp_days)
    return jwt.encode(
        {"token_type": token_type, "exp": int(exp.timestamp()), "jti": jti},
        "secret",
        algorithm="HS256",
    )


@pytest.fixture
def tokens_client() -> TokensClientExt:
    return TokensClientExt(
        base_url="https://label-studio.example.com",
        api_key=_jwt("refresh"),
        client_wrapper=MagicMock(),
    )


def test_resolve_x_api_key_leaves_legacy_unchanged(tokens_client: TokensClientExt) -> None:
    assert tokens_client.resolve_x_api_key_header_value("legacy-api-key-abc") == "legacy-api-key-abc"


def test_resolve_x_api_key_leaves_access_jwt_unchanged(tokens_client: TokensClientExt) -> None:
    access = _jwt("access")
    assert tokens_client.resolve_x_api_key_header_value(access) == access


def test_resolve_x_api_key_replaces_refresh_jwt_with_access(tokens_client: TokensClientExt) -> None:
    refresh = tokens_client._api_key
    access = _jwt("access")
    with patch.object(type(tokens_client), "api_key", new_callable=PropertyMock, return_value=access):
        assert tokens_client.resolve_x_api_key_header_value(refresh) == access


def test_resolve_x_api_key_refreshes_mismatched_refresh_jwt(tokens_client: TokensClientExt) -> None:
    other_refresh = _jwt("refresh", jti="other")
    access = _jwt("access", jti="access-for-other")
    with patch.object(
        tokens_client,
        "refresh",
        return_value=TokenRefreshResponse(access=access),
    ) as mock_refresh:
        assert tokens_client.resolve_x_api_key_header_value(other_refresh) == access
    mock_refresh.assert_called_once_with(refresh_token=other_refresh)


def test_jwt_token_type_returns_none_for_legacy(tokens_client: TokensClientExt) -> None:
    assert tokens_client.jwt_token_type("not-a-jwt") is None


def test_jwt_token_type_returns_claim_for_jwt(tokens_client: TokensClientExt) -> None:
    assert tokens_client.jwt_token_type(_jwt("access")) == "access"


def _client_with_refresh_endpoint(base_url: str, issued: list, *, access_exp_seconds: int = 300):
    import httpx

    from label_studio_sdk.client import LabelStudio

    requests: list = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        exp = datetime.now(timezone.utc) + timedelta(seconds=access_exp_seconds)
        issued.append(jwt.encode({"token_type": "access", "exp": int(exp.timestamp()), "jti": str(len(issued))}, "s"))
        return httpx.Response(200, json={"access": issued[-1]})

    client = LabelStudio(
        api_key=_jwt("refresh"), base_url=base_url, httpx_client=httpx.Client(transport=httpx.MockTransport(handler))
    )
    return client, requests


def test_get_auth_headers_reuses_access_token_until_it_expires() -> None:
    issued: list = []
    client, requests = _client_with_refresh_endpoint("https://ls.example", issued)

    assert client.get_auth_headers() == {"Authorization": f"Bearer {issued[0]}"}
    assert client.get_auth_headers() == {"Authorization": f"Bearer {issued[0]}"}
    assert len(requests) == 1


def test_get_auth_headers_renews_expired_access_token_before_sending() -> None:
    issued: list = []
    client, requests = _client_with_refresh_endpoint("https://ls.example", issued, access_exp_seconds=-1)

    first = client.get_auth_headers()
    second = client.get_auth_headers()

    assert first != second
    assert second == {"Authorization": f"Bearer {issued[1]}"}
    assert len(requests) == 2


def test_get_auth_headers_refresh_discards_cached_access_token() -> None:
    """Server-side expiry the local clock does not see yet (clock skew) is recovered with refresh=True."""
    issued: list = []
    client, requests = _client_with_refresh_endpoint("https://ls.example", issued)

    client.get_auth_headers()
    assert client.get_auth_headers(refresh=True) == {"Authorization": f"Bearer {issued[1]}"}
    assert len(requests) == 2


def test_get_auth_headers_legacy_token_needs_no_network() -> None:
    import httpx

    from label_studio_sdk.client import LabelStudio

    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError(f"unexpected request {request.url}")

    client = LabelStudio(
        api_key="legacy-key",
        base_url="https://ls.example",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    assert client.get_auth_headers() == {"Authorization": "Token legacy-key"}
    assert client.get_auth_headers(refresh=True) == {"Authorization": "Token legacy-key"}


@pytest.mark.parametrize("base_url", ["https://ls.example/label-studio", "https://ls.example/label-studio/"])
def test_refresh_keeps_base_url_path_prefix(base_url: str) -> None:
    issued: list = []
    client, requests = _client_with_refresh_endpoint(base_url, issued)

    client.get_auth_headers()

    assert str(requests[0].url) == "https://ls.example/label-studio/api/token/refresh/"


@pytest.mark.parametrize("refresh", [False, True])
def test_get_auth_headers_sends_access_token_as_is(refresh: bool) -> None:
    """An access token (e.g. a Service Account token) is not a refresh token, so it is never exchanged."""
    import httpx

    from label_studio_sdk.client import LabelStudio

    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError(f"unexpected request {request.url}")

    access = _jwt("access")
    client = LabelStudio(
        api_key=access, base_url="https://ls.example", httpx_client=httpx.Client(transport=httpx.MockTransport(handler))
    )
    assert client.get_auth_headers(refresh=refresh) == {"Authorization": f"Bearer {access}"}
