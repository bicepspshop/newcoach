@echo off
title Coach Assistant - Web Server
echo 🌐 Starting Coach Assistant Web Server...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo 📍 Starting web server on http://localhost:8000
echo.
echo 🚀 NEXT STEPS:
echo    1. Keep this window open
echo    2. Open another terminal and run: ngrok http 8000  
echo    3. Copy the ngrok HTTPS URL (like https://xxxxx.ngrok.io)
echo    4. Update WEB_APP_URL in .env file with that URL
echo    5. Run start_bot.bat to start the bot
echo.
echo ⏹️  Press Ctrl+C to stop
echo ==========================================
echo.

python start_web_server.py

pause
