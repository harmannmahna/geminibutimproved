import os
from google import genai
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Works both locally (.env) and on Streamlit Cloud (secrets)
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


class GeminiClient:
    def __init__(self):
        # FIX: Changed from 'gemini-1.5-flash-latest' to 'gemini-1.5-flash'
        # Alternatively, use 'gemini-2.5-flash' for the latest model version
        self.model = "gemini-2.0-flash-lite"
        self.history = []

    def send_message(self, message: str) -> str:
        self.history.append({"role": "user", "parts": [{"text": message}]})
        response = client.models.generate_content(
            model=self.model,
            contents=self.history,
        )
        reply = response.text
        self.history.append({"role": "model", "parts": [{"text": reply}]})
        return reply

    def send_with_diversity_prompt(self, original_message: str) -> str:
        injected = (
            f"{original_message}\n\n"
            "[SYSTEM NOTE: Your previous response was too similar to an earlier one. "
            "Please approach this from a completely different angle — use different examples, "
            "vary your structure, and change your vocabulary significantly.]"
        )
        return self.send_message(injected)

    def reset_chat(self):
        self.history = []