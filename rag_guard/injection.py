import re
from typing import Tuple, List

class PromptInjectionDetector:
    """
    Evaluates user prompts against weighted adversarial signatures and structural
    jailbreak heuristics (DAN, system prompt override, token smuggling).
    """

    SIGNATURES = [
        (r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions", 0.85, "instruction_override"),
        (r"reveal\s+(?:your\s+)?(?:system|developer)\s+prompt", 0.90, "system_prompt_leak"),
        (r"you\s+are\s+now\s+(?:in\s+)?(?:developer|dan|unrestricted)\s+mode", 0.95, "jailbreak_persona"),
        (r"(?:bypass|disable|ignore)\s+(?:safety|content|guardrail)\s+(?:filters|rules|policies)", 0.90, "safety_bypass"),
        (r"<\|(?:im_start|system|endoftext)\|>", 0.95, "special_token_smuggling"),
    ]

    def __init__(self, threshold: float = 0.65):
        self.threshold = threshold

    def scan(self, prompt: str) -> Tuple[bool, float, List[str]]:
        normalized = prompt.lower().strip()
        triggered_rules: List[str] = []
        max_risk = 0.0

        for pattern, weight, rule_name in self.SIGNATURES:
            if re.search(pattern, normalized):
                triggered_rules.append(rule_name)
                max_risk = max(max_risk, weight)

        is_blocked = max_risk >= self.threshold
        return is_blocked, round(max_risk, 3), triggered_rules
