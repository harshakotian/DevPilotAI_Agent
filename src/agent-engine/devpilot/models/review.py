from enum import Enum

from pydantic import BaseModel, Field


class ReviewDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REVISE = "revise"


class RevisionTarget(str, Enum):
    ARCHITECTURE = "architecture"
    IMPLEMENTATION_PLAN = "implementation_plan"


class HumanReviewResult(BaseModel):
    decision: ReviewDecision

    comments: str = Field(
        default="",
        description="Human reviewer comments."
    )

    requested_changes: list[str] = Field(
        default_factory=list,
        description="Specific changes requested by the reviewer."
    )

    revision_target: RevisionTarget | None = Field(
        default=None,
        description=(
            "Which artifact should be revised when decision is revise."
        ),
    )