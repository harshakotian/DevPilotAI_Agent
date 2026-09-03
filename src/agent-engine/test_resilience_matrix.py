from uuid import uuid4

from langgraph.types import Command

from devpilot.graph.workflow import build_workflow
from devpilot.services.failure_simulator import (
    failure_simulator,
)


VALID_REPOSITORY = (
    "../../samples/SampleProductApi"
)

INVALID_REPOSITORY = (
    "../../samples/DoesNotExist"
)

REQUIREMENT = (
    "Add distributed caching to the "
    "Product API using Redis."
)


def create_config():
    return {
        "configurable": {
            "thread_id": str(uuid4())
        }
    }


def create_initial_state(
    repository_path: str,
    simulate_once: bool = False,
    simulate_always: bool = False,
):
    return {
        "requirement": REQUIREMENT,
        "repository_path": repository_path,
        "status": "new",

        "revision_count": 0,
        "revision_history": [],

        "error_records": [],
        "retry_counts": {},
        "recovery_status": "none",

        "simulate_repository_timeout_once": (
            simulate_once
        ),
        "simulate_repository_timeout_always": (
            simulate_always
        ),
    }


# ============================================================
# Scenario 1
# Normal repository execution
# ============================================================

def test_normal_execution():
    print()
    print("=" * 70)
    print("SCENARIO 1 - NORMAL REPOSITORY")
    print("=" * 70)

    failure_simulator.reset()

    workflow = build_workflow()
    config = create_config()

    initial_state = create_initial_state(
        repository_path=VALID_REPOSITORY
    )

    # Expected:
    # workflow progresses normally until the
    # architecture/plan human-review interrupt.
    workflow.invoke(
        initial_state,
        config=config,
    )

    snapshot = workflow.get_state(
        config
    )

    errors = snapshot.values.get(
        "error_records",
        [],
    )

    repository_exists = (
        snapshot.values.get(
            "repository_evidence"
        )
        is not None
    )

    status = snapshot.values.get(
        "status"
    )

    reached_human_review = (
        status
        == "implementation_planned"
    )

    passed = (
        repository_exists
        and len(errors) == 0
        and reached_human_review
    )

    print(
        "Repository evidence exists:",
        repository_exists,
    )

    print(
        "Errors recorded:",
        len(errors),
    )

    print(
        "Reached normal human-review gate:",
        reached_human_review,
    )

    print(
        "RESULT:",
        "PASS" if passed else "FAIL",
    )

    return passed


# ============================================================
# Scenario 2
# Recoverable repository failure + human correction
# ============================================================

def test_human_repository_recovery():
    print()
    print("=" * 70)
    print(
        "SCENARIO 2 - HUMAN REPOSITORY RECOVERY"
    )
    print("=" * 70)

    failure_simulator.reset()

    workflow = build_workflow()
    config = create_config()

    initial_state = create_initial_state(
        repository_path=INVALID_REPOSITORY
    )

    # --------------------------------------------------------
    # Invocation #1
    #
    # Expected:
    #
    # FileNotFoundError
    # -> recoverable
    # -> HUMAN_REQUIRED
    # -> repository_recovery_required
    # -> interrupt
    # --------------------------------------------------------

    workflow.invoke(
        initial_state,
        config=config,
    )

    failed_snapshot = workflow.get_state(
        config
    )

    errors_before = (
        failed_snapshot.values.get(
            "error_records",
            [],
        )
    )

    failed_status = (
        failed_snapshot.values.get(
            "status"
        )
    )

    recovery_status = (
        failed_snapshot.values.get(
            "recovery_status"
        )
    )

    if hasattr(
        recovery_status,
        "value",
    ):
        recovery_status_value = (
            recovery_status.value
        )
    else:
        recovery_status_value = (
            recovery_status
        )

    failure_recorded = (
        len(errors_before) == 1
        and errors_before[-1].category.value
        == "recoverable"
        and errors_before[-1].requires_human
        is True
    )

    recovery_interrupt_reached = (
        failed_status
        == "repository_evidence_failed"
        and recovery_status_value
        == "human_required"
    )

    print(
        "Recoverable error recorded:",
        failure_recorded,
    )

    print(
        "Human recovery required:",
        recovery_interrupt_reached,
    )

    # --------------------------------------------------------
    # Human fixes repository path
    # --------------------------------------------------------

    recovery_decision = {
        "action": "retry",
        "repository_path": VALID_REPOSITORY,
    }

    # Resume SAME thread.
    workflow.invoke(
        Command(
            resume=recovery_decision
        ),
        config=config,
    )

    recovered_snapshot = workflow.get_state(
        config
    )

    repository_recovered = (
        recovered_snapshot.values.get(
            "repository_evidence"
        )
        is not None
    )

    corrected_path = (
        recovered_snapshot.values.get(
            "repository_path"
        )
        == VALID_REPOSITORY
    )

    errors_after = (
        recovered_snapshot.values.get(
            "error_records",
            [],
        )
    )

    history_preserved = (
        len(errors_after) >= 1
    )

    reached_normal_review = (
        recovered_snapshot.values.get(
            "status"
        )
        == "implementation_planned"
    )

    passed = (
        failure_recorded
        and recovery_interrupt_reached
        and repository_recovered
        and corrected_path
        and history_preserved
        and reached_normal_review
    )

    print(
        "Repository recovered:",
        repository_recovered,
    )

    print(
        "Corrected path stored:",
        corrected_path,
    )

    print(
        "Error history preserved:",
        history_preserved,
    )

    print(
        "Workflow continued normally:",
        reached_normal_review,
    )

    print(
        "RESULT:",
        "PASS" if passed else "FAIL",
    )

    return passed


