"""
AgentGuard Semantic Embedding Service.

Provides a reusable interface for computing semantic embeddings and cosine
similarity between natural-language strings using sentence-transformers.
"""

from typing import Optional
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Singleton service managing the SentenceTransformer embedding model.
    Loads 'all-MiniLM-L6-v2' on demand and calculates semantic similarity.
    """
    _instance: Optional["EmbeddingService"] = None

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._model: Optional[SentenceTransformer] = None

    @classmethod
    def get_instance(cls, model_name: str = "all-MiniLM-L6-v2") -> "EmbeddingService":
        """Access or instantiate the singleton EmbeddingService."""
        if cls._instance is None:
            cls._instance = cls(model_name=model_name)
        return cls._instance

    @property
    def model(self) -> SentenceTransformer:
        """Lazy loader for the SentenceTransformer model."""
        if self._model is None:
            try:
                self._model = SentenceTransformer(self.model_name)
            except Exception as exc:
                raise RuntimeError(
                    f"Failed to load sentence-transformers model '{self.model_name}': {exc}"
                ) from exc
        return self._model

    def encode(self, text: str) -> np.ndarray:
        """
        Convert a text string into a 384-dimensional dense embedding vector.
        """
        if not text or not text.strip():
            raise ValueError("Cannot compute embedding for empty text string.")
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        """
        Compute the cosine similarity between two text strings.
        Returns a float score in [-1.0, 1.0], rounded to 4 decimal places.
        """
        vec_a = self.encode(text_a)
        vec_b = self.encode(text_b)

        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        similarity = float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
        # Clamp to [-1.0, 1.0] to guard against floating point inaccuracies
        similarity = max(-1.0, min(1.0, similarity))
        return round(similarity, 4)


# Helper function for quick access
def get_embedding_service(model_name: str = "all-MiniLM-L6-v2") -> EmbeddingService:
    """Helper function returning the global EmbeddingService singleton."""
    return EmbeddingService.get_instance(model_name=model_name)
