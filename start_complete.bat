@echo off
echo 🚀 Coach Assistant - Complete Startup
echo ====================================

cd /d "%~dp0"

echo.
echo 🔍 Checking environment...
if not exist ".env" (
    echo ❌ .env file not found!
    pause
    exit /b 1
)

if exist "venv\Scripts\activate.bat" (
    echo ✅ Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ Virtual environment not found, using system Python
)

echo.
echo 🗄️ Starting database debug...
python debug_database.py

echo.
echo 🌐 Starting web server...
start "Web Server" cmd /k "python server.py"

timeout /t 3 /nobreak > nul

echo.
echo 🤖 Starting Telegram bot...
start "Telegram Bot" cmd /k "python main.py"

echo.
echo ✅ All services started!
echo 🔗 Web App: http://localhost:8000
echo 📱 Telegram Bot: Running in background
echo.
echo Press any key to exit this window...
pause >nul
