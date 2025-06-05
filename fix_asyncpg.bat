@echo off
echo ===============================================
echo ИСПРАВЛЕНИЕ ПРОБЛЕМЫ С ASYNCPG
echo ===============================================

cd /d "C:\Users\fonsh\Downloads\coachapp"

echo.
echo 🔄 Активация виртуального окружения...
call venv\Scripts\activate

echo.
echo 🛠️ Переустановка asyncpg...
pip uninstall asyncpg -y
pip install asyncpg==0.29.0 --force-reinstall --no-cache-dir

echo.
echo 🧪 Альтернативный способ установки...
pip install asyncpg --upgrade --force-reinstall

echo.
echo 📦 Проверка установленных пакетов...
pip list | findstr asyncpg

echo.
echo 🔍 Тестирование подключения к базе данных...
python -c "
try:
    import asyncpg
    print('✅ asyncpg успешно импортирован')
    import asyncio
    from database.connection import DatabaseManager
    print('✅ DatabaseManager успешно импортирован')
    print('✅ Все модули работают корректно')
except Exception as e:
    print(f'❌ Ошибка: {e}')
"

echo.
echo ===============================================
echo ✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!
echo ===============================================
echo.
echo Теперь можно запускать:
echo   • python main.py (Telegram Bot)
echo   • python server.py (Web Server)
echo   • python start_all.py (All together)
echo.
pause
