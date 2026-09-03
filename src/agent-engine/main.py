from uuid import uuid4

from langgraph.types import Command

from devpilot.graph.workflow import build_workflow


def print_separator(
    title: str,
) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def main():
    # ---------------------------------------------------------
    # Build workflow
    # ---------------------------------------------------------

    workflow = build_workflow()

    # ---------------------------------------------------------
    # Normal DevPilot input
    #
    # Failure simulation is intentionally disabled.
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

        "error_records": [],
        "retry_counts": {},
        "recovery_status": "none",

        "simulate_repository_timeout_once": False,
        "simulate_repository_timeout_always": False,
    }

    # ---------------------------------------------------------
    # Workflow thread
    # ---------------------------------------------------------

    thread_id = str(
        uuid4()
    )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    print_separator(
        "Starting DevPilot AI"
    )

    print(
        "Thread ID:",
        thread_id,
    )

    # ---------------------------------------------------------
    # First invocation
    #
    # Normal expected route:
    #
    # Requirement
    # ↓
    # Repository Intelligence
    # ↓
    # Architecture
    # ↓
    # Implementation Plan
    # ↓
    # Human Review interrupt
    # ---------------------------------------------------------

    result = workflow.invoke(
        initial_state,
        config=config,
    )

    # ---------------------------------------------------------
    # Inspect current checkpoint
    # ---------------------------------------------------------

    snapshot = workflow.get_state(
        config
    )

    current_status = (
        snapshot.values.get(
            "status"
        )
    )

    print_separator(
        "Workflow Paused"
    )

    print(
        "Current Status:",
        current_status,
    )

    # ---------------------------------------------------------
    # Clarification path
    # ---------------------------------------------------------

    if (
        current_status
        == "needs_clarification"
    ):
        analysis = snapshot.values.get(
            "requirement_analysis"
        )

        print()
        print(
            "Requirement requires clarification."
        )

        if analysis is not None:
            print()
            print(
                "Clarification Questions:"
            )

            for question in (
                analysis.clarification_questions
            ):
                print(
                    f"- {question}"
                )

        return

    # ---------------------------------------------------------
    # Repository recovery path
    #
    # In normal execution we don't expect this.
    # If it happens, display the error and stop.
    #
    # A real UI will later provide an interactive
    # recovery decision.
    # ---------------------------------------------------------

    if (
        current_status
        == "repository_evidence_failed"
    ):
        print()
        print(
            "Repository recovery is required."
        )

        errors = snapshot.values.get(
            "error_records",
            [],
        )

        if errors:
            latest_error = errors[-1]

            print(
                "Error:",
                latest_error.message,
            )

        return

    # ---------------------------------------------------------
    # Human architecture / implementation-plan approval
    #
    # For CLI MVP testing we simulate the human approval.
    #
    # In Portfolio V2 this comes from the UI.
    # ---------------------------------------------------------

    human_decision = {
        "decision": "approve",
        "comments": (
            "Architecture and implementation plan "
            "approved for specialist review."
        ),
        "requested_changes": [],
        "revision_target": None,
    }

    print_separator(
        "Human Review Decision"
    )

    print(
        "Decision:",
        human_decision[
            "decision"
        ],
    )

    print(
        "Comments:",
        human_decision[
            "comments"
        ],
    )

    # ---------------------------------------------------------
    # Resume same thread
    #
    # Expected:
    #
    # Human Approval
    # ↓
    # Security + Testing
    # ↓
    # Evaluator
    # ↓
    # Deterministic Policy
    # ↓
    # PASS / REVISE / ESCALATE
    # ---------------------------------------------------------

    result = workflow.invoke(
        Command(
            resume=human_decision
        ),
        config=config,
    )

    # ---------------------------------------------------------
    # Final status
    # ---------------------------------------------------------

    print_separator(
        "DevPilot Workflow Complete"
    )

    final_status = result.get(
        "status"
    )

    print(
        "Final Status:",
        final_status,
    )

    # ---------------------------------------------------------
    # Requirement Analysis
    # ---------------------------------------------------------

    requirement_analysis = result.get(
        "requirement_analysis"
    )

    if requirement_analysis is not None:
        print_separator(
            "Requirement Analysis"
        )

        print(
            requirement_analysis.model_dump_json(
                indent=2
            )
        )

    # ---------------------------------------------------------
    # Repository Analysis
    # ---------------------------------------------------------

    repository_analysis = result.get(
        "repository_analysis"
    )

    if repository_analysis is not None:
        print_separator(
            "Repository Analysis"
        )

        print(
            repository_analysis.model_dump_json(
                indent=2
            )
        )

    # ---------------------------------------------------------
    # Architecture
    # ---------------------------------------------------------

    architecture = result.get(
        "architecture_proposal"
    )

    if architecture is not None:
        print_separator(
            "Architecture Proposal"
        )

        print(
            architecture.model_dump_json(
                indent=2
            )
        )

    # ---------------------------------------------------------
    # Implementation Plan
    # ---------------------------------------------------------

    implementation_plan = result.get(
        "implementation_plan"
    )

    if implementation_plan is not None:
        print_separator(
            "Implementation Plan"
        )

        print(
            implementation_plan.model_dump_json(
                indent=2
            )
        )

    # ---------------------------------------------------------
    # Security Review
    # ---------------------------------------------------------

    security_review = result.get(
        "security_review"
    )

    if security_review is not None:
        print_separator(
            "Security Review"
        )

        print(
            "Overall Risk:",
            security_review.overall_risk.value,
        )

        print(
            "Implementation Blocked:",
            security_review.implementation_blocked,
        )

        print(
            "Findings:",
            len(
                security_review.findings
            ),
        )

    # ---------------------------------------------------------
    # Test Strategy
    # ---------------------------------------------------------

    test_review = result.get(
        "test_review"
    )

    if test_review is not None:
        print_separator(
            "Test Strategy"
        )

        print(
            "Implementation Blocked:",
            test_review.implementation_blocked,
        )

        print(
            "Scenarios:",
            len(
                test_review.scenarios
            ),
        )

    # ---------------------------------------------------------
    # Evaluation
    # ---------------------------------------------------------

    evaluation = result.get(
        "evaluation_result"
    )

    if evaluation is not None:
        print_separator(
            "Quality Evaluation"
        )

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

        if evaluation.required_revisions:
            print()
            print(
                "Required Revisions:"
            )

            for revision in (
                evaluation.required_revisions
            ):
                print(
                    f"- {revision}"
                )

        if evaluation.escalation_reasons:
            print()
            print(
                "Escalation Reasons:"
            )

            for reason in (
                evaluation.escalation_reasons
            ):
                print(
                    f"- {reason}"
                )

    # ---------------------------------------------------------
    # Failure history
    #
    # A successful workflow can still contain recovered errors.
    # ---------------------------------------------------------

    error_records = result.get(
        "error_records",
        [],
    )

    if error_records:
        print_separator(
            "Execution Error History"
        )

        for index, error in enumerate(
            error_records,
            start=1,
        ):
            print()
            print(
                f"Error #{index}"
            )

            print(
                "Source:",
                error.source,
            )

            print(
                "Category:",
                error.category.value,
            )

            print(
                "Type:",
                error.error_type,
            )

            print(
                "Attempt:",
                error.attempt,
            )

            print(
                "Message:",
                error.message,
            )

    # ---------------------------------------------------------
    # Final checkpoint verification
    # ---------------------------------------------------------

    final_snapshot = workflow.get_state(
        config
    )

    print_separator(
        "Final Workflow State"
    )

    print(
        "Saved Status:",
        final_snapshot.values.get(
            "status"
        ),
    )

    print(
        "Repository Analysis:",
        final_snapshot.values.get(
            "repository_analysis"
        )
        is not None,
    )

    print(
        "Architecture Proposal:",
        final_snapshot.values.get(
            "architecture_proposal"
        )
        is not None,
    )

    print(
        "Implementation Plan:",
        final_snapshot.values.get(
            "implementation_plan"
        )
        is not None,
    )

    print(
        "Security Review:",
        final_snapshot.values.get(
            "security_review"
        )
        is not None,
    )

    print(
        "Test Review:",
        final_snapshot.values.get(
            "test_review"
        )
        is not None,
    )

    print(
        "Evaluation Result:",
        final_snapshot.values.get(
            "evaluation_result"
        )
        is not None,
    )

    print_separator(
        "DevPilot AI Execution Finished"
    )


if __name__ == "__main__":
    main()