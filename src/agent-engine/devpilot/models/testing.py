from enum import Enum

from pydantic import BaseModel, Field


class TestPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestScenario(BaseModel):
    title: str = Field(
        description="Short description of the test scenario."
    )

    test_type: str = Field(
        description=(
            "Type of test such as unit, integration, "
            "contract, resilience, performance, or manual."
        )
    )

    priority: TestPriority = Field(
        description="Priority of the test scenario."
    )

    target: str = Field(
        description="Component or behavior being tested."
    )

    preconditions: list[str] = Field(
        default_factory=list
    )

    steps: list[str] = Field(
        default_factory=list
    )

    expected_result: str = Field(
        description="Expected successful outcome."
    )

    failure_condition: str = Field(
        default="",
        description=(
            "What would indicate the test has failed."
        )
    )

    evidence: list[str] = Field(
        default_factory=list,
        description=(
            "Requirement, architecture, repository, or plan "
            "evidence motivating this test."
        ),
    )


class TestReview(BaseModel):
    summary: str = Field(
        description="Overall testing assessment."
    )

    scenarios: list[TestScenario] = Field(
        default_factory=list
    )

    coverage_gaps: list[str] = Field(
        default_factory=list,
        description=(
            "Important behavior not adequately covered "
            "by the implementation plan."
        ),
    )

    regression_areas: list[str] = Field(
        default_factory=list,
        description=(
            "Existing areas that could regress because "
            "of the proposed change."
        ),
    )

    non_functional_tests: list[str] = Field(
        default_factory=list,
        description=(
            "Performance, resilience, availability, "
            "security-adjacent, or operational tests."
        ),
    )

    implementation_blocked: bool = Field(
        description=(
            "Whether testing gaps are serious enough "
            "to block implementation."
        )
    )

    confidence: str = Field(
        description="Review confidence: low, medium, or high."
    )