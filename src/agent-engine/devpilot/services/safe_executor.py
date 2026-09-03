from collections.abc import Callable
from typing import TypeVar

from devpilot.models.execution import ExecutionResult
from devpilot.services.error_service import (
    create_error_record,
)


T = TypeVar("T")


def execute_safely(
    source: str,
    attempt: int,
    operation: Callable[[], T],
) -> ExecutionResult[T]:
    try:
        value = operation()

        return ExecutionResult[T](
            success=True,
            value=value,
        )

    except Exception as exception:
        error = create_error_record(
            source=source,
            exception=exception,
            attempt=attempt,
        )

        return ExecutionResult[T](
            success=False,
            error=error,
        )