#!/usr/bin/env python3
"""
Improved HTTP server for serving the web app with database error handling
"""

import http.server
import socketserver
import os
import sys
import json
import asyncio
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import database connection
try:
    from database.connection import DatabaseManager
    DB_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Database module not available: {e}")
    DB_AVAILABLE = False

PORT = int(os.environ.get("PORT", 8000))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    
    def end_headers(self):
        # Add CORS headers for development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        # API endpoints
        if parsed_path.path == '/api/health':
            self.handle_health_check()
        elif parsed_path.path == '/api/db-status':
            self.handle_db_status()
        else:
            # Serve static files
            super().do_GET()
    
    def handle_health_check(self):
        """Health check endpoint"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            'status': 'ok',
            'message': 'Coach Assistant Web Server is running',
            'database': DB_AVAILABLE
        }
        self.wfile.write(json.dumps(response).encode())
    
    def handle_db_status(self):
        """Database status check endpoint"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if not DB_AVAILABLE:
            response = {
                'status': 'error',
                'message': 'Database module not available',
                'database_url': os.getenv('DATABASE_URL', 'Not set')
            }
        else:
            try:
                # Test database connection
                db = DatabaseManager()
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def test_connection():
                    try:
                        await db.connect()
                        # Test a simple query
                        result = await db.fetch_one("SELECT 1 as test")
                        await db.disconnect()
                        return True, "Database connection successful"
                    except Exception as e:
                        return False, str(e)
                
                success, message = loop.run_until_complete(test_connection())
                loop.close()
                
                if success:
                    response = {
                        'status': 'ok',
                        'message': message,
                        'supabase_url': 'https://nludsxoqhhlfpehhblgg.supabase.co'
                    }
                else:
                    response = {
                        'status': 'error',
                        'message': f'Database connection failed: {message}',
                        'database_url': os.getenv('DATABASE_URL', 'Not set')
                    }
                    
            except Exception as e:
                response = {
                    'status': 'error',
                    'message': f'Error testing database: {str(e)}',
                    'database_url': os.getenv('DATABASE_URL', 'Not set')
                }
        
        self.wfile.write(json.dumps(response, indent=2).encode())

def main():
    """Main server function"""
    # Change to the directory containing static files
    script_dir = Path(__file__).parent
    static_files = ['index.html', 'style.css', 'script.js']
    
    # Check if we have static files in current directory
    if all((script_dir / file).exists() for file in static_files):
        os.chdir(script_dir)
        print(f"📁 Serving from: {script_dir}")
    elif (script_dir / 'web').exists():
        os.chdir(script_dir / 'web')
        print(f"📁 Serving from: {script_dir / 'web'}")
    else:
        print(f"📁 Serving from: {script_dir} (static files may not be available)")
        os.chdir(script_dir)
    
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print(f"🌐 Coach Assistant Web Server Starting...")
            print(f"📍 Port: {PORT}")
            print(f"🔗 Local URL: http://localhost:{PORT}")
            print(f"🔗 Health Check: http://localhost:{PORT}/api/health")
            print(f"🔗 DB Status: http://localhost:{PORT}/api/db-status")
            print(f"")
            
            # Check database status on startup
            if DB_AVAILABLE:
                print(f"🔍 Checking database connection...")
                try:
                    db = DatabaseManager()
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    async def startup_check():
                        try:
                            await db.connect()
                            coaches = await db.fetch_all("SELECT COUNT(*) as count FROM coaches")
                            await db.disconnect()
                            return coaches[0]['count']
                        except Exception as e:
                            return str(e)
                    
                    result = loop.run_until_complete(startup_check())
                    loop.close()
                    
                    if isinstance(result, int):
                        print(f"✅ Database connected! Found {result} coaches in database")
                    else:
                        print(f"❌ Database connection failed: {result}")
                        
                except Exception as e:
                    print(f"⚠️ Database check error: {e}")
            else:
                print(f"⚠️ Database module not available")
            
            print(f"")
            print(f"🚀 Server ready! Visit http://localhost:{PORT}")
            print(f"⏹️ Press Ctrl+C to stop")
            print(f"=" * 60)
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n👋 Web server stopped by user")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} is already in use!")
            print(f"💡 Try a different port: PORT=8001 python server.py")
        else:
            print(f"❌ Server error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
