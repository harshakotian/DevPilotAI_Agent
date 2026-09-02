from devpilot.agents.requirement_agent import RequirementAnalyst
from devpilot.graph.state import DevPilotState
from devpilot.services.llm_factory import create_llm_service
from devpilot.tools.repository_scanner import (
    scan_repository,
)
from devpilot.agents.repository_agent import RepositoryAnalyst
from devpilot.services.repository_evidence_service import (
    RepositoryEvidenceService,
)
from devpilot.agents.architect_agent import (
    ArchitectAgent,
)
from devpilot.agents.planning_agent import (
    ImplementationPlanningAgent,
)
from langgraph.types import interrupt
from devpilot.models.review import (
    HumanReviewResult,
)
from devpilot.agents.security_agent import SecurityReviewAgent
from devpilot.agents.testing_agent import TestStrategyAgent
from devpilot.agents.evaluator_agent import (
    EvaluatorAgent,
)
from devpilot.services.evaluation_policy import (
    enforce_evaluation_policy,
)
def receive_requirement(
    state: DevPilotState,
) -> DevPilotState:
    requirement = state["requirement"]

    print(
        f"Received requirement: {requirement}"
    )

    return {
        **state,
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

    print("Requirement validated.")

    return {
        **state,
        "status": "requirement_validated",
    }


def analyze_requirement(
    state: DevPilotState,
) -> DevPilotState:
    print(
        "Running Requirement Analyst..."
    )

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
        **state,
        "requirement_analysis": analysis,
        "status": "requirement_analyzed",
    }

def request_clarification(
    state: DevPilotState,
) -> DevPilotState:
    analysis = state["requirement_analysis"]

    print()
    print("Requirement needs clarification.")

    print("Clarification questions:")

    for question in analysis.clarification_questions:
        print(f"- {question}")

    return {
        **state,
        "status": "needs_clarification",
    }

