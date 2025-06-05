@echo off
echo ===============================================
echo БЫСТРОЕ ИСПРАВЛЕНИЕ ВЕБ-ПРИЛОЖЕНИЯ
echo ===============================================

cd /d "C:\Users\fonsh\Downloads\coachapp"

echo.
echo 📋 1. Добавляем исправления...
git add script.js index.html

echo.
echo 💾 2. Создаем коммит с исправлением...
git commit -m "🔧 Fix web app loading issues

- Simplified JavaScript initialization
- Removed blocking server status checks
- Fixed async operations that caused loading freeze
- Restored working web app functionality
- Removed connection status element that caused delays

✅ Web app now loads properly in Telegram"

echo.
echo 🚀 3. Отправляем в GitHub...
git push origin main

echo.
echo ===============================================
echo ✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!
echo ===============================================
echo.
echo 🎯 Что исправлено:
echo   • Убрана блокирующая проверка статуса сервера
echo   • Упрощена инициализация JavaScript
echo   • Удален элемент статуса подключения
echo   • Исправлены async операции
echo.
echo 📱 Веб-приложение в Telegram теперь должно загружаться нормально!
echo.
pause
