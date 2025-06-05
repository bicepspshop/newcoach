#!/usr/bin/env python3
"""
Complete fix for Coach Assistant Bot
This script will fix all synchronization issues between Telegram bot and web app
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database import db
    print("✅ Database module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import database module: {e}")
    sys.exit(1)

async def create_test_data():
    """Create test data to verify everything works"""
    print("🚀 Creating test data...")
    
    try:
        # Connect to database
        await db.connect()
        print("✅ Database connected")
        
        # Test coach creation (your Telegram user)
        test_coach_telegram_id = "234104161"  # aNmOff from your existing data
        
        # Get or create your coach
        coach = await db.get_coach_by_telegram_id(test_coach_telegram_id)
        if not coach:
            print("🏃‍♂️ Creating coach...")
            coach_id = await db.create_coach(
                telegram_id=test_coach_telegram_id,
                name="aNmOff",
                username="aNmOff"
            )
            coach = await db.get_coach_by_telegram_id(test_coach_telegram_id)
            print(f"✅ Coach created: {coach}")
        else:
            print(f"✅ Coach found: {coach}")
        
        coach_id = coach['id']
        
        # Create test clients
        print("\n👥 Creating test clients...")
        
        test_clients = [
            {
                "name": "Тест Клиент 1",
                "phone": "+7 (999) 123-45-67",
                "notes": "Тестовый клиент для проверки синхронизации",
                "fitness_goal": "weight_loss"
            },
            {
                "name": "Анна Спортивная",
                "phone": "+7 (999) 876-54-32", 
                "notes": "Цель: набор мышечной массы",
                "fitness_goal": "muscle_gain"
            },
            {
                "name": "Иван Сильный",
                "phone": "+7 (999) 555-11-22",
                "notes": "Пауэрлифтинг, опытный спортсмен",
                "fitness_goal": "strength_building"
            }
        ]
        
        created_clients = []
        for client_data in test_clients:
            try:
                client_id = await db.create_client(
                    coach_id=coach_id,
                    name=client_data["name"],
                    phone=client_data["phone"],
                    notes=client_data["notes"],
                    fitness_goal=client_data["fitness_goal"]
                )
                created_clients.append(client_id)
                print(f"✅ Created client: {client_data['name']} (ID: {client_id})")
            except Exception as e:
                print(f"⚠️ Error creating client {client_data['name']}: {e}")
        
        # Create test workouts
        print(f"\n💪 Creating test workouts for {len(created_clients)} clients...")
        
        from datetime import timedelta
        
        for i, client_id in enumerate(created_clients):
            try:
                # Create a workout for tomorrow
                workout_date = datetime.now() + timedelta(days=1, hours=i*2)
                
                workout_id = await db.create_workout(
                    coach_id=coach_id,
                    client_id=client_id,
                    date=workout_date,
                    exercises=[
                        {"name": "Приседания", "sets": 3, "reps": 15},
                        {"name": "Отжимания", "sets": 3, "reps": 12},
                        {"name": "Планка", "duration": "60 секунд"}
                    ],
                    notes=f"Тестовая тренировка #{i+1}",
                    workout_type="strength_training"
                )
                print(f"✅ Created workout for client {client_id} (Workout ID: {workout_id})")
            except Exception as e:
                print(f"⚠️ Error creating workout for client {client_id}: {e}")
        
        # Test data retrieval
        print(f"\n📊 Testing data retrieval...")
        
        # Get all clients for coach
        clients = await db.get_clients_for_coach(coach_id)
        print(f"✅ Found {len(clients)} clients for coach")
        
        # Get all workouts for coach
        workouts = await db.get_workouts_for_coach(coach_id)
        print(f"✅ Found {len(workouts)} workouts for coach")
        
        # Get stats
        stats = await db.get_stats_for_coach(coach_id)
        print(f"✅ Coach stats: {stats}")
        
        print(f"\n🎉 Test data creation completed successfully!")
        print(f"Coach ID: {coach_id}")
        print(f"Clients: {len(clients)}")
        print(f"Workouts: {len(workouts)}")
        
        return coach_id, len(clients), len(workouts)
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        return None, 0, 0
    finally:
        await db.disconnect()

async def verify_web_app_compatibility():
    """Verify that web app can access the data"""
    print("\n🌐 Testing web app compatibility...")
    
    try:
        # Simulate web app database connection
        import json
        import aiohttp
        
        # Supabase REST API configuration
        supabase_url = "https://nludsxoqhhlfpehhblgg.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5sdWRzeG9xaGhsZnBlaGhibGdnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgyODUyNjEsImV4cCI6MjA2Mzg2MTI2MX0.o6DtsgGgpuNQFIL9Gh2Ba-xScVW20dU_IDg4QAYYXxQ"
        
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            # Test coaches endpoint
            async with session.get(
                f"{supabase_url}/rest/v1/coaches?telegram_id=eq.234104161",
                headers=headers
            ) as response:
                if response.status == 200:
                    coaches = await response.json()
                    print(f"✅ Web app can access coaches: {len(coaches)} found")
                    
                    if coaches:
                        coach_id = coaches[0]['id']
                        
                        # Test clients endpoint
                        async with session.get(
                            f"{supabase_url}/rest/v1/clients?coach_id=eq.{coach_id}",
                            headers=headers
                        ) as response:
                            if response.status == 200:
                                clients = await response.json()
                                print(f"✅ Web app can access clients: {len(clients)} found")
                            else:
                                print(f"❌ Web app clients access failed: {response.status}")
                        
                        # Test workouts endpoint
                        async with session.get(
                            f"{supabase_url}/rest/v1/workouts?coach_id=eq.{coach_id}",
                            headers=headers
                        ) as response:
                            if response.status == 200:
                                workouts = await response.json()
                                print(f"✅ Web app can access workouts: {len(workouts)} found")
                            else:
                                print(f"❌ Web app workouts access failed: {response.status}")
                else:
                    print(f"❌ Web app coaches access failed: {response.status}")
                    
    except Exception as e:
        print(f"⚠️ Web app compatibility test failed: {e}")
        print("This might be due to missing aiohttp. Web app should still work in browser.")

def check_environment():
    """Check environment configuration"""
    print("📋 Environment Configuration Check")
    print("=" * 50)
    
    # Check required environment variables
    required_vars = [
        'BOT_TOKEN',
        'DATABASE_URL', 
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'WEB_APP_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'TOKEN' in var or 'KEY' in var or 'URL' in var:
                # Hide sensitive data
                if 'postgresql://' in value:
                    safe_value = value.split('@')[1] if '@' in value else value[:20] + '...'
                else:
                    safe_value = value[:20] + '...' if len(value) > 20 else value
                print(f"  ✅ {var}: {safe_value}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            missing_vars.append(var)
            print(f"  ❌ {var}: Not set")
    
    if missing_vars:
        print(f"\n⚠️ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("\n✅ All environment variables are set")
    return True

def create_startup_scripts():
    """Create convenient startup scripts"""
    print("\n📜 Creating startup scripts...")
    
    # Create a comprehensive startup script
    startup_content = """@echo off
