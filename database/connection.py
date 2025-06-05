import asyncpg
import asyncio
import json
from typing import Optional, List, Dict, Any
import os
from datetime import datetime


class DatabaseManager:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        # Updated Supabase connection
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
                statement_cache_size=0  # Disable prepared statement cache for pgbouncer
            )
            print("✅ Database connected successfully to new Supabase instance")
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
    async def create_coach(self, telegram_id: str, name: str, username: str = None) -> int:
        """Create a new coach and return their ID"""
        query = """
        INSERT INTO coaches (telegram_id, name, username) 
        VALUES ($1, $2, $3) 
        RETURNING id
        """
        row = await self.fetch_one(query, telegram_id, name, username)
        return row['id']
    
    async def get_coach_by_telegram_id(self, telegram_id: str) -> Optional[Dict[str, Any]]:
        """Get coach by Telegram ID"""
        query = "SELECT * FROM coaches WHERE telegram_id = $1"
        row = await self.fetch_one(query, telegram_id)
        return dict(row) if row else None
    
    async def get_coach(self, coach_id: int) -> Optional[Dict[str, Any]]:
        """Get coach by ID"""
        query = "SELECT * FROM coaches WHERE id = $1"
        row = await self.fetch_one(query, coach_id)
        return dict(row) if row else None
    
    # Client operations
    async def create_client(self, coach_id: int, name: str, telegram_id: str = None, 
                          phone: str = None, notes: str = None, fitness_goal: str = None) -> int:
        """Create a new client and return their ID"""
        query = """
        INSERT INTO clients (coach_id, name, telegram_id, phone, notes, fitness_goal) 
        VALUES ($1, $2, $3, $4, $5, $6) 
        RETURNING id
        """
        row = await self.fetch_one(query, coach_id, name, telegram_id, phone, notes, fitness_goal)
        return row['id']
    
    async def get_clients_for_coach(self, coach_id: int) -> List[Dict[str, Any]]:
        """Get all clients for a coach"""
        query = "SELECT * FROM clients WHERE coach_id = $1 ORDER BY created_at DESC"
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
            query = f"UPDATE clients SET {', '.join(updates)} WHERE id = ${param_count}"
            values.append(client_id)
            await self.execute_query(query, *values)
    
    async def delete_client(self, client_id: int):
        """Delete a client"""
        query = "DELETE FROM clients WHERE id = $1"
        await self.execute_query(query, client_id)
    
    # Workout operations
    async def create_workout(self, coach_id: int, client_id: int, date: datetime,
                           exercises: List[Dict] = None, notes: str = None, workout_type: str = None) -> int:
        """Create a new workout and return its ID"""
        query = """
        INSERT INTO workouts (coach_id, client_id, date, exercises, notes, workout_type) 
        VALUES ($1, $2, $3, $4, $5, $6) 
        RETURNING id
        """
        exercises_json = json.dumps(exercises or [])
        row = await self.fetch_one(query, coach_id, client_id, date, exercises_json, notes, workout_type)
        return row['id']
    
    async def get_workouts_for_coach(self, coach_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get workouts for a coach with client information"""
        query = """
        SELECT w.*, c.name as client_name 
        FROM workouts w 
        JOIN clients c ON w.client_id = c.id 
        WHERE w.coach_id = $1 
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
        query = "UPDATE workouts SET status = $1"
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
        
        # Count clients
        query = "SELECT COUNT(*) as count FROM clients WHERE coach_id = $1"
        row = await self.fetch_one(query, coach_id)
        stats['clients_count'] = row['count']
        
        # Count workouts
        query = "SELECT COUNT(*) as count FROM workouts WHERE coach_id = $1"
        row = await self.fetch_one(query, coach_id)
        stats['workouts_count'] = row['count']
        
        # Count completed workouts
        query = "SELECT COUNT(*) as count FROM workouts WHERE coach_id = $1 AND status = 'completed'"
        row = await self.fetch_one(query, coach_id)
        stats['completed_workouts'] = row['count']
        
        return stats


# Global database manager instance
db = DatabaseManager()
