from abc import ABC, abstractmethod
import math
from typing import List


class EmbeddingProvider(ABC):
    """
    Abstract interface for generating dense semantic vector embeddings.
    Conforms to TECH_STACK.md Section 13.
    """
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Dimensionality of the output vector (e.g. 384 for all-MiniLM-L6-v2)."""
        pass

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Embeds a single text string into a float vector."""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embeds a batch of texts into a list of float vectors."""
        pass

    @staticmethod
    def cosine_similarity(a: List[float], b: List[float]) -> float:
        """
        Computes cosine similarity between two float vectors: (a . b) / (||a|| * ||b||).
        Returns a float between -1.0 and 1.0.
        """
        if not a or not b or len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return max(-1.0, min(1.0, dot_product / (norm_a * norm_b)))
