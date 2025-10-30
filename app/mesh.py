# app/mesh.py
import hashlib
import hmac
import ipaddress
import json
import os
import pathlib
import re

import requests
import yaml
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

ROOT = pathlib.Path(__file__).resolve().parent.parent
CUSTODIAN_DIR = ROOT / "custodian"
MANIFEST = yaml.safe_load(
    open(CUSTODIAN_DIR / "manifest.yaml", "r", encoding="utf-8")
)
POLICY = yaml.safe_load(
    open(CUSTODIAN_DIR / "policy.yaml", "r", encoding="utf-8")
)
PEERS = json.load(open(CUSTODIAN_DIR / "peers.json", "r", encoding="utf-8"))

KEY_PATH = CUSTODIAN_DIR / "secret.key"
if not KEY_PATH.exists():
    # generate a default key if missing (user should rotate ASAP)
    KEY_PATH.write_bytes(os.urandom(32))

SECRET = KEY_PATH.read_bytes()


def redactions(text: str) -> str:
    rules = POLICY.get("privacy", {}).get("redactions", [])
    out = text
    for r in rules:
        try:
            out = re.sub(r.get("pattern", ""), "[REDACTED]", out, flags=re.I)
        except re.error:
            pass
    return out


def origin_allowed(ip: str) -> bool:
    allow = POLICY.get("guardrails", {}).get("allowed_request_origins", [])
    if not allow:
        return True
    try:
        ipaddr = ipaddress.ip_address(ip)
        for cidr in allow:
            if ipaddr in ipaddress.ip_network(cidr, strict=False):
                return True
        return False
    except Exception:
        return False


def sign(payload: bytes) -> str:
    return hmac.new(SECRET, payload, hashlib.sha256).hexdigest()


def verify_signature(payload: bytes, hexdigest: str) -> bool:
    expected = sign(payload)
    return hmac.compare_digest(expected, hexdigest or "")


app = FastAPI(title="Custodian Mesh")


class AskIn(BaseModel):
    query: str
    k: int | None = 5


@app.get("/hello")
def hello():
    return {
        "id": MANIFEST.get("id"),
        "name": MANIFEST.get("name"),
        "owner": MANIFEST.get("owner"),
        "version": MANIFEST.get("version"),
        "llm_stick_version": MANIFEST.get("llm_stick_version"),
        "kb_ready": os.path.exists(
            ROOT / MANIFEST["storage"]["index_dir"] / "embeddings.npy"
        ),
    }


@app.get("/caps")
def caps():
    return {
        "generator": MANIFEST["models"]["generator"],
        "embedder": MANIFEST["models"]["embedder"],
        "share_policy": POLICY.get("share", {}),
    }


@app.post("/ask")
async def ask(request: Request, body: AskIn):
    # gate by origin
    client_ip = request.client.host if request.client else "0.0.0.0"
    if not origin_allowed(client_ip):
        raise HTTPException(status_code=403, detail="Origin not allowed")

    # optional signature check
    if MANIFEST["security"].get("require_signed_requests", True):
        raw = await request.body()
        sig = request.headers.get("X-Custodian-Signature", "")
        if not verify_signature(raw, sig):
            raise HTTPException(status_code=401, detail="Bad signature")

    # guard empty index
    index_dir = ROOT / MANIFEST["storage"]["index_dir"]
    if POLICY.get("guardrails", {}).get(
        "refuse_external_if_index_empty", True
    ):
        if not (index_dir / "embeddings.npy").exists():
            raise HTTPException(status_code=409, detail="Index not ready")

    # call local RAG API
    rag_url = "http://127.0.0.1:11434/chat"
    try:
        r = requests.post(
            rag_url, json={"query": body.query, "k": body.k or 5}, timeout=120
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"Local RAG not available: {e}"
        )

    # apply share policy
    share = POLICY.get("share", {})
    answer = data.get("answer", "")
    ctx = data.get("context", [])

    if not share.get("raw_text", False):
        # convert to abstractive-only by limiting and redacting
        max_snips = int(share.get("max_snippets", 3))
        max_chars = int(share.get("max_chars_per_snippet", 800))
        cited = []
        for c in ctx[:max_snips]:
            t = c.get("text", "")[:max_chars]
            if share.get("include_provenance", True):
                cited.append(
                    {
                        "path": c.get("path"),
                        "chunk_id": c.get("chunk_id"),
                        "text": redactions(t),
                    }
                )
            else:
                cited.append({"text": redactions(t)})
        # redact answer too (it may echo content)
        answer = redactions(answer)
        return {"summary": answer, "snippets": cited}

    # raw share allowed
    return {
        "answer": redactions(answer),
        "context": [
            {
                "path": c["path"],
                "chunk_id": c["chunk_id"],
                "text": redactions(c["text"]),
            }
            for c in ctx
        ],
    }
