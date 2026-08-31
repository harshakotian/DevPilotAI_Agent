from devpilot.models.repository import (
    RepositoryAnalysis,
    RepositoryEvidence,
)
from devpilot.models.requirement import (
    RequirementAnalysis,
)
from devpilot.services.llm_service import (
    LLMService,
)


class RepositoryAnalyst:
    def __init__(
        self,
        llm_service: LLMService,
    ):
        self._llm_service = llm_service

    def analyze(
        self,
        requirement: str,
        requirement_analysis: RequirementAnalysis,
        evidence: RepositoryEvidence,
    ) -> RepositoryAnalysis:
        system_prompt = """
You are a senior software repository analyst.

Your responsibility is to analyze repository evidence
in the context of a software engineering requirement.

You must ground conclusions only in the supplied
repository evidence.

Rules:

1. Do not claim that something exists unless the
   supplied repository evidence supports it.

2. Distinguish confirmed repository facts from
   reasonable inferences.

3. Do not invent files, classes, services,
   dependencies, databases, packages, or architecture.

4. When evidence is insufficient, record the
   uncertainty instead of guessing.

5. Identify files that are likely relevant to the
   requested change.

6. Identify existing capabilities supported by the
   evidence.

7. Identify requested capabilities that were not
   found in the collected evidence.

8. For significant claims, include repository evidence
   with the supporting source file and line number
   when one is available.

9. A zero-result text search means that the searched
   term was not found in the inspected evidence.
   It does not prove with absolute certainty that the
   capability cannot exist.

10. Confidence must be one of:
    low, medium, high.

11. Do not design the new architecture.
    Architecture design belongs to a later agent.
"""

        user_prompt = f"""
ORIGINAL REQUIREMENT

{requirement}


STRUCTURED REQUIREMENT ANALYSIS

{requirement_analysis.model_dump_json(indent=2)}


COLLECTED REPOSITORY EVIDENCE

{evidence.model_dump_json(indent=2)}


Analyze the current repository as it relates to the
requirement.
"""

        return self._llm_service.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=RepositoryAnalysis,
        )