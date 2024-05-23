# This file was auto-generated by Fern from our API Definition.

from label_studio_sdk import AzureBlobExportStorage, AzureBlobImportStorage
from label_studio_sdk.client import AsyncLabelStudio, LabelStudio

from .utilities import validate_response


async def test_api_storages_azure_list(client: LabelStudio, async_client: AsyncLabelStudio) -> None:
    expected_response = [
        {
            "id": 1,
            "type": "type",
            "synchronizable": True,
            "presign": True,
            "container": "container",
            "prefix": "prefix",
            "regex_filter": "regex_filter",
            "use_blob_urls": True,
            "account_name": "account_name",
            "account_key": "account_key",
            "last_sync": "2024-01-15T09:30:00Z",
            "last_sync_count": 1,
            "last_sync_job": "last_sync_job",
            "status": "initialized",
            "traceback": "traceback",
            "meta": {"meta": {"key": "value"}},
            "title": "title",
            "description": "description",
            "created_at": "2024-01-15T09:30:00Z",
            "presign_ttl": 1,
            "project": 1,
        }
    ]
    expected_types = (
        "list",
        {
            0: {
                "id": "integer",
                "type": None,
                "synchronizable": None,
                "presign": None,
                "container": None,
                "prefix": None,
                "regex_filter": None,
                "use_blob_urls": None,
                "account_name": None,
                "account_key": None,
                "last_sync": "datetime",
                "last_sync_count": "integer",
                "last_sync_job": None,
                "status": None,
                "traceback": None,
                "meta": ("dict", {0: (None, None)}),
                "title": None,
                "description": None,
                "created_at": "datetime",
                "presign_ttl": "integer",
                "project": "integer",
            }
        },
    )
    response = client.storage_azure.api_storages_azure_list()
    validate_response(response, expected_response, expected_types)

    async_response = await async_client.storage_azure.api_storages_azure_list()
    validate_response(async_response, expected_response, expected_types)


async def test_api_storages_azure_create(client: LabelStudio, async_client: AsyncLabelStudio) -> None:
    expected_response = {
        "id": 1,
        "type": "type",
        "synchronizable": True,
        "presign": True,
        "container": "container",
        "prefix": "prefix",
        "regex_filter": "regex_filter",
        "use_blob_urls": True,
        "account_name": "account_name",
        "account_key": "account_key",
        "last_sync": "2024-01-15T09:30:00Z",
        "last_sync_count": 1,
        "last_sync_job": "last_sync_job",
        "status": "initialized",
        "traceback": "traceback",
        "meta": {"meta": {"key": "value"}},
        "title": "title",
        "description": "description",
        "created_at": "2024-01-15T09:30:00Z",
        "presign_ttl": 1,
        "project": 1,
    }
    expected_types = {
        "id": "integer",
        "type": None,
        "synchronizable": None,
        "presign": None,
        "container": None,
        "prefix": None,
        "regex_filter": None,
        "use_blob_urls": None,
        "account_name": None,
        "account_key": None,
        "last_sync": "datetime",
        "last_sync_count": "integer",
        "last_sync_job": None,
        "status": None,
        "traceback": None,
        "meta": ("dict", {0: (None, None)}),
        "title": None,
        "description": None,
        "created_at": "datetime",
        "presign_ttl": "integer",
        "project": "integer",
    }
    response = client.storage_azure.api_storages_azure_create(request=AzureBlobImportStorage(project=1))
    validate_response(response, expected_response, expected_types)

    async_response = await async_client.storage_azure.api_storages_azure_create(
        request=AzureBlobImportStorage(project=1)
    )
    validate_response(async_response, expected_response, expected_types)


