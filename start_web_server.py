#!/usr/bin/env python3
"""
Simple HTTP server for serving the web app locally
Then expose it via ngrok
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Change to web directory
web_dir = Path(__file__).parent / 'web'
os.chdir(web_dir)

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == "__main__":
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print(f"🌐 Starting web server...")
            print(f"📍 Serving web app from: {web_dir}")
            print(f"🔗 Local URL: http://localhost:{PORT}")
            print(f"")
            print(f"🚀 Next steps:")
            print(f"   1. Keep this server running")
            print(f"   2. In another terminal, run: ngrok http {PORT}")
            print(f"   3. Copy the ngrok HTTPS URL") 
            print(f"   4. Update WEB_APP_URL in .env file")
            print(f"   5. Restart the bot")
            print(f"")
            print(f"⏹️  Press Ctrl+C to stop the server")
            print(f"=" * 50)
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n👋 Web server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
