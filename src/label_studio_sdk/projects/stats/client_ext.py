import typing
from json.decoder import JSONDecodeError

from label_studio_sdk.projects.stats.client import AsyncStatsClient, StatsClient

from ...core.api_error import ApiError
from ...core.jsonable_encoder import jsonable_encoder
from ...core.request_options import RequestOptions
from ...core.unchecked_base_model import construct_type
from .types.stats_total_agreement_response import StatsTotalAgreementResponse

class StatsClientExt(StatsClient):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def total_agreement(
            self,
            id: int,
            *,
            per_label: typing.Optional[bool] = None,
            request_options: typing.Optional[RequestOptions] = None,
        ) -> typing.Optional[StatsTotalAgreementResponse]:
            """
            Overall or per-label total agreement across the project.

            Parameters
            ----------
            id : int

            per_label : typing.Optional[bool]
                Return agreement per label

            request_options : typing.Optional[RequestOptions]
                Request-specific configuration.

            Returns
            -------
            StatsTotalAgreementResponse
                Total agreement
            None
                No data to compute agreement

            Examples
            --------
            from label_studio_sdk import LabelStudio

            client = LabelStudio(
                api_key="YOUR_API_KEY",
            )
            client.projects.stats.total_agreement(
                id=1,
            )
            """
            _response = self._client_wrapper.httpx_client.request(
                f"api/projects/{jsonable_encoder(id)}/stats/total_agreement",
                method="GET",
                params={
                    "per_label": per_label,
                },
                request_options=request_options,
            )
            try:
                if _response.status_code == 204:
                    return None
                if 200 <= _response.status_code < 300:
                    return typing.cast(
                        StatsTotalAgreementResponse,
                        construct_type(
                            type_=StatsTotalAgreementResponse,  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                _response_json = _response.json()
            except JSONDecodeError:
                raise ApiError(status_code=_response.status_code, body=_response.text)
            raise ApiError(status_code=_response.status_code, body=_response_json)

    


class AsyncStatsClientExt(AsyncStatsClient):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    async def total_agreement(
        self,
        id: int,
        *,
        per_label: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Optional[StatsTotalAgreementResponse]:
        """
        Overall or per-label total agreement across the project.

        Parameters
        ----------
        id : int

        per_label : typing.Optional[bool]
            Return agreement per label

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        StatsTotalAgreementResponse
            Total agreement
        None
            No data to compute agreement

        Examples
        --------
        import asyncio

        from label_studio_sdk import AsyncLabelStudio

        client = AsyncLabelStudio(
            api_key="YOUR_API_KEY",
        )


        async def main() -> None:
            await client.projects.stats.total_agreement(
                id=1,
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            f"api/projects/{jsonable_encoder(id)}/stats/total_agreement",
            method="GET",
            params={
                "per_label": per_label,
            },
            request_options=request_options,
        )
        try:
            if _response.status_code == 204:
                return None
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    StatsTotalAgreementResponse,
                    construct_type(
                        type_=StatsTotalAgreementResponse,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
