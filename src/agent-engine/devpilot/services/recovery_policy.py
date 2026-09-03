from devpilot.models.errors import (
    ErrorRecord,
    RecoveryStatus,
)


def determine_recovery_status(
    error: ErrorRecord,
) -> RecoveryStatus:
    if error.retryable:
        return RecoveryStatus.RETRYING

    if error.requires_human:
        return RecoveryStatus.HUMAN_REQUIRED

    return RecoveryStatus.FAILED