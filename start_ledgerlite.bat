@echo off
REM LedgerLite Startup Script for Windows
REM This script provides an easy way to start LedgerLite on Windows

echo 🚀 Starting LedgerLite...

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo 📦 Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  Virtual environment not found. Using system Python...
)

REM Check if package is installed
python -c "import ledgerlite" 2>nul
if %errorlevel% neq 0 (
    echo ❌ LedgerLite package not found. Installing...
    pip install -e .
)

REM Start the application
echo 📱 Launching LedgerLite...
python -m ledgerlite.app.main

echo 👋 LedgerLite closed.
pause


