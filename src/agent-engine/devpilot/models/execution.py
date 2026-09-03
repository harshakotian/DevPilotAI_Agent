from typing import Generic, TypeVar

from pydantic import BaseModel

from devpilot.models.errors import ErrorRecord


T = TypeVar("T")


class ExecutionResult(BaseModel, Generic[T]):
    success: bool

    value: T | None = None

    error: ErrorRecord | None = None