@echo off
echo 🤖 Coach Assistant Bot - Simplified Start
echo =======================================

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    echo ✅ Активация виртуального окружения...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ Виртуальное окружение не найдено
    goto :error
)

echo.
echo 🔍 Проверка основных зависимостей...
python -c "import aiogram" 2>nul || (
    echo ❌ aiogram не установлен
    echo 💡 Запустите fix_dependencies.bat
    goto :error
)

python -c "import requests" 2>nul || (
    echo ❌ requests не установлен
    echo 💡 Запустите fix_dependencies.bat
    goto :error
)

echo ✅ Зависимости в порядке

echo.
echo 🚀 Запуск Telegram бота...
echo 📱 Бот будет использовать HTTP API для базы данных
echo 🔗 Веб-приложение: %WEB_APP_URL%
echo.

python main.py

goto :end

:error
echo.
echo ❌ Ошибка запуска!
echo 💡 Попробуйте:
echo    1. fix_dependencies.bat
echo    2. start_bot_simple.bat
pause
goto :end

:end
