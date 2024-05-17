# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ..core.datetime_utils import serialize_datetime
from .filter_group import FilterGroup
from .view_data import ViewData
from .view_ordering import ViewOrdering
from .view_selected_items import ViewSelectedItems

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class View(pydantic.BaseModel):
    id: typing.Optional[int]
    filter_group: typing.Optional[FilterGroup]
    data: typing.Optional[ViewData] = pydantic.Field(description="Custom view data")
    ordering: typing.Optional[ViewOrdering] = pydantic.Field(description="Ordering parameters")
    selected_items: typing.Optional[ViewSelectedItems] = pydantic.Field(description="Selected items")
    user: typing.Optional[int] = pydantic.Field(description="User who made this view")
    project: int = pydantic.Field(description="Project ID")

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