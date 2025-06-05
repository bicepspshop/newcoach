"""
Database initialization script for Supabase
Creates necessary tables for Coach Assistant Bot
"""

import asyncio
import os
from dotenv import load_dotenv
from database.connection import DatabaseManager

# Загружаем переменные окружения
load_dotenv()

async def init_database():
    """Initialize database with required tables"""
    print("🔄 Инициализация базы данных Supabase...")
    
    db = DatabaseManager()
    
    try:
        await db.connect()
        print("✅ Подключение к базе данных установлено")
        
        # Create coaches table
        print("📋 Создание таблицы coaches...")
        await db.execute_query("""
            CREATE TABLE IF NOT EXISTS coaches (
                id SERIAL PRIMARY KEY,
                telegram_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                username VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create clients table
        print("📋 Создание таблицы clients...")
        await db.execute_query("""
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                coach_id INTEGER REFERENCES coaches(id) ON DELETE CASCADE,
                name VARCHAR(100) NOT NULL,
                telegram_id VARCHAR(50),
                phone VARCHAR(20),
                notes TEXT,
                fitness_goal VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create workouts table
        print("📋 Создание таблицы workouts...")
        await db.execute_query("""
            CREATE TABLE IF NOT EXISTS workouts (
                id SERIAL PRIMARY KEY,
                coach_id INTEGER REFERENCES coaches(id) ON DELETE CASCADE,
                client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
                date TIMESTAMP WITH TIME ZONE NOT NULL,
                exercises JSONB DEFAULT '[]',
                notes TEXT,
                workout_type VARCHAR(50),
                status VARCHAR(20) DEFAULT 'planned',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create indexes
        print("📊 Создание индексов...")
        await db.execute_query("CREATE INDEX IF NOT EXISTS idx_coaches_telegram_id ON coaches(telegram_id)")
        await db.execute_query("CREATE INDEX IF NOT EXISTS idx_clients_coach_id ON clients(coach_id)")
        await db.execute_query("CREATE INDEX IF NOT EXISTS idx_workouts_coach_id ON workouts(coach_id)")
        await db.execute_query("CREATE INDEX IF NOT EXISTS idx_workouts_client_id ON workouts(client_id)")
        await db.execute_query("CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts(date)")
        
        # Проверяем созданные таблицы
        print("\n📊 Проверка созданных таблиц:")
        tables = await db.fetch_all("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            AND table_name IN ('coaches', 'clients', 'workouts')
            ORDER BY table_name;
        """)
        
        for table in tables:
            print(f"  ✓ {table['table_name']}")
        
        print("✅ База данных успешно инициализирована!")
        print("\n🎉 Теперь можно запускать приложение:")
        print("  • Бот: python main.py")
        print("  • Веб-сервер: python server.py")
        print(f"  • Supabase URL: https://nludsxoqhhlfpehhblgg.supabase.co")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")
        print("\n🔧 Возможные решения:")
        print("1. Проверьте правильность DATABASE_URL в .env файле")
        print("2. Убедитесь, что Supabase проект активен")
        print("3. Проверьте доступ к интернету")
        raise
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(init_database())
