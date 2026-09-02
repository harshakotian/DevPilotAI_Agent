from enum import Enum

from pydantic import BaseModel, Field


class SecuritySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityFinding(BaseModel):
    title: str = Field(
        description="Short title describing the security concern."
    )

    severity: SecuritySeverity = Field(
        description="Security severity."
    )

    category: str = Field(
        description=(
            "Security category such as secrets, authentication, "
            "authorization, data exposure, configuration, "
            "availability, dependency risk, or logging."
        )
    )

    description: str = Field(
        description="Explanation of the identified security concern."
    )

    evidence: list[str] = Field(
        default_factory=list,
        description=(
            "Requirement, repository, architecture, or plan evidence "
            "supporting the finding."
        ),
    )

    impact: str = Field(
        description="Potential consequence if the issue is not addressed."
    )

    recommendation: str = Field(
        description="Recommended mitigation or security control."
    )

    blocks_implementation: bool = Field(
        default=False,
        description=(
            "Whether this finding should block implementation "
            "until resolved."
        ),
    )


class SecurityReview(BaseModel):
    summary: str = Field(
        description="Overall security assessment."
    )

    findings: list[SecurityFinding] = Field(
        default_factory=list
    )

    positive_controls: list[str] = Field(
        default_factory=list,
        description=(
            "Security-positive architecture or planning decisions already present."
        ),
    )

    missing_information: list[str] = Field(
        default_factory=list,
        description=(
            "Security-relevant information that is unavailable "
            "or requires clarification."
        ),
    )

    overall_risk: SecuritySeverity = Field(
        description="Overall security risk level."
    )

    implementation_blocked: bool = Field(
        description=(
            "Whether unresolved security concerns should block implementation."
        )
    )

    confidence: str = Field(
        description="Review confidence: low, medium, or high."
    )