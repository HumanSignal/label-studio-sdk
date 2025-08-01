import json
import time
import asyncio
import typing
import pandas as pd
from .client import ExportsClient, AsyncExportsClient
from io import BytesIO
from label_studio_sdk.versions.client import VersionsClient, AsyncVersionsClient
from label_studio_sdk.core.api_error import ApiError


class ExportTimeoutError(ApiError):

    def __init__(self, export_snapshot):
        super().__init__(
            status_code=500,
            body=(
                f"Export job timed out: "
                f"unable to retrieve export job {export_snapshot.id}. "
                f"Current status: {export_snapshot.status}. "
                f"Try manually checking the running job with "
                f"`ls.projects.exports.get(id=<PROJECT_ID>, export_pk={export_snapshot.id})`."
            )
        )

class ExportFailedError(ApiError):

    def __init__(self, export_snapshot):
        super().__init__(
            status_code=500,
            body=f"Export failed: {export_snapshot}"
        )


def _check_status(export_snapshot, converted_format_id, status):
    if converted_format_id:
        converted_format = next((c for c in export_snapshot.converted_formats if c.id == converted_format_id), None)
        if converted_format and converted_format.status == status:
            return True
    else:
        if export_snapshot.status == status:
            return True
    return False


class ExportsClientExt(ExportsClient):

    def _bytestream_to_fileobj(self, bytestream: typing.Iterable[bytes] | bytes) -> typing.BinaryIO:
        buffer = BytesIO()
        if isinstance(bytestream, typing.Iterable):
            for chunk in bytestream:
                buffer.write(chunk)
        else:
            buffer.write(bytestream)
        buffer.seek(0)
        return buffer

    def _bytestream_to_binary(self, bytestream: typing.Iterable[bytes]) -> bytes:
        fileobj = self._bytestream_to_fileobj(bytestream)
        return fileobj.getvalue()

    def _bytestream_to_json(self, bytestream: typing.Iterable[bytes]) -> dict:
        fileobj = self._bytestream_to_fileobj(bytestream)
        return json.load(fileobj)

    def _bytestream_to_pandas(self, bytestream: typing.Iterable[bytes]) -> pd.DataFrame:
        fileobj = self._bytestream_to_fileobj(bytestream)
        return pd.read_csv(fileobj)

    def _poll_export(self, project_id, export_snapshot, converted_format_id, timeout):
        start_time = time.time()
        while not _check_status(export_snapshot, None, 'completed'):
            export_snapshot = self.get(id=project_id, export_pk=export_snapshot.id)
            if _check_status(export_snapshot, None, 'failed'):
                raise ExportFailedError(export_snapshot)
            if time.time() - start_time > timeout:
                raise ExportTimeoutError(export_snapshot)
            time.sleep(1)

    def _get_bytestream(
        self,
        project_id: int,
        export_type: str,
        timeout: int = 60,
        create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None,
        convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None,
        download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None,
    ):
        version = VersionsClient(client_wrapper=self._client_wrapper).get()

        if version.edition == "Enterprise":
            # Enterprise edition exports are async, so we need to wait for the export job to complete
            export_snapshot = self.create(project_id, **(create_kwargs or {}))
            # Poll for base (JSON) export to complete
            self._poll_export(project_id, export_snapshot, None, timeout)
            # Convert to requested format if not JSON
            if export_type != "JSON":
                converted_proc = self.convert(id=project_id, export_pk=export_snapshot.id, export_type=export_type, **(convert_kwargs or {}))
                self._poll_export(project_id, export_snapshot, converted_proc.converted_format, timeout)

            bytestream = self.download(id=project_id, export_pk=export_snapshot.id, export_type=export_type, request_options={'chunk_size': 1024}, **(download_kwargs or {}))
        else:
            # Community edition exports are sync, so we can download the file immediately
            bytestream = self.download_sync(project_id, export_type=export_type, download_all_tasks=True, download_resources=True)
        return bytestream

    def as_file(self, project_id: int, export_type: str = "JSON", timeout: int = 60, create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None):
        bytestream = self._get_bytestream(project_id, export_type, timeout, create_kwargs, convert_kwargs, download_kwargs)
        return self._bytestream_to_fileobj(bytestream)

    def as_binary(self, project_id: int, export_type: str = "JSON", timeout: int = 60, create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None):
        bytestream = self._get_bytestream(project_id, export_type, timeout, create_kwargs, convert_kwargs, download_kwargs)
        return self._bytestream_to_binary(bytestream)

    def as_json(self, project_id: int, timeout: int = 60, create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None):
        bytestream = self._get_bytestream(project_id, "JSON", timeout, create_kwargs, convert_kwargs, download_kwargs)
        return self._bytestream_to_json(bytestream)

    def as_pandas(self, project_id: int, timeout: int = 60, create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None):
        bytestream = self._get_bytestream(project_id, "CSV", timeout, create_kwargs, convert_kwargs, download_kwargs)
        return self._bytestream_to_pandas(bytestream)

