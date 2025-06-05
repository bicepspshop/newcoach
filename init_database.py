import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

async def init_database():
    """Инициализация базы данных Supabase"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL не найден в .env файле")
        return
    
    try:
        print("🔄 Подключение к базе данных...")
        conn = await asyncpg.connect(database_url)
        
        print("📋 Создание таблиц...")
        
        # SQL для создания таблиц
        sql_commands = [
            """
            CREATE TABLE IF NOT EXISTS coaches (
                id SERIAL PRIMARY KEY,
                telegram_id VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                username VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                coach_id INTEGER REFERENCES coaches(id) ON DELETE CASCADE,
                name VARCHAR(100) NOT NULL,
                telegram_id VARCHAR(20),
                phone VARCHAR(20),
                notes TEXT,
                fitness_goal TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """,
            """
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
            );
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_coaches_telegram_id ON coaches(telegram_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_clients_coach_id ON clients(coach_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_workouts_coach_id ON workouts(coach_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_workouts_client_id ON workouts(client_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts(date);
            """
        ]
        
        for sql in sql_commands:
            await conn.execute(sql)
            print("✅ Выполнена команда SQL")
        
        # Проверяем созданные таблицы
        print("\n📊 Проверка созданных таблиц:")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        for table in tables:
            print(f"  ✓ {table['table_name']}")
        
        # Создаем тестового тренера
        print("\n👤 Создание тестового тренера...")
        try:
            await conn.execute("""
                INSERT INTO coaches (telegram_id, name, username) 
                VALUES ('test_coach', 'Тестовый Тренер', 'test_coach')
                ON CONFLICT (telegram_id) DO NOTHING;
            """)
            print("✅ Тестовый тренер создан")
        except Exception as e:
            print(f"⚠️  Тестовый тренер уже существует или ошибка: {e}")
        
        await conn.close()
        print("\n🎉 База данных успешно инициализирована!")
        print("🔗 Ваш проект Supabase готов к работе:")
        print(f"   URL: https://nludsxoqhhlfpehhblgg.supabase.co")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")
        print("\n🔧 Возможные решения:")
        print("1. Проверьте правильность DATABASE_URL в .env файле")
        print("2. Убедитесь, что Supabase проект активен")
        print("3. Проверьте доступ к интернету")

if __name__ == "__main__":
    asyncio.run(init_database())
