import typing
from datetime import datetime, timezone

import httpx
import jwt

from .api_error import ApiError
from .http_client import AsyncHttpClient, HttpClient


class BaseClientWrapper:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: typing.Optional[float] = None,
        use_legacy_token: typing.Optional[bool] = None,
    ):
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout
        self._access_token = None
        self._access_token_expiration = None

        # If user doesn't specify use_legacy_token, infer token type
        if use_legacy_token is None:
            # If we can't decode as a jwt, assume it's a legacy token
            self.use_legacy_token = not self._is_valid_jwt_token(api_key)
        else:
            self.use_legacy_token = use_legacy_token

        # even in the async case, refreshing access token (when the existing one is expired) should be sync
        # TODO do we need some kind of barrier to avoid many conflicting calls here?
        from ..tokens.client import TokensClient

        self._tokens_client = TokensClient(client_wrapper=self)

    def _refresh_access_token(self) -> None:
        """
        Use the refresh token to get a new access token.

        Raises
        ------
        ApiError
            If token refresh fails
        """
        try:
            response = self._tokens_client.refresh(refresh=self._api_key)
            new_token = response.access
        except Exception as e:
            raise ApiError(body=f"Failed to refresh access token: {str(e)}")
        self._set_access_token(new_token)

    @property
    def api_key(self) -> str:
        """
        Get the API key to use for authentication.
        For non-legacy tokens, this will refresh the access token if needed.
        """
        if not self.use_legacy_token:
            if (not self._access_token) or self._access_token_is_expired():
                self._refresh_access_token()
            return self._access_token
        return self._api_key

    def get_headers(self) -> typing.Dict[str, str]:
        headers: typing.Dict[str, str] = {
            "X-Fern-Language": "Python",
            "X-Fern-SDK-Name": "label-studio-sdk",
            "X-Fern-SDK-Version": "1.0.11",
        }
        headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _access_token_is_expired(self) -> bool:
        """Check if the access token is expired, based on cached expiration time."""
        if self._access_token_expiration is None:
            return True

        return self._access_token_expiration <= datetime.now(timezone.utc).timestamp()

    def _is_valid_jwt_token(self, token: str) -> bool:
        """Check if a token is a valid JWT token by attempting to decode its header."""
        try:
            jwt.get_unverified_header(token)
            return True
        except (jwt.InvalidTokenError, IndexError, AttributeError):
            return False

    def _set_access_token(self, token: str) -> None:
        """
        Set the access token and cache its expiration time.

        Parameters
        ----------
        token : str
            A JWT token to store

        Raises
        ------
        ApiError
            If the token cannot be decoded or has no expiration claim
        """
        try:
            # Decode without verification since we just want to check expiration
            decoded = jwt.decode(token, options={"verify_signature": False})
            exp = decoded.get("exp")
            if exp is None:
                # Refuse to use API tokens without an expiration claim
                raise ApiError(
                    body="No expiration set for access token, refusing to use for authentication"
                )
        except jwt.InvalidTokenError as e:
            raise ApiError(body=f"Failed to decode access token: {str(e)}")

        self._access_token_expiration = exp
        self._access_token = token

    def get_timeout(self) -> typing.Optional[float]:
        return self._timeout

    def get_base_url(self) -> str:
        return self._base_url


class SyncClientWrapper(BaseClientWrapper):
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: typing.Optional[float] = None,
        httpx_client: httpx.Client,
        use_legacy_token: typing.Optional[bool] = None,
    ):
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            use_legacy_token=use_legacy_token,
        )

        self.httpx_client = HttpClient(
            httpx_client=httpx_client,
            base_headers=self.get_headers,
            base_timeout=self.get_timeout,
            base_url=self.get_base_url,
        )


class AsyncClientWrapper(BaseClientWrapper):
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: typing.Optional[float] = None,
        httpx_client: httpx.AsyncClient,
        use_legacy_token: typing.Optional[bool] = None,
    ):
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            use_legacy_token=use_legacy_token,
        )
        from ..tokens.client import AsyncTokensClient

        self._tokens_client = AsyncTokensClient(client_wrapper=self)

        self.httpx_client = AsyncHttpClient(
            httpx_client=httpx_client,
            base_headers=self.get_headers,
            base_timeout=self.get_timeout,
            base_url=self.get_base_url,
        )
