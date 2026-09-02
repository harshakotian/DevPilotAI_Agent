from uuid import uuid4

from langgraph.types import Command

from devpilot.graph.workflow import build_workflow


def main():
    workflow = build_workflow()

    # ---------------------------------------------------------
    # Initial State
    # ---------------------------------------------------------
    initial_state = {
        "requirement": (
            "Add distributed caching to the "
            "Product API using Redis."
        ),
        "repository_path": (
            "../../samples/SampleProductApi"
        ),
        "status": "new",
        "revision_count": 0,
        "revision_history": [],
    }

    # ---------------------------------------------------------
    # Thread / Checkpoint Configuration
    # ---------------------------------------------------------
    thread_id = str(uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    print()
    print("=" * 70)
    print("Starting DevPilot AI Workflow")
    print("=" * 70)
    print("Thread ID:", thread_id)

    # ---------------------------------------------------------
    # Invocation #1
    #
    # Expected:
    # Requirement
    # -> Repository
    # -> Architecture
    # -> Plan
    # -> Human Review
    # -> INTERRUPT
    # ---------------------------------------------------------
    workflow.invoke(
        initial_state,
        config=config,
    )

    print()
    print("=" * 70)
    print("First Human Review Reached")
    print("=" * 70)

    snapshot = workflow.get_state(
        config
    )

    print(
        "Current Status:",
        snapshot.values.get("status"),
    )

    print(
        "Revision Count:",
        snapshot.values.get(
            "revision_count",
            0,
        ),
    )

    # ---------------------------------------------------------
    # Verify specialist reviews have NOT run yet
    # ---------------------------------------------------------
    print()
    print("Before approval:")

    print(
        "Security Review Exists:",
        snapshot.values.get(
            "security_review"
        )
        is not None,
    )

    print(
        "Test Review Exists:",
        snapshot.values.get(
            "test_review"
        )
        is not None,
    )

    # Expected:
    #
    # Security Review Exists: False
    # Test Review Exists: False

    # ---------------------------------------------------------
    # Human Decision #1
    #
    # Request ARCHITECTURE revision.
    # ---------------------------------------------------------
    first_decision = {
        "decision": "revise",
        "comments": (
            "Architecture needs stronger Redis "
            "failure handling."
        ),
        "requested_changes": [
            (
                "Define explicit application behavior "
                "when Redis is unavailable."
            ),
            (
                "Avoid coupling ProductService directly "
                "to Redis-specific APIs."
            ),
            (
                "Ensure the design supports graceful "
                "fallback to the uncached path."
            ),
        ],
        "revision_target": "architecture",
    }

    print()
    print("=" * 70)
    print("Human Decision #1")
    print("=" * 70)

    print(
        "Decision:",
        first_decision["decision"],
    )

    print(
        "Revision Target:",
        first_decision["revision_target"],
    )

    print("Requested Changes:")

    for change in first_decision[
        "requested_changes"
    ]:
        print(f"- {change}")

    # ---------------------------------------------------------
    # Invocation #2
    #
    # Expected:
    #
    # Resume human_review
    # -> prepare_revision
    # -> Architect reruns
    # -> Planner reruns
    # -> Human Review again
    # -> INTERRUPT
    #
    # IMPORTANT:
    # Security/Test should NOT run here.
    # ---------------------------------------------------------
    workflow.invoke(
        Command(
            resume=first_decision
        ),
        config=config,
    )

    print()
    print("=" * 70)
    print("Second Human Review Reached")
    print("=" * 70)

    revised_snapshot = workflow.get_state(
        config
    )

    print(
        "Current Status:",
        revised_snapshot.values.get(
            "status"
        ),
    )

    print(
        "Revision Count:",
        revised_snapshot.values.get(
            "revision_count",
            0,
        ),
    )

    # ---------------------------------------------------------
    # Verify specialist reviews STILL have not run
    # ---------------------------------------------------------
    print()
    print("After revision, before second approval:")

    print(
        "Security Review Exists:",
        revised_snapshot.values.get(
            "security_review"
        )
        is not None,
    )

    print(
        "Test Review Exists:",
        revised_snapshot.values.get(
            "test_review"
        )
        is not None,
    )

    # These should still both be False.

    # ---------------------------------------------------------
    # Show revised architecture
    # ---------------------------------------------------------
    architecture = revised_snapshot.values.get(
        "architecture_proposal"
    )

    if architecture is not None:
        print()
        print("=" * 70)
        print("Revised Architecture Proposal")
        print("=" * 70)

        print(
            architecture.model_dump_json(
                indent=2
            )
        )

    # ---------------------------------------------------------
    # Show regenerated implementation plan
    # ---------------------------------------------------------
    implementation_plan = (
        revised_snapshot.values.get(
            "implementation_plan"
        )
    )

    if implementation_plan is not None:
        print()
        print("=" * 70)
        print("Regenerated Implementation Plan")
        print("=" * 70)

        print(
            implementation_plan.model_dump_json(
                indent=2
            )
        )

    # ---------------------------------------------------------
    # Human Decision #2
    #
    # Approve revised architecture + plan.
    # ---------------------------------------------------------
    second_decision = {
        "decision": "approve",
        "comments": (
            "Revised architecture and implementation "
            "plan approved for specialist review."
        ),
        "requested_changes": [],
        "revision_target": None,
    }

    print()
    print("=" * 70)
    print("Human Decision #2")
    print("=" * 70)

    print(
        "Decision:",
        second_decision["decision"],
    )

    print(
        "Comments:",
        second_decision["comments"],
    )

    # ---------------------------------------------------------
    # Invocation #3
    #
    # Expected:
    #
    # Human approval
    # -> approval_completed
    # -> Security Review
    # -> Test Strategy
    # -> specialist_reviews_completed
    # -> END
    # ---------------------------------------------------------
    result = workflow.invoke(
        Command(
            resume=second_decision
        ),
        config=config,
    )

    # ---------------------------------------------------------
    # Final Result
    # ---------------------------------------------------------
    print()
    print("=" * 70)
    print("DevPilot Workflow Complete")
    print("=" * 70)

    print(
        "Final Status:",
        result.get("status"),
    )

    print(
        "Revision Count:",
        result.get(
            "revision_count",
            0,
        ),
    )

    # ---------------------------------------------------------
    # Security Review
    # ---------------------------------------------------------
    security_review = result.get(
        "security_review"
    )

    if security_review is not None:
        print()
        print("=" * 70)
        print("Security Review")
        print("=" * 70)

        print(
            security_review.model_dump_json(
                indent=2
            )
        )

        print()
        print(
            "Overall Security Risk:",
            security_review.overall_risk.value,
        )

        print(
            "Security Implementation Blocked:",
            security_review.implementation_blocked,
        )

    # ---------------------------------------------------------
    # Test Review
    # ---------------------------------------------------------
    test_review = result.get(
        "test_review"
    )

    if test_review is not None:
        print()
        print("=" * 70)
        print("Test Strategy Review")
        print("=" * 70)

        print(
            test_review.model_dump_json(
                indent=2
            )
        )

        print()
        print(
            "Testing Implementation Blocked:",
            test_review.implementation_blocked,
        )

    # ---------------------------------------------------------
    # Final persisted-state verification
    # ---------------------------------------------------------
    final_snapshot = workflow.get_state(
        config
    )

    print()
    print("=" * 70)
    print("Final Checkpoint Verification")
    print("=" * 70)

    print(
        "Saved Status:",
        final_snapshot.values.get(
            "status"
        ),
    )

    print(
        "Security Review Stored:",
        final_snapshot.values.get(
            "security_review"
        )
        is not None,
    )

    print(
        "Test Review Stored:",
        final_snapshot.values.get(
            "test_review"
        )
        is not None,
    )

    print(
        "Revision Count:",
        final_snapshot.values.get(
            "revision_count",
            0,
        ),
    )

    # ---------------------------------------------------------
    # Review History
    # ---------------------------------------------------------
    revision_history = (
        final_snapshot.values.get(
            "revision_history",
            [],
        )
    )

    print(
        "Human Review History Entries:",
        len(revision_history),
    )

    for index, review in enumerate(
        revision_history,
        start=1,
    ):
        print()
        print(
            f"Review #{index}"
        )

        print(
            "Decision:",
            review.decision.value,
        )

        if review.revision_target is not None:
            print(
                "Revision Target:",
                review.revision_target.value,
            )

        print(
            "Comments:",
            review.comments,
        )

    # ---------------------------------------------------------
    # Checkpoint 7D.11 Assertions
    # ---------------------------------------------------------
    print()
    print("=" * 70)
    print("Checkpoint 7D.11 Verification")
    print("=" * 70)

    final_status = result.get(
        "status"
    )

    revision_count = result.get(
        "revision_count",
        0,
    )

    security_exists = (
        result.get("security_review")
        is not None
    )

    testing_exists = (
        result.get("test_review")
        is not None
    )

    status_ok = (
        final_status
        == "specialist_reviews_completed"
    )

    revision_ok = (
        revision_count == 1
    )

    print(
        "Final status correct:",
        status_ok,
    )

    print(
        "Exactly one revision occurred:",
        revision_ok,
    )

    print(
        "Security review generated:",
        security_exists,
    )

    print(
        "Test review generated:",
        testing_exists,
    )

    if (
        status_ok
        and revision_ok
        and security_exists
        and testing_exists
    ):
        print()
        print(
            "CHECKPOINT 7D.11 TEST PASSED"
        )
    else:
        print()
        print(
            "CHECKPOINT 7D.11 TEST FAILED"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()