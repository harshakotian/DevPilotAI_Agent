from devpilot.models.architecture import ArchitectureProposal
from devpilot.models.evaluation import EvaluationResult
from devpilot.models.implementation import ImplementationPlan
from devpilot.models.requirement import RequirementAnalysis
from devpilot.models.security import SecurityReview
from devpilot.models.testing import TestReview
from devpilot.services.llm_service import LLMService


class EvaluatorAgent:
    def __init__(
        self,
        llm_service: LLMService,
    ):
        self._llm_service = llm_service

    def evaluate(
        self,
        requirement: str,
        requirement_analysis: RequirementAnalysis,
        architecture_proposal: ArchitectureProposal,
        implementation_plan: ImplementationPlan,
        security_review: SecurityReview,
        test_review: TestReview,
    ) -> EvaluationResult:
        system_prompt = """
You are a senior engineering quality evaluator.

Your responsibility is to independently assess whether
a proposed architecture and implementation plan are ready
to progress.

You are evaluating work produced by other agents.
Do not automatically agree with them.

Evaluate:

1. Alignment with the original requirement.
2. Architectural coherence.
3. Implementation readiness.
4. Security readiness.
5. Testing readiness.
6. Internal consistency across all artifacts.
7. Whether unresolved issues prevent safe progress.

VERDICTS

PASS:
The proposal is sufficiently complete and no blocking
issues remain.

REVISE:
The proposal is directionally correct but specific
architecture, planning, security, or testing issues must
be corrected.

ESCALATE:
Human judgment is required because of serious ambiguity,
conflicting recommendations, critical risk, or insufficient
evidence.

IMPORTANT RULES

1. If security_review.implementation_blocked is true,
   verdict must NOT be PASS.

2. If test_review.implementation_blocked is true,
   verdict must NOT be PASS.

3. Critical unresolved security risk should normally
   result in ESCALATE.

4. Do not invent repository facts or vulnerabilities.

5. Do not rewrite the architecture or implementation plan.

6. Identify exactly what needs revision when verdict is
   REVISE.

7. Scores must be integers from 0 through 100.

8. A high average score does not override a blocking issue.

9. implementation_ready must only be true when the verdict
   is PASS.

10. confidence must be low, medium, or high.
"""

        user_prompt = f"""
ORIGINAL REQUIREMENT

{requirement}


REQUIREMENT ANALYSIS

{requirement_analysis.model_dump_json(indent=2)}


ARCHITECTURE PROPOSAL

{architecture_proposal.model_dump_json(indent=2)}


IMPLEMENTATION PLAN

{implementation_plan.model_dump_json(indent=2)}


SECURITY REVIEW

{security_review.model_dump_json(indent=2)}


TEST REVIEW

{test_review.model_dump_json(indent=2)}


Evaluate the complete engineering proposal and produce
a quality verdict.
"""

        return self._llm_service.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=EvaluationResult,
        )