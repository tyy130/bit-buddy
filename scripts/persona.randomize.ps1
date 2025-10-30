\
# scripts/persona.randomize.ps1
param(
  [string]$BoundsJson = "{}"
)
$ErrorActionPreference = "Stop"
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path "$PSScriptRoot\.."

$venv = Join-Path $root ".venv"
if (-not (Test-Path $venv)) { Write-Host "Run scripts\setup.ps1 first." -ForegroundColor Yellow; exit 1 }
$env:VIRTUAL_ENV = $venv
$env:PATH = "$venv\Scripts;$env:PATH"

python - << 'PY'
import json, sys
from app.persona import randomize_persona
bounds = json.loads(r'''{}''')
print(randomize_persona(bounds))
PY
