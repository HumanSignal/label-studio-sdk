import threading
import typing
from datetime import datetime, timezone
import inspect

import httpx
import jwt

from ..core.api_error import ApiError
from ..types.access_token_response import AccessTokenResponse


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


    def _is_valid_jwt_token(self, token: str, raise_if_expired: bool = False) -> bool:
        """Check if a token is a valid JWT token by attempting to decode its header and check expiration."""
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
        except jwt.InvalidTokenError:
            # presumably a lagacy token
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

    def _set_access_token(self, token: str) -> None:
        """Set the access token and cache its expiration time."""
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            expiration = decoded.get("exp")
            if expiration is not None:
                self._access_token_expiration = datetime.fromtimestamp(expiration, timezone.utc)
        except jwt.InvalidTokenError:
            pass
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

    def refresh(self) -> AccessTokenResponse:
        """Refresh the access token and return the token response."""
        # We don't do this often, just use a separate sync httpx client for simplicity here
        # (avoids complicated state management and sync vs async handling)
        # Create a new client with the same parameters as the existing one
        existing_client = self._client_wrapper.httpx_client.httpx_client

        # Get all parameters from httpx.Client.__init__
        client_params = {}
        sig = inspect.signature(httpx.Client.__init__)
        for param_name in sig.parameters:
            if param_name != 'self':  # Skip 'self' parameter
                try:
                    value = getattr(existing_client, param_name, None)
                    if value is not None:
                        client_params[param_name] = value
                except AttributeError:
                    continue

        with httpx.Client(**client_params) as sync_client:
            response = sync_client.request(
                method="POST",
                url=f"{self._base_url}/api/token/refresh/",
                json={"refresh": self._api_key},
                headers={"Content-Type": "application/json"},
            )
            
            if response.status_code == 200:
                return AccessTokenResponse.parse_obj(response.json())
            else:
                raise ApiError(status_code=response.status_code, body=response.json())
