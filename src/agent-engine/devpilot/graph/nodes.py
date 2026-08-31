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

    proposal = architect.design(
        requirement=state["requirement"],
        requirement_analysis=state[
            "requirement_analysis"
        ],
        repository_analysis=state[
            "repository_analysis"
        ],
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
    )

    print("Implementation plan complete.")

    return {
        **state,
        "implementation_plan": plan,
        "status": "implementation_planned",
    }