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
                f"Export job timed out after {timeout} seconds: "
                f"unable to retrieve export job {export_snapshot.id}. "
                f"Current status: {export_snapshot.status}. "
                f"Try manually checking the running job with "
                f"`ls.projects.exports.get(project_id={project_id}, export_pk={export_snapshot.id})`."
            )
        )
        
        
def _bytestream_to_fileobj(bytestream: typing.Iterable[bytes]) -> typing.BinaryIO:
    buffer = BytesIO()
    for chunk in bytestream:
        buffer.write(chunk)
    buffer.seek(0)
    return buffer

def _bytestream_to_binary(bytestream: typing.Iterable[bytes]) -> bytes:
    fileobj = _bytestream_to_fileobj(bytestream)
    return fileobj.getvalue()

def _bytestream_to_json(bytestream: typing.Iterable[bytes]) -> dict:
    fileobj = _bytestream_to_fileobj(bytestream)
    return json.load(fileobj)

def _bytestream_to_pandas(bytestream: typing.Iterable[bytes]) -> pd.DataFrame:
    fileobj = _bytestream_to_fileobj(bytestream)
    return pd.read_csv(fileobj)

class ExportsClientExt(ExportsClient):
    
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
            if export_type != "JSON":
                self.convert(project_id, export_pk=export_snapshot.id, export_type=export_type, **(convert_kwargs or {}))
            start_time = time.time()
            while export_snapshot.status != "completed":
                export_snapshot = self.get(project_id, export_pk=export_snapshot.id)
                if time.time() - start_time > timeout:
                    raise ExportTimeoutError(export_snapshot)
                time.sleep(1)
            bytestream = self.download(project_id, export_pk=export_snapshot.id, export_type=export_type, request_options={'chunk_size': 1024}, **(download_kwargs or {}))
        else:
            # Community edition exports are sync, so we can download the file immediately
            bytestream = self.download_sync(project_id, export_type=export_type, download_all_tasks=True, download_resources=True)
        return bytestream
    
    def as_file(self, project_id: int, export_type: str = "JSON", timeout: int = 60, create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None):
        bytestream = self._get_bytestream(project_id, export_type, timeout, create_kwargs, convert_kwargs, download_kwargs)
        return _bytestream_to_fileobj(bytestream)
    
    def as_binary(self, project_id: int, export_type: str = "JSON", timeout: int = 60, create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None):
        bytestream = self._get_bytestream(project_id, export_type, timeout, create_kwargs, convert_kwargs, download_kwargs)
        return _bytestream_to_binary(bytestream)
    
    def as_json(self, project_id: int, timeout: int = 60, create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None):
        bytestream = self._get_bytestream(project_id, "JSON", timeout, create_kwargs, convert_kwargs, download_kwargs)
        return _bytestream_to_json(bytestream)
    
    def as_pandas(self, project_id: int, timeout: int = 60, create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None):
        bytestream = self._get_bytestream(project_id, "CSV", timeout, create_kwargs, convert_kwargs, download_kwargs)
        return _bytestream_to_pandas(bytestream)
    
class AsyncExportsClientExt(AsyncExportsClient):

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
            if export_type != "JSON":
                await self.convert(project_id, export_pk=export_snapshot.id, export_type=export_type, **(convert_kwargs or {}))
            start_time = time.time()
            while export_snapshot.status != "completed":
                export_snapshot = await self.get(project_id, export_pk=export_snapshot.id)
                if time.time() - start_time > timeout:
                    raise ExportTimeoutError(export_snapshot)
                await asyncio.sleep(1)
            bytestream = await self.download(project_id, export_pk=export_snapshot.id, export_type=export_type, request_options={'chunk_size': 1024}, **(download_kwargs or {}))
        else:
            bytestream = await self.download_sync(project_id, export_type=export_type, download_all_tasks=True, download_resources=True)
        return bytestream
    
    async def as_file(self, project_id: int, export_type: str = "JSON", timeout: int = 60, create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None):
        bytestream = await self._get_bytestream(project_id, export_type, timeout, create_kwargs, convert_kwargs, download_kwargs)
        return _bytestream_to_fileobj(bytestream)
    
    async def as_binary(self, project_id: int, export_type: str = "JSON", timeout: int = 60, create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None):
        bytestream = await self._get_bytestream(project_id, export_type, timeout, create_kwargs, convert_kwargs, download_kwargs)
        return _bytestream_to_binary(bytestream)
    
    async def as_json(self, project_id: int, timeout: int = 60, create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None):
        bytestream = await self._get_bytestream(project_id, "JSON", timeout, create_kwargs, convert_kwargs, download_kwargs)
        return _bytestream_to_json(bytestream)
    
    async def as_pandas(self, project_id: int, timeout: int = 60, create_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, convert_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, download_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None):
        bytestream = await self._get_bytestream(project_id, "CSV", timeout, create_kwargs, convert_kwargs, download_kwargs)
        return _bytestream_to_pandas(bytestream)
