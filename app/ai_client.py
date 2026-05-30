from .providers.ollama_provider import generate_response as generate_with_ollama
from .providers.gemini_provider import generate_response as generate_with_gemini


def generate_response(prompt: str, provider: str = "ollama") -> str:
    if provider == "gemini":
        return generate_with_gemini(prompt)

    if provider == "ollama":
        return generate_with_ollama(prompt)

    raise ValueError(f"Unsupported AI provider: {provider}")