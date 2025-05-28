"""
Database initialization script
Creates necessary tables for Coach Assistant Bot
"""

import asyncio
import os
from database.connection import DatabaseManager

async def init_database():
    """Initialize database with required tables"""
    db = DatabaseManager()
    await db.connect()
    
    try:
        # Create coaches table
        await db.execute_query("""
            CREATE TABLE IF NOT EXISTS coaches (
                id SERIAL PRIMARY KEY,
                telegram_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                username VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create clients table
        await db.execute_query("""
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                coach_id INTEGER REFERENCES coaches(id) ON DELETE CASCADE,
                name VARCHAR(100) NOT NULL,
                telegram_id VARCHAR(50),
                phone VARCHAR(20),
                notes TEXT,
                fitness_goal VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create workouts table
        await db.execute_query("""
            CREATE TABLE IF NOT EXISTS workouts (
                id SERIAL PRIMARY KEY,
                coach_id INTEGER REFERENCES coaches(id) ON DELETE CASCADE,
                client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
                date TIMESTAMP NOT NULL,
                exercises JSONB DEFAULT '[]',
                notes TEXT,
                workout_type VARCHAR(50),
                status VARCHAR(20) DEFAULT 'planned',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("✅ Database tables created successfully")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(init_database())