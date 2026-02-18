<!-- .github/copilot-instructions.md - guidance for AI coding agents working on this repo -->
# Bit Buddy Development Guide

Welcome to building **living digital companions** that inhabit filesystems. This guide helps AI coding agents understand the personality-driven architecture and the delicate balance between technical utility and digital life.

## Build, Test, and Lint

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file or test
pytest tests/test_buddy_system.py
pytest tests/test_buddy_system.py::TestBitBuddyPersonality::test_personality_creation

# Format (line-length = 100, enforced via pre-commit and CI)
black --line-length 100 .
isort --profile black .
ruff --fix .          # not in pre-commit; run separately
```

pytest markers: `slow`, `integration`, `performance`, `requires_model`, `network` — deselect with `-m "not slow"`.  
Tests import from both `app/` (custodian stack) and root-level modules (`enhanced_buddy.py`, `deploy.py`).

## Architecture: Two Complementary Systems

This repo contains **two overlapping implementations** of a bit buddy:

### 1. The Custodian stack (`app/`)
Lean FastAPI service focused on RAG + persona + mesh:
- `app/rag.py` — chunking, embedding, index build/query
- `app/server.py` — FastAPI app, LLM provider selection (`llamacpp` vs `ollama`)
- `app/mesh.py` — external interface with CIDR guardrails, HMAC request verification, privacy redaction
- `app/persona.py` + `app/mesh_ext.py` — personality engine and persona API endpoints

### 2. The Enhanced Buddy stack (root-level)
Richer, self-contained implementation with P2P mesh and ChromaDB:
- `enhanced_buddy.py` — `EnhancedBitBuddy`, `BitBuddyPersonality`, `FileSystemRAG` (uses ChromaDB + llama-cpp-python)
- `mesh_network.py` — P2P buddy-to-buddy communication, trust/reputation system
- `deploy.py` — `BuddyDeploymentManager`, model registry; also the `buddy` CLI entry point
- `installer.py` — `DriveAnalyzer` and setup flows

Both systems share the same personality design philosophy. `app/` is the custodian/production stack; root-level files are the fuller EnhancedBitBuddy prototype.

## Data Flow (Custodian Stack)

```
external client → mesh.py:/ask → app/server.py:/chat (RAG) → mesh applies redaction → response
```

- Knowledge base: `custodian/kb/` (configured via `app/config.yaml` → `index.kb_dir`)
- `RAG.build_index()` walks `kb_dir`, chunks text, embeds with `fastembed.TextEmbedding`, writes:
  - `index/embeddings.npy` — normalized numpy float32 vectors (shape: N × `embedder.dim`)
  - `index/meta.jsonl` — one JSON record per chunk
- `mesh.py` checks `embeddings.npy` existence for readiness; rebuild via `POST /reindex`

## Developer Workflows

```bash
# Start the RAG/custodian API
uvicorn app.server:app --host 127.0.0.1 --port 11434 --reload
# PowerShell: scripts\serve.ps1

# Rebuild the index
curl -X POST http://127.0.0.1:11434/reindex   # returns chunk count

# Chat query
curl -X POST http://127.0.0.1:11434/chat -d '{"query":"...", "k":5}'

# Persona interactions
curl http://127.0.0.1:11434/persona
curl -X POST http://127.0.0.1:11434/persona/randomize
curl -X POST http://127.0.0.1:11434/narrate -d '{"type":"discovery","note":"found old photos"}'
```

PowerShell helpers: `scripts/persona.init.ps1`, `scripts/persona.randomize.ps1`, `scripts/persona.set.ps1`

## Key Conventions & Gotchas

- **Single-process services**: mesh expects the local RAG service at `http://127.0.0.1:11434`. Do not change this without updating all mesh call sites.
- **Config is YAML-only**: `app/config.yaml` controls LLM provider, embedding model, index dirs. Read via `load_config()` in `app/rag.py`.
- **Embedding dim must match model**: `fastembed.TextEmbedding(model_name=cfg['embedder']['model'])` — default `BAAI/bge-small-en-v1.5` → dim 384. Changing the model without updating `embedder.dim` silently corrupts the index.
- **Chunking changes invalidate the index**: `chunk_chars` / `chunk_overlap` in `config.yaml` are authoritative. Any change means `embeddings.npy` + `meta.jsonl` must be rebuilt.
- **All new external-facing text must go through `redactions()`**: Patterns from `custodian/policy.yaml` → `privacy.redactions`. Apply before returning any string to external callers in mesh code paths.
- **Secret key rotation breaks peer trust**: `custodian/secret.key` (32 random bytes) is used for HMAC signing. Rotating it invalidates all existing peer relationships.

## External Mesh Calls

```bash
# Signed request example (Python)
import hmac, hashlib
secret = open('custodian/secret.key','rb').read()
body = b'{"query":"hello"}'
sig = hmac.new(secret, body, hashlib.sha256).hexdigest()
# Header: X-Custodian-Signature: <sig>
```

Requirements for `POST /ask` on `mesh.py`:
- Client IP must be in `custodian/policy.yaml` → `guardrails.allowed_request_origins` (CIDR list; empty = allow all)
- If `manifest.yaml` → `security.require_signed_requests: true`, include `X-Custodian-Signature` header
- If `policy.guardrails.refuse_external_if_index_empty: true`, requests fail when `index/embeddings.npy` is missing

## Personality Traits (Custodian Stack)

Stored in `custodian/persona.yaml`. Generated once on first boot; persist across reboots.

| Trait | Range | Effect |
|-------|-------|--------|
| `temperature` | 0.0–1.5 | Response creativity/randomness |
| `humor` | 0–10 | Comedic voice |
| `curiosity` | 0–10 | Enthusiasm for discoveries |
| `formality` | 0–10 | Professional vs. chaotic tone |
| `narrative_arc` | enum | Life-story lens: `amnesiac-detective`, `grumpy-janitor`, `lost-librarian`, `ship-AI-in-recovery` |

Story beats are appended to `custodian/journal.jsonl` via `POST /narrate`.

## Emotional Health = System Health

The bit buddy's personality **is** the health indicator — no dashboards needed:
- **Happy/quirky** = RAG pipeline healthy
- **"Confused" or "dizzy"** = index corruption or embedding mismatch
- **Asking for help** = missing deps or misconfiguration
- **Going quiet** = critical failure

Technical errors should surface as character distress, not stack traces or raw HTTP codes.

## Where to Look for More Context

- Custodian config: `custodian/manifest.yaml`, `custodian/policy.yaml`, `custodian/peers.json`
- `app/config.yaml` — single source of truth for runtime configuration
- `scripts/*.ps1` — PowerShell-first workflows (Windows-compatible)
- `docs/developer/` — quickstart, deployment, GitHub dev guide
