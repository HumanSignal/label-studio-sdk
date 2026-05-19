import threading
import urllib.parse
import typing
from datetime import datetime, timezone
import ssl

import httpx
import jwt

from ..core.api_error import ApiError
from ..types.token_refresh_response import TokenRefreshResponse


class TokensClientExt:
    """Client for managing authentication tokens."""

    def __init__(self, base_url: str, api_key: str, client_wrapper=None):
        self._base_url = base_url
        self._api_key = api_key
        self._client_wrapper = client_wrapper
        self._use_legacy_token = not self._is_valid_jwt_token(api_key, raise_if_expired=True)

        # cache state for access token when using jwt-based api_key
        self._access_token: typing.Optional[str] = None
        self._access_token_expiration: typing.Optional[datetime] = None
        # Used to keep simultaneous refresh requests from spamming refresh endpoint
        self._token_refresh_lock = threading.Lock()


    def _decode_jwt_payload(self, token: str) -> typing.Optional[typing.Dict[str, typing.Any]]:
        """Decode JWT claims without verification, or None if not a JWT."""
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except jwt.InvalidTokenError:
            return None

    def _is_valid_jwt_token(self, token: str, raise_if_expired: bool = False) -> bool:
        """Check if a token is a valid JWT token by attempting to decode its header and check expiration."""
        decoded = self._decode_jwt_payload(token)
        if decoded is None:
            return False
        expiration = decoded.get("exp")
        if expiration is None:
            raise ApiError(
                status_code=401,
                body={"detail": "API key does not have an expiration set, and is not valid. Please obtain a new refresh token."}
            )
        expiration_time = datetime.fromtimestamp(expiration, timezone.utc)
        if expiration_time < datetime.now(timezone.utc):
            if raise_if_expired:
                raise ApiError(
                    status_code=401,
                    body={"detail": "API key has expired. Please obtain a new refresh token."}
                )
            else:
                return False
        return True

    def jwt_token_type(self, token: str) -> typing.Optional[str]:
        """Return the JWT token_type claim, or None for legacy (non-JWT) tokens."""
        if not self._is_valid_jwt_token(token, raise_if_expired=False):
            return None
        decoded = self._decode_jwt_payload(token)
        return decoded.get("token_type") if decoded is not None else None

    def resolve_x_api_key_header_value(self, value: str) -> str:
        """Return the X-API-Key header value to send on the wire.

        Legacy API keys are returned unchanged. JWT refresh tokens are exchanged for
        access tokens via :meth:`refresh`. JWT access tokens are returned unchanged.
        """
        if self.jwt_token_type(value) != "refresh":
            return value
        if value == self._api_key:
            return self.api_key
        return self.refresh(refresh_token=value).access

    def _set_access_token(self, token: str) -> None:
        """Set the access token and cache its expiration time."""
        decoded = self._decode_jwt_payload(token)
        if decoded is not None:
            expiration = decoded.get("exp")
            if expiration is not None:
                self._access_token_expiration = datetime.fromtimestamp(expiration, timezone.utc)
        self._access_token = token

    @property
    def api_key(self) -> str:
        """Get the current access token, refreshing if necessary."""
        # Legacy tokens: just return the API key directly
        if self._use_legacy_token:
            return self._api_key

        # JWT tokens: handle refresh if needed
        if (not self._access_token) or (not self._is_valid_jwt_token(self._access_token)):
            with self._token_refresh_lock:
                # Check again after acquiring lock, in case another invocation already refreshed
                if (not self._access_token) or (not self._is_valid_jwt_token(self._access_token)):
                    token_response = self.refresh()
                    self._set_access_token(token_response.access)
        
        return self._access_token

    def _get_client_params(self, existing_client: httpx.AsyncClient) -> dict:
        """Extract parameters from an existing client to create a new one.

        Args:
            existing_client: The existing client to extract parameters from.

        Returns:
            dict: Parameters for creating a new client.
        """
        return {
            'auth': existing_client.auth,
            'params': existing_client.params,
            'headers': existing_client.headers,
            'cookies': existing_client.cookies,
            'timeout': existing_client.timeout,
            'follow_redirects': existing_client.follow_redirects,
            'max_redirects': existing_client.max_redirects,
            'event_hooks': existing_client.event_hooks,
            'base_url': existing_client.base_url,
            'trust_env': existing_client.trust_env,
            'default_encoding': existing_client._default_encoding,
            'verify': existing_client._transport._pool._ssl_context.verify_mode != ssl.CERT_NONE,
            'http1': existing_client._transport._pool._http1,
            'http2': existing_client._transport._pool._http2,
            'limits': httpx.Limits(
                max_connections=existing_client._transport._pool._max_connections,
                max_keepalive_connections=existing_client._transport._pool._max_keepalive_connections,
                keepalive_expiry=existing_client._transport._pool._keepalive_expiry
            )
        }

    def refresh(self, refresh_token: typing.Optional[str] = None) -> TokenRefreshResponse:
        """Refresh the access token and return the token response."""
        token = self._api_key if refresh_token is None else refresh_token
        existing_client = self._client_wrapper.httpx_client.httpx_client

        # For sync client, use it directly
        if isinstance(existing_client, httpx.Client):
            response = existing_client.request(
                method="POST",
                url=urllib.parse.urljoin(f"{self._base_url}", "api/token/refresh/"),
                json={"refresh": token},
                headers={"Content-Type": "application/json"},
            )
        else:
            # If an async client was used, get all parameters from the client to init a new sync client
            client_params = self._get_client_params(existing_client)

            with httpx.Client(**client_params) as sync_client:
                response = sync_client.request(
                    method="POST",
                    url=urllib.parse.urljoin(f"{self._base_url}/", "api/token/refresh/"),
                    json={"refresh": token},
                    headers={"Content-Type": "application/json"},
                )

        if response.status_code == 200:
            return TokenRefreshResponse.parse_obj(response.json())
        else:
            raise ApiError(status_code=response.status_code, body=response.json())
