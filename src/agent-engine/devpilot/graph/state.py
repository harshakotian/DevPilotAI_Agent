from typing import TypedDict

from devpilot.models.architecture import (
    ArchitectureProposal,
)
from devpilot.models.evaluation import (
    EvaluationResult,
)
from devpilot.models.errors import (
    ErrorRecord,
    RecoveryStatus,
)
from devpilot.models.implementation import (
    ImplementationPlan,
)
from devpilot.models.repository import (
    RepositoryAnalysis,
    RepositoryEvidence,
    RepositorySummary,
)
from devpilot.models.requirement import (
    RequirementAnalysis,
)
from devpilot.models.review import (
    HumanReviewResult,
)
from devpilot.models.security import (
    SecurityReview,
)
from devpilot.models.testing import (
    TestReview,
)


class DevPilotState(
    TypedDict,
    total=False,
):
    # ---------------------------------------------------------
    # Input
    # ---------------------------------------------------------
    requirement: str
    repository_path: str

    # ---------------------------------------------------------
    # Requirement Analysis
    # ---------------------------------------------------------
    requirement_analysis: RequirementAnalysis

    # ---------------------------------------------------------
    # Repository Intelligence
    # ---------------------------------------------------------
    repository_summary: RepositorySummary
    repository_evidence: RepositoryEvidence
    repository_analysis: RepositoryAnalysis

    # ---------------------------------------------------------
    # Architecture + Planning
    # ---------------------------------------------------------
    architecture_proposal: ArchitectureProposal
    implementation_plan: ImplementationPlan

    # ---------------------------------------------------------
    # Human Review
    # ---------------------------------------------------------
    human_review: HumanReviewResult
    revision_count: int
    revision_history: list[HumanReviewResult]

    # ---------------------------------------------------------
    # Specialist Reviews
    # ---------------------------------------------------------
    security_review: SecurityReview
    test_review: TestReview

    # ---------------------------------------------------------
    # Evaluation
    # ---------------------------------------------------------
    evaluation_result: EvaluationResult

    # ---------------------------------------------------------
    # Failure / Recovery State
    # ---------------------------------------------------------
    error_records: list[ErrorRecord]

    retry_counts: dict[str, int]

    recovery_status: RecoveryStatus

    failed_node: str

    # ---------------------------------------------------------
    # Failure Simulation
    # Used only for controlled resilience testing.
    # ---------------------------------------------------------
    simulate_repository_timeout_once: bool

    simulate_repository_timeout_always: bool

    # ---------------------------------------------------------
    # Workflow Status
    # ---------------------------------------------------------
    status: str