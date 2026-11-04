from .base_client import LabelStudioBase, AsyncLabelStudioBase
from .tasks.client_ext import TasksClientExt, AsyncTasksClientExt
from .projects.client_ext import ProjectsClientExt, AsyncProjectsClientExt
import typing


class LabelStudio(LabelStudioBase):
    """"""
    __doc__ += LabelStudioBase.__doc__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tasks_ext: typing.Optional[TasksClientExt] = None
        self._projects_ext: typing.Optional[ProjectsClientExt] = None

    def get_auth_headers(self, *, refresh: bool = False) -> typing.Dict[str, str]:
        """The authentication header this client sends on its next request.

        A JWT refresh token (personal access token) is exchanged for an access token, which is reused until it
        expires and renewed before it is sent. Legacy tokens are returned as-is. ``refresh=True`` discards the
        cached access token first, for a request the server rejected as unauthenticated although the local
        clock still considered the token valid.
        """
        if refresh:
            self._client_wrapper._tokens_client.discard_access_token()
        headers = self._client_wrapper.get_headers()
        return {key: value for key, value in headers.items() if key.lower() in ("authorization", "x-api-key")}

    @property
    def tasks(self) -> TasksClientExt:  # type: ignore[override]
        # Fern-generated base clients often expose `tasks` as a read-only @property.
        # We override it to return our extended client without assigning to the property.
        if self._tasks_ext is None:
            self._tasks_ext = TasksClientExt(client_wrapper=self._client_wrapper)
        return self._tasks_ext

    @property
    def projects(self) -> ProjectsClientExt:  # type: ignore[override]
        if self._projects_ext is None:
            self._projects_ext = ProjectsClientExt(client_wrapper=self._client_wrapper)
        return self._projects_ext


class AsyncLabelStudio(AsyncLabelStudioBase):
    """"""
    __doc__ += AsyncLabelStudioBase.__doc__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tasks_ext: typing.Optional[AsyncTasksClientExt] = None
        self._projects_ext: typing.Optional[AsyncProjectsClientExt] = None

    @property
    def tasks(self) -> AsyncTasksClientExt:  # type: ignore[override]
        if self._tasks_ext is None:
            self._tasks_ext = AsyncTasksClientExt(client_wrapper=self._client_wrapper)
        return self._tasks_ext

    @property
    def projects(self) -> AsyncProjectsClientExt:  # type: ignore[override]
        if self._projects_ext is None:
            self._projects_ext = AsyncProjectsClientExt(client_wrapper=self._client_wrapper)
        return self._projects_ext
