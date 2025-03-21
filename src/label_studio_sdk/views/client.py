# This file was auto-generated by Fern from our API Definition.

import typing
from ..core.client_wrapper import SyncClientWrapper
from ..core.request_options import RequestOptions
from ..types.view import View
from ..core.pydantic_utilities import parse_obj_as
from json.decoder import JSONDecodeError
from ..core.api_error import ApiError
from .types.views_create_request_data import ViewsCreateRequestData
from ..core.serialization import convert_and_respect_annotation_metadata
from ..core.jsonable_encoder import jsonable_encoder
from .types.views_update_request_data import ViewsUpdateRequestData
from ..core.client_wrapper import AsyncClientWrapper

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class ViewsClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def list(
        self, *, project: typing.Optional[int] = None, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.List[View]:
        """

        List all views for a specific project. A view is a tab in the Data Manager where you can set filters and customize which tasks and information appears.

        You will need to provide the project ID. You can find this in the URL when viewing the project in Label Studio, or you can use [List all projects](../projects/list).

        Parameters
        ----------
        project : typing.Optional[int]
            Project ID

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        typing.List[View]


        Examples
        --------
        from label_studio_sdk import LabelStudio

        client = LabelStudio(
            api_key="YOUR_API_KEY",
        )
        client.views.list()
        """
        _response = self._client_wrapper.httpx_client.request(
            "api/dm/views/",
            method="GET",
            params={
                "project": project,
            },
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    typing.List[View],
                    parse_obj_as(
                        type_=typing.List[View],  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def create(
        self,
        *,
        data: typing.Optional[ViewsCreateRequestData] = OMIT,
        project: typing.Optional[int] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> View:
        """

        Create a new Data Manager view for a specific project. A view is a tab in the Data Manager where you can set filters and customize what tasks and information appears.

        You will need to provide the project ID. You can find this in the URL when viewing the project in Label Studio, or you can use [List all projects](../projects/list).

        Parameters
        ----------
        data : typing.Optional[ViewsCreateRequestData]
            Custom view data

        project : typing.Optional[int]
            Project ID

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        View


        Examples
        --------
        from label_studio_sdk import LabelStudio

        client = LabelStudio(
            api_key="YOUR_API_KEY",
        )
        client.views.create()
        """
        _response = self._client_wrapper.httpx_client.request(
            "api/dm/views/",
            method="POST",
            json={
                "data": convert_and_respect_annotation_metadata(
                    object_=data, annotation=ViewsCreateRequestData, direction="write"
                ),
                "project": project,
            },
            headers={
                "content-type": "application/json",
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    View,
                    parse_obj_as(
                        type_=View,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def delete_all(self, *, project: int, request_options: typing.Optional[RequestOptions] = None) -> None:
        """

        Delete all views for a specific project. A view is a tab in the Data Manager where you can set filters and customize what tasks appear.

        You will need to provide the project ID. You can find this in the URL when viewing the project in Label Studio, or you can use [List all projects](../projects/list).

        Parameters
        ----------
        project : int

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        None

        Examples
        --------
        from label_studio_sdk import LabelStudio

        client = LabelStudio(
            api_key="YOUR_API_KEY",
        )
        client.views.delete_all(
            project=1,
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "api/dm/views/reset/",
            method="DELETE",
            json={
                "project": project,
            },
            headers={
                "content-type": "application/json",
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def get(self, id: str, *, request_options: typing.Optional[RequestOptions] = None) -> View:
        """

        Get the details about a specific Data Manager view (tab). You will need to supply the view ID. You can find this using [List views](list).

        Parameters
        ----------
        id : str
            View ID

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        View


        Examples
        --------
        from label_studio_sdk import LabelStudio

        client = LabelStudio(
            api_key="YOUR_API_KEY",
        )
        client.views.get(
            id="id",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            f"api/dm/views/{jsonable_encoder(id)}/",
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    View,
                    parse_obj_as(
                        type_=View,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def delete(self, id: str, *, request_options: typing.Optional[RequestOptions] = None) -> None:
        """
        Delete a specific Data Manager view (tab) by ID. You can find the view using [List views](list).

        Parameters
        ----------
        id : str
            View ID

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        None

        Examples
        --------
        from label_studio_sdk import LabelStudio

        client = LabelStudio(
            api_key="YOUR_API_KEY",
        )
        client.views.delete(
            id="id",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            f"api/dm/views/{jsonable_encoder(id)}/",
            method="DELETE",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def update(
        self,
        id: str,
        *,
        data: typing.Optional[ViewsUpdateRequestData] = OMIT,
        project: typing.Optional[int] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> View:
        """

        You can update a specific Data Manager view (tab) with additional filters and other customizations. You will need to supply the view ID. You can find this using [List views](list).

        Parameters
        ----------
        id : str
            View ID

        data : typing.Optional[ViewsUpdateRequestData]
            Custom view data

        project : typing.Optional[int]
            Project ID

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        View


        Examples
        --------
        from label_studio_sdk import LabelStudio

        client = LabelStudio(
            api_key="YOUR_API_KEY",
        )
        client.views.update(
            id="id",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            f"api/dm/views/{jsonable_encoder(id)}/",
            method="PATCH",
            json={
                "data": convert_and_respect_annotation_metadata(
                    object_=data, annotation=ViewsUpdateRequestData, direction="write"
                ),
                "project": project,
            },
            headers={
                "content-type": "application/json",
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    View,
                    parse_obj_as(
                        type_=View,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncViewsClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def list(
        self, *, project: typing.Optional[int] = None, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.List[View]:
        """

        List all views for a specific project. A view is a tab in the Data Manager where you can set filters and customize which tasks and information appears.

        You will need to provide the project ID. You can find this in the URL when viewing the project in Label Studio, or you can use [List all projects](../projects/list).

        Parameters
        ----------
        project : typing.Optional[int]
            Project ID

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        typing.List[View]


        Examples
        --------
        import asyncio

        from label_studio_sdk import AsyncLabelStudio

        client = AsyncLabelStudio(
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.views.list()


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            "api/dm/views/",
            method="GET",
            params={
                "project": project,
            },
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    typing.List[View],
                    parse_obj_as(
                        type_=typing.List[View],  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def create(
        self,
        *,
        data: typing.Optional[ViewsCreateRequestData] = OMIT,
        project: typing.Optional[int] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> View:
        """

        Create a new Data Manager view for a specific project. A view is a tab in the Data Manager where you can set filters and customize what tasks and information appears.

        You will need to provide the project ID. You can find this in the URL when viewing the project in Label Studio, or you can use [List all projects](../projects/list).

        Parameters
        ----------
        data : typing.Optional[ViewsCreateRequestData]
            Custom view data

        project : typing.Optional[int]
            Project ID

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        View


        Examples
        --------
        import asyncio

        from label_studio_sdk import AsyncLabelStudio

        client = AsyncLabelStudio(
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.views.create()


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            "api/dm/views/",
            method="POST",
            json={
                "data": convert_and_respect_annotation_metadata(
                    object_=data, annotation=ViewsCreateRequestData, direction="write"
                ),
                "project": project,
            },
            headers={
                "content-type": "application/json",
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    View,
                    parse_obj_as(
                        type_=View,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def delete_all(self, *, project: int, request_options: typing.Optional[RequestOptions] = None) -> None:
        """

        Delete all views for a specific project. A view is a tab in the Data Manager where you can set filters and customize what tasks appear.

        You will need to provide the project ID. You can find this in the URL when viewing the project in Label Studio, or you can use [List all projects](../projects/list).

        Parameters
        ----------
        project : int

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        None

        Examples
        --------
        import asyncio

        from label_studio_sdk import AsyncLabelStudio

        client = AsyncLabelStudio(
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.views.delete_all(
                project=1,
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            "api/dm/views/reset/",
            method="DELETE",
            json={
                "project": project,
            },
            headers={
                "content-type": "application/json",
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def get(self, id: str, *, request_options: typing.Optional[RequestOptions] = None) -> View:
        """

        Get the details about a specific Data Manager view (tab). You will need to supply the view ID. You can find this using [List views](list).

        Parameters
        ----------
        id : str
            View ID

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        View


        Examples
        --------
        import asyncio

        from label_studio_sdk import AsyncLabelStudio

        client = AsyncLabelStudio(
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.views.get(
                id="id",
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            f"api/dm/views/{jsonable_encoder(id)}/",
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    View,
                    parse_obj_as(
                        type_=View,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def delete(self, id: str, *, request_options: typing.Optional[RequestOptions] = None) -> None:
        """
        Delete a specific Data Manager view (tab) by ID. You can find the view using [List views](list).

        Parameters
        ----------
        id : str
            View ID

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        None

        Examples
        --------
        import asyncio

        from label_studio_sdk import AsyncLabelStudio

        client = AsyncLabelStudio(
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.views.delete(
                id="id",
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            f"api/dm/views/{jsonable_encoder(id)}/",
            method="DELETE",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def update(
        self,
        id: str,
        *,
        data: typing.Optional[ViewsUpdateRequestData] = OMIT,
        project: typing.Optional[int] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> View:
        """

        You can update a specific Data Manager view (tab) with additional filters and other customizations. You will need to supply the view ID. You can find this using [List views](list).

        Parameters
        ----------
        id : str
            View ID

        data : typing.Optional[ViewsUpdateRequestData]
            Custom view data

        project : typing.Optional[int]
            Project ID

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        View


        Examples
        --------
        import asyncio

        from label_studio_sdk import AsyncLabelStudio

        client = AsyncLabelStudio(
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.views.update(
                id="id",
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            f"api/dm/views/{jsonable_encoder(id)}/",
            method="PATCH",
            json={
                "data": convert_and_respect_annotation_metadata(
                    object_=data, annotation=ViewsUpdateRequestData, direction="write"
                ),
                "project": project,
            },
            headers={
                "content-type": "application/json",
            },
            request_options=request_options,
            omit=OMIT,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    View,
                    parse_obj_as(
                        type_=View,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
