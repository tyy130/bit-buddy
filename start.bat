@echo off
REM Bit Buddy Start Script for Windows
REM This script automatically activates the virtual environment and runs the application

setlocal

set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%venv

REM Check if virtual environment exists
if not exist "%VENV_DIR%" (
    echo ❌ Virtual environment not found at %VENV_DIR%
    echo.
    echo Please run setup first:
    echo   python setup.py
    echo.
    echo This will:
    echo   1. Create a virtual environment
    echo   2. Install all dependencies
    echo   3. Guide you through initial configuration
    exit /b 1
)

REM Check if activate script exists
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo ❌ Virtual environment appears corrupted (activate script missing)
    echo.
    echo Please re-run setup:
    echo   rmdir /s /q venv
    echo   python setup.py
    exit /b 1
)

REM Activate virtual environment
call "%VENV_DIR%\Scripts\activate.bat"

REM Verify activation worked by checking VIRTUAL_ENV is set
if "%VIRTUAL_ENV%"=="" (
    echo ❌ Failed to activate virtual environment
    echo.
    echo Please try re-running setup:
    echo   rmdir /s /q venv
    echo   python setup.py
    exit /b 1
)

REM Check if start_buddy.py exists (created after full interactive setup)
if exist "%SCRIPT_DIR%start_buddy.py" (
    echo 🤖 Starting Bit Buddy...
    python "%SCRIPT_DIR%start_buddy.py" %*
) else (
    REM Fallback to RAG server if no buddy configured yet
    echo 🤖 Starting Bit Buddy RAG Server...
    echo    (Run 'python setup.py' for full interactive setup with buddy creation)
    echo.
    uvicorn app.server:app --host 127.0.0.1 --port 8000 %*
)

endlocal
