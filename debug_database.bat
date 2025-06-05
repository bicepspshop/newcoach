@echo off
echo 🔍 Coach Assistant Database Debug
echo ==============================

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    echo ✅ Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ Virtual environment not found, using system Python
)

echo.
echo 🚀 Running database debug...
python debug_database.py

echo.
echo Press any key to exit...
pause >nul
