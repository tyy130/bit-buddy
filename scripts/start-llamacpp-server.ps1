\
# scripts/start-llamacpp-server.ps1
# Assumes you placed a llama.cpp server binary in /bin (e.g., server.exe)
# And a GGUF model in /models, matching app/config.yaml llamacpp.model path.

$ErrorActionPreference = "Stop"
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path "$PSScriptRoot\.."

$server = Join-Path $root "bin\server.exe"
if (-not (Test-Path $server)) {
  Write-Host "Missing llama.cpp server binary at bin\server.exe" -ForegroundColor Yellow
  Write-Host "Download from: https://github.com/ggerganov/llama.cpp/releases (server binary)" -ForegroundColor Yellow
  exit 1
}

# Edit ports/threads as desired
& $server --api --host 127.0.0.1 --port 8080 --chat-template llama-3 \
  -m (Join-Path $root "models\phi-3-mini-4k-instruct.Q4_K_M.gguf") `
  --n-gpu-layers 0 --ctx-size 4096 --batch-size 512
