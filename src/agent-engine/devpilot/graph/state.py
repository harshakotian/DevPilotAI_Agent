from typing import TypedDict

from devpilot.models.architecture import ArchitectureProposal
from devpilot.models.implementation import ImplementationPlan
from devpilot.models.repository import (
    RepositoryAnalysis,
    RepositoryEvidence,
    RepositorySummary,
)
from devpilot.models.requirement import RequirementAnalysis
from devpilot.models.review import HumanReviewResult
from devpilot.models.security import SecurityReview
from devpilot.models.testing import TestReview
from devpilot.models.evaluation import (
    EvaluationResult,
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

    human_review: HumanReviewResult
    revision_count: int
    revision_history: list[HumanReviewResult]

    security_review: SecurityReview
    test_review: TestReview
    
    evaluation_result: EvaluationResult

    status: str
    errors: list[str]