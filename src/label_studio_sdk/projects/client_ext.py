from .client import ProjectsClient, AsyncProjectsClient

from label_studio_sdk._extensions.pager_ext import SyncPagerExt, AsyncPagerExt, T


class ProjectsClientExt(ProjectsClient):

    def list(self, **kwargs) -> SyncPagerExt[T]:
        return SyncPagerExt.from_sync_pager(super().list(**kwargs))

    list.__doc__ = ProjectsClient.list.__doc__


class AsyncProjectsClientExt(AsyncProjectsClient):

    async def list(self, **kwargs):
        return await AsyncPagerExt.from_async_pager(await super().list(**kwargs))

    list.__doc__ = AsyncProjectsClient.list.__doc__
