# run_demo.ps1 - Test Bit Buddy MVP
Write-Host "=== 🤖 Bit Buddy MVP Test ===" -ForegroundColor Cyan
Write-Host ""

# Try to find working Python
$pythonPaths = @(
    "python",
    "python3", 
    "py",
    "C:\Python312\python.exe",
    "C:\Python311\python.exe",
    "C:\Program Files\Python312\python.exe"
)

$workingPython = $null
foreach ($pythonPath in $pythonPaths) {
    try {
        $version = & $pythonPath --version 2>$null
        if ($version -like "*Python 3.*") {
            $workingPython = $pythonPath
            Write-Host "✅ Found Python: $pythonPath ($version)" -ForegroundColor Green
            break
        }
    }
    catch {
        # Silently continue
    }
}

if (-not $workingPython) {
    Write-Host "❌ No working Python found!" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and ensure it's in your PATH" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Manual test: Open the bit_buddy.py file and run the demo code at the bottom"
    exit 1
}

Write-Host ""
Write-Host "🚀 Testing core bit buddy functionality..." -ForegroundColor Yellow

# Test the core module directly
try {
    & $workingPython bit_buddy.py
    Write-Host ""
    Write-Host "✅ Core test successful!" -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "❌ Test failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Try installing dependencies first:" -ForegroundColor Yellow
    Write-Host "   $workingPython -m pip install fastapi uvicorn pydantic requests"
    exit 1
}

Write-Host ""
Write-Host "=== 🎉 MVP Ready! ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "To experience the full interactive demo:" -ForegroundColor White
Write-Host "1. Terminal 1: $workingPython server.py" -ForegroundColor Gray
Write-Host "2. Terminal 2: $workingPython demo.py" -ForegroundColor Gray
Write-Host ""
Write-Host "Your bit buddy is alive and waiting! 🤖✨" -ForegroundColor Green