from devpilot.config.retry import MAX_RETRIES
from devpilot.graph.state import DevPilotState
from devpilot.models.errors import RecoveryStatus
from devpilot.models.evaluation import EvaluationVerdict
from devpilot.models.review import (
    ReviewDecision,
    RevisionTarget,
)


MAX_REVISIONS = 3


# ============================================================
# Requirement Routing
# ============================================================

def route_after_requirement_analysis(
    state: DevPilotState,
) -> str:
    analysis = state[
        "requirement_analysis"
    ]

    if analysis.is_actionable:
        return "proceed"

    return "clarification"


# ============================================================
# Human Review Routing
# ============================================================

def route_after_human_review(
    state: DevPilotState,
) -> str:
    review = state[
        "human_review"
    ]

    if (
        review.decision
        == ReviewDecision.APPROVE
    ):
        return "approved"

    if (
        review.decision
        == ReviewDecision.REVISE
    ):
        return "revise"

    return "rejected"


# ============================================================
# Human Revision Routing
# ============================================================

def route_revision_target(
    state: DevPilotState,
) -> str:
    revision_count = state.get(
        "revision_count",
        0,
    )

    if revision_count > MAX_REVISIONS:
        return "limit_reached"

    review = state[
        "human_review"
    ]

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


# ============================================================
# Repository Failure / Recovery Routing
# ============================================================

def route_after_repository_evidence(
    state: DevPilotState,
) -> str:
    status = state.get(
        "status"
    )

    # --------------------------------------------------------
    # Repository collection succeeded
    # --------------------------------------------------------

    if (
        status
        == "repository_evidence_collected"
    ):
        return "success"

    # --------------------------------------------------------
    # Normalize recovery status
    #
    # Depending on graph/checkpoint state, this may
    # be either the enum or its string representation.
    # --------------------------------------------------------

    recovery_status = state.get(
        "recovery_status"
    )

    if isinstance(
        recovery_status,
        RecoveryStatus,
    ):
        recovery_value = (
            recovery_status.value
        )
    else:
        recovery_value = (
            recovery_status
        )

    failed_node = state.get(
        "failed_node",
        "collect_repository_evidence",
    )

    retry_counts = state.get(
        "retry_counts",
        {},
    )

    attempts = retry_counts.get(
        failed_node,
        0,
    )

    # --------------------------------------------------------
    # Transient failure
    #
    # Initial attempt + MAX_RETRIES.
    #
    # MAX_RETRIES = 2 means:
    #
    # Attempt 1 -> retry
    # Attempt 2 -> retry
    # Attempt 3 -> retry exhausted
    # --------------------------------------------------------

    if (
        recovery_value
        == RecoveryStatus.RETRYING.value
    ):
        if attempts <= MAX_RETRIES:
            return "retry"

        return "retry_exhausted"

    # --------------------------------------------------------
    # Recoverable failure requiring human intervention
    # --------------------------------------------------------

    if (
        recovery_value
        == RecoveryStatus.HUMAN_REQUIRED.value
    ):
        return "human"

    # --------------------------------------------------------
    # Unrecoverable / unknown failure
    # --------------------------------------------------------

    return "fatal"


# ============================================================
# Evaluation Routing
# ============================================================

def route_after_evaluation(
    state: DevPilotState,
) -> str:
    evaluation = state[
        "evaluation_result"
    ]

    if (
        evaluation.verdict
        == EvaluationVerdict.PASS
    ):
        return "pass"

    if (
        evaluation.verdict
        == EvaluationVerdict.REVISE
    ):
        return "revise"

    return "escalate"