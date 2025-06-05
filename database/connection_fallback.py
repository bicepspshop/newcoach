"""
Alternative database connection using requests (HTTP REST API)
Fallback solution if asyncpg doesn't work
"""

import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

class SimpleDatabase:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL', 'https://nludsxoqhhlfpehhblgg.supabase.co')
        self.supabase_key = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5sdWRzeG9xaGhsZnBlaGhibGdnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgyODUyNjEsImV4cCI6MjA2Mzg2MTI2MX0.o6DtsgGgpuNQFIL9Gh2Ba-xScVW20dU_IDg4QAYYXxQ')
        self.base_url = f"{self.supabase_url}/rest/v1"
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        print("✅ Simple Database initialized (HTTP REST API)")
    
    def request(self, endpoint: str, method: str = 'GET', data: dict = None) -> List[Dict]:
        """Make HTTP request to Supabase REST API"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data if data else None,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return response.json() if response.text else []
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Request error: {e}")
            return []
    
    # Coach operations
    def get_coach_by_telegram_id(self, telegram_id: str) -> Optional[Dict[str, Any]]:
        """Get coach by Telegram ID"""
        coaches = self.request(f"/coaches?telegram_id=eq.{telegram_id}")
        return coaches[0] if coaches else None
    
    def create_coach(self, telegram_id: str, name: str, username: str = None) -> int:
        """Create a new coach and return their ID"""
        coach_data = {
            'telegram_id': telegram_id,
            'name': name,
            'username': username,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        coaches = self.request('/coaches', 'POST', coach_data)
        return coaches[0]['id'] if coaches else None
    
    def get_coach(self, coach_id: int) -> Optional[Dict[str, Any]]:
        """Get coach by ID"""
        coaches = self.request(f"/coaches?id=eq.{coach_id}")
        return coaches[0] if coaches else None
    
    # Client operations
    def create_client(self, coach_id: int, name: str, telegram_id: str = None, 
                     phone: str = None, notes: str = None, fitness_goal: str = None) -> int:
        """Create a new client and return their ID"""
        client_data = {
            'coach_id': coach_id,
            'name': name,
            'telegram_id': telegram_id,
            'phone': phone,
            'notes': notes,
            'fitness_goal': fitness_goal,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        clients = self.request('/clients', 'POST', client_data)
        if clients:
            # Also create trainer_client relationship if possible
            try:
                self.request('/trainer_client', 'POST', {
                    'trainer_id': coach_id,
                    'client_id': clients[0]['id'],
                    'created_at': datetime.now().isoformat()
                })
            except:
                pass  # Ignore if table doesn't exist
            
            return clients[0]['id']
        return None
    
    def get_clients_for_coach(self, coach_id: int) -> List[Dict[str, Any]]:
        """Get all clients for a coach"""
        # Try direct approach first
        clients = self.request(f"/clients?coach_id=eq.{coach_id}&order=created_at.desc")
        
        # If no results, try through trainer_client relationship
        if not clients:
            relations = self.request(f"/trainer_client?trainer_id=eq.{coach_id}")
            if relations:
                client_ids = [str(r['client_id']) for r in relations]
                if client_ids:
                    clients = self.request(f"/clients?id=in.({','.join(client_ids)})&order=created_at.desc")
        
        return clients or []
    
    def get_client(self, client_id: int) -> Optional[Dict[str, Any]]:
        """Get client by ID"""
        clients = self.request(f"/clients?id=eq.{client_id}")
        return clients[0] if clients else None
    
    def update_client(self, client_id: int, name: str = None, telegram_id: str = None,
                     phone: str = None, notes: str = None, fitness_goal: str = None):
        """Update client information"""
        update_data = {'updated_at': datetime.now().isoformat()}
        
        if name is not None:
            update_data['name'] = name
        if telegram_id is not None:
            update_data['telegram_id'] = telegram_id
        if phone is not None:
            update_data['phone'] = phone
        if notes is not None:
            update_data['notes'] = notes
        if fitness_goal is not None:
            update_data['fitness_goal'] = fitness_goal
        
        return self.request(f"/clients?id=eq.{client_id}", 'PATCH', update_data)
    
    def delete_client(self, client_id: int):
        """Delete a client"""
        # Delete from trainer_client relationship first
        self.request(f"/trainer_client?client_id=eq.{client_id}", 'DELETE')
        # Delete client
        return self.request(f"/clients?id=eq.{client_id}", 'DELETE')
    
    # Workout operations
    def create_workout(self, coach_id: int, client_id: int, date: datetime,
                      exercises: List[Dict] = None, notes: str = None, workout_type: str = None) -> int:
        """Create a new workout and return its ID"""
        workout_data = {
            'coach_id': coach_id,
            'client_id': client_id,
            'date': date.isoformat() if isinstance(date, datetime) else date,
            'exercises': json.dumps(exercises or []),
            'notes': notes,
            'workout_type': workout_type,
            'status': 'planned',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        workouts = self.request('/workouts', 'POST', workout_data)
        return workouts[0]['id'] if workouts else None
    
    def get_workouts_for_coach(self, coach_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get workouts for a coach"""
        # Try direct approach first
        workouts = self.request(f"/workouts?coach_id=eq.{coach_id}&order=date.desc&limit={limit}")
        
        # If no results, try through client relationships
        if not workouts:
            clients = self.get_clients_for_coach(coach_id)
            if clients:
                client_ids = [str(c['id']) for c in clients]
                if client_ids:
                    workouts = self.request(f"/workouts?client_id=in.({','.join(client_ids)})&order=date.desc&limit={limit}")
        
        return workouts or []
    
    def get_workout(self, workout_id: int) -> Optional[Dict[str, Any]]:
        """Get workout by ID"""
        workouts = self.request(f"/workouts?id=eq.{workout_id}")
        return workouts[0] if workouts else None
    
    def update_workout_status(self, workout_id: int, status: str, notes: str = None):
        """Update workout status and notes"""
        update_data = {
            'status': status,
            'updated_at': datetime.now().isoformat()
        }
        
        if notes is not None:
            update_data['notes'] = notes
        
        return self.request(f"/workouts?id=eq.{workout_id}", 'PATCH', update_data)
    
    def get_stats_for_coach(self, coach_id: int) -> Dict[str, Any]:
        """Get statistics for a coach"""
        try:
            clients = self.get_clients_for_coach(coach_id)
            workouts = self.get_workouts_for_coach(coach_id)
            completed_workouts = [w for w in workouts if w.get('status') == 'completed']
            
            return {
                'clients_count': len(clients),
                'workouts_count': len(workouts),
                'completed_workouts': len(completed_workouts)
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                'clients_count': 0,
                'workouts_count': 0,
                'completed_workouts': 0
            }

