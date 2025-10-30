\
param(
  [Parameter(Mandatory=$true)][string]$PackagePath
)
# scripts/upgrade.ps1 — apply a local upgrade zip safely
$ErrorActionPreference = "Stop"
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path "$PSScriptRoot\.."

if (-not (Test-Path $PackagePath)) { throw "Missing upgrade package" }

$staging = Join-Path $root "_staging"
if (Test-Path $staging) { Remove-Item $staging -Recurse -Force }
New-Item -ItemType Directory -Path $staging | Out-Null

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory($PackagePath, $staging)

# Basic allowlist: only app/, scripts/, custodian/.
$allowed = @("app", "scripts", "custodian")
Get-ChildItem $staging | ForEach-Object {
  if ($allowed -notcontains $_.Name) {
    Write-Host "Skipping disallowed: $($_.Name)"
    Remove-Item $_.FullName -Recurse -Force
  }
}

# Copy
Copy-Item -Path (Join-Path $staging "*") -Destination $root -Recurse -Force
Remove-Item $staging -Recurse -Force
Write-Host "⬆️ Upgrade applied." -ForegroundColor Green
