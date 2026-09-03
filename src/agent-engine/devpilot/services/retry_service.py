def get_next_attempt(
    retry_counts: dict[str, int],
    source: str,
) -> int:
    return (
        retry_counts.get(
            source,
            0,
        )
        + 1
    )


def mark_attempt(
    retry_counts: dict[str, int],
    source: str,
    attempt: int,
) -> dict[str, int]:
    updated = dict(
        retry_counts
    )

    updated[source] = attempt

    return updated


def reset_attempts(
    retry_counts: dict[str, int],
    source: str,
) -> dict[str, int]:
    updated = dict(
        retry_counts
    )

    updated[source] = 0

    return updated