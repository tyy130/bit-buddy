\
# scripts/index.ps1
$ErrorActionPreference = "Stop"
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path "$PSScriptRoot\.."

# Activate venv
$env:VIRTUAL_ENV = "$root\.venv"
$env:PATH = "$root\.venv\Scripts;$env:PATH"

# Call /reindex via local import to avoid server roundtrip
python - << 'PY'
from app.rag import load_config, RAG
cfg = load_config()
rag = RAG(cfg)
n = rag.build_index()
print(f"Indexed chunks: {n}")
PY
