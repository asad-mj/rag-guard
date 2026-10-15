from typing import List, Optional
from pydantic import BaseModel
from rag_guard.pii import PIIRedactor
from rag_guard.injection import PromptInjectionDetector
from rag_guard.faithfulness import FaithfulnessEvaluator

class GuardResult(BaseModel):
    safe: bool
    sanitized_prompt: str
    pii_detected: List[str]
    injection_risk_score: float
    triggered_rules: List[str]
    faithfulness_score: Optional[float] = None
    reason: str

class RAGShield:
    """End-to-end deterministic guardrail pipeline for enterprise RAG applications."""

    def __init__(self, injection_threshold: float = 0.65, min_faithfulness: float = 0.45):
        self.pii = PIIRedactor()
        self.injection = PromptInjectionDetector(threshold=injection_threshold)
        self.faithfulness = FaithfulnessEvaluator()
        self.min_faithfulness = min_faithfulness

    def evaluate(
        self,
        prompt: str,
        context: Optional[str] = None,
        response: Optional[str] = None
    ) -> GuardResult:
        sanitized, pii_types = self.pii.redact(prompt)
        blocked, risk_score, rules = self.injection.scan(prompt)

        faith_score: Optional[float] = None
        if context is not None and response is not None:
            faith_score = self.faithfulness.score_grounding(context, response)

        if blocked:
            return GuardResult(
                safe=False,
                sanitized_prompt=sanitized,
                pii_detected=pii_types,
                injection_risk_score=risk_score,
                triggered_rules=rules,
                faithfulness_score=faith_score,
                reason=f"Blocked due to adversarial prompt injection: {', '.join(rules)}"
            )

        if faith_score is not None and faith_score < self.min_faithfulness:
            return GuardResult(
                safe=False,
                sanitized_prompt=sanitized,
                pii_detected=pii_types,
                injection_risk_score=risk_score,
                triggered_rules=["low_context_faithfulness"],
                faithfulness_score=faith_score,
                reason=f"Hallucination risk: faithfulness score ({faith_score}) below threshold ({self.min_faithfulness})"
            )

        return GuardResult(
            safe=True,
            sanitized_prompt=sanitized,
            pii_detected=pii_types,
            injection_risk_score=risk_score,
            triggered_rules=[],
            faithfulness_score=faith_score,
            reason="Passed all security and grounding checks."
        )
