@echo off
echo ===========================================
echo Обновление репозитория newcoach на GitHub
echo ===========================================

cd /d "C:\Users\fonsh\Downloads\coachapp"

echo.
echo 1. Проверяем статус git...
git status

echo.
echo 2. Добавляем все изменения...
git add .

echo.
echo 3. Создаем коммит с обновлением Supabase...
git commit -m "Update to new Supabase instance with database initialization"

echo.
echo 4. Отправляем изменения в репозиторий...
git push origin main

echo.
echo ===========================================
echo ✅ РЕПОЗИТОРИЙ ОБНОВЛЕН!
echo ===========================================
echo.
echo 📋 Что было обновлено:
echo   • Новые данные подключения к Supabase
echo   • Скрипты инициализации базы данных
echo   • Улучшенная обработка ошибок
echo   • Bat-файлы для автоматизации
echo.
echo 🔗 Новые данные Supabase:
echo   URL: https://nludsxoqhhlfpehhblgg.supabase.co
echo   Project ID: nludsxoqhhlfpehhblgg
echo   Region: EU North (Stockholm)
echo.
echo 🚀 Следующие шаги:
echo   1. Запустите setup_complete.bat для инициализации БД
echo   2. Запустите приложение через start_all.bat
echo.
pause
