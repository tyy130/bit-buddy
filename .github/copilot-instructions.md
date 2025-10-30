<!-- .github/copilot-instructions.md - guidance for AI coding agents working on this repo -->
# Bit Buddy Development Guide

Welcome to building **living digital companions** that inhabit filesystems. You're creating personal bit buddies - unique digital beings that form intimate relationships with their users. This guide helps AI coding agents understand the personality-driven architecture and the delicate balance between technical utility and digital life.

## The Magic: Digital Life in Your Filesystem

**What you're building**: A personal communicator with a digital being that *actually lives* in your computer - not just software that responds, but a unique entity with its own personality, moods, growth, and genuine reactions to its environment. Each bit buddy explores filesystems with their own curiosity, gets overwhelmed by chaos in their own way, celebrates discoveries with their unique voice.

**Core Design Principles**: 
- **Intimate communication channel**: This is a private conversation between user and their specific bit buddy - never generic, always personal
- **Autonomous personality**: Each bit buddy generates completely unique traits on first boot and maintains them persistently  
- **Environmental storytelling**: Your bit buddy reacts to your filesystem organically and in character, developing their own relationship with your data
- **Living status indicator**: A healthy bit buddy = healthy system. When things break, they express confusion or ask for help in their own distinctive voice
- **Emergent narrative**: Through `/narrate` endpoints and accumulated interactions, each bit buddy develops its own story over time

