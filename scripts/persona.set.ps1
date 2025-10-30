\
# scripts/persona.set.ps1
param(
  [Parameter(Mandatory=$true)][string]$Patch
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
from app.persona import patch_persona
patch = json.loads(sys.argv[1])
print(patch_persona(patch))
PY
