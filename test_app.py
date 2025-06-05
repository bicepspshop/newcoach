"""
Простой тест работы приложения
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

async def test_application():
    """Тестирование основных функций приложения"""
    print("🧪 Тестирование Coach Assistant...")
    print("=" * 50)
    
    try:
        print("📋 1. Импорт модулей...")
        from database.connection import DatabaseManager
        print("   ✅ DatabaseManager импортирован")
        
        print("\n🔗 2. Подключение к базе данных...")
        db = DatabaseManager()
        await db.connect()
        print("   ✅ Подключение успешно")
        
        print("\n👤 3. Тестирование операций с тренерами...")
        # Получаем существующего тренера
        coach = await db.get_coach_by_telegram_id("234104161")
        if coach:
            print(f"   ✅ Найден тренер: {coach['name']} (ID: {coach['id']})")
            coach_id = coach['id']
        else:
            print("   ⚠️ Тренер не найден, создаем нового...")
            coach_id = await db.create_coach("234104161", "aNmOff", "aNmOff")
            print(f"   ✅ Создан тренер с ID: {coach_id}")
        
        print("\n👥 4. Тестирование клиентов...")
        clients = await db.get_clients_for_coach(coach_id)
        print(f"   ✅ Найдено клиентов: {len(clients)}")
        
        print("\n💪 5. Тестирование тренировок...")
        workouts = await db.get_workouts_for_coach(coach_id)
        print(f"   ✅ Найдено тренировок: {len(workouts)}")
        
        print("\n📊 6. Получение статистики...")
        stats = await db.get_stats_for_coach(coach_id)
        print(f"   ✅ Статистика:")
        print(f"      • Клиенты: {stats['clients_count']}")
        print(f"      • Тренировки: {stats['workouts_count']}")
        print(f"      • Завершено: {stats['completed_workouts']}")
        
        print("\n🔐 7. Отключение от базы данных...")
        await db.disconnect()
        print("   ✅ Отключение успешно")
        
        print("\n" + "=" * 50)
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Приложение готово к использованию")
        print("\n📋 Что можно запускать:")
        print("   • python main.py - Telegram бот")
        print("   • python server.py - Веб-сервер")
        print("   • python start_all.py - Всё вместе")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        print("\n🔧 Возможные решения:")
        print("   1. Запустите fix_asyncpg.bat для исправления библиотек")
        print("   2. Проверьте подключение к интернету")
        print("   3. Убедитесь, что Supabase проект активен")
        print(f"   4. Проверьте переменные окружения в .env файле")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(test_application())
        if not result:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
