from devpilot.graph.state import DevPilotState

from devpilot.models.review import (
    ReviewDecision,
    RevisionTarget,
)

MAX_REVISIONS = 3

def route_after_requirement_analysis(
    state: DevPilotState,
) -> str:
    analysis = state["requirement_analysis"]

    if analysis.is_actionable:
        return "proceed"

    return "clarification"

def route_after_human_review(
    state: DevPilotState,
) -> str:
    review = state["human_review"]

    if review.decision == ReviewDecision.APPROVE:
        return "approved"

    if review.decision == ReviewDecision.REVISE:
        return "revise"

    return "rejected"

def route_revision_target(
    state: DevPilotState,
) -> str:
    if state.get("revision_count", 0) > MAX_REVISIONS:
        return "limit_reached"

    review = state["human_review"]

    if (
        review.revision_target
        == RevisionTarget.ARCHITECTURE
    ):
        return "architecture"

    if (
        review.revision_target
        == RevisionTarget.IMPLEMENTATION_PLAN
    ):
        return "implementation_plan"

    return "invalid"