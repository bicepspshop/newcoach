@echo off
echo ===============================================
echo ПОЛНАЯ НАСТРОЙКА COACH BOT ПРИЛОЖЕНИЯ
echo ===============================================

cd /d "C:\Users\fonsh\Downloads\coachapp"

echo.
echo 🔄 Активация виртуального окружения...
if exist venv (
    call venv\Scripts\activate
) else (
    echo ❌ Виртуальное окружение не найдено!
    echo Запустите setup.bat сначала
    pause
    exit /b 1
)

echo.
echo 📦 Обновление зависимостей...
pip install -r requirements.txt

echo.
echo 🚀 Инициализация базы данных Supabase...
python init_db.py

echo.
echo ===============================================
echo ✅ НАСТРОЙКА ЗАВЕРШЕНА!
echo ===============================================
echo.
echo Теперь можно запускать:
echo.
echo 🤖 Telegram Bot:
echo    python main.py
echo.
echo 🌐 Веб-сервер:
echo    python server.py
echo.
echo 🔧 Или все вместе:
echo    python start_all.py
echo.
echo 📊 Supabase Dashboard:
echo    https://nludsxoqhhlfpehhblgg.supabase.co
echo.
pause