# ============================================================
# Scenario 3
# Transient timeout + automatic retry
# ============================================================

def test_transient_auto_retry():
    print()
    print("=" * 70)
    print(
        "SCENARIO 3 - TRANSIENT AUTO RETRY"
    )
    print("=" * 70)

    failure_simulator.reset()

    workflow = build_workflow()
    config = create_config()

    initial_state = create_initial_state(
        repository_path=VALID_REPOSITORY,
        simulate_once=True,
    )

    # Expected:
    #
    # attempt 1 -> TimeoutError
    # -> transient
    # -> automatic retry
    #
    # attempt 2 -> success
    #
    # -> normal workflow continues
    workflow.invoke(
        initial_state,
        config=config,
    )

    snapshot = workflow.get_state(
        config
    )

    errors = snapshot.values.get(
        "error_records",
        [],
    )

    transient_error_exists = (
        len(errors) == 1
        and errors[0].category.value
        == "transient"
        and errors[0].error_type
        == "TimeoutError"
        and errors[0].retryable
        is True
        and errors[0].requires_human
        is False
    )

    repository_recovered = (
        snapshot.values.get(
            "repository_evidence"
        )
        is not None
    )

    retry_counts = (
        snapshot.values.get(
            "retry_counts",
            {},
        )
    )

    retry_count_reset = (
        retry_counts.get(
            "collect_repository_evidence",
            0,
        )
        == 0
    )

    repository_path_unchanged = (
        snapshot.values.get(
            "repository_path"
        )
        == VALID_REPOSITORY
    )

    reached_normal_review = (
        snapshot.values.get(
            "status"
        )
        == "implementation_planned"
    )

    passed = (
        transient_error_exists
        and repository_recovered
        and retry_count_reset
        and repository_path_unchanged
        and reached_normal_review
    )

    print(
        "Transient error recorded:",
        transient_error_exists,
    )

    print(
        "Automatic retry succeeded:",
        repository_recovered,
    )

    print(
        "Retry counter reset:",
        retry_count_reset,
    )

    print(
        "No repository correction required:",
        repository_path_unchanged,
    )

    print(
        "Workflow continued normally:",
        reached_normal_review,
    )

    print(
        "RESULT:",
        "PASS" if passed else "FAIL",
    )

    return passed


# ============================================================
# Scenario 4
# Persistent transient failure + retry exhaustion
# ============================================================

def test_retry_exhaustion():
    print()
    print("=" * 70)
    print(
        "SCENARIO 4 - RETRY EXHAUSTION"
    )
    print("=" * 70)

    failure_simulator.reset()

    workflow = build_workflow()
    config = create_config()

    initial_state = create_initial_state(
        repository_path=VALID_REPOSITORY,
        simulate_always=True,
    )

    # Expected:
    #
    # attempt 1 -> timeout -> retry
    # attempt 2 -> timeout -> retry
    # attempt 3 -> timeout
    # -> retry_exhausted
    # -> END
    result = workflow.invoke(
        initial_state,
        config=config,
    )

    errors = result.get(
        "error_records",
        [],
    )

    retry_counts = result.get(
        "retry_counts",
        {},
    )

    attempts = retry_counts.get(
        "collect_repository_evidence",
        0,
    )

    recovery_status = result.get(
        "recovery_status"
    )

    if hasattr(
        recovery_status,
        "value",
    ):
        recovery_status_value = (
            recovery_status.value
        )
    else:
        recovery_status_value = (
            recovery_status
        )

    status_ok = (
        result.get("status")
        == "retry_exhausted"
    )

    recovery_status_ok = (
        recovery_status_value
        == "retry_exhausted"
    )

    attempts_ok = (
        attempts == 3
    )

    error_history_ok = (
        len(errors) == 3
    )

    all_errors_transient = (
        len(errors) == 3
        and all(
            error.category.value
            == "transient"
            for error in errors
        )
    )

    attempts_recorded_correctly = (
        len(errors) == 3
        and [
            error.attempt
            for error in errors
        ]
        == [1, 2, 3]
    )

    repository_never_completed = (
        result.get(
            "repository_evidence"
        )
        is None
    )

    passed = (
        status_ok
        and recovery_status_ok
        and attempts_ok
        and error_history_ok
        and all_errors_transient
        and attempts_recorded_correctly
        and repository_never_completed
    )

    print(
        "Status retry_exhausted:",
        status_ok,
    )

    print(
        "Recovery status correct:",
        recovery_status_ok,
    )

    print(
        "Exactly 3 attempts:",
        attempts_ok,
    )

    print(
        "Exactly 3 errors recorded:",
        error_history_ok,
    )

    print(
        "All errors transient:",
        all_errors_transient,
    )

    print(
        "Attempts recorded as 1, 2, 3:",
        attempts_recorded_correctly,
    )

    print(
        "Repository never completed:",
        repository_never_completed,
    )

    print(
        "RESULT:",
        "PASS" if passed else "FAIL",
    )

    return passed


# ============================================================
# Main Regression Matrix
# ============================================================

def main():
    results = {
        "normal_execution": (
            test_normal_execution()
        ),

        "human_repository_recovery": (
            test_human_repository_recovery()
        ),

        "transient_auto_retry": (
            test_transient_auto_retry()
        ),

        "retry_exhaustion": (
            test_retry_exhaustion()
        ),
    }

    print()
    print("=" * 70)
    print(
        "CHECKPOINT 9E - RESILIENCE MATRIX"
    )
    print("=" * 70)

    for name, passed in results.items():
        print(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    all_passed = all(
        results.values()
    )

    print()
    print("=" * 70)

    if all_passed:
        print(
            "CHECKPOINT 9E PASSED"
        )
    else:
        print(
            "CHECKPOINT 9E FAILED"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()