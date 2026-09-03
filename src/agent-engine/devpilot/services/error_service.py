from devpilot.models.errors import (
    ErrorCategory,
    ErrorRecord,
)
from devpilot.services.error_classifier import (
    classify_exception,
)


def create_error_record(
    source: str,
    exception: Exception,
    attempt: int,
) -> ErrorRecord:
    category = classify_exception(
        exception
    )

    retryable = (
        category
        == ErrorCategory.TRANSIENT
    )

    requires_human = (
        category
        == ErrorCategory.RECOVERABLE
    )

    return ErrorRecord(
        source=source,
        category=category,
        error_type=type(exception).__name__,
        message=str(exception),
        attempt=attempt,
        retryable=retryable,
        requires_human=requires_human,
    )