from backend.gemini_client import GeminiClient
from backend.repetitiondetector import RepetitionDetector


class GeminiPlusAgent:
    """
    Orchestrates GeminiClient + RepetitionDetector.
    This is the single entry point the frontend calls.
    Voice input is handled separately before calling .chat().
    """

    def __init__(self):
        self.gemini = GeminiClient()
        self.detector = RepetitionDetector(threshold=0.85, memory_size=6)

    def chat(self, user_message: str) -> dict:
        """
        Send a message and get a response with metadata.

        Returns:
        {
            "response":            str,   # text to show the user
            "repetition_detected": bool,  # was first attempt repetitive?
            "similarity_score":    float, # highest similarity found (0–1)
            "retried":             bool   # did we use the diversity prompt?
        }
        """
        # --- First attempt ---
        raw_response = self.gemini.send_message(user_message)
        is_repetitive, score = self.detector.is_repetitive(raw_response)

        if not is_repetitive:
            self.detector.add_response(raw_response)
            return {
                "response": raw_response,
                "repetition_detected": False,
                "similarity_score": score,
                "retried": False,
            }

        # --- Repetition detected: retry with diversity injection ---
        print(f"[Agent] ⚠ Repetition detected (score={score}). Retrying...")
        diverse_response = self.gemini.send_with_diversity_prompt(user_message)

        # Store the retried response (avoids looping on the same detection)
        self.detector.add_response(diverse_response)

        return {
            "response": diverse_response,
            "repetition_detected": True,
            "similarity_score": score,
            "retried": True,
        }

    def reset(self):
        """Full reset — clears both Gemini history and repetition memory."""
        self.gemini.reset_chat()
        self.detector.reset()
        print("[Agent] Chat and memory reset.")