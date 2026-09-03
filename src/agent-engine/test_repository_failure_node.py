from devpilot.graph.nodes import (
    collect_repository_evidence,
)


def main():
    state = {
        "requirement": (
            "Add distributed caching to the "
            "Product API using Redis."
        ),
        "repository_path": (
            "../../samples/DoesNotExist"
        ),
        "status": "requirement_analyzed",
        "error_records": [],
        "retry_counts": {},
        "recovery_status": "none",
        "simulate_repository_timeout_once": False,
        "simulate_repository_timeout_always": False,
    }

    result = collect_repository_evidence(
        state
    )

    print()
    print("=" * 70)
    print("DIRECT NODE RESULT")
    print("=" * 70)

    print(
        "status:",
        result.get("status"),
    )

    print(
        "failed_node:",
        result.get("failed_node"),
    )

    recovery_status = result.get(
        "recovery_status"
    )

    if hasattr(
        recovery_status,
        "value",
    ):
        recovery_status = (
            recovery_status.value
        )

    print(
        "recovery_status:",
        recovery_status,
    )

    print(
        "retry_counts:",
        result.get(
            "retry_counts",
            {},
        ),
    )

    errors = result.get(
        "error_records",
        [],
    )

    print(
        "error_count:",
        len(errors),
    )

    if errors:
        error = errors[-1]

        print()
        print("Latest Error")

        print(
            "source:",
            error.source,
        )

        print(
            "category:",
            error.category.value,
        )

        print(
            "error_type:",
            error.error_type,
        )

        print(
            "attempt:",
            error.attempt,
        )

        print(
            "retryable:",
            error.retryable,
        )

        print(
            "requires_human:",
            error.requires_human,
        )


if __name__ == "__main__":
    main()