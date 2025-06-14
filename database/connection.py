"""
Database connection manager with automatic fallback
Supports both asyncpg (preferred) and HTTP REST API (fallback)
"""

import os
from datetime import datetime
from typing import Optional, List, Dict, Any

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
    print("✅ asyncpg available - using PostgreSQL direct connection")
except ImportError as e:
    ASYNCPG_AVAILABLE = False
    print(f"⚠️ asyncpg not available: {e}")
    print("🔄 Falling back to HTTP REST API")

# Force HTTP API mode for Python 3.13 compatibility
if ASYNCPG_AVAILABLE:
    try:
        # Test if asyncpg works with current Python version
        import sys
        if sys.version_info >= (3, 13):
            print("⚠️ Python 3.13 detected - forcing HTTP API mode for compatibility")
            ASYNCPG_AVAILABLE = False
    except:
        ASYNCPG_AVAILABLE = False

if ASYNCPG_AVAILABLE:
    # Use original asyncpg implementation
    import asyncio
    import json
    
    class DatabaseManager:
        def __init__(self):
            self.pool: Optional[asyncpg.Pool] = None
            self.database_url = os.getenv('DATABASE_URL', 'postgresql://postgres.nludsxoqhhlfpehhblgg:frjDNeVdtQv02KC7@aws-0-eu-north-1.pooler.supabase.com:6543/postgres')
            
        async def connect(self):
            """Initialize database connection pool"""
            if not self.database_url:
                raise ValueError("DATABASE_URL not found in environment variables")
                
            try:
                self.pool = await asyncpg.create_pool(
                    self.database_url,
                    min_size=1,
                    max_size=10,
                    command_timeout=60,
                    statement_cache_size=0
                )
                print("✅ Database connected successfully to Supabase (asyncpg)")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                raise
        
        async def disconnect(self):
            """Close database connection pool"""
            if self.pool:
                await self.pool.close()
                print("✅ Database disconnected")
        
        async def execute_query(self, query: str, *args):
            """Execute a query that doesn't return data"""
            async with self.pool.acquire() as conn:
                return await conn.execute(query, *args)
        
        async def fetch_one(self, query: str, *args):
            """Fetch a single row"""
            async with self.pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
        
        async def fetch_all(self, query: str, *args):
            """Fetch multiple rows"""
            async with self.pool.acquire() as conn:
                return await conn.fetch(query, *args)
        
        # Coach operations
        async def get_coach_by_telegram_id(self, telegram_id: str) -> Optional[Dict[str, Any]]:
            """Get coach by Telegram ID"""
            try:
                query = "SELECT * FROM coaches WHERE telegram_id = $1"
                row = await self.fetch_one(query, telegram_id)
                return dict(row) if row else None
            except Exception as e:
                print(f"Error getting coach: {e}")
                return None
        
        async def create_coach(self, telegram_id: str, name: str, username: str = None) -> int:
            """Create a new coach and return their ID"""
            try:
                query = """
                INSERT INTO coaches (telegram_id, name, username, created_at, updated_at) 
                VALUES ($1, $2, $3, NOW(), NOW()) 
                RETURNING id
                """
                row = await self.fetch_one(query, telegram_id, name, username)
                return row['id']
            except Exception as e:
                print(f"Error creating coach: {e}")
                existing = await self.get_coach_by_telegram_id(telegram_id)
                if existing:
                    return existing['id']
                raise
        
        async def get_coach(self, coach_id: int) -> Optional[Dict[str, Any]]:
            """Get coach by ID"""
            query = "SELECT * FROM coaches WHERE id = $1"
            row = await self.fetch_one(query, coach_id)
            return dict(row) if row else None
        
        # Client operations
        async def create_client(self, coach_id: int, name: str, telegram_id: str = None, 
                              phone: str = None, notes: str = None, fitness_goal: str = None) -> int:
            """Create a new client and return their ID"""
            try:
                query = """
                INSERT INTO clients (coach_id, name, telegram_id, phone, notes, fitness_goal, created_at, updated_at) 
                VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW()) 
                RETURNING id
                """
                row = await self.fetch_one(query, coach_id, name, telegram_id, phone, notes, fitness_goal)
                client_id = row['id']
                
                # Also create relationship in trainer_client if it exists
                try:
                    relation_query = """
                    INSERT INTO trainer_client (trainer_id, client_id, created_at) 
                    VALUES ($1, $2, NOW())
                    """
                    await self.execute_query(relation_query, coach_id, client_id)
                except Exception:
                    pass  # Ignore if table doesn't exist
                
                return client_id
            except Exception as e:
                print(f"Error creating client: {e}")
                raise
        
        async def get_clients_for_coach(self, coach_id: int) -> List[Dict[str, Any]]:
            """Get all clients for a coach"""
            try:
                query = """
                SELECT * FROM clients 
                WHERE coach_id = $1 OR id IN (
                    SELECT client_id FROM trainer_client WHERE trainer_id = $1
                )
                ORDER BY created_at DESC
                """
                rows = await self.fetch_all(query, coach_id)
                return [dict(row) for row in rows]
            except Exception:
                query = """
                SELECT c.* FROM clients c
                JOIN trainer_client tc ON c.id = tc.client_id
                WHERE tc.trainer_id = $1
                ORDER BY c.created_at DESC
                """
                rows = await self.fetch_all(query, coach_id)
                return [dict(row) for row in rows]
        
        async def get_client(self, client_id: int) -> Optional[Dict[str, Any]]:
            """Get client by ID"""
            query = "SELECT * FROM clients WHERE id = $1"
            row = await self.fetch_one(query, client_id)
            return dict(row) if row else None
        
        async def update_client(self, client_id: int, name: str = None, telegram_id: str = None,
                              phone: str = None, notes: str = None, fitness_goal: str = None):
            """Update client information"""
            updates = []
            values = []
            param_count = 1
            
            if name is not None:
                updates.append(f"name = ${param_count}")
                values.append(name)
                param_count += 1
            if telegram_id is not None:
                updates.append(f"telegram_id = ${param_count}")
                values.append(telegram_id)
                param_count += 1
            if phone is not None:
                updates.append(f"phone = ${param_count}")
                values.append(phone)
                param_count += 1
            if notes is not None:
                updates.append(f"notes = ${param_count}")
                values.append(notes)
                param_count += 1
            if fitness_goal is not None:
                updates.append(f"fitness_goal = ${param_count}")
                values.append(fitness_goal)
                param_count += 1
            
            if updates:
                updates.append(f"updated_at = NOW()")
                query = f"UPDATE clients SET {', '.join(updates)} WHERE id = ${param_count}"
                values.append(client_id)
                await self.execute_query(query, *values)
        
        async def delete_client(self, client_id: int):
            """Delete a client"""
            await self.execute_query("DELETE FROM trainer_client WHERE client_id = $1", client_id)
            query = "DELETE FROM clients WHERE id = $1"
            await self.execute_query(query, client_id)
        
        # Workout operations
        async def create_workout(self, coach_id: int, client_id: int, date: datetime,
                               exercises: List[Dict] = None, notes: str = None, workout_type: str = None) -> int:
            """Create a new workout and return its ID"""
            try:
                query = """
                INSERT INTO workouts (coach_id, client_id, date, exercises, notes, workout_type, created_at, updated_at) 
                VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW()) 
                RETURNING id
                """
                exercises_json = json.dumps(exercises or [])
                row = await self.fetch_one(query, coach_id, client_id, date, exercises_json, notes, workout_type)
                return row['id']
            except Exception as e:
                print(f"Error creating workout: {e}")
                query = """
                INSERT INTO workouts (client_id, date, exercises, notes, workout_type, created_at, updated_at) 
                VALUES ($1, $2, $3, $4, $5, NOW(), NOW()) 
                RETURNING id
                """
                exercises_json = json.dumps(exercises or [])
                row = await self.fetch_one(query, client_id, date, exercises_json, notes, workout_type)
                return row['id']
        
        async def get_workouts_for_coach(self, coach_id: int, limit: int = 50) -> List[Dict[str, Any]]:
            """Get workouts for a coach with client information"""
            try:
                query = """
                SELECT w.*, c.name as client_name 
                FROM workouts w 
                JOIN clients c ON w.client_id = c.id 
                WHERE w.coach_id = $1 OR c.id IN (
                    SELECT client_id FROM trainer_client WHERE trainer_id = $1
                )
                ORDER BY w.date DESC 
                LIMIT $2
                """
                rows = await self.fetch_all(query, coach_id, limit)
                return [dict(row) for row in rows]
            except Exception:
                query = """
                SELECT w.*, c.name as client_name 
                FROM workouts w 
                JOIN clients c ON w.client_id = c.id 
                JOIN trainer_client tc ON c.id = tc.client_id
                WHERE tc.trainer_id = $1
                ORDER BY w.date DESC 
                LIMIT $2
                """
                rows = await self.fetch_all(query, coach_id, limit)
                return [dict(row) for row in rows]
        
        async def get_workout(self, workout_id: int) -> Optional[Dict[str, Any]]:
            """Get workout by ID with client information"""
            query = """
            SELECT w.*, c.name as client_name 
            FROM workouts w 
            JOIN clients c ON w.client_id = c.id 
            WHERE w.id = $1
            """
            row = await self.fetch_one(query, workout_id)
            return dict(row) if row else None
        
        async def update_workout_status(self, workout_id: int, status: str, notes: str = None):
            """Update workout status and notes"""
            query = "UPDATE workouts SET status = $1, updated_at = NOW()"
            values = [status]
            param_count = 2
            
            if notes is not None:
                query += f", notes = ${param_count}"
                values.append(notes)
                param_count += 1
            
            query += f" WHERE id = ${param_count}"
            values.append(workout_id)
            
            await self.execute_query(query, *values)
        
        async def get_stats_for_coach(self, coach_id: int) -> Dict[str, Any]:
            """Get statistics for a coach"""
            stats = {}
            
            try:
                query = """
                SELECT COUNT(*) as count FROM clients 
                WHERE coach_id = $1 OR id IN (
                    SELECT client_id FROM trainer_client WHERE trainer_id = $1
                )
                """
                row = await self.fetch_one(query, coach_id)
                stats['clients_count'] = row['count']
                
                query = """
                SELECT COUNT(*) as count FROM workouts 
                WHERE coach_id = $1 OR client_id IN (
                    SELECT client_id FROM trainer_client WHERE trainer_id = $1
                )
                """
                row = await self.fetch_one(query, coach_id)
                stats['workouts_count'] = row['count']
                
                query = """
                SELECT COUNT(*) as count FROM workouts 
                WHERE (coach_id = $1 OR client_id IN (
                    SELECT client_id FROM trainer_client WHERE trainer_id = $1
                )) AND status = 'completed'
                """
                row = await self.fetch_one(query, coach_id)
                stats['completed_workouts'] = row['count']
                
            except Exception as e:
                print(f"Error getting stats: {e}")
                stats = {
                    'clients_count': 0,
                    'workouts_count': 0,
                    'completed_workouts': 0
                }
            
            return stats

