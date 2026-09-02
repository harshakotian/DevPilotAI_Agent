from enum import Enum

from pydantic import BaseModel, Field


class EvaluationVerdict(str, Enum):
    PASS = "pass"
    REVISE = "revise"
    ESCALATE = "escalate"


class EvaluationIssue(BaseModel):
    title: str = Field(
        description="Short description of the quality issue."
    )

    source: str = Field(
        description=(
            "Artifact responsible for or exposing the issue, "
            "such as architecture, implementation_plan, "
            "security_review, or test_review."
        )
    )

    severity: str = Field(
        description="Issue severity: low, medium, high, or critical."
    )

    description: str = Field(
        description="Explanation of the issue."
    )

    recommendation: str = Field(
        description="Recommended corrective action."
    )

    blocks_progress: bool = Field(
        default=False,
        description=(
            "Whether the issue prevents the proposal from progressing."
        ),
    )


class EvaluationScore(BaseModel):
    requirement_alignment: int = Field(
        ge=0,
        le=100,
        description=(
            "How well the proposal satisfies the original requirement."
        ),
    )

    architectural_quality: int = Field(
        ge=0,
        le=100,
    )

    implementation_readiness: int = Field(
        ge=0,
        le=100,
    )

    security_readiness: int = Field(
        ge=0,
        le=100,
    )

    test_readiness: int = Field(
        ge=0,
        le=100,
    )


class EvaluationResult(BaseModel):
    summary: str

    verdict: EvaluationVerdict

    scores: EvaluationScore

    issues: list[EvaluationIssue] = Field(
        default_factory=list
    )

    strengths: list[str] = Field(
        default_factory=list
    )

    required_revisions: list[str] = Field(
        default_factory=list
    )

    escalation_reasons: list[str] = Field(
        default_factory=list
    )

    implementation_ready: bool

    confidence: str = Field(
        description="Evaluation confidence: low, medium, or high."
    )