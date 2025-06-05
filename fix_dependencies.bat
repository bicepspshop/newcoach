@echo off
echo 🔧 Исправление зависимостей Python
echo ================================

cd /d "%~dp0"

echo ✅ Активация виртуального окружения...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ❌ Виртуальное окружение не найдено!
    echo Создание нового виртуального окружения...
    python -m venv venv
    call venv\Scripts\activate.bat
)

echo.
echo 🗑️ Удаление поврежденных пакетов...
pip uninstall -y pydantic pydantic-core asyncpg

echo.
echo 📦 Обновление pip...
python -m pip install --upgrade pip

echo.
echo 📥 Установка исправленных зависимостей...
pip install -r requirements_fixed.txt

echo.
echo 🔧 Установка совместимых версий...
pip install "pydantic>=2.4.0,<2.6" --force-reinstall
pip install "pydantic-core>=2.14.0,<2.15" --force-reinstall

echo.
echo ✅ Проверка установки...
python -c "import aiogram; print('✅ aiogram работает')"
python -c "import requests; print('✅ requests работает')"
python -c "import pydantic; print('✅ pydantic работает')"

echo.
echo 🎉 Зависимости исправлены!
echo 📝 Теперь можно запускать бота без asyncpg
echo.
pause
