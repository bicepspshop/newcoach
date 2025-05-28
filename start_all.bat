@echo off
title Coach Assistant - Unified Launcher
echo.
echo 🚀 Starting Coach Assistant with automatic setup...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Run the unified launcher
python start_all.py

echo.
echo 👋 All services stopped
pause
