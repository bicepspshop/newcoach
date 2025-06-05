@echo off
echo ===============================================
echo Инициализация базы данных Supabase
echo ===============================================

cd /d "C:\Users\fonsh\Downloads\coachapp"

echo.
echo 🔄 Активация виртуального окружения...
call venv\Scripts\activate

echo.
echo 📋 Установка зависимостей...
pip install python-dotenv

echo.
echo 🚀 Запуск инициализации базы данных...
python init_database.py

echo.
echo ===============================================
echo Готово! Проверьте результат выше.
echo ===============================================
echo.
echo Если все прошло успешно, теперь можно:
echo 1. Запустить бота: python main.py
echo 2. Запустить веб-сервер: python server.py
echo.
pause