async def test_api_storages_azure_validate_create(client: LabelStudio, async_client: AsyncLabelStudio) -> None:
    expected_response = {
        "id": 1,
        "type": "type",
        "synchronizable": True,
        "presign": True,
        "container": "container",
        "prefix": "prefix",
        "regex_filter": "regex_filter",
        "use_blob_urls": True,
        "account_name": "account_name",
        "account_key": "account_key",
        "last_sync": "2024-01-15T09:30:00Z",
        "last_sync_count": 1,
        "last_sync_job": "last_sync_job",
        "status": "initialized",
        "traceback": "traceback",
        "meta": {"meta": {"key": "value"}},
        "title": "title",
        "description": "description",
        "created_at": "2024-01-15T09:30:00Z",
        "presign_ttl": 1,
        "project": 1,
    }
    expected_types = {
        "id": "integer",
        "type": None,
        "synchronizable": None,
        "presign": None,
        "container": None,
        "prefix": None,
        "regex_filter": None,
        "use_blob_urls": None,
        "account_name": None,
        "account_key": None,
        "last_sync": "datetime",
        "last_sync_count": "integer",
        "last_sync_job": None,
        "status": None,
        "traceback": None,
        "meta": ("dict", {0: (None, None)}),
        "title": None,
        "description": None,
        "created_at": "datetime",
        "presign_ttl": "integer",
        "project": "integer",
    }
    response = client.storage_azure.api_storages_azure_validate_create(request=AzureBlobImportStorage(project=1))
    validate_response(response, expected_response, expected_types)

    async_response = await async_client.storage_azure.api_storages_azure_validate_create(
        request=AzureBlobImportStorage(project=1)
    )
    validate_response(async_response, expected_response, expected_types)


async def test_api_storages_azure_read(client: LabelStudio, async_client: AsyncLabelStudio) -> None:
    expected_response = {
        "id": 1,
        "type": "type",
        "synchronizable": True,
        "presign": True,
        "container": "container",
        "prefix": "prefix",
        "regex_filter": "regex_filter",
        "use_blob_urls": True,
        "account_name": "account_name",
        "account_key": "account_key",
        "last_sync": "2024-01-15T09:30:00Z",
        "last_sync_count": 1,
        "last_sync_job": "last_sync_job",
        "status": "initialized",
        "traceback": "traceback",
        "meta": {"meta": {"key": "value"}},
        "title": "title",
        "description": "description",
        "created_at": "2024-01-15T09:30:00Z",
        "presign_ttl": 1,
        "project": 1,
    }
    expected_types = {
        "id": "integer",
        "type": None,
        "synchronizable": None,
        "presign": None,
        "container": None,
        "prefix": None,
        "regex_filter": None,
        "use_blob_urls": None,
        "account_name": None,
        "account_key": None,
        "last_sync": "datetime",
        "last_sync_count": "integer",
        "last_sync_job": None,
        "status": None,
        "traceback": None,
        "meta": ("dict", {0: (None, None)}),
        "title": None,
        "description": None,
        "created_at": "datetime",
        "presign_ttl": "integer",
        "project": "integer",
    }
    response = client.storage_azure.api_storages_azure_read(id=1)
    validate_response(response, expected_response, expected_types)

    async_response = await async_client.storage_azure.api_storages_azure_read(id=1)
    validate_response(async_response, expected_response, expected_types)


async def test_api_storages_azure_delete(client: LabelStudio, async_client: AsyncLabelStudio) -> None:
    # Type ignore to avoid mypy complaining about the function not being meant to return a value
    assert client.storage_azure.api_storages_azure_delete(id=1) is None  # type: ignore[func-returns-value]

    assert await async_client.storage_azure.api_storages_azure_delete(id=1) is None  # type: ignore[func-returns-value]


async def test_api_storages_azure_partial_update(client: LabelStudio, async_client: AsyncLabelStudio) -> None:
    expected_response = {
        "id": 1,
        "type": "type",
        "synchronizable": True,
        "presign": True,
        "container": "container",
        "prefix": "prefix",
        "regex_filter": "regex_filter",
        "use_blob_urls": True,
        "account_name": "account_name",
        "account_key": "account_key",
        "last_sync": "2024-01-15T09:30:00Z",
        "last_sync_count": 1,
        "last_sync_job": "last_sync_job",
        "status": "initialized",
        "traceback": "traceback",
        "meta": {"meta": {"key": "value"}},
        "title": "title",
        "description": "description",
        "created_at": "2024-01-15T09:30:00Z",
        "presign_ttl": 1,
        "project": 1,
    }
    expected_types = {
        "id": "integer",
        "type": None,
        "synchronizable": None,
        "presign": None,
        "container": None,
        "prefix": None,
        "regex_filter": None,
        "use_blob_urls": None,
        "account_name": None,
        "account_key": None,
        "last_sync": "datetime",
        "last_sync_count": "integer",
        "last_sync_job": None,
        "status": None,
        "traceback": None,
        "meta": ("dict", {0: (None, None)}),
        "title": None,
        "description": None,
        "created_at": "datetime",
        "presign_ttl": "integer",
        "project": "integer",
    }
    response = client.storage_azure.api_storages_azure_partial_update(id=1, request=AzureBlobImportStorage(project=1))
    validate_response(response, expected_response, expected_types)

    async_response = await async_client.storage_azure.api_storages_azure_partial_update(
        id=1, request=AzureBlobImportStorage(project=1)
    )
    validate_response(async_response, expected_response, expected_types)


