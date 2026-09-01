from uuid import uuid4

from langgraph.types import Command

from devpilot.graph.workflow import build_workflow


def main():
    workflow = build_workflow()

    # ---------------------------------------------------------
    # Initial DevPilot State
    # ---------------------------------------------------------

    initial_state = {
        "requirement": (
            "Add distributed caching to the Product API "
            "using Redis."
            # "Make the system better."
        ),
        "repository_path": (
            "../../samples/SampleProductApi"
        ),
        "status": "new",
        "revision_count": 0,
        "revision_history": [],
    }

    # ---------------------------------------------------------
    # Create a unique workflow thread
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

    print(
        f"Thread ID: {thread_id}"
    )

    # ---------------------------------------------------------
    # First Invocation
    #
    # Expected:
    #
    # Requirement Analyst
    # Repository Analysis
    # Architect
    # Implementation Planner
    # Human Review
    #
    # Then graph INTERRUPTS.
    # ---------------------------------------------------------

    result = workflow.invoke(
        initial_state,
        config=config,
    )

    print()
    print("=" * 70)
    print("Workflow paused for first human review")
    print("=" * 70)

    # ---------------------------------------------------------
    # Examine checkpointed state
    # ---------------------------------------------------------

    snapshot = workflow.get_state(
        config
    )

    print(
        "Current status:",
        snapshot.values.get("status"),
    )

    print(
        "Revision count:",
        snapshot.values.get(
            "revision_count",
            0,
        ),
    )

    # ---------------------------------------------------------
    # FIRST HUMAN DECISION
    #
    # Request an ARCHITECTURE revision.
    # ---------------------------------------------------------

    first_decision = {
        "decision": "revise",
        "comments": (
            "Architecture needs stronger Redis "
            "failure handling."
        ),
        "requested_changes": [
            (
                "Define behavior when Redis is "
                "temporarily unavailable."
            ),
            (
                "Avoid coupling ProductService "
                "directly to Redis-specific APIs."
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
        print(
            f"- {change}"
        )

    # ---------------------------------------------------------
    # Resume the SAME thread
    #
    # Expected path:
    #
    # human_review
    #      ↓
    # prepare_revision
    #      ↓
    # design_architecture
    #      ↓
    # create_implementation_plan
    #      ↓
    # human_review
    #      ↓
    # INTERRUPT AGAIN
    # ---------------------------------------------------------

    result = workflow.invoke(
        Command(
            resume=first_decision
        ),
        config=config,
    )

    print()
    print("=" * 70)
    print(
        "Workflow paused for second human review"
    )
    print("=" * 70)

    # ---------------------------------------------------------
    # Examine state after architecture revision
    # ---------------------------------------------------------

    snapshot = workflow.get_state(
        config
    )

    print(
        "Current status:",
        snapshot.values.get("status"),
    )

    print(
        "Revision count:",
        snapshot.values.get(
            "revision_count",
            0,
        ),
    )

    revision_history = snapshot.values.get(
        "revision_history",
        [],
    )

    print(
        "Review history entries:",
        len(revision_history),
    )

    # ---------------------------------------------------------
    # Optional:
    # Print revised architecture
    # ---------------------------------------------------------

    architecture = snapshot.values.get(
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
    # Optional:
    # Print regenerated implementation plan
    # ---------------------------------------------------------

    implementation_plan = (
        snapshot.values.get(
            "implementation_plan"
        )
    )

    if implementation_plan is not None:
        print()
        print("=" * 70)
        print(
            "Regenerated Implementation Plan"
        )
        print("=" * 70)

        print(
            implementation_plan.model_dump_json(
                indent=2
            )
        )

    # ---------------------------------------------------------
    # SECOND HUMAN DECISION
    #
    # Approve revised architecture + plan.
    # ---------------------------------------------------------

    second_decision = {
        "decision": "approve",
        "comments": (
            "Revised architecture and "
            "implementation plan approved."
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

    # ---------------------------------------------------------
    # Resume SAME thread again
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
        result["status"],
    )

    print(
        "Final Revision Count:",
        result.get(
            "revision_count",
            0,
        ),
    )

    final_history = result.get(
        "revision_history",
        [],
    )

    print(
        "Total Human Reviews:",
        len(final_history),
    )

    # ---------------------------------------------------------
    # Display human review history
    # ---------------------------------------------------------

    if final_history:
        print()
        print("=" * 70)
        print("Human Review History")
        print("=" * 70)

        for index, review in enumerate(
            final_history,
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

            print(
                "Comments:",
                review.comments,
            )

            if review.revision_target:
                print(
                    "Revision Target:",
                    review.revision_target.value,
                )

            if review.requested_changes:
                print(
                    "Requested Changes:"
                )

                for change in (
                    review.requested_changes
                ):
                    print(
                        f"- {change}"
                    )


if __name__ == "__main__":
    main()