"""FastAPI service for the India Earthquake RAG prototype.

Run (from backend/):  uvicorn app.api.main:app --port 8000
"""
from __future__ import annotations

import logging
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ..config import PROJECT_ROOT, settings
from ..generation.llm import get_llm
from ..generation.rag import answer_question
from ..index.keyword import get_keyword_index
from ..index.vector_store import get_vector_store
from ..ingestion.pipeline import corpus_summary, ingest, refresh_keyword_index

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("api")
_ingest_lock = threading.Lock()

EXAMPLE_QUESTIONS = [
    "What information is available about the 2001 Gujarat earthquake?",
    "What does the Disaster Management Act 2005 say about disaster management?",
    "What earthquake information is available for Sikkim?",
    "Summarize the earthquake information available in the ISRO data.",
    "What emergency response information is present in the knowledge base?",
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    n = refresh_keyword_index()
    log.info("Keyword index ready (%d chunks). LLM: %s", n, get_llm().describe())
    if n == 0:
        log.warning("Knowledge base is empty – run `python -m scripts.ingest` or POST /api/ingest")
    yield
    get_vector_store().close()
    get_vector_store.cache_clear()


app = FastAPI(title="India Earthquake RAG", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    top_k: int | None = Field(None, ge=1, le=20)


class IngestRequest(BaseModel):
    rebuild: bool = False


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "chunks_indexed": get_vector_store().count(),
        "keyword_index_size": len(get_keyword_index()),
        "collection": settings.collection,
        "embedding_model": settings.embedding_model,
        "vector_db": f"Qdrant ({'server ' + settings.qdrant_url if settings.qdrant_url else 'embedded, on-disk'})",
        "llm": get_llm().describe(),
        "top_k": settings.top_k,
    }


@app.get("/api/corpus")
def corpus():
    return corpus_summary()


@app.get("/api/examples")
def examples():
    return {"examples": EXAMPLE_QUESTIONS}


@app.post("/api/ask")
def ask(req: AskRequest):
    if get_vector_store().count() == 0:
        raise HTTPException(503, "The knowledge base is empty. Run ingestion first.")
    try:
        return answer_question(req.question, top_k=req.top_k)
    except Exception as e:  # surface a clean error to the UI
        log.exception("ask failed")
        raise HTTPException(500, f"Internal error while answering: {e}") from e


@app.post("/api/ingest")
def run_ingest(req: IngestRequest):
    if not _ingest_lock.acquire(blocking=False):
        raise HTTPException(409, "Ingestion already running")
    try:
        report = ingest(rebuild=req.rebuild)
        return {k: report[k] for k in ("ingested", "skipped", "removed", "errors", "total_chunks")}
    finally:
        _ingest_lock.release()


# ---- serve the built React app (frontend/dist) if present -----------------
_DIST = PROJECT_ROOT / "frontend" / "dist"
if _DIST.exists():
    app.mount("/assets", StaticFiles(directory=_DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        f = _DIST / path
        return FileResponse(f if path and f.is_file() else _DIST / "index.html")
