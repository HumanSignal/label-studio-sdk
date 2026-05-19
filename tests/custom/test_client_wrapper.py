from unittest.mock import patch

from label_studio_sdk.core.client_wrapper import BaseClientWrapper


def test_preserves_custom_authorization_when_x_api_key_is_provided() -> None:
    wrapper = BaseClientWrapper(
        base_url="https://label-studio.example.com",
        api_key="sdk-api-key",
        headers={
            "Authorization": "Bearer platform-token",
            "X-API-Key": "label-studio-api-key",
        },
    )

    headers = wrapper.get_headers()

    assert headers["Authorization"] == "Bearer platform-token"
    assert headers["X-API-Key"] == "label-studio-api-key"


def test_preserves_lowercase_authorization_when_x_api_key_is_provided() -> None:
    wrapper = BaseClientWrapper(
        base_url="https://label-studio.example.com",
        api_key="sdk-api-key",
        headers={
            "authorization": "Bearer platform-token",
            "X-API-Key": "label-studio-api-key",
        },
    )

    headers = wrapper.get_headers()

    assert headers["authorization"] == "Bearer platform-token"
    assert "Authorization" not in headers


def test_x_api_key_detection_is_case_insensitive() -> None:
    wrapper = BaseClientWrapper(
        base_url="https://label-studio.example.com",
        api_key="sdk-api-key",
        headers={
            "Authorization": "Bearer platform-token",
            "x-api-key": "label-studio-api-key",
        },
    )

    headers = wrapper.get_headers()

    assert headers["Authorization"] == "Bearer platform-token"
    assert headers["x-api-key"] == "label-studio-api-key"


def test_does_not_add_sdk_authorization_when_x_api_key_is_provided() -> None:
    wrapper = BaseClientWrapper(
        base_url="https://label-studio.example.com",
        api_key="sdk-api-key",
        headers={"X-API-Key": "label-studio-api-key"},
    )

    headers = wrapper.get_headers()

    assert "Authorization" not in headers
    assert headers["X-API-Key"] == "label-studio-api-key"


def test_normalizes_x_api_key_via_tokens_client() -> None:
    wrapper = BaseClientWrapper(
        base_url="https://label-studio.example.com",
        api_key="sdk-api-key",
        headers={
            "Authorization": "Bearer platform-token",
            "X-API-Key": "refresh-jwt-value",
        },
    )

    with patch.object(
        wrapper._tokens_client,
        "resolve_x_api_key_header_value",
        side_effect=lambda value: f"resolved:{value}",
    ) as mock_resolve:
        headers = wrapper.get_headers()

    mock_resolve.assert_called_once_with("refresh-jwt-value")
    assert headers["X-API-Key"] == "resolved:refresh-jwt-value"
    assert headers["Authorization"] == "Bearer platform-token"


def test_sets_sdk_authorization_when_x_api_key_is_not_provided() -> None:
    wrapper = BaseClientWrapper(
        base_url="https://label-studio.example.com",
        api_key="sdk-api-key",
        headers={"Authorization": "Bearer platform-token"},
    )

    headers = wrapper.get_headers()

    assert headers["Authorization"] == "Token sdk-api-key"
