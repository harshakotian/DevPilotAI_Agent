from enum import Enum

from pydantic import BaseModel, Field


class ErrorCategory(str, Enum):
    TRANSIENT = "transient"
    RECOVERABLE = "recoverable"
    FATAL = "fatal"


class ErrorRecord(BaseModel):
    source: str = Field(
        description="Node, agent, service, or tool where the error occurred."
    )

    category: ErrorCategory

    error_type: str = Field(
        description="Exception or logical error type."
    )

    message: str

    attempt: int = Field(
        ge=1,
        description="Attempt number on which this error occurred."
    )

    retryable: bool

    requires_human: bool = False

    details: dict[str, str] = Field(
        default_factory=dict
    )


class RecoveryStatus(str, Enum):
    NONE = "none"
    RETRYING = "retrying"
    RETRY_EXHAUSTED = "retry_exhausted"
    HUMAN_REQUIRED = "human_required"
    FAILED = "failed"
    RECOVERED = "recovered"