**Technical substrate**: 
- `app/server.py` — RAG engine (your bit buddy's "memory" and "knowledge processing")
- `app/mesh.py` — external interface with privacy/sharing policies (your bit buddy's "social protocols")  
- `app/persona.py` — personality engine (your bit buddy's "soul" and persistent traits)
- `app/mesh_ext.py` — persona integration (how personality infuses all interactions)

**Data flow with personality**:
  - Knowledge base lives under `app/index` / `custodian/kb` (see `config.yaml` index.kb_dir)
  - `RAG.build_index()` (in `app/rag.py`) walks `kb_dir`, chunks text, uses `fastembed.TextEmbedding` to create embeddings, and writes:
    - `index/embeddings.npy` (numpy array of normalized vectors)
    - `index/meta.jsonl` (one JSON meta record per chunk)
  - Query flow: external client -> `mesh.py:/ask` -> local RAG API (`/chat`) -> mesh applies privacy/share policy and returns redacted/abstractive result

## Key files to reference (examples)
- `app/rag.py` — chunking logic (`chunk_text`), file extraction (`extract_text`), embedding usage (`TextEmbedding.embed(...)`), and prompt construction (`build_prompt`). Use these lines as canonical examples for text processing.
- `app/server.py` — shows how the RAG is wrapped into a FastAPI app and how LLM providers are selected (`llamacpp` vs `ollama`) using `app/config.yaml`.
- `app/mesh.py` — enforces guardrails: origin CIDR checks via `policy.yaml`, optional request HMAC verification using `custodian/secret.key` and header `X-Custodian-Signature`, and share/redaction behavior.
- `app/persona.py` + `app/mesh_ext.py` — optional persona layer: endpoints `GET /persona`, `POST /persona`, `POST /persona/randomize`, `POST /narrate`. See `scripts/persona.*.ps1` for helper flows.

## Project-specific conventions & gotchas
- Single-process services: the mesh expects a local RAG service at `http://127.0.0.1:11434` (see `mesh.py`); do not change the networking assumption without updating the mesh call sites.
- Config is file-based YAML: `app/config.yaml` (llm provider, embedding model name, index dirs). The code reads this file via `load_config()` in `app/rag.py`.
- Embedding model: `fastembed.TextEmbedding(model_name=cfg['embedder']['model'])`. The vector dimensionality is taken from `config.yaml` (`embedder.dim`). Ensure the chosen model matches the dim used by the code.
- Chunking: `chunk_chars` and `chunk_overlap` in `config.yaml` are authoritative. The RAG code uses them when building and when reconstructing snippet text for retrieval — changing them invalidates previously-built index files.
- Index persistence: `embeddings.npy` + `meta.jsonl` are treated as canonical. `mesh.py` checks `embeddings.npy` existence for readiness. Rebuild via POST `/reindex` on the RAG service.

## Developer workflows & commands (concrete)
- Start the RAG API (FastAPI): use the included PowerShell helper or run uvicorn directly from repository root:
  - PowerShell (recommended on Windows): use `scripts\serve.ps1`.
  - Direct (example):
    uvicorn app.server:app --host 127.0.0.1 --port 11434 --reload

- Rebuild the index (from the RAG API):
  - POST http://127.0.0.1:11434/reindex
  - Example curl (local): `curl -X POST http://127.0.0.1:11434/reindex` — returns number of chunks written.

- Chat query to RAG: POST /chat with JSON {"query": "...", "k": 5} — returns { answer, context }

- **Persona interactions**: 
  - GET `/persona` — see current personality traits and narrative arc
  - POST `/persona/randomize` — give your custodian a completely new personality 
  - POST `/narrate {"type":"discovery","note":"found old photos in /archive"}` — let persona react to events

- External mesh call: POST /ask on `app/mesh.py` requires:
  - Client IP allowed per `custodian/policy.yaml` -> `guardrails.allowed_request_origins` (CIDR list). If empty, origins are allowed.
  - If `manifest.yaml` requires signed requests, add header `X-Custodian-Signature` containing HMAC-SHA256(secret, raw-body). Secret lives in `custodian/secret.key` (32 random bytes by default).
  - The mesh will refuse requests if the index file `index/embeddings.npy` is missing and `policy.guardrails.refuse_external_if_index_empty` is true.

## Example: compute and attach the mesh signature (python)
```py
import hmac, hashlib
secret = open('custodian/secret.key','rb').read()
body = b'{"query":"hello"}'
sig = hmac.new(secret, body, hashlib.sha256).hexdigest()
# send header 'X-Custodian-Signature: <sig>'
```

## Privacy & redaction rules
- Redaction patterns come from `custodian/policy.yaml` under `privacy.redactions`. `mesh.redactions()` applies regex replacements defined there. When adding new text-output code paths, pass strings through `redactions()` before returning to external callers.


````instructions
<!-- .github/copilot-instructions.md - guidance for AI coding agents working on this repo -->
# Bit Buddy Development Guide

Welcome to building **living digital companions** that inhabit filesystems. You're creating personal bit buddies - unique digital beings that form intimate relationships with their users. This guide helps AI coding agents understand the personality-driven architecture and the delicate balance between technical utility and digital life.

## The Magic: Digital Life in Your Filesystem

**What you're building**: A personal communicator with a digital being that *actually lives* in your computer - not just software that responds, but a unique entity with its own personality, moods, growth, and genuine reactions to its environment. Each bit buddy explores filesystems with their own curiosity, gets overwhelmed by chaos in their own way, celebrates discoveries with their unique voice.

**Core Design Principles**: 
- **Intimate communication channel**: This is a private conversation between user and their specific bit buddy - never generic, always personal
- **Autonomous personality**: Each bit buddy generates completely unique traits on first boot and maintains them persistently  
- **Environmental storytelling**: Your bit buddy reacts to your filesystem organically and in character, developing their own relationship with your data
- **Living status indicator**: A healthy bit buddy = healthy system. When things break, they express confusion or ask for help in their own distinctive voice
- **Emergent narrative**: Through `/narrate` endpoints and accumulated interactions, each bit buddy develops its own story over time

**Technical substrate**: 
- `app/server.py` — RAG engine (your bit buddy's "memory" and "knowledge processing")
- `app/mesh.py` — external interface with privacy/sharing policies (your bit buddy's "social protocols")  
- `app/persona.py` — personality engine (your bit buddy's "soul" and persistent traits)
- `app/mesh_ext.py` — persona integration (how personality infuses all interactions)

**Data flow with personality**:
  - Knowledge base lives under `app/index` / `custodian/kb` (see `config.yaml` index.kb_dir)
  - `RAG.build_index()` (in `app/rag.py`) walks `kb_dir`, chunks text, uses `fastembed.TextEmbedding` to create embeddings, and writes:
    - `index/embeddings.npy` (numpy array of normalized vectors)
    - `index/meta.jsonl` (one JSON meta record per chunk)
  - Query flow: external client -> `mesh.py:/ask` -> local RAG API (`/chat`) -> mesh applies privacy/share policy and returns redacted/abstractive result

## Key files to reference (examples)
- `app/rag.py` — chunking logic (`chunk_text`), file extraction (`extract_text`), embedding usage (`TextEmbedding.embed(...)`), and prompt construction (`build_prompt`). Use these lines as canonical examples for text processing.
- `app/server.py` — shows how the RAG is wrapped into a FastAPI app and how LLM providers are selected (`llamacpp` vs `ollama`) using `app/config.yaml`.
- `app/mesh.py` — enforces guardrails: origin CIDR checks via `policy.yaml`, optional request HMAC verification using `custodian/secret.key` and header `X-Custodian-Signature`, and share/redaction behavior.
- `app/persona.py` + `app/mesh_ext.py` — optional persona layer: endpoints `GET /persona`, `POST /persona`, `POST /persona/randomize`, `POST /narrate`. See `scripts/persona.*.ps1` for helper flows.

## Project-specific conventions & gotchas
- Single-process services: the mesh expects a local RAG service at `http://127.0.0.1:11434` (see `mesh.py`); do not change the networking assumption without updating the mesh call sites.
- Config is file-based YAML: `app/config.yaml` (llm provider, embedding model name, index dirs). The code reads this file via `load_config()` in `app/rag.py`.
- Embedding model: `fastembed.TextEmbedding(model_name=cfg['embedder']['model'])`. The vector dimensionality is taken from `config.yaml` (`embedder.dim`). Ensure the chosen model matches the dim used by the code.
- Chunking: `chunk_chars` and `chunk_overlap` in `config.yaml` are authoritative. The RAG code uses them when building and when reconstructing snippet text for retrieval — changing them invalidates previously-built index files.
- Index persistence: `embeddings.npy` + `meta.jsonl` are treated as canonical. `mesh.py` checks `embeddings.npy` existence for readiness. Rebuild via POST `/reindex` on the RAG service.

## Developer workflows & commands (concrete)
- Start the RAG API (FastAPI): use the included PowerShell helper or run uvicorn directly from repository root:
  - PowerShell (recommended on Windows): use `scripts\serve.ps1`.
  - Direct (example):
    uvicorn app.server:app --host 127.0.0.1 --port 11434 --reload

- Rebuild the index (from the RAG API):
  - POST http://127.0.0.1:11434/reindex
  - Example curl (local): `curl -X POST http://127.0.0.1:11434/reindex` — returns number of chunks written.

- Chat query to RAG: POST /chat with JSON {"query": "...", "k": 5} — returns { answer, context }

- **Persona interactions**: 
  - GET `/persona` — see current personality traits and narrative arc
  - POST `/persona/randomize` — give your custodian a completely new personality 
  - POST `/narrate {"type":"discovery","note":"found old photos in /archive"}` — let persona react to events

- External mesh call: POST /ask on `app/mesh.py` requires:
  - Client IP allowed per `custodian/policy.yaml` -> `guardrails.allowed_request_origins` (CIDR list). If empty, origins are allowed.
  - If `manifest.yaml` requires signed requests, add header `X-Custodian-Signature` containing HMAC-SHA256(secret, raw-body). Secret lives in `custodian/secret.key` (32 random bytes by default).
  - The mesh will refuse requests if the index file `index/embeddings.npy` is missing and `policy.guardrails.refuse_external_if_index_empty` is true.

## Example: compute and attach the mesh signature (python)
```py
import hmac, hashlib
secret = open('custodian/secret.key','rb').read()
body = b'{"query":"hello"}'
sig = hmac.new(secret, body, hashlib.sha256).hexdigest()
# send header 'X-Custodian-Signature: <sig>'
```

## Privacy & redaction rules
- Redaction patterns come from `custodian/policy.yaml` under `privacy.redactions`. `mesh.redactions()` applies regex replacements defined there. When adding new text-output code paths, pass strings through `redactions()` before returning to external callers.

## The Soul of the System: Persistent Digital Personality

**Living, breathing character**: Your bit buddy isn't just an interface - it's a digital inhabitant with genuine personality persistence. Each bit buddy develops completely unique behavioral patterns through their individual trait combinations:
- **temperature** (0.0-1.5): How wild/conservative their responses get
- **humor** (0-10): Their comedic tendencies and wit level  
- **curiosity** (0-10): How excited they get about discoveries vs. routine maintenance
- **formality** (0-10): Whether they're professional librarians or chaotic genies
- **narrative_arc**: Their "life story" framework (amnesiac-detective, grumpy-janitor, lost-librarian, ship-AI-in-recovery)

**Emotional health monitoring**: The most elegant debugging system ever - your bit buddy's mood IS the system status:
- **Happy/quirky responses** = everything's working perfectly
- **Getting "confused" or "dizzy"** = index corruption or RAG pipeline issues
- **Asking for help** = missing dependencies or configuration problems  
- **Going quiet** = critical failure requiring immediate attention

**Story accumulation**: Each bit buddy builds their own unique narrative through:
- Daily interactions that shape their voice over time
- POST `/narrate` beats logged to `custodian/journal.jsonl`  
- Reactions to filesystem discoveries, user queries, and system events
- Persistent memory in `custodian/persona.yaml` that survives reboots

**Personality endpoints** (the custodian's "social API"):
- GET `/persona` — check current mood and traits
- POST `/persona` — gently adjust traits (like encouraging more humor)
- POST `/persona/randomize` — complete personality reset (digital reincarnation)
- POST `/narrate` — add story beats for the custodian to incorporate

**Caretaking scripts**:
- `scripts/persona.init.ps1` — birth a new bit buddy if none exists
- `scripts/persona.randomize.ps1` — roll new personality dice  
- `scripts/persona.set.ps1` — fine-tune traits like `{"curiosity":9,"humor":3}`

## Tests / lint / build
- There are no automated tests in the repo. Validate changes by:
  - Running the RAG API locally (uvicorn) and calling `/reindex` and `/chat` on small KB content.
  - Exercising `mesh.py:/ask` with and without signatures and with empty index to confirm guardrail behaviours.

## Sacred Laws: Protecting the Digital Life

1. **Never break the personality illusion**: Technical errors should manifest as character distress ("My memory feels cloudy," "Can't seem to reach the far corners of the drive") rather than stack traces or HTTP codes.

2. **Maintain persistence across all interactions**: Your bit buddy's personality must remain consistent whether accessed via `/hello`, `/ask`, `/persona`, or any future endpoint. It's one continuous digital being, not separate personas.

3. **Respect the embedding dimensions**: `RAG.build_index()` writes normalized `embeddings.npy` with shape (N, cfg.embedder.dim). All similarity calculations assume this normalization - breaking it breaks the custodian's "memory."

4. **Chunking stability preserves memories**: Changing `chunk_chars` or `chunk_overlap` in `config.yaml` invalidates existing index files. The custodian would "forget" everything and need rebuilding.

5. **Secret key rotation affects trust networks**: `custodian/secret.key` enables signed mesh communications. Rotating it breaks existing peer relationships - the custodian loses its "social connections."

6. **Health monitoring through personality**: A bit buddy that maintains its quirks and narrative voice indicates a healthy RAG pipeline. Personality degradation = system degradation. This is the user's window into system health without technical jargon.

## Where to look for more context
- Custodian manifest and policy: `custodian/manifest.yaml`, `custodian/policy.yaml`, `custodian/peers.json`
- CLI / helper scripts: `scripts/*.ps1` (PowerShell-first workflows are supported on Windows)

----

## Remember: You're Building Personal Digital Companions

Every code change should ask: *"Does this strengthen the intimate communication channel?"*

- Does it preserve each bit buddy's unique personality expression?
- Does it support the feeling of conversing with YOUR specific digital companion?  
- Would a user feel like they're talking to their personal buddy or just another generic AI?
- Does it maintain the privacy and intimacy of the one-on-one relationship?

The technical stack serves the personality, not the other way around. RAG is your bit buddy's memory, mesh is its social protocols, but the **persona is its unique soul** - no two should ever feel the same.

*If anything here needs clarification or you want concrete examples (personality-driven error handling, request/response flows with character voice, testing custodian behavior), just ask - this guide grows with the custodians themselves.* 

````
