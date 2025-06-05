"""
Script to check and adapt to existing Supabase database structure
"""

import asyncio
import os
from dotenv import load_dotenv
from database.connection import DatabaseManager

# Загружаем переменные окружения
load_dotenv()

async def check_database_structure():
    """Check existing database structure and adapt if needed"""
    print("🔍 Проверка структуры базы данных...")
    
    db = DatabaseManager()
    
    try:
        await db.connect()
        print("✅ Подключение к базе данных установлено")
        
        # Проверяем существующие таблицы
        print("\n📊 Существующие таблицы:")
        tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        tables = await db.fetch_all(tables_query)
        
        existing_tables = []
        for table in tables:
            table_name = table['table_name']
            existing_tables.append(table_name)
            print(f"  ✓ {table_name}")
        
        # Проверяем структуру ключевых таблиц
        key_tables = ['coaches', 'clients', 'workouts', 'trainer_client']
        
        for table_name in key_tables:
            if table_name in existing_tables:
                print(f"\n🔍 Структура таблицы {table_name}:")
                structure = await db.get_table_structure(table_name)
                for col in structure:
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    print(f"    {col['column_name']}: {col['data_type']} {nullable}")
            else:
                print(f"\n❌ Таблица {table_name} не найдена")
        
        # Проверяем данные в таблице coaches
        print(f"\n👤 Данные в таблице coaches:")
        coaches = await db.fetch_all("SELECT * FROM coaches LIMIT 5")
        for coach in coaches:
            print(f"    ID: {coach['id']}, Telegram: {coach['telegram_id']}, Name: {coach['name']}")
        
        # Добавляем недостающие столбцы если нужно
        await add_missing_columns(db, existing_tables)
        
        # Тестируем подключение
        print(f"\n🧪 Тестирование операций с базой данных...")
        await test_database_operations(db)
        
        print("✅ Проверка структуры базы данных завершена!")
        
    except Exception as e:
        print(f"❌ Ошибка при проверке базы данных: {e}")
        raise
    finally:
        await db.disconnect()

async def add_missing_columns(db, existing_tables):
    """Add missing columns to existing tables"""
    print(f"\n🔧 Проверка и добавление недостающих столбцов...")
    
    try:
        # Добавляем недостающие столбцы в coaches если нужно
        if 'coaches' in existing_tables:
            alter_queries = [
                "ALTER TABLE coaches ADD COLUMN IF NOT EXISTS created_at timestamptz DEFAULT NOW()",
                "ALTER TABLE coaches ADD COLUMN IF NOT EXISTS updated_at timestamptz DEFAULT NOW()"
            ]
            for query in alter_queries:
                try:
                    await db.execute_query(query)
                    print(f"    ✓ Выполнено: {query.split('ADD COLUMN IF NOT EXISTS')[1].split()[0] if 'ADD COLUMN' in query else 'ALTER'}")
                except Exception as e:
                    print(f"    ⚠️ {query.split('ADD COLUMN IF NOT EXISTS')[1].split()[0] if 'ADD COLUMN' in query else 'ALTER'}: {e}")
        
        # Добавляем недостающие столбцы в clients если нужно
        if 'clients' in existing_tables:
            alter_queries = [
                "ALTER TABLE clients ADD COLUMN IF NOT EXISTS coach_id integer",
                "ALTER TABLE clients ADD COLUMN IF NOT EXISTS fitness_goal varchar(100)",
                "ALTER TABLE clients ADD COLUMN IF NOT EXISTS created_at timestamptz DEFAULT NOW()",
                "ALTER TABLE clients ADD COLUMN IF NOT EXISTS updated_at timestamptz DEFAULT NOW()"
            ]
            for query in alter_queries:
                try:
                    await db.execute_query(query)
                    print(f"    ✓ Выполнено: {query.split('ADD COLUMN IF NOT EXISTS')[1].split()[0]}")
                except Exception as e:
                    print(f"    ⚠️ {query.split('ADD COLUMN IF NOT EXISTS')[1].split()[0]}: уже существует или ошибка")
        
        # Добавляем недостающие столбцы в workouts если нужно
        if 'workouts' in existing_tables:
            alter_queries = [
                "ALTER TABLE workouts ADD COLUMN IF NOT EXISTS coach_id integer",
                "ALTER TABLE workouts ADD COLUMN IF NOT EXISTS status varchar(20) DEFAULT 'planned'",
                "ALTER TABLE workouts ADD COLUMN IF NOT EXISTS workout_type varchar(50)",
                "ALTER TABLE workouts ADD COLUMN IF NOT EXISTS created_at timestamptz DEFAULT NOW()",
                "ALTER TABLE workouts ADD COLUMN IF NOT EXISTS updated_at timestamptz DEFAULT NOW()"
            ]
            for query in alter_queries:
                try:
                    await db.execute_query(query)
                    print(f"    ✓ Выполнено: {query.split('ADD COLUMN IF NOT EXISTS')[1].split()[0]}")
                except Exception as e:
                    print(f"    ⚠️ {query.split('ADD COLUMN IF NOT EXISTS')[1].split()[0]}: уже существует или ошибка")
        
    except Exception as e:
        print(f"    ❌ Ошибка при добавлении столбцов: {e}")

async def test_database_operations(db):
    """Test basic database operations"""
    try:
        # Тест получения тренера
        coach = await db.get_coach_by_telegram_id("234104161")
        if coach:
            print(f"    ✓ Найден тренер: {coach['name']} (ID: {coach['id']})")
            
            # Тест получения клиентов
            clients = await db.get_clients_for_coach(coach['id'])
            print(f"    ✓ Найдено клиентов: {len(clients)}")
            
            # Тест получения тренировок
            workouts = await db.get_workouts_for_coach(coach['id'])
            print(f"    ✓ Найдено тренировок: {len(workouts)}")
            
            # Тест статистики
            stats = await db.get_stats_for_coach(coach['id'])
            print(f"    ✓ Статистика: {stats}")
        else:
            print(f"    ⚠️ Тренер с ID 234104161 не найден")
            
    except Exception as e:
        print(f"    ❌ Ошибка при тестировании: {e}")

if __name__ == "__main__":
    asyncio.run(check_database_structure())
