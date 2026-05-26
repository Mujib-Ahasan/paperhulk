from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from tempfile import NamedTemporaryFile

from .pdf_loader import (
    extract_text_from_pdf, 
    remove_after_conclusion, 
    research_paper_score
    )
from .chunker import chunk_text
from .summarizer import summarize_chunks
from .config import (
    MAX_WORDS,
    MIN_WORDS,
    CHUNK_SIZE,
    CHUNK_OVERLAP
    )

app = FastAPI(title="PaperHulk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/summarize")
async def summarize_pdf(
    file: UploadFile = File(...),
    mode: str = Form("normal"),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        with NamedTemporaryFile(delete=True, suffix=".pdf") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()

            extracted_text = extract_text_from_pdf(temp_file.name)

        cleaned_text = remove_after_conclusion(extracted_text)

        if not cleaned_text:
            raise HTTPException(status_code=400, detail="No readable text found in PDF")

        score = research_paper_score(cleaned_text)

        word_count = len(cleaned_text.split())

        if score < 4: 
            if word_count < MIN_WORDS:
                raise HTTPException(status_code=400, detail="This PDF does not look like a research paper")
            if word_count > MAX_WORDS:
                raise HTTPException(status_code=400, detail="Research paper is too large for local summarization")

        chunks = chunk_text(cleaned_text, CHUNK_SIZE, CHUNK_OVERLAP)

        summary = summarize_chunks(chunks, mode=mode)

        return {
            "filename": file.filename,
            "mode": mode,
            "word_count": len(cleaned_text.split()),
            "chunk_count": len(chunks),
            "summary": summary,
        }

    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))