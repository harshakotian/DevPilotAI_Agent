from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from devpilot.graph.nodes import (
    receive_requirement,
    validate_requirement,
    analyze_requirement,
    request_clarification,
    collect_repository_evidence,
    analyze_repository,
    design_architecture,
    create_implementation_plan,
    human_review,
    approval_completed,
    review_rejected,
    prepare_revision,
    revision_limit_reached,
)

from devpilot.graph.routing import (
    route_after_requirement_analysis,
    route_after_human_review,
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

    workflow.add_edge(
        "collect_repository_evidence",
        "analyze_repository",
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

    workflow.add_edge(
        "approval_completed",
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