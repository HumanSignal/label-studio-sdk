import typing

from .client import TasksClient, AsyncTasksClient
from label_studio_sdk.core.pagination import SyncPager, AsyncPager, T
from label_studio_sdk.core.api_error import ApiError


class SyncPagerExt(SyncPager, typing.Generic[T]):

    @classmethod
    def from_sync_pager(cls, sync_pager: SyncPager) -> 'SyncPagerExt':
        return cls(
            get_next=sync_pager.get_next,
            has_next=sync_pager.has_next,
            items=sync_pager.items
        )

    def __iter__(self) -> typing.Iterator[T]:  # type: ignore
        # Extends the iterator to catch 404 errors at the end of the pagination
        try:
            for item in super().__iter__():
                yield item
        except ApiError as exc:
            if exc.status_code == 404:
                return
            raise


class AsyncPagerExt(AsyncPager, typing.Generic[T]):

    @classmethod
    async def from_async_pager(cls, async_pager: AsyncPager) -> 'AsyncPagerExt':
        return cls(
            get_next=async_pager.get_next,
            has_next=async_pager.has_next,
            items=async_pager.items
        )

    async def __aiter__(self) -> typing.AsyncIterator[T]:  # type: ignore
        # Extends the iterator to catch 404 errors at the end of the pagination
        try:
            async for item in super().__aiter__():
                yield item
        except ApiError as exc:
            if exc.status_code == 404:
                return
            raise


class TasksClientExt(TasksClient):

    def list(self, **kwargs) -> SyncPagerExt[T]:
        return SyncPagerExt.from_sync_pager(super().list(**kwargs))

    list.__doc__ = TasksClient.list.__doc__


class AsyncTasksClientExt(AsyncTasksClient):

    async def list(self, **kwargs):
        return await AsyncPagerExt.from_async_pager(await super().list(**kwargs))

    list.__doc__ = AsyncTasksClient.list.__doc__
