@echo off
echo 🔧 Альтернативное исправление зависимостей
echo ==========================================

cd /d "%~dp0"

echo ✅ Активация виртуального окружения...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ❌ Виртуальное окружение не найдено!
    echo Создание нового...
    python -m venv venv
    call venv\Scripts\activate.bat
)

echo.
echo 🗑️ Полная очистка зависимостей...
pip uninstall -y aiogram pydantic pydantic-core aiohttp aiofiles magic-filter typing-extensions

echo.
echo 📦 Обновление pip до последней версии...
python -m pip install --upgrade pip

echo.
echo 📥 Установка базовых зависимостей...
pip install requests python-dotenv

echo.
echo 🔧 Попытка установки pydantic с готовыми wheels...
pip install --only-binary=all "pydantic>=2.0,<2.5"

if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ Не удалось установить pydantic 2.x, пробуем 1.x...
    pip install "pydantic>=1.10,<2.0"
)

echo.
echo 📱 Установка aiogram...
pip install "aiogram>=3.0,<3.5"

if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ Не удалось установить aiogram 3.x, пробуем 2.x...
    pip install "aiogram>=2.25,<3.0"
)

echo.
echo ✅ Проверка установки...
python -c "import requests; print('✅ requests работает')" || echo "❌ requests не работает"
python -c "import pydantic; print('✅ pydantic работает, версия:', pydantic.__version__)" || echo "❌ pydantic не работает"
python -c "import aiogram; print('✅ aiogram работает, версия:', aiogram.__version__)" || echo "❌ aiogram не работает"

echo.
echo 🎉 Установка завершена!
pause
