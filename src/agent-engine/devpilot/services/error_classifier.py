from devpilot.models.errors import (
    ErrorCategory,
)


def classify_exception(
    exception: Exception,
) -> ErrorCategory:

    if isinstance(
        exception,
        (
            TimeoutError,
            ConnectionError,
        ),
    ):
        return ErrorCategory.TRANSIENT

    if isinstance(
        exception,
        (
            FileNotFoundError,
            NotADirectoryError,
            ValueError,
        ),
    ):
        return ErrorCategory.RECOVERABLE

    return ErrorCategory.FATAL