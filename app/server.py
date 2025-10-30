# app/server.py
import os, json, requests
from fastapi import FastAPI
from pydantic import BaseModel
from .rag import RAG, load_config

cfg = load_config()
rag = RAG(cfg)

app = FastAPI(title="LLM Stick RAG")

class ChatIn(BaseModel):
    query: str
    k: int | None = 5

@app.post("/reindex")
def reindex():
    n_chunks = rag.build_index()
    return {"status": "ok", "chunks": n_chunks}

@app.post("/chat")
def chat(inp: ChatIn):
    ctx = rag.retrieve(inp.query, k=inp.k or 5)
    prompt = rag.build_prompt(inp.query, ctx)

    if cfg["llm"]["provider"] == "llamacpp":
        url = cfg["llm"]["llamacpp"]["base_url"].rstrip("/") + "/v1/chat/completions"
        payload = {
            "model": cfg["llm"]["llamacpp"]["model"],
            "messages": [
                {"role": "system", "content": "You are a concise assistant that only uses the provided context."},
                {"role": "user", "content": prompt}
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
        payload = {
            "model": cfg["llm"]["ollama"]["model"],
            "messages": [
                {"role": "system", "content": "You are a concise assistant that only uses the provided context."},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        text = data["message"]["content"]

    return {"answer": text, "context": ctx}
