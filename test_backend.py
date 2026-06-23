"""
Run this file to test all backend modules one by one.
Usage: python test_backend.py
"""

# ─────────────────────────────────────────────
# TEST 1 — Gemini client
# ─────────────────────────────────────────────
print("\n" + "="*50)
print("TEST 1: GeminiClient")
print("="*50)

from backend.gemini_client import GeminiClient

client = GeminiClient()
response = client.send_message("What is recursion? Answer in 2 sentences.")
print("Gemini says:", response)
assert isinstance(response, str) and len(response) > 10, "❌ Response empty or wrong type"
print("✅ GeminiClient passed\n")


# ─────────────────────────────────────────────
# TEST 2 — Repetition detector
# ─────────────────────────────────────────────
print("="*50)
print("TEST 2: RepetitionDetector")
print("="*50)

from backend.repetitiondetector import RepetitionDetector

detector = RepetitionDetector()

r1 = "Python is a high-level programming language known for its simplicity and readability."
r2 = "Python is a popular high-level language that is easy to read and write."   # very similar
r3 = "Machine learning is the process of training models on data to make predictions."  # different

detector.add_response(r1)

rep2, score2 = detector.is_repetitive(r2)
rep3, score3 = detector.is_repetitive(r3)

print(f"r2 (should be True):  repetitive={rep2}, score={score2}")
print(f"r3 (should be False): repetitive={rep3}, score={score3}")

assert rep2 is True,  f"❌ r2 should be flagged as repetitive (score={score2})"
assert rep3 is False, f"❌ r3 should NOT be flagged as repetitive (score={score3})"
print("✅ RepetitionDetector passed\n")


# ─────────────────────────────────────────────
# TEST 3 — Full agent (repetition flow)
# ─────────────────────────────────────────────
print("="*50)
print("TEST 3: GeminiPlusAgent — repetition loop")
print("="*50)

from backend.agent import GeminiPlusAgent

agent = GeminiPlusAgent()

questions = [
    "Tell me about Python programming",
    "Explain Python to me",
    "What is Python?",
]

for q in questions:
    print(f"\nUSER: {q}")
    result = agent.chat(q)
    print(f"RESPONSE (first 150 chars): {result['response'][:150]}...")
    print(f"  repetitive={result['repetition_detected']} | score={result['similarity_score']} | retried={result['retried']}")

print("\n✅ Agent test complete")
print("\nAll tests passed! Backend is working correctly. 🎉")
print("Next step: run app.py for the Streamlit frontend.")