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
