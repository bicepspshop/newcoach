@echo off
title Coach Assistant - Quick Setup
color 0A
echo =============================================
echo     🏋️‍♂️ COACH ASSISTANT SETUP GUIDE
echo =============================================
echo.
echo 📋 SETUP STEPS:
echo.
echo 1️⃣ START WEB SERVER
echo    • Run: start_web_server.bat
echo    • Keep that window open
echo.
echo 2️⃣ START NGROK (in new terminal)
echo    • Open new Command Prompt/PowerShell
echo    • Run: ngrok http 8000
echo    • Copy the HTTPS URL (like https://xxxxx.ngrok.io)
echo.
echo 3️⃣ UPDATE CONFIG
echo    • Edit .env file
echo    • Change WEB_APP_URL to your ngrok URL
echo    • Example: WEB_APP_URL=https://abc123.ngrok.io
echo.
echo 4️⃣ START BOT
echo    • Run: start_bot.bat
echo    • Bot will connect to fixed database
echo.
echo 🔧 CURRENT SETTINGS:
echo    • Database: ✅ Fixed (using transaction pooler)
echo    • Bot Token: ✅ Configured
echo    • Web App: ⏳ Needs ngrok URL
echo.
echo 📱 TESTING:
echo    • Send /start to your bot in Telegram
echo    • Try adding clients and workouts
echo    • Open web app from bot menu
echo.
echo ❓ TROUBLESHOOTING:
echo    • Database errors: Check internet connection
echo    • Bot not responding: Check bot token
echo    • Web app not loading: Check ngrok URL in .env
echo.
echo =============================================
echo Press any key to continue...
pause >nul

echo.
echo 🚀 Ready to start? Choose option:
echo.
echo [1] Start Web Server
echo [2] Start Bot (after ngrok setup)
echo [3] Open .env file for editing
echo [4] Exit
echo.
set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    start start_web_server.bat
    echo ✅ Web server started in new window
    echo Now run: ngrok http 8000
    pause
)
if "%choice%"=="2" (
    start start_bot.bat
    echo ✅ Bot started in new window
    pause
)
if "%choice%"=="3" (
    notepad .env
    echo ✅ .env file opened for editing
    pause
)
if "%choice%"=="4" (
    echo 👋 Goodbye!
    exit
)

echo.
echo Invalid choice. Please run setup.bat again.
pause