# Global database manager instance - Simple version
simple_db = SimpleDatabase()

# Async wrapper functions for compatibility
class AsyncDatabaseWrapper:
    def __init__(self, simple_db):
        self.db = simple_db
        self.pool = None  # For compatibility
    
    async def connect(self):
        """Initialize connection (no-op for HTTP API)"""
        print("✅ Database connected (HTTP REST API)")
    
    async def disconnect(self):
        """Close connection (no-op for HTTP API)"""
        print("✅ Database disconnected")
    
    async def get_coach_by_telegram_id(self, telegram_id: str):
        return self.db.get_coach_by_telegram_id(telegram_id)
    
    async def create_coach(self, telegram_id: str, name: str, username: str = None):
        return self.db.create_coach(telegram_id, name, username)
    
    async def get_coach(self, coach_id: int):
        return self.db.get_coach(coach_id)
    
    async def create_client(self, coach_id: int, name: str, telegram_id: str = None, 
                          phone: str = None, notes: str = None, fitness_goal: str = None):
        return self.db.create_client(coach_id, name, telegram_id, phone, notes, fitness_goal)
    
    async def get_clients_for_coach(self, coach_id: int):
        return self.db.get_clients_for_coach(coach_id)
    
    async def get_client(self, client_id: int):
        return self.db.get_client(client_id)
    
    async def update_client(self, client_id: int, name: str = None, telegram_id: str = None,
                          phone: str = None, notes: str = None, fitness_goal: str = None):
        return self.db.update_client(client_id, name, telegram_id, phone, notes, fitness_goal)
    
    async def delete_client(self, client_id: int):
        return self.db.delete_client(client_id)
    
    async def create_workout(self, coach_id: int, client_id: int, date: datetime,
                           exercises: List[Dict] = None, notes: str = None, workout_type: str = None):
        return self.db.create_workout(coach_id, client_id, date, exercises, notes, workout_type)
    
    async def get_workouts_for_coach(self, coach_id: int, limit: int = 50):
        return self.db.get_workouts_for_coach(coach_id, limit)
    
    async def get_workout(self, workout_id: int):
        return self.db.get_workout(workout_id)
    
    async def update_workout_status(self, workout_id: int, status: str, notes: str = None):
        return self.db.update_workout_status(workout_id, status, notes)
    
    async def get_stats_for_coach(self, coach_id: int):
        return self.db.get_stats_for_coach(coach_id)

# Create async wrapper
db_fallback = AsyncDatabaseWrapper(simple_db)
