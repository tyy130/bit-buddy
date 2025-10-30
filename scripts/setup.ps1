\
# scripts/setup.ps1
$ErrorActionPreference = "Stop"
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path "$PSScriptRoot\.."

# Create venv on the USB
python -m venv "$root\.venv"
$env:VIRTUAL_ENV = "$root\.venv"
$env:PATH = "$root\.venv\Scripts;$env:PATH"

# Upgrade pip and install requirements locally to the USB
python -m pip install --upgrade pip
pip install -r "$root\requirements.txt"

Write-Host "✅ Environment ready in $root\.venv" -ForegroundColor Green
