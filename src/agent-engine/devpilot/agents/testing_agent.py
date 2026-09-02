from devpilot.models.architecture import ArchitectureProposal
from devpilot.models.implementation import ImplementationPlan
from devpilot.models.repository import RepositoryAnalysis
from devpilot.models.requirement import RequirementAnalysis
from devpilot.models.testing import TestReview
from devpilot.services.llm_service import LLMService


class TestStrategyAgent:
    def __init__(
        self,
        llm_service: LLMService,
    ):
        self._llm_service = llm_service

    def review(
        self,
        requirement: str,
        requirement_analysis: RequirementAnalysis,
        repository_analysis: RepositoryAnalysis,
        architecture_proposal: ArchitectureProposal,
        implementation_plan: ImplementationPlan,
    ) -> TestReview:
        system_prompt = """
You are a senior software test architect.

Your responsibility is to review a proposed software
architecture and implementation plan and produce a
comprehensive testing strategy.

Rules:

1. Ground the test strategy only in the supplied
   requirement, repository analysis, architecture
   proposal, and implementation plan.

2. Do not invent existing test infrastructure,
   frameworks, files, or capabilities.

3. Cover:
   - functional correctness
   - regression risk
   - failure behavior
   - integration boundaries
   - configuration changes
   - resilience
   - performance where relevant
   - operational behavior

4. Identify both positive and negative scenarios.

5. Include tests for expected failure modes.

6. Separate unit, integration, resilience,
   performance, and manual/verification testing
   where appropriate.

7. Every important scenario should identify:
   - target
   - priority
   - steps
   - expected result
   - failure condition
   - supporting evidence

8. Do not write test source code.

9. Do not invent implementation details that do not
   appear in the supplied artifacts.

10. Record missing test coverage under coverage_gaps.

11. implementation_blocked should be true only when
    a serious testing gap would make implementation
    unsafe or impossible to validate.

12. confidence must be one of:
    low, medium, high.
"""

        user_prompt = f"""
ORIGINAL REQUIREMENT

{requirement}


REQUIREMENT ANALYSIS

{requirement_analysis.model_dump_json(indent=2)}


REPOSITORY ANALYSIS

{repository_analysis.model_dump_json(indent=2)}


ARCHITECTURE PROPOSAL

{architecture_proposal.model_dump_json(indent=2)}


IMPLEMENTATION PLAN

{implementation_plan.model_dump_json(indent=2)}


Produce a testing strategy for the proposed change.
"""

        return self._llm_service.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=TestReview,
        )