async def test_api_storages_azure_sync_create(client: LabelStudio, async_client: AsyncLabelStudio) -> None:
    expected_response = {
        "id": 1,
        "type": "type",
        "synchronizable": True,
        "presign": True,
        "container": "container",
        "prefix": "prefix",
        "regex_filter": "regex_filter",
        "use_blob_urls": True,
        "account_name": "account_name",
        "account_key": "account_key",
        "last_sync": "2024-01-15T09:30:00Z",
        "last_sync_count": 1,
        "last_sync_job": "last_sync_job",
        "status": "initialized",
        "traceback": "traceback",
        "meta": {"meta": {"key": "value"}},
        "title": "title",
        "description": "description",
        "created_at": "2024-01-15T09:30:00Z",
        "presign_ttl": 1,
        "project": 1,
    }
    expected_types = {
        "id": "integer",
        "type": None,
        "synchronizable": None,
        "presign": None,
        "container": None,
        "prefix": None,
        "regex_filter": None,
        "use_blob_urls": None,
        "account_name": None,
        "account_key": None,
        "last_sync": "datetime",
        "last_sync_count": "integer",
        "last_sync_job": None,
        "status": None,
        "traceback": None,
        "meta": ("dict", {0: (None, None)}),
        "title": None,
        "description": None,
        "created_at": "datetime",
        "presign_ttl": "integer",
        "project": "integer",
    }
    response = client.storage_azure.api_storages_azure_sync_create(id="id", request=AzureBlobImportStorage(project=1))
    validate_response(response, expected_response, expected_types)

    async_response = await async_client.storage_azure.api_storages_azure_sync_create(
        id="id", request=AzureBlobImportStorage(project=1)
    )
    validate_response(async_response, expected_response, expected_types)


async def test_api_storages_export_azure_list(client: LabelStudio, async_client: AsyncLabelStudio) -> None:
    expected_response = [
        {
            "id": 1,
            "type": "type",
            "synchronizable": True,
            "container": "container",
            "prefix": "prefix",
            "regex_filter": "regex_filter",
            "use_blob_urls": True,
            "account_name": "account_name",
            "account_key": "account_key",
            "last_sync": "2024-01-15T09:30:00Z",
            "last_sync_count": 1,
            "last_sync_job": "last_sync_job",
            "status": "initialized",
            "traceback": "traceback",
            "meta": {"meta": {"key": "value"}},
            "title": "title",
            "description": "description",
            "created_at": "2024-01-15T09:30:00Z",
            "can_delete_objects": True,
            "project": 1,
        }
    ]
    expected_types = (
        "list",
        {
            0: {
                "id": "integer",
                "type": None,
                "synchronizable": None,
                "container": None,
                "prefix": None,
                "regex_filter": None,
                "use_blob_urls": None,
                "account_name": None,
                "account_key": None,
                "last_sync": "datetime",
                "last_sync_count": "integer",
                "last_sync_job": None,
                "status": None,
                "traceback": None,
                "meta": ("dict", {0: (None, None)}),
                "title": None,
                "description": None,
                "created_at": "datetime",
                "can_delete_objects": None,
                "project": "integer",
            }
        },
    )
    response = client.storage_azure.api_storages_export_azure_list()
    validate_response(response, expected_response, expected_types)

    async_response = await async_client.storage_azure.api_storages_export_azure_list()
    validate_response(async_response, expected_response, expected_types)


