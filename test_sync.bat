@echo off
echo 🧪 Coach Assistant - Test Suite
echo ===============================

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo.
echo 🔍 Running comprehensive tests...
python fix_sync_issues.py

echo.
echo Press any key to exit...
pause >nul
