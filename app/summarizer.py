from .ai_client import generate_response
from .prompts import (
    technical_summary_prompt,
    simple_summary_prompt,
    final_summary_prompt,
)


def summarize_chunk(chunk: str, mode: str = "technical", provider: str = "ollama",) -> str:
    """Summarize a single text chunk."""

    if not chunk or not chunk.strip():
        return ""

    if mode == "simple":
        prompt = simple_summary_prompt(chunk)
    else:
        prompt = technical_summary_prompt(chunk)

    summary = generate_response(prompt, provider=provider)

    return summary.strip()


def summarize_chunks(chunks: list[str], mode: str = "technical", provider: str = "ollama", progress_callback=None,) -> list[str]:
    """Summarize all chunks one by one."""

    chunk_summaries = []

    for index, chunk in enumerate(chunks, start=1):
        summary = summarize_chunk(chunk, mode, provider)

        if summary:
            chunk_summaries.append(
                f"Chunk {index} Summary:\n{summary}"
            )

        if progress_callback:
            progress_callback(index)

    return chunk_summaries


def generate_final_summary(chunk_summaries: list[str], mode: str = "technical", provider: str = "ollama",) -> str:
    """Generate final summary from all chunk summaries."""

    if not chunk_summaries:
        return "No chunk summaries available to generate final summary."

    combined_summary = "\n\n".join(chunk_summaries)

    prompt = final_summary_prompt(combined_summary, mode)

    final_summary = generate_response(prompt, provider=provider)

    return final_summary.strip()


def summarize_paper(chunks: list[str], mode: str = "technical", provider: str = "ollama", progress_callback=None,) -> str:
    """Full paper summarization workflow."""

    if not chunks:
        return "No chunks found to summarize."

    chunk_summaries = summarize_chunks(
        chunks,
        mode,
        provider,
        progress_callback,)

    final_summary = generate_final_summary(
        chunk_summaries,
        mode,
        provider,
    )

    if progress_callback:
        progress_callback(len(chunks) + 1)

    return final_summary