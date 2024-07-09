from .client import TasksClient, AsyncTasksClient
from label_studio_sdk._extensions.pager_ext import SyncPagerExt, AsyncPagerExt, T


class TasksClientExt(TasksClient):

    def list(self, **kwargs) -> SyncPagerExt[T]:
        # use `fields: all` by default and return the full data
        kwargs['fields'] = kwargs.get('fields', 'all')
        return SyncPagerExt.from_sync_pager(super().list(**kwargs))

    list.__doc__ = TasksClient.list.__doc__


class AsyncTasksClientExt(AsyncTasksClient):

    async def list(self, **kwargs):
        # use `fields: all` by default and return the full data
        kwargs['fields'] = kwargs.get('fields', 'all')
        return await AsyncPagerExt.from_async_pager(await super().list(**kwargs))

    list.__doc__ = AsyncTasksClient.list.__doc__
