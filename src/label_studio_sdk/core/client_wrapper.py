import importlib.metadata
import platform
import typing

import httpx
from .http_client import AsyncHttpClient, HttpClient
from .logging import LogConfig, Logger, create_logger

try:
    VERSION = importlib.metadata.version("label-studio-sdk")
except importlib.metadata.PackageNotFoundError:
    VERSION = "unknown"


class BaseClientWrapper:
    def __init__(
        self,
        *,
        api_key: str,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        base_url: str,
        timeout: typing.Optional[float] = None,
        max_retries: int = 2,
        logging: typing.Optional[typing.Union[LogConfig, Logger]] = None,
    ):
        self._base_url = base_url
        self._timeout = timeout
        self._max_retries = max_retries
        self._headers = headers
        self._logger = create_logger(logging)

        # even in the async case, refreshing access token (when the existing one is expired) should be sync
        from ..tokens.client_ext import TokensClientExt

        self._tokens_client = TokensClientExt(base_url=base_url, api_key=api_key, client_wrapper=self)

    def get_timeout(self) -> typing.Optional[float]:
        return self._timeout

    def get_max_retries(self) -> int:
        return self._max_retries

    def get_base_url(self) -> str:
        return self._base_url

    def get_custom_headers(self) -> typing.Optional[typing.Dict[str, str]]:
        return self._headers

    def _uses_x_api_key(self) -> bool:
        return any(header.lower() == "x-api-key" for header in (self.get_custom_headers() or {}))

    def _normalize_x_api_key_headers(self, headers: typing.Dict[str, str]) -> None:
        """Upgrade JWT refresh tokens in X-API-Key to access tokens via TokensClientExt."""
        for key in list(headers):
            if key.lower() == "x-api-key":
                headers[key] = self._tokens_client.resolve_x_api_key_header_value(headers[key])

    def get_headers(self) -> typing.Dict[str, str]:
        headers: typing.Dict[str, str] = {
            "User-Agent": f"label_studio_sdk/{VERSION}",
            "X-Fern-Language": "Python",
            "X-Fern-SDK-Name": "label-studio-sdk",
            "X-Fern-SDK-Version": VERSION,
            "X-Fern-Runtime": f"python/{platform.python_version()}",
            "X-Fern-Platform": f"{platform.system().lower()}/{platform.release()}",
            **(self.get_custom_headers() or {}),
        }
        if self._uses_x_api_key():
            self._normalize_x_api_key_headers(headers)
            return headers
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
        headers: typing.Optional[typing.Dict[str, str]] = None,
        base_url: str,
        timeout: typing.Optional[float] = None,
        max_retries: int = 2,
        httpx_client: httpx.Client,
        logging: typing.Optional[typing.Union[LogConfig, Logger]] = None,
    ):
        super().__init__(
            api_key=api_key,
            headers=headers,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            logging=logging,
        )
        self.httpx_client = HttpClient(
            httpx_client=httpx_client,
            base_headers=self.get_headers,
            base_timeout=self.get_timeout,
            base_url=self.get_base_url,
            base_max_retries=self.get_max_retries(),
        )


class AsyncClientWrapper(BaseClientWrapper):
    def __init__(
        self,
        *,
        api_key: str,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        base_url: str,
        timeout: typing.Optional[float] = None,
        max_retries: int = 2,
        httpx_client: httpx.AsyncClient,
        logging: typing.Optional[typing.Union[LogConfig, Logger]] = None,
    ):
        super().__init__(
            api_key=api_key,
            headers=headers,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            logging=logging,
        )
        self.httpx_client = AsyncHttpClient(
            httpx_client=httpx_client,
            base_headers=self.get_headers,
            base_timeout=self.get_timeout,
            base_url=self.get_base_url,
            base_max_retries=self.get_max_retries(),
        )
