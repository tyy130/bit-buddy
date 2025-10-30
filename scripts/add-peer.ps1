\
param(
  [Parameter(Mandatory=$true)][string]$Name,
  [Parameter(Mandatory=$true)][string]$Url,
  [string]$Pub = ""
)

$ErrorActionPreference = "Stop"
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path "$PSScriptRoot\.."

$pf = Join-Path $root "custodian\peers.json"
if (-not (Test-Path $pf)) { '{"peers":[]}' | Set-Content -Encoding UTF8 $pf }
$json = Get-Content -Raw $pf | ConvertFrom-Json
if (-not $json.peers) { $json | Add-Member -NotePropertyName peers -NotePropertyValue @() }

# Upsert by name
$existing = $json.peers | Where-Object { $_.id -eq $Name }
if ($existing) {
  $existing.url = $Url
  $existing.pub = $Pub
} else {
  $json.peers += @{ id = $Name; url = $Url; pub = $Pub }
}

($json | ConvertTo-Json -Depth 5) | Set-Content -Encoding UTF8 $pf
Write-Host "🤝 Added/updated peer '$Name' -> $Url" -ForegroundColor Green
