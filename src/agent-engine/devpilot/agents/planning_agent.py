from devpilot.models.architecture import ArchitectureProposal
from devpilot.models.implementation import ImplementationPlan
from devpilot.models.repository import RepositoryAnalysis
from devpilot.models.requirement import RequirementAnalysis
from devpilot.services.llm_service import LLMService


class ImplementationPlanningAgent:
    def __init__(
        self,
        llm_service: LLMService,
    ):
        self._llm_service = llm_service

    def plan(
        self,
        requirement: str,
        requirement_analysis: RequirementAnalysis,
        repository_analysis: RepositoryAnalysis,
        architecture_proposal: ArchitectureProposal,
    ) -> ImplementationPlan:
        system_prompt = """
You are a senior software implementation planner.

Your responsibility is to convert an approved architecture
proposal into a practical, ordered engineering implementation plan.

Rules:

1. Use the supplied repository analysis as the source of truth
   for the current system.

2. Use the supplied architecture proposal as the target design.

3. Do not redesign the architecture unless an inconsistency makes
   the plan impossible. Record such issues under unresolved questions.

4. Produce implementation steps in dependency-aware execution order.

5. Identify existing files likely to be modified.

6. You may identify likely new files when the architecture clearly
   requires them, but label them as new rather than pretending they exist.

7. Do not generate source code.

8. Do not invent packages, services, databases, or infrastructure
   unless justified by the architecture proposal.

9. Include dependency/package changes separately.

10. Include configuration changes separately.

11. Include testing for normal behavior, failure behavior,
    and important edge cases.

12. Include concrete end-to-end verification criteria.

13. Include rollback considerations for changes that could affect
    runtime behavior or infrastructure.

14. Preserve unresolved architecture or requirement questions.

15. Confidence must be one of:
    low, medium, high.
"""

        user_prompt = f"""
ORIGINAL REQUIREMENT

{requirement}


REQUIREMENT ANALYSIS

{requirement_analysis.model_dump_json(indent=2)}


REPOSITORY ANALYSIS

{repository_analysis.model_dump_json(indent=2)}


APPROVED ARCHITECTURE PROPOSAL

{architecture_proposal.model_dump_json(indent=2)}


Produce an ordered engineering implementation plan.
Do not write source code.
"""

        return self._llm_service.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=ImplementationPlan,
        )