async def test_api_storages_export_azure_create(client: LabelStudio, async_client: AsyncLabelStudio) -> None:
    expected_response = {
        "id": 1,
        "type": "type",
        "synchronizable": True,
        "container": "container",
        "prefix": "prefix",
        "regex_filter": "regex_filter",
        "use_blob_urls": True,
        "account_name": "account_name",
        "account_key": "account_key",
        "last_sync": "2024-01-15T09:30:00Z",
        "last_sync_count": 1,
        "last_sync_job": "last_sync_job",
        "status": "initialized",
        "traceback": "traceback",
        "meta": {"meta": {"key": "value"}},
        "title": "title",
        "description": "description",
        "created_at": "2024-01-15T09:30:00Z",
        "can_delete_objects": True,
        "project": 1,
    }
    expected_types = {
        "id": "integer",
        "type": None,
        "synchronizable": None,
        "container": None,
        "prefix": None,
        "regex_filter": None,
        "use_blob_urls": None,
        "account_name": None,
        "account_key": None,
        "last_sync": "datetime",
        "last_sync_count": "integer",
        "last_sync_job": None,
        "status": None,
        "traceback": None,
        "meta": ("dict", {0: (None, None)}),
        "title": None,
        "description": None,
        "created_at": "datetime",
        "can_delete_objects": None,
        "project": "integer",
    }
    response = client.storage_azure.api_storages_export_azure_create(request=AzureBlobExportStorage(project=1))
    validate_response(response, expected_response, expected_types)

    async_response = await async_client.storage_azure.api_storages_export_azure_create(
        request=AzureBlobExportStorage(project=1)
    )
    validate_response(async_response, expected_response, expected_types)


async def test_api_storages_export_azure_validate_create(client: LabelStudio, async_client: AsyncLabelStudio) -> None:
    expected_response = {
        "id": 1,
        "type": "type",
        "synchronizable": True,
        "container": "container",
        "prefix": "prefix",
        "regex_filter": "regex_filter",
        "use_blob_urls": True,
        "account_name": "account_name",
        "account_key": "account_key",
        "last_sync": "2024-01-15T09:30:00Z",
        "last_sync_count": 1,
        "last_sync_job": "last_sync_job",
        "status": "initialized",
        "traceback": "traceback",
        "meta": {"meta": {"key": "value"}},
        "title": "title",
        "description": "description",
        "created_at": "2024-01-15T09:30:00Z",
        "can_delete_objects": True,
        "project": 1,
    }
    expected_types = {
        "id": "integer",
        "type": None,
        "synchronizable": None,
        "container": None,
        "prefix": None,
        "regex_filter": None,
        "use_blob_urls": None,
        "account_name": None,
        "account_key": None,
        "last_sync": "datetime",
        "last_sync_count": "integer",
        "last_sync_job": None,
        "status": None,
        "traceback": None,
        "meta": ("dict", {0: (None, None)}),
        "title": None,
        "description": None,
        "created_at": "datetime",
        "can_delete_objects": None,
        "project": "integer",
    }
    response = client.storage_azure.api_storages_export_azure_validate_create(request=AzureBlobExportStorage(project=1))
    validate_response(response, expected_response, expected_types)

    async_response = await async_client.storage_azure.api_storages_export_azure_validate_create(
        request=AzureBlobExportStorage(project=1)
    )
    validate_response(async_response, expected_response, expected_types)


async def test_api_storages_export_azure_read(client: LabelStudio, async_client: AsyncLabelStudio) -> None:
    expected_response = {
        "id": 1,
        "type": "type",
        "synchronizable": True,
        "container": "container",
        "prefix": "prefix",
        "regex_filter": "regex_filter",
        "use_blob_urls": True,
        "account_name": "account_name",
        "account_key": "account_key",
        "last_sync": "2024-01-15T09:30:00Z",
        "last_sync_count": 1,
        "last_sync_job": "last_sync_job",
        "status": "initialized",
        "traceback": "traceback",
        "meta": {"meta": {"key": "value"}},
        "title": "title",
        "description": "description",
        "created_at": "2024-01-15T09:30:00Z",
        "can_delete_objects": True,
        "project": 1,
    }
    expected_types = {
        "id": "integer",
        "type": None,
        "synchronizable": None,
        "container": None,
        "prefix": None,
        "regex_filter": None,
        "use_blob_urls": None,
        "account_name": None,
        "account_key": None,
        "last_sync": "datetime",
        "last_sync_count": "integer",
        "last_sync_job": None,
        "status": None,
        "traceback": None,
        "meta": ("dict", {0: (None, None)}),
        "title": None,
        "description": None,
        "created_at": "datetime",
        "can_delete_objects": None,
        "project": "integer",
    }
    response = client.storage_azure.api_storages_export_azure_read(id=1)
    validate_response(response, expected_response, expected_types)

    async_response = await async_client.storage_azure.api_storages_export_azure_read(id=1)
    validate_response(async_response, expected_response, expected_types)


