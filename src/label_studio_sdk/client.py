from .base_client import LabelStudioBase, AsyncLabelStudioBase
from .tasks.client_ext import TasksClientExt, AsyncTasksClientExt
from .projects.client_ext import ProjectsClientExt, AsyncProjectsClientExt
from .core.api_error import ApiError


class LabelStudio(LabelStudioBase):
    """"""
    __doc__ += LabelStudioBase.__doc__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tasks = TasksClientExt(client_wrapper=self._client_wrapper)
        self.projects = ProjectsClientExt(client_wrapper=self._client_wrapper)


class AsyncLabelStudio(AsyncLabelStudioBase):
    """"""
    __doc__ += AsyncLabelStudioBase.__doc__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tasks = AsyncTasksClientExt(client_wrapper=self._client_wrapper)
        self.projects = AsyncProjectsClientExt(client_wrapper=self._client_wrapper)
        
        try:
            version = self.version.get()
            self.edition = version.edition
        except Exception as e:
            raise ApiError(status_code=500, body=f"Unable to access Label Studio instance. Please check if the base_url={self._base_url} is correct and the server is running.") from e
