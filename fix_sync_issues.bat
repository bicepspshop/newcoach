@echo off
echo 🔧 Coach Assistant - Исправление проблем синхронизации
echo =================================================

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    echo ✅ Активация виртуального окружения...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ Виртуальное окружение не найдено, используется системный Python
)

echo.
echo 🚀 Запуск исправления проблем синхронизации...
python fix_sync_issues.py

echo.
echo Press any key to exit...
pause >nul
