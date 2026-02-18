# app/server.py

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .rag import RAG, load_config

cfg = load_config()
# Defer RAG construction to startup to avoid import-time failures when
# embeddings or external LLM services are not available. If initialization
# fails, `rag` will remain None and endpoints will return a 503 with an
# explanatory message.
rag: RAG | None = None
rag_init_error: str | None = None

app = FastAPI(title="LLM Stick RAG")
executor = ThreadPoolExecutor(max_workers=2)


def _ensure_rag() -> bool:
    """Ensure the global `rag` is initialized. Returns True on success.

    If initialization fails the function logs a warning and returns False.
    """
    global rag, rag_init_error
    if rag is not None:
        return True
    try:
        rag = RAG(cfg)
        rag_init_error = None
        return True
    except Exception as e:
        rag_init_error = str(e)
        logging.getLogger("app.server").warning("RAG initialization failed: %s", e)
        return False


class ChatIn(BaseModel):
    query: str
    k: int | None = 5


@app.post("/reindex")
async def reindex():
    if not _ensure_rag():
        raise HTTPException(
            status_code=503,
            detail="RAG service not available; initialization failed",
        )

    # Run build_index in thread pool to avoid blocking event loop
    loop = asyncio.get_event_loop()
    n_chunks = await loop.run_in_executor(executor, rag.build_index)
    return {"status": "ok", "chunks": n_chunks}


@app.post("/chat")
def chat(inp: ChatIn):
    if not _ensure_rag():
        raise HTTPException(
            status_code=503,
            detail="RAG service not available; initialization failed",
        )

    ctx = rag.retrieve(inp.query, k=inp.k or 5)
    prompt = rag.build_prompt(inp.query, ctx)

    if cfg["llm"]["provider"] == "llamacpp":
        base_url = cfg["llm"]["llamacpp"]["base_url"].rstrip("/")
        url = f"{base_url}/v1/chat/completions"
        system_msg = "You are a concise assistant that only uses " "the provided context."
        payload = {
            "model": cfg["llm"]["llamacpp"]["model"],
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 512,
        }
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        text = data["choices"][0]["message"]["content"]
    else:
        # Ollama
        url = cfg["llm"]["ollama"]["base_url"].rstrip("/") + "/api/chat"
        system_msg = "You are a concise assistant that only uses " "the provided context."
        payload = {
            "model": cfg["llm"]["ollama"]["model"],
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        text = data["message"]["content"]

    return {"answer": text, "context": ctx}


@app.get("/")
def root():
    """Root endpoint to help web users discover the RAG service."""
    return {
        "service": "LLM Stick RAG",
        "status": "ok",
        "endpoints": ["GET /", "GET /health", "POST /chat", "POST /reindex"],
        "note": (
            "This service exposes a small RAG API. "
            "Use /chat to query and /reindex to rebuild the index."
        ),
    }


@app.get("/health")
def health():
    """Health check endpoint for production readiness monitoring."""
    if rag is not None:
        return {
            "status": "healthy",
            "rag_initialized": True,
            "ready": True,
        }
    # Attempt lazy init to see if it would work
    if _ensure_rag():
        return {
            "status": "healthy",
            "rag_initialized": True,
            "ready": True,
        }
    return {
        "status": "unhealthy",
        "rag_initialized": False,
        "ready": False,
        "error": rag_init_error or "RAG initialization failed",
    }
