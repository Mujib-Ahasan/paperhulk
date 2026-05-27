import ollama
from .config import MODEL_NAME 

def generate_response(prompt: str) -> str:
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response["message"]["content"]

    except Exception as e:
        raise RuntimeError(f"Failed to connect with Ollama: {e}") from e