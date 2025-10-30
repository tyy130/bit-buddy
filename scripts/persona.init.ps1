\
# scripts/persona.init.ps1
$ErrorActionPreference = "Stop"
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path "$PSScriptRoot\.."

$venv = Join-Path $root ".venv"
if (-not (Test-Path $venv)) { Write-Host "Run scripts\setup.ps1 first." -ForegroundColor Yellow; exit 1 }
$env:VIRTUAL_ENV = $venv
$env:PATH = "$venv\Scripts;$env:PATH"

python - << 'PY'
from app.persona import ensure_persona, load_persona
ensure_persona()
print(load_persona())
PY
