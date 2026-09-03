from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from devpilot.graph.nodes import (
    evaluate_proposal,
    evaluation_escalated,
    evaluation_passed,
    evaluation_revision_required,
    receive_requirement,
    repository_recovery_required,
    validate_requirement,
    analyze_requirement,
    request_clarification,
    collect_repository_evidence,
    retry_exhausted,
    analyze_repository,
    design_architecture,
    create_implementation_plan,
    human_review,
    approval_completed,
    review_rejected,
    prepare_revision,
    revision_limit_reached,
    perform_security_review,
    perform_test_review,
    specialist_reviews_completed,
    workflow_failed,
)

from devpilot.graph.routing import (
    route_after_evaluation,
    route_after_requirement_analysis,
    route_after_human_review,
    route_after_repository_evidence,
    route_revision_target,
)

from devpilot.graph.state import DevPilotState


def build_workflow():
    # ---------------------------------------------------------
    # Checkpointer
    # ---------------------------------------------------------
    # For MVP we use in-memory persistence.
    # Later this can be replaced with SQLite/PostgreSQL.
    checkpointer = InMemorySaver()

    # ---------------------------------------------------------
    # Create Graph
    # ---------------------------------------------------------
    workflow = StateGraph(DevPilotState)

    # ---------------------------------------------------------
    # Register Nodes
    # ---------------------------------------------------------

    workflow.add_node(
        "receive_requirement",
        receive_requirement,
    )

    workflow.add_node(
        "validate_requirement",
        validate_requirement,
    )

    workflow.add_node(
        "analyze_requirement",
        analyze_requirement,
    )

    workflow.add_node(
        "request_clarification",
        request_clarification,
    )

    workflow.add_node(
        "collect_repository_evidence",
        collect_repository_evidence,
    )

    workflow.add_node(
        "retry_exhausted",
        retry_exhausted,
    )

    workflow.add_node(
        "repository_recovery_required",
        repository_recovery_required,
    )

    workflow.add_node(
        "workflow_failed",
        workflow_failed,
    )
    workflow.add_node(
        "analyze_repository",
        analyze_repository,
    )

    workflow.add_node(
        "design_architecture",
        design_architecture,
    )

    workflow.add_node(
        "create_implementation_plan",
        create_implementation_plan,
    )

    workflow.add_node(
        "human_review",
        human_review,
    )

    workflow.add_node(
        "approval_completed",
        approval_completed,
    )

    workflow.add_node(
        "perform_security_review",
        perform_security_review,
    )

    workflow.add_node(
        "perform_test_review",
        perform_test_review,
    )

    workflow.add_node(
        "specialist_reviews_completed",
        specialist_reviews_completed,
    )

    workflow.add_node(
        "review_rejected",
        review_rejected,
    )

    workflow.add_node(
        "prepare_revision",
        prepare_revision,
    )

    workflow.add_node(
        "revision_limit_reached",
        revision_limit_reached,
    )

    workflow.add_node(
        "evaluate_proposal",
        evaluate_proposal,
    )

    workflow.add_node(
        "evaluation_passed",
        evaluation_passed,
    )

    workflow.add_node(
        "evaluation_revision_required",
        evaluation_revision_required,
    )

    workflow.add_node(
        "evaluation_escalated",
        evaluation_escalated,
    )
    
    # ---------------------------------------------------------
    # Initial Workflow
    # ---------------------------------------------------------

    workflow.add_edge(
        START,
        "receive_requirement",
    )

    workflow.add_edge(
        "receive_requirement",
        "validate_requirement",
    )

    workflow.add_edge(
        "validate_requirement",
        "analyze_requirement",
    )

    # ---------------------------------------------------------
    # Conditional Routing - Requirement Analysis
    # ---------------------------------------------------------

    workflow.add_conditional_edges(
        "analyze_requirement",
        route_after_requirement_analysis,
        {
            "proceed": "collect_repository_evidence",
            "clarification": "request_clarification",
        },
    )

    # ---------------------------------------------------------
    # Clarification Path
    # ---------------------------------------------------------

    workflow.add_edge(
        "request_clarification",
        END,
    )

    # ---------------------------------------------------------
    # Repository Intelligence Path
    # ---------------------------------------------------------

    workflow.add_conditional_edges(
        "collect_repository_evidence",
        route_after_repository_evidence,
        {
            "success": "analyze_repository",
            "retry": "collect_repository_evidence",
            "retry_exhausted": "retry_exhausted",
            "human": "repository_recovery_required",
            "fatal": "workflow_failed",
        },
    )

    workflow.add_edge(
        "workflow_failed",
        END,
    )

    workflow.add_edge(
        "repository_recovery_required",
        "collect_repository_evidence",
    )

    workflow.add_edge(
        "retry_exhausted",
        END,
    )
    
    workflow.add_edge(
        "analyze_repository",
        "design_architecture",
    )

    # ---------------------------------------------------------
    # Architecture -> Implementation Planning
    # ---------------------------------------------------------

    workflow.add_edge(
        "design_architecture",
        "create_implementation_plan",
    )

    # ---------------------------------------------------------
    # Implementation Plan -> Human Review
    # ---------------------------------------------------------

    workflow.add_edge(
        "create_implementation_plan",
        "human_review",
    )

    # ---------------------------------------------------------
    # Human Review Decision Routing
    # ---------------------------------------------------------

    workflow.add_conditional_edges(
        "human_review",
        route_after_human_review,
        {
            "approved": "approval_completed",
            "rejected": "review_rejected",
            "revise": "prepare_revision",
        },
    )

    # ---------------------------------------------------------
    # Approved Path
    # ---------------------------------------------------------

    # workflow.add_edge(
    #     "approval_completed",
    #     END,
    # )

    # ---------------------------------------------------------
    # Fan-Out Path for Specialist Reviews (Security & Testing)
    # ---------------------------------------------------------
    
    workflow.add_edge(
        "approval_completed",
        "perform_security_review",
    )

    workflow.add_edge(
        "approval_completed",
        "perform_test_review",
    )

    # ---------------------------------------------------------
    # Fan-In Path for Specialist Reviews (Security & Testing)
    # ---------------------------------------------------------
    
    workflow.add_edge(
        [
            "perform_security_review",
            "perform_test_review",
        ],
        "specialist_reviews_completed",
    )

    workflow.add_edge(
        "specialist_reviews_completed",
        "evaluate_proposal",
    )

    workflow.add_conditional_edges(
        "evaluate_proposal",
        route_after_evaluation,
        {
            "pass": "evaluation_passed",
            "revise": "evaluation_revision_required",
            "escalate": "evaluation_escalated",
        },
    )

    workflow.add_edge(
        "evaluation_passed",
        END,
    )

    workflow.add_edge(
        "evaluation_revision_required",
        END,
    )

    workflow.add_edge(
        "evaluation_escalated",
        END,
    )
    # ---------------------------------------------------------
    # Rejected Path
    # ---------------------------------------------------------

    workflow.add_edge(
        "review_rejected",
        END,
    )

    # ---------------------------------------------------------
    # Revision Routing
    # ---------------------------------------------------------
    #
    # If architecture needs revision:
    #
    # prepare_revision
    #       ↓
    # design_architecture
    #       ↓
    # create_implementation_plan
    #       ↓
    # human_review
    #
    # If only implementation plan needs revision:
    #
    # prepare_revision
    #       ↓
    # create_implementation_plan
    #       ↓
    # human_review
    #

    workflow.add_conditional_edges(
        "prepare_revision",
        route_revision_target,
        {
            "architecture": "design_architecture",
            "implementation_plan": (
                "create_implementation_plan"
            ),
            "invalid": "review_rejected",
            "limit_reached": "revision_limit_reached",
        },
    )

    workflow.add_edge(
        "revision_limit_reached",
        END,
    )

    # ---------------------------------------------------------
    # Compile Workflow
    # ---------------------------------------------------------

    return workflow.compile(
        checkpointer=checkpointer
    )