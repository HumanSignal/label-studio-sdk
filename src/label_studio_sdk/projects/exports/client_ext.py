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
        
        
def _filestream_to_fileobj(filestream: typing.Iterable[bytes]) -> typing.BinaryIO:
    buffer = BytesIO()
    for chunk in filestream:
        buffer.write(chunk)
    buffer.seek(0)
    return buffer
        

def _filestream_to_binary(filestream: typing.Iterable[bytes]) -> bytes:
    fileobj = _filestream_to_fileobj(filestream)
    return fileobj.getvalue()


def _filestream_to_json(filestream: typing.Iterable[bytes]) -> dict:
    fileobj = _filestream_to_fileobj(filestream)
    return json.load(fileobj)


class ExportsClientExt(ExportsClient):
    
    def _get_filestream(self, project_id: int, export_type: str, timeout: int = 60):
        version = VersionsClient(client_wrapper=self._client_wrapper).get()
        
        if version.edition == "Enterprise":
            # Enterprise edition exports are async, so we need to wait for the export job to complete
            export_snapshot = self.create(project_id)
            self.convert(project_id, export_pk=export_snapshot.id, export_type=export_type)
            start_time = time.time()
            while export_snapshot.status != "completed":
                export_snapshot = self.get(project_id, export_pk=export_snapshot.id)
                if time.time() - start_time > timeout:
                    raise ExportTimeoutError(export_snapshot)
                time.sleep(1)
            filestream = self.download(project_id, export_pk=export_snapshot.id, export_type=export_type, request_options={'chunk_size': 1024})
        else:
            # Community edition exports are sync, so we can download the file immediately
            filestream = self.download_sync(project_id, export_type="JSON", download_all_tasks=True, download_resources=True)
        return filestream
    
    def as_file(self, project_id: int, export_type: str = "JSON", timeout: int = 60):
        filestream = self._get_filestream(project_id, export_type, timeout)
        return _filestream_to_fileobj(filestream)
    
    def as_binary(self, project_id: int, export_type: str = "JSON", timeout: int = 60):
        filestream = self._get_filestream(project_id, export_type, timeout)
        return _filestream_to_binary(filestream)
    
    def as_json(self, project_id: int, timeout: int = 60):
        filestream = self._get_filestream(project_id, "JSON", timeout)
        return _filestream_to_json(filestream)
    
    def as_pandas(self, project_id: int, timeout: int = 60):
        filestream = self._get_filestream(project_id, "CSV", timeout)
        return pd.read_csv(filestream)
    
    
class AsyncExportsClientExt(AsyncExportsClient):

    async def _get_filestream(self, project_id: int, export_type: str, timeout: int = 60):
        version = await AsyncVersionsClient(client_wrapper=self._client_wrapper).get()
        if version.edition == "Enterprise":
            # Enterprise edition exports are async, so we need to wait for the export job to complete
            export_snapshot = await self.create(project_id)
            await self.convert(project_id, export_pk=export_snapshot.id, export_type=export_type)
            start_time = time.time()
            while export_snapshot.status != "completed":
                export_snapshot = await self.get(project_id, export_pk=export_snapshot.id)
                if time.time() - start_time > timeout:
                    raise ExportTimeoutError(export_snapshot)
                await asyncio.sleep(1)
            filestream = await self.download(project_id, export_pk=export_snapshot.id, export_type=export_type, request_options={'chunk_size': 1024})
        else:
            filestream = await self.download_sync(project_id, export_type=export_type, download_all_tasks=True, download_resources=True)
        return filestream
    
    async def as_file(self, project_id: int, export_type: str = "JSON", timeout: int = 60):
        filestream = await self._get_filestream(project_id, export_type, timeout)
        return _filestream_to_fileobj(filestream)
    
    async def as_binary(self, project_id: int, export_type: str = "JSON", timeout: int = 60):
        filestream = await self._get_filestream(project_id, export_type, timeout)
        return _filestream_to_binary(filestream)
    
    async def as_json(self, project_id: int, timeout: int = 60):
        filestream = await self._get_filestream(project_id, "JSON", timeout)
        return _filestream_to_json(filestream)
    
    async def as_pandas(self, project_id: int, timeout: int = 60):
        filestream = await self._get_filestream(project_id, "CSV", timeout)
        return pd.read_csv(filestream)