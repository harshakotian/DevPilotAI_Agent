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
    # Thread / Checkpoint Config
    # ---------------------------------------------------------
    thread_id = str(uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    print()
    print("=" * 70)
    print("Starting DevPilot AI - Checkpoint 8 Test")
    print("=" * 70)

    print(
        "Thread ID:",
        thread_id,
    )

    # ---------------------------------------------------------
    # Invocation #1
    #
    # Expected:
    #
    # Requirement
    # -> Repository
    # -> Architect
    # -> Planner
    # -> Human Review
    # -> INTERRUPT
    # ---------------------------------------------------------
    workflow.invoke(
        initial_state,
        config=config,
    )

    print()
    print("=" * 70)
    print("Human Review Reached")
    print("=" * 70)

    snapshot = workflow.get_state(
        config
    )

    print(
        "Current Status:",
        snapshot.values.get(
            "status"
        ),
    )

    # ---------------------------------------------------------
    # Human Approval
    #
    # Allow proposal to move to:
    # Security + Test Review + Evaluator
    # ---------------------------------------------------------
    human_decision = {
        "decision": "approve",
        "comments": (
            "Architecture and implementation "
            "plan approved for specialist review."
        ),
        "requested_changes": [],
        "revision_target": None,
    }

    print()
    print("=" * 70)
    print("Human Decision")
    print("=" * 70)

    print(
        "Decision:",
        human_decision["decision"],
    )

    # ---------------------------------------------------------
    # Invocation #2
    #
    # Expected:
    #
    # approval_completed
    #
    # Security ─┐
    #           ├─ specialist_reviews_completed
    # Testing ──┘
    #
    # -> Evaluator
    # -> Evaluation Policy
    # -> PASS / REVISE / ESCALATE
    # ---------------------------------------------------------
    result = workflow.invoke(
        Command(
            resume=human_decision
        ),
        config=config,
    )

    # ---------------------------------------------------------
    # Workflow Result
    # ---------------------------------------------------------
    print()
    print("=" * 70)
    print("DevPilot Workflow Complete")
    print("=" * 70)

    final_status = result.get(
        "status"
    )

    print(
        "Final Status:",
        final_status,
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
        print("Security Review Summary")
        print("=" * 70)

        print(
            "Overall Risk:",
            security_review.overall_risk.value,
        )

        print(
            "Implementation Blocked:",
            security_review.implementation_blocked,
        )

        print(
            "Finding Count:",
            len(
                security_review.findings
            ),
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
        print("Test Review Summary")
        print("=" * 70)

        print(
            "Implementation Blocked:",
            test_review.implementation_blocked,
        )

        print(
            "Scenario Count:",
            len(
                test_review.scenarios
            ),
        )

    # ---------------------------------------------------------
    # Evaluation Result
    # ---------------------------------------------------------
    evaluation = result.get(
        "evaluation_result"
    )

    if evaluation is not None:
        print()
        print("=" * 70)
        print("Evaluation Result")
        print("=" * 70)

        print(
            "Verdict:",
            evaluation.verdict.value,
        )

        print(
            "Implementation Ready:",
            evaluation.implementation_ready,
        )

        print(
            "Confidence:",
            evaluation.confidence,
        )

        print()
        print("Scores")

        print(
            "Requirement Alignment:",
            evaluation.scores.requirement_alignment,
        )

        print(
            "Architectural Quality:",
            evaluation.scores.architectural_quality,
        )

        print(
            "Implementation Readiness:",
            evaluation.scores.implementation_readiness,
        )

        print(
            "Security Readiness:",
            evaluation.scores.security_readiness,
        )

        print(
            "Test Readiness:",
            evaluation.scores.test_readiness,
        )

        print()
        print("Blocking / Required Revisions")

        if evaluation.required_revisions:
            for revision in (
                evaluation.required_revisions
            ):
                print(
                    f"- {revision}"
                )
        else:
            print(
                "None"
            )

        if evaluation.escalation_reasons:
            print()
            print("Escalation Reasons")

            for reason in (
                evaluation.escalation_reasons
            ):
                print(
                    f"- {reason}"
                )

    else:
        print()
        print(
            "WARNING: Evaluation result "
            "was not generated."
        )

    # ---------------------------------------------------------
    # Persisted State Verification
    # ---------------------------------------------------------
    final_snapshot = workflow.get_state(
        config
    )

    print()
    print("=" * 70)
    print("Checkpoint State Verification")
    print("=" * 70)

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
        "Evaluation Result Stored:",
        final_snapshot.values.get(
            "evaluation_result"
        )
        is not None,
    )

    print(
        "Saved Status:",
        final_snapshot.values.get(
            "status"
        ),
    )

    # ---------------------------------------------------------
    # Expected Result for Current Redis Scenario
    # ---------------------------------------------------------
    print()
    print("=" * 70)
    print("Checkpoint 8 Verification")
    print("=" * 70)

    if evaluation is None:
        print(
            "CHECKPOINT 8 FAILED:"
        )

        print(
            "Evaluator did not produce a result."
        )

        return

    security_blocked = (
        security_review is not None
        and security_review.implementation_blocked
    )

    test_blocked = (
        test_review is not None
        and test_review.implementation_blocked
    )

    print(
        "Security Blocked:",
        security_blocked,
    )

    print(
        "Testing Blocked:",
        test_blocked,
    )

    print(
        "Evaluator Verdict:",
        evaluation.verdict.value,
    )

    print(
        "Implementation Ready:",
        evaluation.implementation_ready,
    )

    # ---------------------------------------------------------
    # Policy Assertions
    # ---------------------------------------------------------
    policy_ok = True

    if (
        security_blocked
        or test_blocked
    ):
        if (
            evaluation.verdict.value
            == "pass"
        ):
            policy_ok = False

            print()
            print(
                "ERROR: Blocking specialist "
                "review incorrectly resulted "
                "in PASS."
            )

    if (
        evaluation.verdict.value
        != "pass"
        and evaluation.implementation_ready
    ):
        policy_ok = False

        print()
        print(
            "ERROR: implementation_ready "
            "must be False when verdict "
            "is not PASS."
        )

    # ---------------------------------------------------------
    # Final Check
    # ---------------------------------------------------------
    expected_statuses = {
        "quality_gate_passed",
        "quality_revision_required",
        "quality_escalated",
    }

    status_ok = (
        final_status
        in expected_statuses
    )

    print()
    print(
        "Valid quality-gate status:",
        status_ok,
    )

    print(
        "Deterministic policy respected:",
        policy_ok,
    )

    if (
        status_ok
        and policy_ok
    ):
        print()
        print(
            "CHECKPOINT 8 WORKFLOW TEST PASSED"
        )
    else:
        print()
        print(
            "CHECKPOINT 8 WORKFLOW TEST FAILED"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()