# This file was auto-generated by Fern from our API Definition.

import enum
import typing

T_Result = typing.TypeVar("T_Result")


class GcsImportStorageStatus(str, enum.Enum):
    INITIALIZED = "initialized"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    FAILED = "failed"
    COMPLETED = "completed"

    def visit(
        self,
        initialized: typing.Callable[[], T_Result],
        queued: typing.Callable[[], T_Result],
        in_progress: typing.Callable[[], T_Result],
        failed: typing.Callable[[], T_Result],
        completed: typing.Callable[[], T_Result],
    ) -> T_Result:
        if self is GcsImportStorageStatus.INITIALIZED:
            return initialized()
        if self is GcsImportStorageStatus.QUEUED:
            return queued()
        if self is GcsImportStorageStatus.IN_PROGRESS:
            return in_progress()
        if self is GcsImportStorageStatus.FAILED:
            return failed()
        if self is GcsImportStorageStatus.COMPLETED:
            return completed()