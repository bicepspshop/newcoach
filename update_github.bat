@echo off
echo 🚀 Coach Assistant - Обновление GitHub
echo ====================================

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    echo ✅ Активация виртуального окружения...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ Виртуальное окружение не найдено, используется системный Python
)

echo.
echo 📤 Обновление веб-приложения в GitHub...
python update_github.py

pause
