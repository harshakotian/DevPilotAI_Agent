from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from devpilot.graph.nodes import (
    receive_requirement,
    validate_requirement,
    analyze_requirement,
    request_clarification,
    collect_repository_evidence,
    analyze_repository,
    design_architecture,
    create_implementation_plan,
)

from devpilot.graph.routing import (
    route_after_requirement_analysis,
)

from devpilot.graph.state import DevPilotState

def build_workflow():
    workflow = StateGraph(
        DevPilotState
    )

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

    # ---------------------------------------------------------
    # Start of Workflow
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
    # Conditional Routing
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
    # Engineering Analysis Path
    # ---------------------------------------------------------

    workflow.add_edge(
        "collect_repository_evidence",
        "analyze_repository",
    )
    
    workflow.add_edge(
        "analyze_repository",
        "design_architecture",
    )

    workflow.add_edge(
        "design_architecture",
        "create_implementation_plan",
    )

    workflow.add_edge(
        "create_implementation_plan",
        END,
    )

    # ---------------------------------------------------------
    # Compile Graph
    # ---------------------------------------------------------

    return workflow.compile()