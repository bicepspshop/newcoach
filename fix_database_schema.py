#!/usr/bin/env python3
"""
Database Schema Fix for Coach Assistant
This script will recreate the database schema with correct structure
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def fix_database_schema():
    """Fix the database schema by recreating tables with correct structure"""
    print("🔧 Fixing database schema...")
    
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
            
            # Read SQL schema file
            schema_file = os.path.join(os.path.dirname(__file__), 'fix_database_schema.sql')
            with open(schema_file, 'r', encoding='utf-8') as f:
                sql_commands = f.read()
            
            # Split by semicolon and execute each command
            commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
            
            for i, command in enumerate(commands):
                if command and not command.startswith('--'):
                    try:
                        result = await conn.execute(command)
                        print(f"✅ Executed command {i+1}/{len(commands)}")
                    except Exception as e:
                        if "already exists" in str(e) or "does not exist" in str(e):
                            print(f"⚠️ Command {i+1}: {str(e)[:100]}...")
                        else:
                            print(f"❌ Error in command {i+1}: {e}")
            
            # Test the new schema
            print("\n🔍 Testing new schema...")
            
            # Check coaches
            coaches = await conn.fetch("SELECT COUNT(*) as count FROM coaches")
            print(f"✅ Coaches table: {coaches[0]['count']} records")
            
            # Check clients
            clients = await conn.fetch("SELECT COUNT(*) as count FROM clients")
            print(f"✅ Clients table: {clients[0]['count']} records")
            
            # Check workouts
            workouts = await conn.fetch("SELECT COUNT(*) as count FROM workouts")
            print(f"✅ Workouts table: {workouts[0]['count']} records")
            
            # Test schema by describing tables
            client_columns = await conn.fetch("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'clients' 
                ORDER BY ordinal_position
            """)
            
            print(f"\n📋 Clients table structure:")
            for col in client_columns:
                print(f"  - {col['column_name']}: {col['data_type']}")
            
            await conn.close()
            print("✅ Database connection closed")
            
            return True
            
        except ImportError:
            print("⚠️ asyncpg not available, using HTTP API")
            return await fix_schema_via_http()
            
    except Exception as e:
        print(f"❌ Error fixing database schema: {e}")
        import traceback
        traceback.print_exc()
        return False

async def fix_schema_via_http():
    """Fix schema using HTTP API"""
    print("🌐 Using Supabase HTTP API to fix schema...")
    
    try:
        import aiohttp
        import json
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL or SUPABASE_KEY not found")
        
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            # We can't create tables via REST API, but we can check current structure
            print("⚠️ Cannot create tables via REST API.")
            print("📋 Please run the SQL commands manually in Supabase dashboard:")
            print("   1. Go to https://app.supabase.com")
            print("   2. Open your project")
            print("   3. Go to SQL Editor")
            print("   4. Copy and paste the contents of 'fix_database_schema.sql'")
            print("   5. Run the SQL commands")
            
            return False
            
    except ImportError:
        print("❌ aiohttp not available, cannot use HTTP API")
        return False
    except Exception as e:
        print(f"❌ HTTP API error: {e}")
        return False

def show_manual_instructions():
    """Show manual instructions for fixing the schema"""
    print("\n" + "="*60)
    print("📋 MANUAL DATABASE FIX INSTRUCTIONS")
    print("="*60)
    print()
    print("Since automatic schema fix failed, please follow these steps:")
    print()
    print("1. 🌐 Go to https://app.supabase.com")
    print("2. 🔑 Login to your account")
    print("3. 📁 Open your project: nludsxoqhhlfpehhblgg")
    print("4. 🛠️ Go to 'SQL Editor' tab")
    print("5. 📄 Create a new query")
    print("6. 📋 Copy the contents of 'fix_database_schema.sql'")
    print("7. 📝 Paste into the SQL editor")
    print("8. ▶️ Run the SQL commands")
    print()
    print("The SQL file is located at:")
    print(f"📁 {os.path.join(os.getcwd(), 'fix_database_schema.sql')}")
    print()
    print("After running the SQL commands, run this script again to test:")
    print("📝 python fix_database_schema.py")
    print()
    print("="*60)

async def test_fixed_schema():
    """Test if the schema has been fixed"""
    print("\n🔍 Testing if schema is fixed...")
    
    try:
        from database import db
        
        await db.connect()
        print("✅ Database connected")
        
        # Test creating a client
        coach_id = 1  # Your coach ID
        test_client_id = await db.create_client(
            coach_id=coach_id,
            name="Schema Test Client",
            phone="+7 (999) 000-00-00",
            notes="Testing fixed schema",
            fitness_goal="general_fitness"
        )
        
        if test_client_id:
            print(f"✅ Schema is fixed! Created test client with ID: {test_client_id}")
            
            # Clean up test client
            await db.delete_client(test_client_id)
            print("✅ Test client cleaned up")
            
            await db.disconnect()
            return True
        else:
            print("❌ Schema still has issues")
            await db.disconnect()
            return False
            
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False

async def main():
    """Main function"""
    print("🔧 Coach Assistant - Database Schema Fix")
    print("=" * 50)
    
    # First, test if schema is already fixed
    schema_ok = await test_fixed_schema()
    
    if schema_ok:
        print("\n🎉 Database schema is already correct!")
        print("✅ No fixes needed.")
        return
    
    print("\n🔧 Database schema needs fixing...")
    
    # Try to fix automatically
    fixed = await fix_database_schema()
    
    if not fixed:
        show_manual_instructions()
        return
    
    # Test again
    schema_ok = await test_fixed_schema()
    
    if schema_ok:
        print("\n🎉 Database schema successfully fixed!")
        print("✅ You can now run your bot and web app.")
        print("📝 Next: run 'start_complete.bat' to start all services")
    else:
        print("\n❌ Schema fix verification failed")
        show_manual_instructions()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