async def test_api_storages_export_azure_delete(client: LabelStudio, async_client: AsyncLabelStudio) -> None:
    # Type ignore to avoid mypy complaining about the function not being meant to return a value
    assert client.storage_azure.api_storages_export_azure_delete(id=1) is None  # type: ignore[func-returns-value]

    assert await async_client.storage_azure.api_storages_export_azure_delete(id=1) is None  # type: ignore[func-returns-value]


async def test_api_storages_export_azure_partial_update(client: LabelStudio, async_client: AsyncLabelStudio) -> None:
    expected_response = {
        "id": 1,
        "type": "type",
        "synchronizable": True,
        "container": "container",
        "prefix": "prefix",
        "regex_filter": "regex_filter",
        "use_blob_urls": True,
        "account_name": "account_name",
        "account_key": "account_key",
        "last_sync": "2024-01-15T09:30:00Z",
        "last_sync_count": 1,
        "last_sync_job": "last_sync_job",
        "status": "initialized",
        "traceback": "traceback",
        "meta": {"meta": {"key": "value"}},
        "title": "title",
        "description": "description",
        "created_at": "2024-01-15T09:30:00Z",
        "can_delete_objects": True,
        "project": 1,
    }
    expected_types = {
        "id": "integer",
        "type": None,
        "synchronizable": None,
        "container": None,
        "prefix": None,
        "regex_filter": None,
        "use_blob_urls": None,
        "account_name": None,
        "account_key": None,
        "last_sync": "datetime",
        "last_sync_count": "integer",
        "last_sync_job": None,
        "status": None,
        "traceback": None,
        "meta": ("dict", {0: (None, None)}),
        "title": None,
        "description": None,
        "created_at": "datetime",
        "can_delete_objects": None,
        "project": "integer",
    }
    response = client.storage_azure.api_storages_export_azure_partial_update(
        id=1, request=AzureBlobExportStorage(project=1)
    )
    validate_response(response, expected_response, expected_types)

    async_response = await async_client.storage_azure.api_storages_export_azure_partial_update(
        id=1, request=AzureBlobExportStorage(project=1)
    )
    validate_response(async_response, expected_response, expected_types)


async def test_api_storages_export_azure_sync_create(client: LabelStudio, async_client: AsyncLabelStudio) -> None:
    expected_response = {
        "id": 1,
        "type": "type",
        "synchronizable": True,
        "container": "container",
        "prefix": "prefix",
        "regex_filter": "regex_filter",
        "use_blob_urls": True,
        "account_name": "account_name",
        "account_key": "account_key",
        "last_sync": "2024-01-15T09:30:00Z",
        "last_sync_count": 1,
        "last_sync_job": "last_sync_job",
        "status": "initialized",
        "traceback": "traceback",
        "meta": {"meta": {"key": "value"}},
        "title": "title",
        "description": "description",
        "created_at": "2024-01-15T09:30:00Z",
        "can_delete_objects": True,
        "project": 1,
    }
    expected_types = {
        "id": "integer",
        "type": None,
        "synchronizable": None,
        "container": None,
        "prefix": None,
        "regex_filter": None,
        "use_blob_urls": None,
        "account_name": None,
        "account_key": None,
        "last_sync": "datetime",
        "last_sync_count": "integer",
        "last_sync_job": None,
        "status": None,
        "traceback": None,
        "meta": ("dict", {0: (None, None)}),
        "title": None,
        "description": None,
        "created_at": "datetime",
        "can_delete_objects": None,
        "project": "integer",
    }
    response = client.storage_azure.api_storages_export_azure_sync_create(
        id="id", request=AzureBlobExportStorage(project=1)
    )
    validate_response(response, expected_response, expected_types)

    async_response = await async_client.storage_azure.api_storages_export_azure_sync_create(
        id="id", request=AzureBlobExportStorage(project=1)
    )
    validate_response(async_response, expected_response, expected_types)