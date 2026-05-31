import asyncio
import logging
import uuid
from datetime import datetime
from tempfile import NamedTemporaryFile

from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

from .chunker import chunk_text
from .config import CHUNK_OVERLAP, CHUNK_SIZE, MAX_WORDS, MIN_WORDS
from .pdf_loader import (
    extract_text_from_pdf,
    remove_after_conclusion,
    research_paper_score,
)
from .summarizer import summarize_paper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.getLogger("python_multipart").setLevel(logging.WARNING)

app = FastAPI(title="PaperHulk API")

job_progress = {}

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


@app.websocket("/ws/progress/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    await websocket.accept()

    try:
        while True:
            progress = job_progress.get(job_id)

            if progress:
                await websocket.send_json(progress)

                if progress.get("status") in ["done", "failed", "cancelled"]:
                    break

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for job: {job_id}")


@app.post("/summarize/start")
async def start_summary_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: str = Form("normal"),
    provider: str = Form("ollama"),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)

    job_id = str(uuid.uuid4())

    job_progress[job_id] = {
        "status": "starting",
        "completed": 0,
        "total": 1,
        "filename": file.filename,
        "file_size_mb": round(file_size_mb, 2),
        "summary": None,
        "cancelled": False,
    }

    background_tasks.add_task(
        run_summary_job,
        job_id,
        file.filename,
        content,
        mode,
        provider,
    )

    return {"job_id": job_id}


def run_summary_job(
    job_id: str,
    filename: str,
    content: bytes,
    mode: str,
    provider: str,
):
    try:
        logger.debug(f"Started summary job: {job_id}")

        with NamedTemporaryFile(delete=True, suffix=".pdf") as temp_file:
            temp_file.write(content)
            temp_file.flush()
            temp_file.seek(0)

            extracted_text = extract_text_from_pdf(temp_file)

        cleaned_text = remove_after_conclusion(extracted_text)

        if not cleaned_text:
            job_progress[job_id].update(
                {
                    "status": "failed",
                    "error": "No readable text found in PDF",
                }
            )
            return

        score = research_paper_score(cleaned_text)
        word_count = len(cleaned_text.split())

        if score < 4:
            if word_count < MIN_WORDS:
                job_progress[job_id].update(
                    {
                        "status": "failed",
                        "error": "This PDF does not look like a research paper",
                    }
                )
                return

            if word_count > MAX_WORDS:
                job_progress[job_id].update(
                    {
                        "status": "failed",
                        "error": "Research paper is too large for local summarization",
                    }
                )
                return

        chunks = chunk_text(cleaned_text, CHUNK_SIZE, CHUNK_OVERLAP)
        total_steps = len(chunks) + 1

        job_progress[job_id].update(
            {
                "status": "running",
                "completed": 0,
                "total": total_steps,
                "word_count": word_count,
                "chunk_count": len(chunks),
            }
        )

        def update_progress(completed: int):
            if job_progress[job_id].get("cancelled"):
                raise RuntimeError("Summarization cancelled by user")
            job_progress[job_id].update(
                {
                    "status": "running",
                    "completed": completed,
                    "total": total_steps,
                }
            )

        summary = summarize_paper(
            chunks,
            mode=mode,
            provider=provider,
            progress_callback=update_progress,
        )

        job_progress[job_id].update(
            {
                "status": "done",
                "completed": total_steps,
                "total": total_steps,
                "filename": filename,
                "mode": mode,
                "provider": provider,
                "word_count": word_count,
                "chunk_count": len(chunks),
                "summary": summary,
                "timestamp": datetime.now().isoformat(),
            }
        )

        logger.debug(f"Summary job completed: {job_id}")

    except Exception as err:
        logger.exception("Unexpected error during background summarization job")
        
        if job_progress[job_id].get("cancelled"):
            job_progress[job_id].update(
                {
                    "status": "cancelled",
                    "error": "Summarization cancelled by user",
                }
            )
        else:
            job_progress[job_id].update(
                {
                    "status": "failed",
                    "error": str(err),
                }
            )


@app.post("/summarize")
async def summarize_pdf(
    file: UploadFile = File(...),
    mode: str = Form("normal"),
    provider: str = Form("ollama"),
):
    logger.debug("Received summarize request")

    if not file.filename.endswith(".pdf"):
        logger.warning("Uploaded file is not a PDF")
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        with NamedTemporaryFile(delete=True, suffix=".pdf") as temp_file:
            logger.debug("Created temporary PDF file")
            content = await file.read()
            file_size_mb = len(content) / (1024 * 1024)

            logger.debug(f"Uploaded file size: {file_size_mb:.2f} MB")

            temp_file.write(content)
            temp_file.flush()
            temp_file.seek(0)

            extracted_text = extract_text_from_pdf(temp_file)

        cleaned_text = remove_after_conclusion(extracted_text)

        if not cleaned_text:
            raise HTTPException(status_code=400, detail="No readable text found in PDF")

        score = research_paper_score(cleaned_text)
        word_count = len(cleaned_text.split())

        if score < 4:
            if word_count < MIN_WORDS:
                raise HTTPException(
                    status_code=400,
                    detail="This PDF does not look like a research paper",
                )

            if word_count > MAX_WORDS:
                raise HTTPException(
                    status_code=400,
                    detail="Research paper is too large for local summarization",
                )

        chunks = chunk_text(cleaned_text, CHUNK_SIZE, CHUNK_OVERLAP)

        summary = await run_in_threadpool(
            summarize_paper,
            chunks,
            mode,
            provider,
        )

        return {
            "filename": file.filename,
            "mode": mode,
            "provider": provider,
            "word_count": word_count,
            "chunk_count": len(chunks),
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as err:
        logger.exception("Unexpected error during summarization pipeline")
        raise HTTPException(status_code=500, detail=str(err))

@app.post("/summarize/jobs/{job_id}/cancel")
def cancel_summary_job(job_id: str):
    if job_id not in job_progress:
        raise HTTPException(status_code=404, detail="Job not found")

    job_progress[job_id]["cancelled"] = True
    job_progress[job_id]["status"] = "cancelling"

    return {"status": "cancelling"}