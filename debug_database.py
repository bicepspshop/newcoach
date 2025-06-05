#!/usr/bin/env python3
"""
Debug script to test database connection and operations
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

async def test_database():
    """Test database connection and operations"""
    print("🔍 Testing database connection...")
    
    try:
        # Connect to database
        await db.connect()
        print("✅ Database connected successfully")
        
        # Test creating a demo coach
        print("\n📝 Testing coach creation...")
        demo_coach_id = await db.create_coach(
            telegram_id="test_debug_123456",
            name="Debug Test Coach",
            username="debug_coach"
        )
        print(f"✅ Demo coach created with ID: {demo_coach_id}")
        
        # Test getting the coach
        coach = await db.get_coach_by_telegram_id("test_debug_123456")
        if coach:
            print(f"✅ Coach retrieved: {coach['name']} (ID: {coach['id']})")
            
            # Test creating a demo client
            print("\n👥 Testing client creation...")
            client_id = await db.create_client(
                coach_id=coach['id'],
                name="Debug Test Client",
                phone="+1234567890",
                notes="Test client for debugging",
                fitness_goal="general_fitness"
            )
            print(f"✅ Demo client created with ID: {client_id}")
            
            # Test getting clients
            clients = await db.get_clients_for_coach(coach['id'])
            print(f"✅ Found {len(clients)} client(s) for coach")
            
            # Test creating a workout
            print("\n💪 Testing workout creation...")
            workout_id = await db.create_workout(
                coach_id=coach['id'],
                client_id=client_id,
                date=datetime.now(),
                exercises=[
                    {"name": "Push-ups", "sets": 3, "reps": 15},
                    {"name": "Squats", "sets": 3, "reps": 20}
                ],
                notes="Debug test workout",
                workout_type="strength_training"
            )
            print(f"✅ Demo workout created with ID: {workout_id}")
            
            # Test getting workouts
            workouts = await db.get_workouts_for_coach(coach['id'])
            print(f"✅ Found {len(workouts)} workout(s) for coach")
            
            # Test getting stats
            print("\n📊 Testing stats...")
            stats = await db.get_stats_for_coach(coach['id'])
            print(f"✅ Stats: {stats}")
            
            # Clean up test data
            print("\n🧹 Cleaning up test data...")
            await db.delete_client(client_id)
            print("✅ Test client deleted")
            
        else:
            print("❌ Failed to retrieve created coach")
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        try:
            await db.disconnect()
            print("✅ Database disconnected")
        except Exception as e:
            print(f"⚠️ Error disconnecting: {e}")

async def check_tables():
    """Check if required tables exist"""
    print("\n🔍 Checking database tables...")
    
    try:
        await db.connect()
        
        tables_to_check = ['coaches', 'clients', 'workouts', 'trainer_client']
        
        for table in tables_to_check:
            try:
                result = await db.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                print(f"✅ Table '{table}': {result['count']} records")
            except Exception as e:
                print(f"❌ Table '{table}': {e}")
                
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
    finally:
        await db.disconnect()

def main():
    """Main function"""
    print("🚀 Database Debug Script")
    print("=" * 50)
    
    # Check environment variables
    print("📋 Environment check:")
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        # Hide password for security
        safe_url = db_url.replace(db_url.split(':')[2].split('@')[0], '***')
        print(f"  DATABASE_URL: {safe_url}")
    else:
        print("  ❌ DATABASE_URL not set")
        return
    
    print(f"  BOT_TOKEN: {'✅ Set' if os.getenv('BOT_TOKEN') else '❌ Not set'}")
    print(f"  WEB_APP_URL: {os.getenv('WEB_APP_URL', 'Not set')}")
    
    print("\n" + "=" * 50)
    
    # Run tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Check tables first
        loop.run_until_complete(check_tables())
        
        # Then test operations
        loop.run_until_complete(test_database())
        
        print("\n🎉 Database debug completed!")
        
    except KeyboardInterrupt:
        print("\n👋 Debug stopped by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
    finally:
        loop.close()

if __name__ == "__main__":
    main()
