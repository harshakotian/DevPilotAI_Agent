from devpilot.graph.state import DevPilotState


def route_after_requirement_analysis(
    state: DevPilotState,
) -> str:
    analysis = state["requirement_analysis"]

    if analysis.is_actionable:
        return "proceed"

    return "clarification"