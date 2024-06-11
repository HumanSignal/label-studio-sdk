from .base_client import LabelStudioBase, AsyncLabelStudioBase
from .tasks.client_ext import TasksClientExt, AsyncTasksClientExt


class LabelStudio(LabelStudioBase):
    """"""
    __doc__ += LabelStudioBase.__doc__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tasks = TasksClientExt(client_wrapper=self._client_wrapper)


class AsyncLabelStudio(AsyncLabelStudioBase):
    """"""
    __doc__ += AsyncLabelStudioBase.__doc__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tasks = AsyncTasksClientExt(client_wrapper=self._client_wrapper)
