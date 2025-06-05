#!/bin/bash

echo "==========================================="
echo "Обновление репозитория newcoach на GitHub"
echo "==========================================="

cd "$(dirname "$0")"

echo
echo "1. Проверяем статус git..."
git status

echo
echo "2. Добавляем все изменения..."
git add .

echo
echo "3. Создаем коммит с обновлением Supabase..."
git commit -m "Update Supabase connection to new instance (nludsxoqhhlfpehhblgg)"

echo
echo "4. Отправляем изменения в репозиторий..."
git push origin main

echo
echo "==========================================="
echo "Готово! Репозиторий обновлен."
echo "==========================================="
echo
echo "Новые данные Supabase:"
echo "URL: https://nludsxoqhhlfpehhblgg.supabase.co"
echo "Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5sdWRzeG9xaGhsZnBlaGhibGdnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgyODUyNjEsImV4cCI6MjA2Mzg2MTI2MX0.o6DtsgGgpuNQFIL9Gh2Ba-xScVW20dU_IDg4QAYYXxQ"
echo "DB: postgresql://postgres.nludsxoqhhlfpehhblgg:frjDNeVdtQv02KC7@aws-0-eu-north-1.pooler.supabase.com:6543/postgres"
echo
