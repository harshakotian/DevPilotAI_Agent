from pydantic import BaseModel, Field


class ImplementationStep(BaseModel):
    order: int = Field(
        description="Execution order of this implementation step."
    )

    title: str = Field(
        description="Short descriptive title for the step."
    )

    objective: str = Field(
        description="What this step is intended to accomplish."
    )

    affected_files: list[str] = Field(
        default_factory=list,
        description="Existing or expected files likely affected by this step."
    )

    actions: list[str] = Field(
        default_factory=list,
        description="Concrete implementation actions to perform."
    )

    dependencies: list[str] = Field(
        default_factory=list,
        description="Prerequisites that must exist before this step."
    )

    validation: list[str] = Field(
        default_factory=list,
        description="Checks that confirm this step was implemented correctly."
    )


class TestPlanItem(BaseModel):
    test_type: str = Field(
        description="Type of test, such as unit, integration, or manual."
    )

    target: str = Field(
        description="What behavior or component should be tested."
    )

    scenarios: list[str] = Field(
        default_factory=list
    )

    expected_result: str = Field(
        description="Expected successful outcome."
    )


class ImplementationPlan(BaseModel):
    summary: str = Field(
        description="Overall implementation strategy."
    )

    prerequisites: list[str] = Field(
        default_factory=list,
        description="Conditions or dependencies required before implementation starts."
    )

    package_changes: list[str] = Field(
        default_factory=list,
        description="Packages, libraries, or dependencies likely to be added or changed."
    )

    configuration_changes: list[str] = Field(
        default_factory=list,
        description="Configuration changes required by the implementation."
    )

    steps: list[ImplementationStep] = Field(
        default_factory=list,
        description="Ordered implementation steps."
    )

    test_plan: list[TestPlanItem] = Field(
        default_factory=list,
        description="Testing required to validate the change."
    )

    verification_criteria: list[str] = Field(
        default_factory=list,
        description="End-to-end criteria proving the requirement has been satisfied."
    )

    rollback_considerations: list[str] = Field(
        default_factory=list,
        description="Considerations for safely reverting the implementation."
    )

    risks: list[str] = Field(
        default_factory=list
    )

    unresolved_questions: list[str] = Field(
        default_factory=list
    )

    confidence: str = Field(
        description="Overall planning confidence: low, medium, or high."
    )