class AsyncExportsClientExt(AsyncExportsClient):

    async def _bytestream_to_fileobj(self, bytestream: typing.AsyncGenerator[bytes, None] | bytes):
        """Convert bytestream to file-like object"""
        fileobj = BytesIO()
        if isinstance(bytestream, typing.AsyncGenerator):
            async for chunk in bytestream:
                fileobj.write(chunk)
        else:
            fileobj.write(bytestream)
        fileobj.seek(0)
        return fileobj

    async def _bytestream_to_binary(self, bytestream):
        """Convert bytestream to binary data"""
        fileobj = await self._bytestream_to_fileobj(bytestream)
        return fileobj.getvalue()

    async def _bytestream_to_json(self, bytestream):
        """Convert bytestream to JSON object"""
        fileobj = await self._bytestream_to_fileobj(bytestream)
        return json.load(fileobj)

    async def _bytestream_to_pandas(self, bytestream):
        """Convert bytestream to pandas DataFrame"""
        fileobj = await self._bytestream_to_fileobj(bytestream)
        return pd.read_csv(fileobj)

    async def _poll_export(self, project_id, export_snapshot, converted_format_id, timeout):
        start_time = time.time()
        while not _check_status(export_snapshot, None, 'completed'):
            export_snapshot = await self.get(id=project_id, export_pk=export_snapshot.id)
            if _check_status(export_snapshot, None, 'failed'):
                raise ExportFailedError(export_snapshot)
            if time.time() - start_time > timeout:
                raise ExportTimeoutError(export_snapshot)
            await asyncio.sleep(1)

    async def _get_bytestream(
        self,
        project_id: int,
        export_type: str,
        timeout: int = 60,
        create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None,
        convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None,
        download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None,
    ):
        version = await AsyncVersionsClient(client_wrapper=self._client_wrapper).get()
        if version.edition == "Enterprise":
            # Enterprise edition exports are async, so we need to wait for the export job to complete
            export_snapshot = await self.create(project_id, **(create_kwargs or {}))
            # Poll for base (JSON) export to complete
            await self._poll_export(project_id, export_snapshot, None, timeout)
            # Convert to requested format if not JSON
            if export_type != "JSON":
                converted_proc = await self.convert(id=project_id, export_pk=export_snapshot.id, export_type=export_type, **(convert_kwargs or {}))
                await self._poll_export(project_id, export_snapshot, converted_proc.converted_format, timeout)

            bytestream = self.download(id=project_id, export_pk=export_snapshot.id, export_type=export_type, request_options={'chunk_size': 1024}, **(download_kwargs or {}))
        else:
            bytestream = self.download_sync(project_id, export_type=export_type, download_all_tasks=True, download_resources=True)
        return bytestream

    async def as_file(self, project_id: int, export_type: str = "JSON", timeout: int = 60, create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None):
        bytestream = await self._get_bytestream(project_id, export_type, timeout, create_kwargs, convert_kwargs, download_kwargs)
        return await self._bytestream_to_fileobj(bytestream)

    async def as_binary(self, project_id: int, export_type: str = "JSON", timeout: int = 60, create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None):
        bytestream = await self._get_bytestream(project_id, export_type, timeout, create_kwargs, convert_kwargs, download_kwargs)
        return await self._bytestream_to_binary(bytestream)

    async def as_json(self, project_id: int, timeout: int = 60, create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None):
        bytestream = await self._get_bytestream(project_id, "JSON", timeout, create_kwargs, convert_kwargs, download_kwargs)
        return await self._bytestream_to_json(bytestream)

    async def as_pandas(self, project_id: int, timeout: int = 60, create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None):
        bytestream = await self._get_bytestream(project_id, "CSV", timeout, create_kwargs, convert_kwargs, download_kwargs)
        return await self._bytestream_to_pandas(bytestream)
