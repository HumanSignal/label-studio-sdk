import typing
from typing_extensions import Annotated
from .client import ProjectsClient, AsyncProjectsClient
from pydantic import model_validator, validator, Field, ConfigDict
from label_studio_sdk._extensions.pager_ext import SyncPagerExt, AsyncPagerExt, T
from label_studio_sdk.types.project import Project
from label_studio_sdk.label_interface import LabelInterface
from .exports.client_ext import ExportsClientExt, AsyncExportsClientExt

from ..core import RequestOptions


class ProjectExt(Project):

    def get_label_interface(self):
        return LabelInterface(self.label_config)


class ProjectsClientExt(ProjectsClient):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exports = ExportsClientExt(client_wrapper=self._client_wrapper)

    def list(self, **kwargs) -> SyncPagerExt[T]:
        return SyncPagerExt.from_sync_pager(super().list(**kwargs))

    list.__doc__ = ProjectsClient.list.__doc__

    def get(self, id: int, *, request_options: typing.Optional[RequestOptions] = None) -> ProjectExt:
        return ProjectExt(**dict(super().get(id, request_options=request_options)))
    
    get.__doc__ = ProjectsClient.get.__doc__


class AsyncProjectsClientExt(AsyncProjectsClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exports = AsyncExportsClientExt(client_wrapper=self._client_wrapper)

    async def get(self, id: int, *, request_options: typing.Optional[RequestOptions] = None) -> ProjectExt:
        return ProjectExt(**dict(await super().get(id, request_options=request_options)))
    
    get.__doc__ = AsyncProjectsClient.get.__doc__

    async def list(self, **kwargs):
        return await AsyncPagerExt.from_async_pager(await super().list(**kwargs))

    list.__doc__ = AsyncProjectsClient.list.__doc__
