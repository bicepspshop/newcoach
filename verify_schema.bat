@echo off
echo 🔍 Coach Assistant - Проверка схемы базы данных
echo ===============================================

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    echo ✅ Активация виртуального окружения...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ Виртуальное окружение не найдено, используется системный Python
)

echo.
echo 🔍 Проверка текущей схемы базы данных...
python verify_schema.py

echo.
echo Press any key to exit...
pause >nul
