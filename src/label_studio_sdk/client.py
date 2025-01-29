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
