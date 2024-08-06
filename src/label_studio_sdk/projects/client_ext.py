import typing
from typing_extensions import Annotated
from .client import ProjectsClient, AsyncProjectsClient
from pydantic import model_validator, validator, Field, ConfigDict
from label_studio_sdk._extensions.pager_ext import SyncPagerExt, AsyncPagerExt, T
from label_studio_sdk.types.project import Project
from label_studio_sdk.label_interface import LabelInterface

from ..core import RequestOptions


class ProjectExt(Project):

    def get_label_interface(self):
        return LabelInterface(self.label_config)


class ProjectsClientExt(ProjectsClient):

    def list(self, **kwargs) -> SyncPagerExt[T]:
        return SyncPagerExt.from_sync_pager(super().list(**kwargs))

    list.__doc__ = ProjectsClient.list.__doc__

    def get(self, id: int, *, request_options: typing.Optional[RequestOptions] = None) -> ProjectExt:
        return ProjectExt(**dict(super().get(id, request_options=request_options)))


class AsyncProjectsClientExt(AsyncProjectsClient):

    async def list(self, **kwargs):
        return await AsyncPagerExt.from_async_pager(await super().list(**kwargs))

    list.__doc__ = AsyncProjectsClient.list.__doc__
