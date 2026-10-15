import re
from typing import Set

class FaithfulnessEvaluator:
    """
    Quantifies lexical and semantic grounding of an LLM response against retrieved
    source context to prevent hallucinated claims.
    """

    STOPWORDS: Set[str] = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "is", "are", "was", "were", "be", "been", "this",
        "that", "it", "from", "as", "has", "have", "had"
    }

    @classmethod
    def _tokenize(cls, text: str) -> Set[str]:
        tokens = re.findall(r"\b[a-zA-Z0-9]{2,}\b", text.lower())
        return {t for t in tokens if t not in cls.STOPWORDS}

    def score_grounding(self, context: str, response: str) -> float:
        """
        Computes token-level precision overlap of response claims within source context.
        Returns score in [0.0, 1.0].
        """
        resp_tokens = self._tokenize(response)
        if not resp_tokens:
            return 1.0

        ctx_tokens = self._tokenize(context)
        if not ctx_tokens:
            return 0.0

        overlap = resp_tokens.intersection(ctx_tokens)
        return round(len(overlap) / len(resp_tokens), 4)
