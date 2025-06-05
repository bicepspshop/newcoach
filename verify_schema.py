#!/usr/bin/env python3
"""
Test and verify current database schema
Works with the existing BIGINT schema
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_current_schema():
    """Test the current database schema"""
    print("🔍 Testing current database schema...")
    
    try:
        # Try to use asyncpg if available
        try:
            import asyncpg
            print("✅ Using asyncpg for direct PostgreSQL connection")
            
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise ValueError("DATABASE_URL not found in environment variables")
            
            # Connect to database
            conn = await asyncpg.connect(database_url)
            print("✅ Connected to database")
            
            # Check table structure
            print("\n📋 Checking table structures...")
            
            # Check coaches table
            coaches_columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'coaches' 
                ORDER BY ordinal_position
            """)
            
            print("📊 Coaches table:")
            for col in coaches_columns:
                print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
            # Check clients table
            clients_columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'clients' 
                ORDER BY ordinal_position
            """)
            
            print("\n👥 Clients table:")
            for col in clients_columns:
                print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
            # Check workouts table
            workouts_columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'workouts' 
                ORDER BY ordinal_position
            """)
            
            print("\n💪 Workouts table:")
            for col in workouts_columns:
                print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
            # Check if coach_id columns exist
            clients_has_coach_id = any(col['column_name'] == 'coach_id' for col in clients_columns)
            workouts_has_coach_id = any(col['column_name'] == 'coach_id' for col in workouts_columns)
            
            print(f"\n✅ Clients table has coach_id: {clients_has_coach_id}")
            print(f"✅ Workouts table has coach_id: {workouts_has_coach_id}")
            
            if not clients_has_coach_id or not workouts_has_coach_id:
                print("❌ Missing coach_id columns!")
                return False
            
            # Test data operations
            print("\n🧪 Testing data operations...")
            
            # Get your coach
            coach = await conn.fetchrow("SELECT * FROM coaches WHERE telegram_id = '234104161'")
            if coach:
                print(f"✅ Found coach: {coach['name']} (ID: {coach['id']})")
                coach_id = coach['id']
                
                # Test creating a client
                try:
                    client_result = await conn.fetchrow("""
                        INSERT INTO clients (coach_id, name, phone, notes, fitness_goal, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
                        RETURNING id, name
                    """, coach_id, "Test Client Schema", "+7 (999) 111-22-33", "Schema test", "general_fitness")
                    
                    if client_result:
                        print(f"✅ Successfully created test client: {client_result['name']} (ID: {client_result['id']})")
                        test_client_id = client_result['id']
                        
                        # Test creating a workout
                        try:
                            from datetime import datetime, timedelta
                            workout_date = datetime.now() + timedelta(days=1)
                            
                            workout_result = await conn.fetchrow("""
                                INSERT INTO workouts (coach_id, client_id, date, notes, workout_type, status, created_at, updated_at)
                                VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
                                RETURNING id
                            """, coach_id, test_client_id, workout_date, "Schema test workout", "strength_training", "planned")
                            
                            if workout_result:
                                print(f"✅ Successfully created test workout (ID: {workout_result['id']})")
                                
                                # Clean up test data
                                await conn.execute("DELETE FROM workouts WHERE id = $1", workout_result['id'])
                                await conn.execute("DELETE FROM clients WHERE id = $1", test_client_id)
                                print("✅ Test data cleaned up")
                                
                                await conn.close()
                                return True
                            else:
                                print("❌ Failed to create test workout")
                        except Exception as e:
                            print(f"❌ Workout creation failed: {e}")
                    else:
                        print("❌ Failed to create test client")
                except Exception as e:
                    print(f"❌ Client creation failed: {e}")
            else:
                print("❌ Coach not found")
            
            await conn.close()
            return False
            
        except ImportError:
            print("⚠️ asyncpg not available, testing via database module...")
            return await test_via_database_module()
            
    except Exception as e:
        print(f"❌ Error testing schema: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_via_database_module():
    """Test schema via the database module"""
    try:
        from database import db
        
        await db.connect()
        print("✅ Database module connected")
        
        # Test coach retrieval
        coach = await db.get_coach_by_telegram_id("234104161")
        if coach:
            print(f"✅ Found coach via module: {coach['name']} (ID: {coach['id']})")
            
            # Test client creation
            try:
                test_client_id = await db.create_client(
                    coach_id=coach['id'],
                    name="Module Test Client",
                    phone="+7 (999) 222-33-44",
                    notes="Testing via database module",
                    fitness_goal="weight_loss"
                )
                
                if test_client_id:
                    print(f"✅ Successfully created client via module (ID: {test_client_id})")
                    
                    # Test workout creation
                    from datetime import datetime, timedelta
                    workout_date = datetime.now() + timedelta(days=1)
                    
                    workout_id = await db.create_workout(
                        coach_id=coach['id'],
                        client_id=test_client_id,
                        date=workout_date,
                        exercises=[{"name": "Test Exercise", "sets": 3, "reps": 10}],
                        notes="Module test workout",
                        workout_type="cardio"
                    )
                    
                    if workout_id:
                        print(f"✅ Successfully created workout via module (ID: {workout_id})")
                        
                        # Test data retrieval
                        clients = await db.get_clients_for_coach(coach['id'])
                        workouts = await db.get_workouts_for_coach(coach['id'])
                        
                        print(f"✅ Retrieved {len(clients)} clients and {len(workouts)} workouts")
                        
                        # Clean up
                        await db.delete_client(test_client_id)
                        print("✅ Test data cleaned up")
                        
                        await db.disconnect()
                        return True
                    else:
                        print("❌ Failed to create workout via module")
                else:
                    print("❌ Failed to create client via module")
            except Exception as e:
                print(f"❌ Module test failed: {e}")
        else:
            print("❌ Coach not found via module")
        
        await db.disconnect()
        return False
        
    except Exception as e:
        print(f"❌ Database module test failed: {e}")
        return False

async def fix_schema_if_needed():
    """Add missing coach_id columns if they don't exist"""
    print("🔧 Checking if schema needs fixing...")
    
    try:
        import asyncpg
        
        database_url = os.getenv('DATABASE_URL')
        conn = await asyncpg.connect(database_url)
        
        # Check if coach_id exists in clients table
        clients_coach_id = await conn.fetchval("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_name = 'clients' AND column_name = 'coach_id'
        """)
        
        # Check if coach_id exists in workouts table  
        workouts_coach_id = await conn.fetchval("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_name = 'workouts' AND column_name = 'coach_id'
        """)
        
        if clients_coach_id == 0:
            print("🔧 Adding coach_id to clients table...")
            await conn.execute("""
                ALTER TABLE clients 
                ADD COLUMN IF NOT EXISTS coach_id BIGINT REFERENCES coaches(id) ON DELETE CASCADE
            """)
            print("✅ Added coach_id to clients table")
        
        if workouts_coach_id == 0:
            print("🔧 Adding coach_id to workouts table...")
            await conn.execute("""
                ALTER TABLE workouts 
                ADD COLUMN IF NOT EXISTS coach_id BIGINT REFERENCES coaches(id) ON DELETE CASCADE
            """)
            print("✅ Added coach_id to workouts table")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Schema fix failed: {e}")
        return False

async def main():
    """Main function"""
    print("🔍 Coach Assistant - Schema Verification")
    print("=" * 50)
    
    # Test current schema
    schema_ok = await test_current_schema()
    
    if schema_ok:
        print("\n🎉 Database schema is working correctly!")
        print("✅ All operations successful")
        print("📝 You can now run your bot and web app")
        return
    
    print("\n🔧 Schema has issues, attempting to fix...")
    
    # Try to fix schema
    fixed = await fix_schema_if_needed()
    
    if fixed:
        # Test again
        schema_ok = await test_current_schema()
        if schema_ok:
            print("\n🎉 Schema successfully fixed and tested!")
        else:
            print("\n❌ Schema fix didn't resolve all issues")
    else:
        print("\n❌ Could not fix schema automatically")
        print("\n📋 Manual steps needed:")
        print("1. Go to Supabase Dashboard")
        print("2. Run your SQL schema script")
        print("3. Make sure all tables have coach_id columns")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
