import hashlib
import math
import re
from typing import List, Optional
from app.core.config import settings
from app.core.logging import logger
from app.embeddings.base import EmbeddingProvider


class LocalEmbeddingProvider(EmbeddingProvider):
    """
    Local embedding provider implementing 384-dimensional dense vectors.
    Uses SentenceTransformer (all-MiniLM-L6-v2) with a resilient deterministic
    offline projection fallback for instant test runs and air-gapped environments.
    """
    def __init__(
        self,
        model_name: Optional[str] = None,
        force_fallback: bool = False,
    ):
        self.model_name = model_name or settings.LOCAL_EMBEDDING_MODEL
        self._dim = 384
        self._model: Optional[SentenceTransformer] = None
        self._force_fallback = force_fallback
        self._initialized = False

    @property
    def dimension(self) -> int:
        return self._dim

    def _get_model(self):
        import os
        if (
            os.environ.get("OFFLINE_EMBEDDINGS") == "1"
            or settings.APP_ENV == "testing"
            or settings.EMBEDDING_PROVIDER != "sentence_transformers"
        ):
            return None

        if not self._initialized and not self._force_fallback:
            try:
                from sentence_transformers import SentenceTransformer
                # Use local_files_only to prevent network blocking/hangs during HTTP requests
                self._model = SentenceTransformer(self.model_name, local_files_only=True)
                logger.info(f"Loaded cached SentenceTransformer model: {self.model_name}")
            except Exception as exc:
                logger.warning(f"Could not load SentenceTransformer ({exc}). Using deterministic projection.")
                self._model = None
            self._initialized = True
        return self._model



    def embed_text(self, text: str) -> List[float]:
        model = self._get_model()
        if model is not None:
            try:
                vec = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
                return [round(float(x), 6) for x in vec.tolist()]
            except Exception as exc:
                logger.warning(f"SentenceTransformer encoding failed: {exc}. Using fallback projection.")

        return self._deterministic_semantic_vector(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        model = self._get_model()
        if model is not None:
            try:
                vecs = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                return [[round(float(x), 6) for x in vec] for vec in vecs.tolist()]
            except Exception as exc:
                logger.warning(f"Batch SentenceTransformer encoding failed: {exc}.")

        return [self._deterministic_semantic_vector(t) for t in texts]

    def _deterministic_semantic_vector(self, text: str) -> List[float]:
        """
        Fast deterministic subword/token hashing projection into R^384.
        Guarantees unit-norm output and meaningful cosine similarity across overlapping terms.
        """
        if not text:
            return [0.0] * self._dim

        vector = [0.0] * self._dim
        # Tokenize words and character 3-grams
        words = re.findall(r"\b[a-zA-Z0-9_\+#\.\-]{2,}\b", text.lower())
        
        # Stop words to downweight
        stopwords = {"the", "and", "for", "with", "this", "that", "from", "are", "you", "your", "will", "have"}

        for word in words:
            weight = 0.2 if word in stopwords else 1.0
            # Word-level hash bucket
            h_val = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h_val % self._dim
            sign = 1.0 if (h_val // self._dim) % 2 == 0 else -1.0
            vector[idx] += sign * weight

            # Subword 3-grams for morphological similarity
            if len(word) >= 3 and weight > 0.5:
                for i in range(len(word) - 2):
                    ngram = word[i : i + 3]
                    h_ng = int(hashlib.sha256(ngram.encode("utf-8")).hexdigest(), 16)
                    ng_idx = h_ng % self._dim
                    ng_sign = 1.0 if (h_ng // self._dim) % 2 == 0 else -1.0
                    vector[ng_idx] += ng_sign * 0.3

        # L2 Normalization to unit sphere
        norm = math.sqrt(sum(x * x for x in vector))
        if norm == 0.0:
            return [1.0 / math.sqrt(self._dim)] * self._dim

        return [round(float(x / norm), 6) for x in vector]


# Default singleton provider
embedding_provider = LocalEmbeddingProvider()
