from .client import TasksClient, AsyncTasksClient
from label_studio_sdk._extensions.pager_ext import SyncPagerExt, AsyncPagerExt, T


class TasksClientExt(TasksClient):

    def list(self, **kwargs) -> SyncPagerExt[T]:
        return SyncPagerExt.from_sync_pager(super().list(**kwargs))

    list.__doc__ = TasksClient.list.__doc__


class AsyncTasksClientExt(AsyncTasksClient):

    async def list(self, **kwargs):
        return await AsyncPagerExt.from_async_pager(await super().list(**kwargs))

    list.__doc__ = AsyncTasksClient.list.__doc__
