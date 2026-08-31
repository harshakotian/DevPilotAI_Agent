from devpilot.agents.architect_agent import ArchitectAgent
from devpilot.agents.planning_agent import ImplementationPlanningAgent
from devpilot.agents.requirement_agent import RequirementAnalyst
from devpilot.agents.repository_agent import RepositoryAnalyst
from devpilot.services.llm_factory import create_llm_service
from devpilot.services.repository_evidence_service import (
    RepositoryEvidenceService,
)


def main():
    requirement = (
        "Add distributed caching to the Product API "
        "using Redis."
    )

    repository_path = (
        "../../samples/SampleProductApi"
    )

    llm_service = create_llm_service()

    requirement_analyst = RequirementAnalyst(
        llm_service=llm_service
    )

    requirement_analysis = requirement_analyst.analyze(
        requirement
    )

    evidence_service = RepositoryEvidenceService()

    evidence = evidence_service.collect(
        repository_path
    )

    repository_analyst = RepositoryAnalyst(
        llm_service=llm_service
    )

    repository_analysis = repository_analyst.analyze(
        requirement=requirement,
        requirement_analysis=requirement_analysis,
        evidence=evidence,
    )

    architect = ArchitectAgent(
        llm_service=llm_service
    )

    architecture_proposal = architect.design(
        requirement=requirement,
        requirement_analysis=requirement_analysis,
        repository_analysis=repository_analysis,
    )

    planner = ImplementationPlanningAgent(
        llm_service=llm_service
    )

    implementation_plan = planner.plan(
        requirement=requirement,
        requirement_analysis=requirement_analysis,
        repository_analysis=repository_analysis,
        architecture_proposal=architecture_proposal,
    )

    print()
    print("Implementation Plan")
    print()

    print(
        implementation_plan.model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":
    main()