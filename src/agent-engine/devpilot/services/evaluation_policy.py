from devpilot.models.evaluation import (
    EvaluationResult,
    EvaluationVerdict,
)
from devpilot.models.security import SecurityReview
from devpilot.models.testing import TestReview


def enforce_evaluation_policy(
    evaluation: EvaluationResult,
    security_review: SecurityReview,
    test_review: TestReview,
) -> EvaluationResult:
    blocked = (
        security_review.implementation_blocked
        or test_review.implementation_blocked
    )

    if (
        blocked
        and evaluation.verdict
        == EvaluationVerdict.PASS
    ):
        evaluation.verdict = (
            EvaluationVerdict.REVISE
        )

        evaluation.implementation_ready = False

        evaluation.required_revisions.append(
            "Resolve specialist review blockers "
            "before implementation can proceed."
        )

    if (
        evaluation.verdict
        != EvaluationVerdict.PASS
    ):
        evaluation.implementation_ready = False

    return evaluation