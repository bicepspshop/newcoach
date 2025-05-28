#!/usr/bin/env python3
import os
from start_web_server import *

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8000))
    
    print(f"🌐 Starting Coach Assistant Web Server...")
    print(f"📍 Port: {PORT}")
    print(f"🚀 Environment: Production")
    
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
            print(f"✅ Server running on port {PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)