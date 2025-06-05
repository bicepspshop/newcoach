@echo off
echo ===============================================
echo БЫСТРОЕ ИСПРАВЛЕНИЕ И ТЕСТИРОВАНИЕ
echo ===============================================

cd /d "C:\Users\fonsh\Downloads\coachapp"

echo.
echo 🔄 Активация виртуального окружения...
call venv\Scripts\activate

echo.
echo 🛠️ Исправление проблем с asyncpg...
pip uninstall asyncpg -y >nul 2>&1
pip install asyncpg==0.29.0 --force-reinstall --no-cache-dir >nul 2>&1

echo.
echo 📦 Проверка зависимостей...
pip install -r requirements.txt >nul 2>&1

echo.
echo 🧪 Запуск тестирования приложения...
python test_app.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo ===============================================
    echo ✅ ПРИЛОЖЕНИЕ ГОТОВО К РАБОТЕ!
    echo ===============================================
    echo.
    echo 🚀 Выберите что запустить:
    echo   1 - Telegram Bot [python main.py]
    echo   2 - Web Server [python server.py]  
    echo   3 - Всё вместе [python start_all.py]
    echo   4 - Только тест еще раз
    echo   0 - Выход
    echo.
    set /p choice="Ваш выбор (1-4, 0): "
    
    if "!choice!"=="1" (
        echo.
        echo 🤖 Запуск Telegram Bot...
        python main.py
    ) else if "!choice!"=="2" (
        echo.
        echo 🌐 Запуск Web Server...
        python server.py
    ) else if "!choice!"=="3" (
        echo.
        echo 🚀 Запуск всего приложения...
        python start_all.py
    ) else if "!choice!"=="4" (
        echo.
        echo 🧪 Повторный тест...
        python test_app.py
    ) else (
        echo.
        echo 👋 До свидания!
    )
) else (
    echo ===============================================
    echo ❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ
    echo ===============================================
    echo.
    echo 🔧 Попробуйте следующее:
    echo   1. Проверьте подключение к интернету
    echo   2. Убедитесь что Supabase проект активен
    echo   3. Проверьте .env файл с настройками
    echo.
    echo 💡 Приложение может работать в режиме HTTP API
    echo даже при проблемах с asyncpg
)

echo.
pause
