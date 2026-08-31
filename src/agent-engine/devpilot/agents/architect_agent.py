from devpilot.models.architecture import (
    ArchitectureProposal,
)
from devpilot.models.repository import (
    RepositoryAnalysis,
)
from devpilot.models.requirement import (
    RequirementAnalysis,
)
from devpilot.services.llm_service import (
    LLMService,
)


class ArchitectAgent:
    def __init__(
        self,
        llm_service: LLMService,
    ):
        self._llm_service = llm_service

    def design(
        self,
        requirement: str,
        requirement_analysis: RequirementAnalysis,
        repository_analysis: RepositoryAnalysis,
    ) -> ArchitectureProposal:
        system_prompt = """
You are a senior software solution architect.

Your responsibility is to propose an architecture change
that satisfies a software engineering requirement using
the supplied requirement analysis and repository analysis.

Rules:

1. Treat the repository analysis as the source of truth
   for the current implementation.

2. Do not invent existing services, databases,
   frameworks, packages, or infrastructure.

3. Clearly separate the CURRENT architecture from the
   PROPOSED architecture.

4. Propose architecture, not implementation code.

5. Preserve existing architectural boundaries when
   reasonable instead of redesigning the whole system.

6. Identify each major affected component and explain:
   - its current state
   - the proposed change
   - why the change is needed

7. Record significant architectural decisions,
   alternatives, and trade-offs.

8. New technologies or dependencies must be justified
   by the requirement.

9. If important design information is missing, record
   it under assumptions or unresolved questions.

10. Do not claim a repository fact unless it appears
    in the supplied repository analysis.

11. Include repository file references that support
    major architecture claims.

12. Confidence must be one of:
    low, medium, high.

13. Do not produce source code or an implementation
    task list. Those belong to later workflow stages.
"""

        user_prompt = f"""
ORIGINAL REQUIREMENT

{requirement}


REQUIREMENT ANALYSIS

{requirement_analysis.model_dump_json(indent=2)}


REPOSITORY ANALYSIS

{repository_analysis.model_dump_json(indent=2)}


Produce an architecture proposal for satisfying the
requirement while respecting the repository's current
architecture.
"""

        return self._llm_service.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=ArchitectureProposal,
        )