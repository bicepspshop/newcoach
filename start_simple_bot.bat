@echo off
echo 🤖 Simple Coach Assistant Bot
echo ===========================

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    echo ✅ Активация виртуального окружения...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ Виртуальное окружение не найдено, используется системный Python
)

echo.
echo 🔍 Проверка минимальных зависимостей...
python -c "import requests" 2>nul || (
    echo ❌ requests не установлен
    echo 📦 Установка requests...
    pip install requests
)

python -c "from dotenv import load_dotenv" 2>nul || (
    echo ❌ python-dotenv не установлен
    echo 📦 Установка python-dotenv...
    pip install python-dotenv
)

echo ✅ Минимальные зависимости в порядке

echo.
echo 🚀 Запуск простого бота...
echo 📱 Бот использует только HTTP API
echo 🌐 Веб-приложение: %WEB_APP_URL%
echo ⚡ Этот бот работает без aiogram и сложных зависимостей
echo.

python simple_bot.py

echo.
echo Press any key to exit...
pause >nul
