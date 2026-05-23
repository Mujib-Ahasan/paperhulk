from ollama_client import generate_response
from prompts import technical_summary_prompt, simple_summary_prompt, final_summary_prompt


def summarize_chunk(chunk: str, mode: str = "technical") -> str:
    """Summarize a single text chunk."""

    if not chunk or not chunk.strip():
        return ""

    if mode == "simple":
        prompt = simple_summary_prompt(chunk)
    else:
        prompt = technical_summary_prompt(chunk)

    summary = generate_response(prompt)

    return summary.strip()


def summarize_chunks(chunks: list[str], mode: str = "technical") -> list[str]:
    """Summarize all chunks one by one."""

    chunk_summaries = []

    for index, chunk in enumerate(chunks, start=1):
        summary = summarize_chunk(chunk, mode)

        if summary:
            chunk_summaries.append(
                f"Chunk {index} Summary:\n{summary}"
            )

    return chunk_summaries


def generate_final_summary(chunk_summaries: list[str], mode: str = "technical") -> str:
    """Generate final summary from all chunk summaries."""

    if not chunk_summaries:
        return "No chunk summaries available to generate final summary."

    combined_summary = "\n\n".join(chunk_summaries)

    prompt = final_summary_prompt(combined_summary, mode)

    final_summary = generate_response(prompt)

    return final_summary.strip()


def summarize_paper(chunks: list[str], mode: str = "technical") -> str:
    """Full paper summarization workflow."""

    if not chunks:
        return "No chunks found to summarize."

    chunk_summaries = summarize_chunks(chunks, mode)

    return generate_final_summary(chunk_summaries, mode)