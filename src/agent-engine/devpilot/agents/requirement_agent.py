from devpilot.models.requirement import RequirementAnalysis
from devpilot.services.llm_service import LLMService


class RequirementAnalyst:
    def __init__(self, llm_service: LLMService):
        self._llm_service = llm_service

    def analyze(
        self,
        requirement: str,
    ) -> RequirementAnalysis:
        system_prompt = """
You are a senior software requirement analyst.

Your task is to analyze a software engineering requirement
and convert it into a structured engineering analysis.

Rules:
1. Do not invent missing facts.
2. Separate explicit constraints from assumptions.
3. Identify clarification questions when important information is missing.
4. Identify likely affected technical areas, but do not pretend that repository evidence exists.
5. Identify requirement-level implementation or operational risks.
6. Set is_actionable to true when the requirement is specific enough to begin meaningful engineering analysis, even if implementation details are still missing.
7. Missing implementation details should be captured as clarification_questions, not automatically make the requirement non-actionable.
8. Set is_actionable to false only when the requested change or desired outcome is too vague to determine what should be analyzed.
9. Keep the analysis concise, practical, and engineering-focused.
"""

        user_prompt = f"""
Analyze the following software engineering requirement:

{requirement}
"""

        return self._llm_service.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=RequirementAnalysis,
        )