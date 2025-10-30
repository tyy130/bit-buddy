@echo off
echo === Bit Buddy MVP Test ===
echo.
echo Testing core functionality...
echo.

REM Try to find Python
set PYTHON_EXE=""
if exist "C:\ProgramData\chocolatey\bin\python3.12.exe" set PYTHON_EXE="C:\ProgramData\chocolatey\bin\python3.12.exe"
if exist "C:\ProgramData\chocolatey\bin\python3.13.exe" set PYTHON_EXE="C:\ProgramData\chocolatey\bin\python3.13.exe"

if %PYTHON_EXE%=="" (
    echo Python not found! Please install Python 3.12+ 
    echo Or update the path in this script
    pause
    exit /b 1
)

echo Using Python: %PYTHON_EXE%
echo.

REM Run the demo
%PYTHON_EXE% bit_buddy.py

echo.
echo === Test Complete ===
echo.
echo To run the full experience:
echo 1. %PYTHON_EXE% server.py    (in one terminal)
echo 2. %PYTHON_EXE% demo.py      (in another terminal)
echo.
pause