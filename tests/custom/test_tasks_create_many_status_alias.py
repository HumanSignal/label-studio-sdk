from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from label_studio_sdk.tasks.client_ext import AsyncTasksClientExt, TasksClientExt
from label_studio_sdk.types.project_import import ProjectImport


@pytest.fixture
def tasks_client() -> TasksClientExt:
    return TasksClientExt(client_wrapper=MagicMock())


@pytest.fixture
def async_tasks_client() -> AsyncTasksClientExt:
    return AsyncTasksClientExt(client_wrapper=MagicMock())


def test_create_many_status_aliases_projects_imports_get(tasks_client: TasksClientExt) -> None:
    expected = MagicMock(spec=ProjectImport)
    mock_imports = MagicMock()
    mock_imports.get.return_value = expected

    with patch("label_studio_sdk.tasks.client_ext.ImportsClient", return_value=mock_imports):
        result = tasks_client.create_many_status(7, 11)

    assert result is expected
    mock_imports.get.assert_called_once_with(7, 11, request_options=None)


@pytest.mark.asyncio
async def test_async_create_many_status_aliases_projects_imports_get(
    async_tasks_client: AsyncTasksClientExt,
) -> None:
    expected = MagicMock(spec=ProjectImport)
    mock_imports = MagicMock()
    mock_imports.get = AsyncMock(return_value=expected)

    with patch("label_studio_sdk.tasks.client_ext.AsyncImportsClient", return_value=mock_imports):
        result = await async_tasks_client.create_many_status(7, 11, request_options=None)

    assert result is expected
    mock_imports.get.assert_awaited_once_with(7, 11, request_options=None)
