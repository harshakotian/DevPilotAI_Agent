from devpilot.agents.architect_agent import ArchitectAgent
from devpilot.agents.evaluator_agent import EvaluatorAgent
from devpilot.agents.planning_agent import ImplementationPlanningAgent
from devpilot.agents.requirement_agent import RequirementAnalyst
from devpilot.agents.repository_agent import RepositoryAnalyst
from devpilot.agents.security_agent import SecurityReviewAgent
from devpilot.agents.testing_agent import TestStrategyAgent

from devpilot.services.llm_factory import create_llm_service
from devpilot.services.repository_evidence_service import (
    RepositoryEvidenceService,
)


def main():
    requirement = (
        "Add distributed caching to the "
        "Product API using Redis."
    )

    repository_path = (
        "../../samples/SampleProductApi"
    )

    llm_service = create_llm_service()

    # ---------------------------------------------------------
    # Requirement
    # ---------------------------------------------------------
    requirement_agent = RequirementAnalyst(
        llm_service
    )

    requirement_analysis = requirement_agent.analyze(
        requirement
    )

    # ---------------------------------------------------------
    # Repository
    # ---------------------------------------------------------
    evidence_service = RepositoryEvidenceService()

    evidence = evidence_service.collect(
        repository_path
    )

    repository_agent = RepositoryAnalyst(
        llm_service
    )

    repository_analysis = repository_agent.analyze(
        requirement=requirement,
        requirement_analysis=requirement_analysis,
        evidence=evidence,
    )

    # ---------------------------------------------------------
    # Architecture
    # ---------------------------------------------------------
    architect = ArchitectAgent(
        llm_service
    )

    architecture = architect.design(
        requirement=requirement,
        requirement_analysis=requirement_analysis,
        repository_analysis=repository_analysis,
    )

    # ---------------------------------------------------------
    # Planning
    # ---------------------------------------------------------
    planner = ImplementationPlanningAgent(
        llm_service
    )

    implementation_plan = planner.plan(
        requirement=requirement,
        requirement_analysis=requirement_analysis,
        repository_analysis=repository_analysis,
        architecture_proposal=architecture,
    )

    # ---------------------------------------------------------
    # Security
    # ---------------------------------------------------------
    security_agent = SecurityReviewAgent(
        llm_service
    )

    security_review = security_agent.review(
        requirement=requirement,
        requirement_analysis=requirement_analysis,
        repository_analysis=repository_analysis,
        architecture_proposal=architecture,
        implementation_plan=implementation_plan,
    )

    # ---------------------------------------------------------
    # Testing
    # ---------------------------------------------------------
    test_agent = TestStrategyAgent(
        llm_service
    )

    test_review = test_agent.review(
        requirement=requirement,
        requirement_analysis=requirement_analysis,
        repository_analysis=repository_analysis,
        architecture_proposal=architecture,
        implementation_plan=implementation_plan,
    )

    # ---------------------------------------------------------
    # Evaluator
    # ---------------------------------------------------------
    evaluator = EvaluatorAgent(
        llm_service
    )

    evaluation = evaluator.evaluate(
        requirement=requirement,
        requirement_analysis=requirement_analysis,
        architecture_proposal=architecture,
        implementation_plan=implementation_plan,
        security_review=security_review,
        test_review=test_review,
    )

    print()
    print("=" * 70)
    print("Evaluation Result")
    print("=" * 70)

    print(
        evaluation.model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":
    main()