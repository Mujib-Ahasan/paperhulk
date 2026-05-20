
def chunk_text(text: str, chunk_size: int = 2500, overlap: int = 200) -> list[str]:
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) <= chunk_size:
            current_chunk += paragraph + "\n\n"
        else:
            if len(current_chunk.strip()) > 300:
                chunks.append(current_chunk.strip())

            overlap_text = current_chunk[-overlap:] if overlap > 0 else ""
            current_chunk = overlap_text + "\n\n" + paragraph + "\n\n"

    if len(current_chunk.strip()) > 300:
        chunks.append(current_chunk.strip())

    return chunks