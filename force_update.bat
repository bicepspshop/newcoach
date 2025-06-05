@echo off
echo ===============================================
echo ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ ВЕБ-ПРИЛОЖЕНИЯ
echo ===============================================

cd /d "C:\Users\fonsh\Downloads\coachapp"

echo.
echo 📋 1. Проверяем текущий статус...
git status

echo.
echo 🔍 2. Принудительно добавляем все файлы...
git add -A

echo.
echo 📋 3. Проверяем что добавлено...
git status

echo.
echo 💾 4. Создаем коммит с исправлениями...
git commit -m "Fix web app loading and update to new Supabase" || echo "Нет изменений для коммита"

echo.
echo 🚀 5. Отправляем в GitHub...
git push origin main

echo.
echo ===============================================
echo ✅ ГОТОВО!
echo ===============================================
echo.
echo 🧪 Теперь протестируйте веб-приложение в Telegram
echo.
echo 📱 Если все еще не работает, проверьте:
echo   1. Кеш Telegram (перезапустите приложение)
echo   2. Открывайте веб-приложение заново
echo   3. Проверьте консоль браузера на ошибки
echo.
pause
