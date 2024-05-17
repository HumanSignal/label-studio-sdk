# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ..core.datetime_utils import serialize_datetime
from .label_create_value import LabelCreateValue

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class LabelCreate(pydantic.BaseModel):
    id: typing.Optional[int]
    created_by: typing.Optional[int]
    organization: typing.Optional[int]
    project: int
    from_name: str
    created_at: typing.Optional[dt.datetime] = pydantic.Field(description="Time of label creation")
    updated_at: typing.Optional[dt.datetime] = pydantic.Field(description="Time of label modification")
    value: LabelCreateValue = pydantic.Field(description="Label value")
    title: str = pydantic.Field(description="Label title")
    description: typing.Optional[str] = pydantic.Field(description="Label description")
    approved: typing.Optional[bool] = pydantic.Field(description="Status of label")
    approved_by: typing.Optional[int] = pydantic.Field(description="User who approved this label")
    projects: typing.Optional[typing.List[int]]

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