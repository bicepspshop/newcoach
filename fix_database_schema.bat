@echo off
echo 🔧 Coach Assistant - Исправление схемы базы данных
echo ===============================================

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    echo ✅ Активация виртуального окружения...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ Виртуальное окружение не найдено, используется системный Python
)

echo.
echo 🗄️ Исправление схемы базы данных...
python fix_database_schema.py

echo.
echo Press any key to exit...
pause >nul
