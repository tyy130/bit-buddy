\
# scripts/serve.ps1
$ErrorActionPreference = "Stop"
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path "$PSScriptRoot\.."

# Activate venv
$venv = Join-Path $root ".venv"
if (-not (Test-Path $venv)) { Write-Host "Run scripts\setup.ps1 first." -ForegroundColor Yellow; exit 1 }
$env:VIRTUAL_ENV = $venv
$env:PATH = "$venv\Scripts;$env:PATH"

# Run FastAPI
python -m uvicorn app.server:app --host 127.0.0.1 --port 11434
