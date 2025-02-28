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
        # httpx_client: typing.Optional[typing.Union[httpx.Client, httpx.AsyncClient]] = None,
    ):
        self._base_url = base_url
        self._timeout = timeout

        # Check if the API key is a JWT token, and if it's expired
        try:
            decoded = jwt.decode(api_key, options={"verify_signature": False})
            expiration = decoded.get("exp")
            if expiration is not None:
                expiration_time = datetime.fromtimestamp(expiration, timezone.utc)
                if expiration_time < datetime.now(timezone.utc):
                    raise ApiError(
                        status_code=401,
                        body={"detail": "API key has expired. Please obtain a new refresh token."}
                    )
        except jwt.InvalidTokenError:
            # Not a JWT token, could be legacy token
            pass

        # even in the async case, refreshing access token (when the existing one is expired) should be sync
        from ..tokens.client_ext import TokensClientExt
        self._tokens_client = TokensClientExt(base_url=base_url, api_key=api_key)


    def get_timeout(self) -> typing.Optional[float]:
        return self._timeout


    def get_base_url(self) -> str:
        return self._base_url


    def get_headers(self) -> typing.Dict[str, str]:
        headers: typing.Dict[str, str] = {
            "X-Fern-Language": "Python",
            "X-Fern-SDK-Name": "label-studio-sdk",
            "X-Fern-SDK-Version": "1.0.11",
        }
        if self._tokens_client._use_legacy_token:
            headers["Authorization"] = f"Token {self._tokens_client.api_key}"
        else:
            headers["Authorization"] = f"Bearer {self._tokens_client.api_key}"
        return headers



class SyncClientWrapper(BaseClientWrapper):
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: typing.Optional[float] = None,
        httpx_client: httpx.Client,
    ):
        super().__init__(api_key=api_key, base_url=base_url, timeout=timeout)
        self.httpx_client = HttpClient(
            httpx_client=httpx_client,
            base_headers=self.get_headers,
            base_timeout=self.get_timeout,
            base_url=self.get_base_url,
        )


class AsyncClientWrapper(BaseClientWrapper):
    def __init__(
        self, *, api_key: str, base_url: str, timeout: typing.Optional[float] = None, httpx_client: httpx.AsyncClient
    ):
        super().__init__(api_key=api_key, base_url=base_url, timeout=timeout)
        self.httpx_client = AsyncHttpClient(
            httpx_client=httpx_client,
            base_headers=self.get_headers,
            base_timeout=self.get_timeout,
            base_url=self.get_base_url,
        )
