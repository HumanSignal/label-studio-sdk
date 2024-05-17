# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ..core.datetime_utils import serialize_datetime
from .local_files_import_storage_meta import LocalFilesImportStorageMeta
from .local_files_import_storage_status import LocalFilesImportStorageStatus

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class LocalFilesImportStorage(pydantic.BaseModel):
    id: typing.Optional[int]
    type: typing.Optional[str]
    synchronizable: typing.Optional[bool]
    path: typing.Optional[str] = pydantic.Field(description="Local path")
    regex_filter: typing.Optional[str] = pydantic.Field(description="Regex for filtering objects")
    use_blob_urls: typing.Optional[bool] = pydantic.Field(description="Interpret objects as BLOBs and generate URLs")
    last_sync: typing.Optional[dt.datetime] = pydantic.Field(description="Last sync finished time")
    last_sync_count: typing.Optional[int] = pydantic.Field(description="Count of tasks synced last time")
    last_sync_job: typing.Optional[str] = pydantic.Field(description="Last sync job ID")
    status: typing.Optional[LocalFilesImportStorageStatus]
    traceback: typing.Optional[str] = pydantic.Field(description="Traceback report for the last failed sync")
    meta: typing.Optional[LocalFilesImportStorageMeta] = pydantic.Field(
        description="Meta and debug information about storage processes"
    )
    title: typing.Optional[str] = pydantic.Field(description="Cloud storage title")
    description: typing.Optional[str] = pydantic.Field(description="Cloud storage description")
    created_at: typing.Optional[dt.datetime] = pydantic.Field(description="Creation time")
    project: int = pydantic.Field(description="A unique integer value identifying this project.")

    def json(self, **kwargs: typing.Any) -> str:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().json(**kwargs_with_defaults)

    def dict(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().dict(**kwargs_with_defaults)

    class Config:
        frozen = True
        smart_union = True
        json_encoders = {dt.datetime: serialize_datetime}