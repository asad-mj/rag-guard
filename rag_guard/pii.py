import re
from typing import Dict, List, Tuple

class PIIRedactor:
    """Detects and masks sensitive PII tokens before LLM ingestion or logging."""

    PATTERNS: Dict[str, re.Pattern] = {
        "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "PHONE": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
        "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "CREDIT_CARD": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
        "API_KEY": re.compile(r"\b(?:sk-[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16})\b"),
    }

    def redact(self, text: str) -> Tuple[str, List[str]]:
        redacted_text = text
        detected_types: List[str] = []

        for label, pattern in self.PATTERNS.items():
            if pattern.search(redacted_text):
                detected_types.append(label)
                redacted_text = pattern.sub(f"[REDACTED_{label}]", redacted_text)

        return redacted_text, detected_types
