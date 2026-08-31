from pydantic import BaseModel, Field


class ArchitectureComponentChange(BaseModel):
    component: str = Field(
        description="Component or architectural area affected."
    )

    current_state: str = Field(
        description="What repository evidence indicates exists today."
    )

    proposed_change: str = Field(
        description="Architectural change being proposed."
    )

    rationale: str = Field(
        description="Why this change is needed."
    )


class ArchitectureDecision(BaseModel):
    decision: str = Field(
        description="Architecture decision being proposed."
    )

    rationale: str = Field(
        description="Reason for the decision."
    )

    alternatives_considered: list[str] = Field(
        default_factory=list,
        description="Reasonable alternative approaches considered."
    )

    tradeoffs: list[str] = Field(
        default_factory=list,
        description="Important advantages or disadvantages of this decision."
    )


class ArchitectureProposal(BaseModel):
    summary: str = Field(
        description="Concise summary of the proposed architecture."
    )

    current_architecture: str = Field(
        description="Current architecture as established from repository analysis."
    )

    target_architecture: str = Field(
        description="Target architecture after implementing the requirement."
    )

    component_changes: list[ArchitectureComponentChange] = Field(
        default_factory=list
    )

    decisions: list[ArchitectureDecision] = Field(
        default_factory=list
    )

    new_dependencies: list[str] = Field(
        default_factory=list,
        description="New logical or technical dependencies likely required."
    )

    configuration_changes: list[str] = Field(
        default_factory=list,
        description="Likely configuration changes."
    )

    operational_considerations: list[str] = Field(
        default_factory=list
    )

    risks: list[str] = Field(
        default_factory=list
    )

    assumptions: list[str] = Field(
        default_factory=list
    )

    unresolved_questions: list[str] = Field(
        default_factory=list
    )

    repository_evidence_references: list[str] = Field(
        default_factory=list,
        description="Repository paths supporting the proposal."
    )

    confidence: str = Field(
        description="Overall architectural confidence: low, medium, or high."
    )