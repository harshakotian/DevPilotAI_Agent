from langgraph.types import interrupt

from devpilot.agents.architect_agent import ArchitectAgent
from devpilot.agents.evaluator_agent import EvaluatorAgent
from devpilot.agents.planning_agent import ImplementationPlanningAgent
from devpilot.agents.repository_agent import RepositoryAnalyst
from devpilot.agents.requirement_agent import RequirementAnalyst
from devpilot.agents.security_agent import SecurityReviewAgent
from devpilot.agents.testing_agent import TestStrategyAgent

from devpilot.config.failure_simulation import (
    SIMULATE_REPOSITORY_TIMEOUT_ALWAYS,
    SIMULATE_REPOSITORY_TIMEOUT_ONCE,
)
from devpilot.config.retry import MAX_RETRIES

from devpilot.graph.state import DevPilotState

from devpilot.models.errors import RecoveryStatus
from devpilot.models.review import HumanReviewResult

from devpilot.services.evaluation_policy import (
    enforce_evaluation_policy,
)
from devpilot.services.failure_simulator import (
    failure_simulator,
)
from devpilot.services.llm_factory import create_llm_service
from devpilot.services.recovery_policy import (
    determine_recovery_status,
)
from devpilot.services.repository_evidence_service import (
    RepositoryEvidenceService,
)
from devpilot.services.retry_service import (
    get_next_attempt,
    mark_attempt,
    reset_attempts,
)
from devpilot.services.safe_executor import (
    execute_safely,
)


# ============================================================
# Requirement
# ============================================================


def receive_requirement(
    state: DevPilotState,
) -> DevPilotState:
    requirement = state["requirement"]

    print()
    print(
        f"Received requirement: {requirement}"
    )

    return {
        "status": "requirement_received",
    }


def validate_requirement(
    state: DevPilotState,
) -> DevPilotState:
    requirement = state["requirement"]

    if not requirement.strip():
        raise ValueError(
            "Requirement cannot be empty."
        )

    print()
    print("Requirement validated.")

    return {
        "status": "requirement_validated",
    }


