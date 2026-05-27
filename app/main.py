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
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.getLogger("python_multipart").setLevel(logging.WARNING)

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
    logger.debug(f"Received summarize request")

    if not file.filename.endswith(".pdf"):
        logger.warning("Uploaded file is not a PDF")
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        with NamedTemporaryFile(delete=True, suffix=".pdf") as temp_file:
            logger.debug("Created temporary PDF file")
            content = await file.read()
            logger.debug(f"Read uploaded file bytes: {len(content)}")

            temp_file.write(content)
            temp_file.flush()
            temp_file.seek(0)

            extracted_text = extract_text_from_pdf(temp_file)

        logger.debug("PDF text extracted successfully")
        cleaned_text = remove_after_conclusion(extracted_text)
        logger.debug("Extracted text cleaned successfully")

        if not cleaned_text:
            logger.warning("No readable text found in PDF")
            raise HTTPException(status_code=400, detail="No readable text found in PDF")

        score = research_paper_score(cleaned_text)

        word_count = len(cleaned_text.split())
        
        if score < 4: 
            if word_count < MIN_WORDS:
                logger.warning("PDF does not look like a research paper")
                raise HTTPException(status_code=400, detail="This PDF does not look like a research paper")
            
            if word_count > MAX_WORDS:
                logger.warning("Research paper too large for local summarization")
                raise HTTPException(status_code=400, detail="Research paper is too large for local summarization")

        
        chunks = chunk_text(cleaned_text, CHUNK_SIZE, CHUNK_OVERLAP)
        logger.debug(f"Chunking completed successfully: {len(chunks)} chunks created")

        summary = summarize_chunks(chunks, mode=mode)
        logger.debug("Summarization completed successfully")

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
        logger.exception("Unexpected error during summarization pipeline")
        raise HTTPException(status_code=500, detail=str(err))