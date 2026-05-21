import ollama

MODEL_NAME = "qwen3:4b"

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
        return f"Failed to connect with Ollama: {e}"