def analyze_requirement(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print("Running Requirement Analyst...")

    llm_service = create_llm_service()

    analyst = RequirementAnalyst(
        llm_service=llm_service
    )

    analysis = analyst.analyze(
        state["requirement"]
    )

    print(
        "Requirement analysis complete."
    )

    return {
        "requirement_analysis": analysis,
        "status": "requirement_analyzed",
    }


def request_clarification(
    state: DevPilotState,
) -> DevPilotState:
    analysis = state[
        "requirement_analysis"
    ]

    print()
    print(
        "Requirement needs clarification."
    )

    print(
        "Clarification questions:"
    )

    for question in (
        analysis.clarification_questions
    ):
        print(
            f"- {question}"
        )

    return {
        "status": "needs_clarification",
    }


# ============================================================
# Repository Evidence + Recovery
# ============================================================


def collect_repository_evidence(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Collecting repository evidence..."
    )

    source = (
        "collect_repository_evidence"
    )

    retry_counts = state.get(
        "retry_counts",
        {},
    )

    attempt = get_next_attempt(
        retry_counts=retry_counts,
        source=source,
    )

    repository_path = state[
        "repository_path"
    ]

    evidence_service = (
        RepositoryEvidenceService()
    )

    # Test-state values override normal configuration.
    simulate_once = state.get(
        "simulate_repository_timeout_once",
        SIMULATE_REPOSITORY_TIMEOUT_ONCE,
    )

    simulate_always = state.get(
        "simulate_repository_timeout_always",
        SIMULATE_REPOSITORY_TIMEOUT_ALWAYS,
    )

    def collect_operation():
        failure_simulator.maybe_fail_repository(
            fail_once=simulate_once,
            fail_always=simulate_always,
        )

        return evidence_service.collect(
            repository_path
        )

    execution = execute_safely(
        source=source,
        attempt=attempt,
        operation=collect_operation,
    )

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    if execution.success:
        evidence = execution.value

        if evidence is None:
            raise RuntimeError(
                "Execution succeeded without a value."
            )

        print()
        print(
            "Repository evidence collected."
        )

        updated_retry_counts = (
            reset_attempts(
                retry_counts=retry_counts,
                source=source,
            )
        )

        return {
            "repository_summary": (
                evidence.repository_summary
            ),
            "repository_evidence": evidence,
            "retry_counts": (
                updated_retry_counts
            ),
            "recovery_status": (
                RecoveryStatus.RECOVERED
            ),
            "status": (
                "repository_evidence_collected"
            ),
        }

    # --------------------------------------------------------
    # FAILURE
    # --------------------------------------------------------

    error_record = execution.error

    if error_record is None:
        raise RuntimeError(
            "Execution failed without an error record."
        )

    errors = list(
        state.get(
            "error_records",
            [],
        )
    )

    errors.append(
        error_record
    )

    updated_retry_counts = (
        mark_attempt(
            retry_counts=retry_counts,
            source=source,
            attempt=attempt,
        )
    )

    recovery_status = (
        determine_recovery_status(
            error_record
        )
    )

    print()
    print(
        "Repository evidence collection failed."
    )

    print(
        "Error:",
        error_record.message,
    )

    print(
        "Category:",
        error_record.category.value,
    )

    print(
        "Recovery:",
        recovery_status.value,
    )

    if (
        recovery_status
        == RecoveryStatus.RETRYING
    ):
        total_allowed_attempts = (
            MAX_RETRIES + 1
        )

        print()

        if attempt < total_allowed_attempts:
            print(
                "Automatic retry will be attempted. "
                f"Attempt {attempt} of "
                f"{total_allowed_attempts} failed."
            )
        else:
            print(
                "Final automatic attempt failed. "
                f"Attempt {attempt} of "
                f"{total_allowed_attempts}."
            )

    return {
        "error_records": errors,
        "retry_counts": (
            updated_retry_counts
        ),
        "failed_node": source,
        "recovery_status": (
            recovery_status
        ),
        "status": (
            "repository_evidence_failed"
        ),
    }


def repository_recovery_required(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Repository recovery requires "
        "human intervention."
    )

    latest_error = state[
        "error_records"
    ][-1]

    recovery_payload = {
        "message": (
            "Repository access failed. "
            "Provide a corrected repository "
            "path or reject the workflow."
        ),
        "error": (
            latest_error.model_dump()
        ),
        "current_repository_path": (
            state.get(
                "repository_path"
            )
        ),
    }

    response = interrupt(
        recovery_payload
    )

    action = response.get(
        "action"
    )

    if action == "retry":
        new_path = response.get(
            "repository_path"
        )

        if not new_path:
            return {
                "status": (
                    "repository_recovery_rejected"
                ),
                "recovery_status": (
                    RecoveryStatus.FAILED
                ),
            }

        return {
            "repository_path": new_path,
            "recovery_status": (
                RecoveryStatus.RETRYING
            ),
            "status": (
                "repository_recovery_ready"
            ),
        }

    return {
        "status": (
            "repository_recovery_rejected"
        ),
        "recovery_status": (
            RecoveryStatus.FAILED
        ),
    }


def retry_exhausted(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Automatic retry limit exhausted."
    )

    failed_node = state.get(
        "failed_node",
        "unknown",
    )

    retry_counts = state.get(
        "retry_counts",
        {},
    )

    attempts = retry_counts.get(
        failed_node,
        0,
    )

    print(
        "Failed Node:",
        failed_node,
    )

    print(
        "Total Attempts:",
        attempts,
    )

    return {
        "status": "retry_exhausted",
        "recovery_status": (
            RecoveryStatus.RETRY_EXHAUSTED
        ),
    }


def workflow_failed(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Workflow terminated due to "
        "an unrecoverable failure."
    )

    return {
        "status": "workflow_failed",
        "recovery_status": (
            RecoveryStatus.FAILED
        ),
    }


# ============================================================
# Repository Analysis
# ============================================================


def analyze_repository(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Running Repository Analyst..."
    )

    llm_service = create_llm_service()

    analyst = RepositoryAnalyst(
        llm_service=llm_service
    )

    analysis = analyst.analyze(
        requirement=state[
            "requirement"
        ],
        requirement_analysis=state[
            "requirement_analysis"
        ],
        evidence=state[
            "repository_evidence"
        ],
    )

    print(
        "Repository analysis complete."
    )

    return {
        "repository_analysis": analysis,
        "status": "repository_analyzed",
    }


# ============================================================
# Architecture
# ============================================================


def design_architecture(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Running Architect Agent..."
    )

    llm_service = create_llm_service()

    architect = ArchitectAgent(
        llm_service=llm_service
    )

    revision_feedback = None

    human_review = state.get(
        "human_review"
    )

    if (
        human_review
        and human_review.decision.value
        == "revise"
        and human_review.revision_target
        is not None
        and human_review.revision_target.value
        == "architecture"
    ):
        revision_feedback = "\n".join(
            human_review.requested_changes
        )

    proposal = architect.design(
        requirement=state[
            "requirement"
        ],
        requirement_analysis=state[
            "requirement_analysis"
        ],
        repository_analysis=state[
            "repository_analysis"
        ],
        revision_feedback=(
            revision_feedback
        ),
    )

    print(
        "Architecture proposal complete."
    )

    return {
        "architecture_proposal": proposal,
        "status": "architecture_proposed",
    }


# ============================================================
# Implementation Planning
# ============================================================


def create_implementation_plan(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Running Implementation "
        "Planning Agent..."
    )

    llm_service = create_llm_service()

    planner = (
        ImplementationPlanningAgent(
            llm_service=llm_service
        )
    )

    revision_feedback = None

    human_review = state.get(
        "human_review"
    )

    if (
        human_review
        and human_review.decision.value
        == "revise"
        and human_review.revision_target
        is not None
        and human_review.revision_target.value
        == "implementation_plan"
    ):
        revision_feedback = "\n".join(
            human_review.requested_changes
        )

    plan = planner.plan(
        requirement=state[
            "requirement"
        ],
        requirement_analysis=state[
            "requirement_analysis"
        ],
        repository_analysis=state[
            "repository_analysis"
        ],
        architecture_proposal=state[
            "architecture_proposal"
        ],
        revision_feedback=(
            revision_feedback
        ),
    )

    print(
        "Implementation plan complete."
    )

    return {
        "implementation_plan": plan,
        "status": "implementation_planned",
    }


# ============================================================
# Human Review
# ============================================================


def human_review(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Human review required."
    )

    review_payload = {
        "message": (
            "Review the architecture proposal "
            "and implementation plan."
        ),
        "architecture_proposal": (
            state[
                "architecture_proposal"
            ].model_dump()
        ),
        "implementation_plan": (
            state[
                "implementation_plan"
            ].model_dump()
        ),
        "revision_count": (
            state.get(
                "revision_count",
                0,
            )
        ),
    }

    review_response = interrupt(
        review_payload
    )

    review = (
        HumanReviewResult.model_validate(
            review_response
        )
    )

    history = list(
        state.get(
            "revision_history",
            [],
        )
    )

    history.append(
        review
    )

    print()
    print(
        "Human decision received:",
        review.decision.value,
    )

    return {
        "human_review": review,
        "revision_history": history,
        "status": (
            "human_review_completed"
        ),
    }


def prepare_revision(
    state: DevPilotState,
) -> DevPilotState:
    revision_count = (
        state.get(
            "revision_count",
            0,
        )
        + 1
    )

    print()
    print(
        f"Preparing revision #{revision_count}..."
    )

    return {
        "revision_count": (
            revision_count
        ),
        "status": "revision_prepared",
    }


def approval_completed(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Architecture and implementation "
        "plan approved."
    )

    return {
        "status": "approved",
    }


def review_rejected(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Architecture or implementation "
        "plan rejected."
    )

    return {
        "status": "rejected",
    }


def revision_limit_reached(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Maximum revision limit reached. "
        "Manual intervention required."
    )

    return {
        "status": (
            "revision_limit_reached"
        ),
    }


# ============================================================
# Specialist Reviews
# ============================================================


def perform_security_review(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Running Security Review Agent..."
    )

    llm_service = create_llm_service()

    security_agent = (
        SecurityReviewAgent(
            llm_service=llm_service
        )
    )

    security_review = (
        security_agent.review(
            requirement=state[
                "requirement"
            ],
            requirement_analysis=state[
                "requirement_analysis"
            ],
            repository_analysis=state[
                "repository_analysis"
            ],
            architecture_proposal=state[
                "architecture_proposal"
            ],
            implementation_plan=state[
                "implementation_plan"
            ],
        )
    )

    print(
        "Security review complete."
    )

    return {
        "security_review": (
            security_review
        ),
    }


def perform_test_review(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Running Test Strategy Agent..."
    )

    llm_service = create_llm_service()

    test_agent = TestStrategyAgent(
        llm_service=llm_service
    )

    test_review = test_agent.review(
        requirement=state[
            "requirement"
        ],
        requirement_analysis=state[
            "requirement_analysis"
        ],
        repository_analysis=state[
            "repository_analysis"
        ],
        architecture_proposal=state[
            "architecture_proposal"
        ],
        implementation_plan=state[
            "implementation_plan"
        ],
    )

    print(
        "Test strategy review complete."
    )

    return {
        "test_review": test_review,
    }


def specialist_reviews_completed(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Specialist reviews completed."
    )

    security_review = state.get(
        "security_review"
    )

    test_review = state.get(
        "test_review"
    )

    if security_review is None:
        raise ValueError(
            "Security review is missing."
        )

    if test_review is None:
        raise ValueError(
            "Test review is missing."
        )

    print(
        "Security Risk:",
        security_review.overall_risk.value,
    )

    print(
        "Security Blocked:",
        security_review.implementation_blocked,
    )

    print(
        "Testing Blocked:",
        test_review.implementation_blocked,
    )

    return {
        "status": (
            "specialist_reviews_completed"
        ),
    }


# ============================================================
# Evaluator
# ============================================================


def evaluate_proposal(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Running Evaluator Agent..."
    )

    llm_service = create_llm_service()

    evaluator = EvaluatorAgent(
        llm_service=llm_service
    )

    evaluation = evaluator.evaluate(
        requirement=state[
            "requirement"
        ],
        requirement_analysis=state[
            "requirement_analysis"
        ],
        architecture_proposal=state[
            "architecture_proposal"
        ],
        implementation_plan=state[
            "implementation_plan"
        ],
        security_review=state[
            "security_review"
        ],
        test_review=state[
            "test_review"
        ],
    )

    # Deterministic policy guard.
    evaluation = enforce_evaluation_policy(
        evaluation=evaluation,
        security_review=state[
            "security_review"
        ],
        test_review=state[
            "test_review"
        ],
    )

    print(
        "Evaluation complete."
    )

    print(
        "Verdict:",
        evaluation.verdict.value,
    )

    print(
        "Implementation Ready:",
        evaluation.implementation_ready,
    )

    return {
        "evaluation_result": evaluation,
        "status": "proposal_evaluated",
    }


def evaluation_passed(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Quality gate passed."
    )

    return {
        "status": (
            "quality_gate_passed"
        ),
    }


def evaluation_revision_required(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Quality gate requires revision."
    )

    return {
        "status": (
            "quality_revision_required"
        ),
    }


def evaluation_escalated(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Quality gate requires "
        "human escalation."
    )

    return {
        "status": (
            "quality_escalated"
        ),
    }