def scan_repository_node(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print("Scanning repository...")

    repository_path = state[
        "repository_path"
    ]

    summary = scan_repository(
        repository_path
    )

    print(
        f"Repository scan complete. "
        f"Files found: {summary.total_files}"
    )

    return {
        **state,
        "repository_summary": summary,
        "status": "repository_scanned",
    }

def collect_repository_evidence(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print("Collecting repository evidence...")

    repository_path = state["repository_path"]

    evidence_service = RepositoryEvidenceService()

    evidence = evidence_service.collect(
        repository_path
    )

    print("Repository evidence collected.")

    return {
        **state,
        "repository_summary": evidence.repository_summary,
        "repository_evidence": evidence,
        "status": "repository_evidence_collected",
    }

def analyze_repository(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print("Running Repository Analyst...")

    llm_service = create_llm_service()

    analyst = RepositoryAnalyst(
        llm_service=llm_service
    )

    analysis = analyst.analyze(
        requirement=state["requirement"],
        requirement_analysis=state[
            "requirement_analysis"
        ],
        evidence=state[
            "repository_evidence"
        ],
    )

    print("Repository analysis complete.")

    return {
        **state,
        "repository_analysis": analysis,
        "status": "repository_analyzed",
    }

def design_architecture(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print("Running Architect Agent...")

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
        and human_review.decision.value == "revise"
        and human_review.revision_target is not None
        and human_review.revision_target.value
        == "architecture"
    ):
        revision_feedback = "\n".join(
            human_review.requested_changes
        )

    proposal = architect.design(
        requirement=state["requirement"],
        requirement_analysis=state[
            "requirement_analysis"
        ],
        repository_analysis=state[
            "repository_analysis"
        ],
        revision_feedback=revision_feedback,
    )

    print("Architecture proposal complete.")

    return {
        **state,
        "architecture_proposal": proposal,
        "status": "architecture_proposed",
    }

def create_implementation_plan(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print("Running Implementation Planning Agent...")

    llm_service = create_llm_service()

    revision_feedback = None

    human_review = state.get(
        "human_review"
    )

    if (
        human_review
        and human_review.decision.value == "revise"
        and human_review.revision_target is not None
        and human_review.revision_target.value
        == "implementation_plan"
    ):
        revision_feedback = "\n".join(
            human_review.requested_changes
        )

    planner = ImplementationPlanningAgent(
        llm_service=llm_service
    )

    plan = planner.plan(
        requirement=state["requirement"],
        requirement_analysis=state[
            "requirement_analysis"
        ],
        repository_analysis=state[
            "repository_analysis"
        ],
        architecture_proposal=state[
            "architecture_proposal"
        ],
        revision_feedback=revision_feedback,
    )

    print("Implementation plan complete.")

    return {
        **state,
        "implementation_plan": plan,
        "status": "implementation_planned",
    }

def human_review(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print("Human review required.")

    review_payload = {
        "message": (
            "Review the architecture proposal and "
            "implementation plan."
        ),
        "architecture_proposal": (
            state["architecture_proposal"].model_dump()
        ),
        "implementation_plan": (
            state["implementation_plan"].model_dump()
        ),
        "revision_count": state.get(
            "revision_count",
            0,
        ),
    }

    review_response = interrupt(
        review_payload
    )

    review = HumanReviewResult.model_validate(
        review_response
    )

    history = list(
        state.get(
            "revision_history",
            [],
        )
    )

    history.append(review)

    print()
    print(
        f"Human decision received: "
        f"{review.decision.value}"
    )

    return {
        **state,
        "human_review": review,
        "revision_history": history,
        "status": "human_review_completed",
    }

def approval_completed(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print("Architecture and implementation plan approved.")

    return {
        **state,
        "status": "approved",
    }


def review_rejected(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print("Architecture or implementation plan rejected.")

    return {
        **state,
        "status": "rejected",
    }

def prepare_revision(
    state: DevPilotState,
) -> DevPilotState:
    review = state["human_review"]

    revision_count = (
        state.get(
            "revision_count",
            0,
        )
        + 1
    )

    print()
    print(
        f"Preparing revision "
        f"#{revision_count}..."
    )

    return {
        **state,
        "revision_count": revision_count,
        "status": "revision_prepared",
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
        **state,
        "status": "revision_limit_reached",
    }

def perform_security_review(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print("Running Security Review Agent...")

    llm_service = create_llm_service()

    security_agent = SecurityReviewAgent(
        llm_service=llm_service
    )

    security_review = security_agent.review(
        requirement=state["requirement"],
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

    print("Security review complete.")

    return {
        "security_review": security_review,
    }

def perform_test_review(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print("Running Test Strategy Agent...")

    llm_service = create_llm_service()

    test_agent = TestStrategyAgent(
        llm_service=llm_service
    )

    test_review = test_agent.review(
        requirement=state["requirement"],
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

    print("Test strategy review complete.")

    return {
        "test_review": test_review,
    }

def specialist_reviews_completed(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print("Specialist reviews completed.")

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
        "status": "specialist_reviews_completed",
    }

def evaluate_proposal(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print("Running Evaluator Agent...")

    llm_service = create_llm_service()

    evaluator = EvaluatorAgent(
        llm_service=llm_service
    )

    # ---------------------------------------------------------
    # Step 1:
    # Let the LLM evaluate the complete proposal.
    # ---------------------------------------------------------
    evaluation = evaluator.evaluate(
        requirement=state["requirement"],
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

    # ---------------------------------------------------------
    # Step 2:
    # Apply deterministic application policy.
    #
    # This protects us from an inconsistent LLM verdict.
    # ---------------------------------------------------------
    evaluation = enforce_evaluation_policy(
        evaluation=evaluation,
        security_review=state[
            "security_review"
        ],
        test_review=state[
            "test_review"
        ],
    )

    print("Evaluation complete.")

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

#Temporary Node for testing the evaluation agent
def evaluation_passed(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Quality gate passed."
    )

    return {
        "status": "quality_gate_passed",
    }


def evaluation_revision_required(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Quality gate requires revision."
    )

    return {
        "status": "quality_revision_required",
    }


def evaluation_escalated(
    state: DevPilotState,
) -> DevPilotState:
    print()
    print(
        "Quality gate requires human escalation."
    )

    return {
        "status": "quality_escalated",
    }