# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ..core.datetime_utils import serialize_datetime
from .converted_format import ConvertedFormat
from .export_counters import ExportCounters
from .export_status import ExportStatus
from .user_simple import UserSimple

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class Export(pydantic.BaseModel):
    title: typing.Optional[str]
    id: typing.Optional[int]
    created_by: typing.Optional[UserSimple]
    created_at: typing.Optional[dt.datetime] = pydantic.Field(description="Creation time")
    finished_at: typing.Optional[dt.datetime] = pydantic.Field(description="Complete or fail time")
    status: typing.Optional[ExportStatus]
    md_5: typing.Optional[str] = pydantic.Field(alias="md5")
    counters: typing.Optional[ExportCounters]
    converted_formats: typing.Optional[typing.List[ConvertedFormat]]

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