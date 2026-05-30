import os

import google.generativeai as genai

from ..config import GEMINI_MODEL


def generate_response(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)

    return response.text