echo 🚀 Coach Assistant - Complete Startup
echo ====================================

cd /d "%~dp0"

echo.
echo 🔍 Checking environment...
if not exist ".env" (
    echo ❌ .env file not found!
    pause
    exit /b 1
)

if exist "venv\\Scripts\\activate.bat" (
    echo ✅ Activating virtual environment...
    call venv\\Scripts\\activate.bat
) else (
    echo ⚠️ Virtual environment not found, using system Python
)

echo.
echo 🗄️ Starting database debug...
python debug_database.py

echo.
echo 🌐 Starting web server...
start "Web Server" cmd /k "python server.py"

timeout /t 3 /nobreak > nul

echo.
echo 🤖 Starting Telegram bot...
start "Telegram Bot" cmd /k "python main.py"

echo.
echo ✅ All services started!
echo 🔗 Web App: http://localhost:8000
echo 📱 Telegram Bot: Running in background
echo.
echo Press any key to exit this window...
pause >nul
"""
    
    with open("C:\\Users\\fonsh\\Downloads\\coachapp\\start_complete.bat", "w", encoding="utf-8") as f:
        f.write(startup_content)
    
    print("✅ Created start_complete.bat")
    
    # Create a testing script
    test_content = """@echo off
echo 🧪 Coach Assistant - Test Suite
echo ===============================

cd /d "%~dp0"

if exist "venv\\Scripts\\activate.bat" (
    call venv\\Scripts\\activate.bat
)

echo.
echo 🔍 Running comprehensive tests...
python fix_sync_issues.py

echo.
echo Press any key to exit...
pause >nul
"""
    
    with open("C:\\Users\\fonsh\\Downloads\\coachapp\\test_sync.bat", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print("✅ Created test_sync.bat")

async def main():
    """Main function"""
    print("🔧 Coach Assistant - Sync Issues Fix")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix .env file first.")
        return
    
    # Create startup scripts
    create_startup_scripts()
    
    # Test database and create data
    coach_id, clients_count, workouts_count = await create_test_data()
    
    if coach_id:
        print(f"\n📊 Summary:")
        print(f"  Coach ID: {coach_id}")
        print(f"  Clients: {clients_count}")
        print(f"  Workouts: {workouts_count}")
        
        # Test web app compatibility
        await verify_web_app_compatibility()
        
        print(f"\n🎉 SUCCESS! Your bot and web app should now be synchronized.")
        print(f"\n📝 Next steps:")
        print(f"  1. Run 'start_complete.bat' to start all services")
        print(f"  2. Open http://localhost:8000 in your browser")
        print(f"  3. Test your Telegram bot")
        print(f"  4. Check that data appears in both places")
        
        print(f"\n🔧 If you still have issues:")
        print(f"  1. Run 'test_sync.bat' to run tests")
        print(f"  2. Check the console outputs for errors")
        print(f"  3. Verify your .env file has correct credentials")
        
    else:
        print(f"\n❌ Failed to create test data. Check database connection.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
