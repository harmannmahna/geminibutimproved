from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class RepetitionDetector:
    def __init__(self, threshold: float = 0.85, memory_size: int = 6):
        """
        threshold:   cosine similarity above this → repetition flagged
        memory_size: how many past responses to keep in memory
        
        The model (all-MiniLM-L6-v2) runs fully locally — no API key needed.
        It converts text into 384-dimensional vectors (~90MB download on first run).
        """
        print("Loading sentence-transformer model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.threshold = threshold
        self.memory_size = memory_size
        self.response_history: list[np.ndarray] = []  # stores embeddings
        self.response_texts: list[str] = []           # stores raw text for debug

    def _embed(self, text: str) -> np.ndarray:
        """Convert text → 384-dim vector."""
        return self.model.encode([text])

    def is_repetitive(self, new_response: str) -> tuple[bool, float]:
        """
        Compare new_response against recent history.
        Returns (is_repetitive, max_similarity_score).
        """
        if not self.response_history:
            return False, 0.0

        new_embedding = self._embed(new_response)

        similarities = [
            cosine_similarity(new_embedding, past_emb)[0][0]
            for past_emb in self.response_history
        ]

        max_score = max(similarities)
        return max_score >= self.threshold, round(float(max_score), 3)

    def add_response(self, response: str):
        """Store a response after it has been approved/returned."""
        self.response_history.append(self._embed(response))
        self.response_texts.append(response)

        # Sliding window — drop oldest if over limit
        if len(self.response_history) > self.memory_size:
            self.response_history.pop(0)
            self.response_texts.pop(0)

    def reset(self):
        """Clear all memory."""
        self.response_history = []
        self.response_texts = []