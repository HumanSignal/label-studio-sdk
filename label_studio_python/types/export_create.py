# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ..core.datetime_utils import serialize_datetime
from .annotation_filter_options import AnnotationFilterOptions
from .converted_format import ConvertedFormat
from .export_create_counters import ExportCreateCounters
from .export_create_status import ExportCreateStatus
from .serialization_options import SerializationOptions
from .task_filter_options import TaskFilterOptions
from .user_simple import UserSimple

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class ExportCreate(pydantic.BaseModel):
    title: typing.Optional[str]
    id: typing.Optional[int]
    created_by: typing.Optional[UserSimple]
    created_at: typing.Optional[dt.datetime] = pydantic.Field(description="Creation time")
    finished_at: typing.Optional[dt.datetime] = pydantic.Field(description="Complete or fail time")
    status: typing.Optional[ExportCreateStatus]
    md_5: typing.Optional[str] = pydantic.Field(alias="md5")
    counters: typing.Optional[ExportCreateCounters]
    converted_formats: typing.Optional[typing.List[ConvertedFormat]]
    task_filter_options: typing.Optional[TaskFilterOptions]
    annotation_filter_options: typing.Optional[AnnotationFilterOptions]
    serialization_options: typing.Optional[SerializationOptions]

    def json(self, **kwargs: typing.Any) -> str:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().json(**kwargs_with_defaults)

    def dict(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().dict(**kwargs_with_defaults)

    class Config:
        frozen = True
        smart_union = True
        allow_population_by_field_name = True
        json_encoders = {dt.datetime: serialize_datetime}