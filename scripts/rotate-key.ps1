\
# scripts/rotate-key.ps1
$ErrorActionPreference = "Stop"
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path "$PSScriptRoot\.."

$kf = Join-Path $root "custodian\secret.key"
[byte[]]$bytes = New-Object byte[] 32
(new-object System.Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes)
[IO.File]::WriteAllBytes($kf, $bytes)
Write-Host "🔑 Wrote new key: $kf" -ForegroundColor Green
