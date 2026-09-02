from devpilot.models.architecture import ArchitectureProposal
from devpilot.models.implementation import ImplementationPlan
from devpilot.models.repository import RepositoryAnalysis
from devpilot.models.requirement import RequirementAnalysis
from devpilot.models.security import SecurityReview
from devpilot.services.llm_service import LLMService


class SecurityReviewAgent:
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
    ) -> SecurityReview:
        system_prompt = """
You are a senior application security architect.

Your responsibility is to review a proposed software
architecture and implementation plan for security concerns.

Rules:

1. Ground findings only in the supplied requirement,
   repository analysis, architecture proposal, and
   implementation plan.

2. Do not invent existing vulnerabilities in source code.

3. Distinguish:
   - confirmed security concerns
   - missing security controls
   - unresolved security information

4. Review areas including:
   - authentication
   - authorization
   - secrets and credentials
   - sensitive data handling
   - transport security
   - configuration security
   - dependency/security package risk
   - logging and information disclosure
   - availability and failure behavior
   - cache-related confidentiality/integrity concerns

5. Security findings must include:
   severity, category, evidence, impact,
   recommendation, and whether implementation
   should be blocked.

6. Do not generate source code.

7. Do not redesign the entire architecture.
   Recommend focused security controls.

8. Do not claim a vulnerability exists unless the
   supplied evidence supports that claim.

9. When information is missing, place it under
   missing_information rather than guessing.

10. overall_risk must be one of:
    low, medium, high, critical.

11. confidence must be one of:
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


Perform a security review of the proposed change.
"""

        return self._llm_service.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=SecurityReview,
        )