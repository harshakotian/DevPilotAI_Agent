from typing import TypedDict

from devpilot.models.requirement import RequirementAnalysis
from devpilot.models.repository import (
    RepositorySummary,
    RepositoryEvidence,
    RepositoryAnalysis,
)
from devpilot.models.architecture import (
    ArchitectureProposal,
)
from devpilot.models.implementation import (
    ImplementationPlan,
)

class DevPilotState(TypedDict, total=False):
    requirement: str
    repository_path: str

    requirement_analysis: RequirementAnalysis

    repository_summary: RepositorySummary
    repository_evidence: RepositoryEvidence
    repository_analysis: RepositoryAnalysis

    architecture_proposal: ArchitectureProposal
    implementation_plan: ImplementationPlan

    status: str
    errors: list[str]