else:
    # Use HTTP REST API fallback
    from .connection_fallback import AsyncDatabaseWrapper, simple_db
    DatabaseManager = AsyncDatabaseWrapper
    
    # Create instance
    db_instance = DatabaseManager(simple_db)
    
    class DatabaseManager:
        def __init__(self):
            self.db = db_instance.db
            self.pool = None
        
        async def connect(self):
            await db_instance.connect()
        
        async def disconnect(self):
            await db_instance.disconnect()
        
        async def get_coach_by_telegram_id(self, telegram_id: str):
            return await db_instance.get_coach_by_telegram_id(telegram_id)
        
        async def create_coach(self, telegram_id: str, name: str, username: str = None):
            return await db_instance.create_coach(telegram_id, name, username)
        
        async def get_coach(self, coach_id: int):
            return await db_instance.get_coach(coach_id)
        
        async def create_client(self, coach_id: int, name: str, telegram_id: str = None, 
                              phone: str = None, notes: str = None, fitness_goal: str = None):
            return await db_instance.create_client(coach_id, name, telegram_id, phone, notes, fitness_goal)
        
        async def get_clients_for_coach(self, coach_id: int):
            return await db_instance.get_clients_for_coach(coach_id)
        
        async def get_client(self, client_id: int):
            return await db_instance.get_client(client_id)
        
        async def update_client(self, client_id: int, name: str = None, telegram_id: str = None,
                              phone: str = None, notes: str = None, fitness_goal: str = None):
            return await db_instance.update_client(client_id, name, telegram_id, phone, notes, fitness_goal)
        
        async def delete_client(self, client_id: int):
            return await db_instance.delete_client(client_id)
        
        async def create_workout(self, coach_id: int, client_id: int, date: datetime,
                               exercises: List[Dict] = None, notes: str = None, workout_type: str = None):
            return await db_instance.create_workout(coach_id, client_id, date, exercises, notes, workout_type)
        
        async def get_workouts_for_coach(self, coach_id: int, limit: int = 50):
            return await db_instance.get_workouts_for_coach(coach_id, limit)
        
        async def get_workout(self, workout_id: int):
            return await db_instance.get_workout(workout_id)
        
        async def update_workout_status(self, workout_id: int, status: str, notes: str = None):
            return await db_instance.update_workout_status(workout_id, status, notes)
        
        async def get_stats_for_coach(self, coach_id: int):
            return await db_instance.get_stats_for_coach(coach_id)

# Global database manager instance
db = DatabaseManager()
