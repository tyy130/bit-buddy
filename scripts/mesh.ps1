\
# scripts/mesh.ps1
$ErrorActionPreference = "Stop"
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path "$PSScriptRoot\.."

# Activate venv from the LLM Stick
$venv = Join-Path $root ".venv"
if (-not (Test-Path $venv)) { Write-Host "Run scripts\setup.ps1 first (from llm-stick root)." -ForegroundColor Yellow; exit 1 }
$env:VIRTUAL_ENV = $venv
$env:PATH = "$venv\Scripts;$env:PATH"

# Launch mesh API
python -m uvicorn app.mesh:app --host 0.0.0.0 --port 11500
