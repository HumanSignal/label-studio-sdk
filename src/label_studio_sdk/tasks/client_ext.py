import typing

from .client import AsyncTasksClient, TasksClient

from label_studio_sdk._extensions.pager_ext import AsyncPagerExt, SyncPagerExt, T
from label_studio_sdk.core.request_options import RequestOptions
from label_studio_sdk.projects.imports.client import AsyncImportsClient, ImportsClient
from label_studio_sdk.types.project_import import ProjectImport


class TasksClientExt(TasksClient):
    def list(self, **kwargs) -> SyncPagerExt[T]:
        # use `fields: all` by default and return the full data
        kwargs["fields"] = kwargs.get("fields", "all")
        return SyncPagerExt.from_sync_pager(super().list(**kwargs))

    list.__doc__ = TasksClient.list.__doc__

    def create_many_status(
        self, id: int, import_pk: int, *, request_options: typing.Optional[RequestOptions] = None
    ) -> ProjectImport:
        """Alias for ``client.projects.imports.get`` (same HTTP endpoint).

        Both ``client.tasks.create_many_status(...)`` and
        ``client.projects.imports.get(...)`` poll
        ``GET /api/projects/{id}/imports/{import_pk}/``.
        """
        return ImportsClient(client_wrapper=self._client_wrapper).get(id, import_pk, request_options=request_options)


class AsyncTasksClientExt(AsyncTasksClient):
    async def list(self, **kwargs):
        # use `fields: all` by default and return the full data
        kwargs["fields"] = kwargs.get("fields", "all")
        return await AsyncPagerExt.from_async_pager(await super().list(**kwargs))

    list.__doc__ = AsyncTasksClient.list.__doc__

    async def create_many_status(
        self, id: int, import_pk: int, *, request_options: typing.Optional[RequestOptions] = None
    ) -> ProjectImport:
        """Alias for ``client.projects.imports.get`` (same HTTP endpoint).

        Both ``client.tasks.create_many_status(...)`` and
        ``client.projects.imports.get(...)`` poll
        ``GET /api/projects/{id}/imports/{import_pk}/``.
        """
        return await AsyncImportsClient(client_wrapper=self._client_wrapper).get(
            id, import_pk, request_options=request_options
        )
