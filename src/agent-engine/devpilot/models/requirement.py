from pydantic import BaseModel, Field


class RequirementAnalysis(BaseModel):
    summary: str = Field(
        description="Concise summary of the requested change."
    )

    engineering_goal: str = Field(
        description="The technical or business outcome the requirement is trying to achieve."
    )

    affected_areas: list[str] = Field(
        default_factory=list,
        description="Likely application, infrastructure, data, or operational areas affected."
    )

    explicit_constraints: list[str] = Field(
        default_factory=list,
        description="Constraints explicitly stated in the original requirement."
    )

    assumptions: list[str] = Field(
        default_factory=list,
        description="Assumptions made because required information is missing."
    )

    clarification_questions: list[str] = Field(
        default_factory=list,
        description="Questions that should be answered before implementation."
    )

    risks: list[str] = Field(
        default_factory=list,
        description="Potential implementation or operational risks visible from the requirement alone."
    )

    is_actionable: bool = Field(
        description="Whether the requirement contains enough information to proceed with engineering analysis."
    )