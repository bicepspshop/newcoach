#!/usr/bin/env python3
"""
🚀 Coach Assistant - Unified Startup Script
Automatically starts web server, ngrok tunnel, updates .env, and launches bot
"""

import subprocess
import time
import json
import requests
import os
import sys
import signal
import atexit
from pathlib import Path

class CoachAssistantLauncher:
    def __init__(self):
        self.processes = []
        self.web_server_port = 8000
        self.ngrok_api_url = "http://localhost:4040/api/tunnels"
        self.env_file = Path(".env")
        
        # Register cleanup function
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def print_header(self):
        print("=" * 60)
        print("🚀 COACH ASSISTANT - UNIFIED LAUNCHER")
        print("=" * 60)
        print("This script will:")
        print("  1. 🌐 Start web server (port 8000)")
        print("  2. 🌍 Start ngrok tunnel")
        print("  3. 📝 Auto-update .env with ngrok URL")
        print("  4. 🤖 Launch the bot")
        print("=" * 60)
        print()
    
    def check_requirements(self):
        """Check if required tools are available"""
        print("🔍 Checking requirements...")
        
        # Check Python
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"  ✅ Python: {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            print("  ❌ Python not found!")
            return False
        
        # Check ngrok
        ngrok_path = Path("ngrok.exe")
        if not ngrok_path.exists():
            print("  ❌ ngrok.exe not found in current directory!")
            print("     Please download ngrok and place ngrok.exe in this folder")
            return False
        else:
            print("  ✅ ngrok.exe found")
        
        # Check .env file
        if not self.env_file.exists():
            print("  ❌ .env file not found!")
            return False
        else:
            print("  ✅ .env file found")
        
        print()
        return True
    
    def start_web_server(self):
        """Start the web server in background"""
        print("🌐 Starting web server...")
        try:
            process = subprocess.Popen(
                [sys.executable, "start_web_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            self.processes.append(("Web Server", process))
            print(f"  ✅ Web server started (PID: {process.pid})")
            
            # Wait a moment for server to start
            time.sleep(2)
            return True
        except Exception as e:
            print(f"  ❌ Failed to start web server: {e}")
            return False
    
    def start_ngrok(self):
        """Start ngrok tunnel in background"""
        print("🌍 Starting ngrok tunnel...")
        try:
            process = subprocess.Popen(
                ["ngrok.exe", "http", str(self.web_server_port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            self.processes.append(("Ngrok", process))
            print(f"  ✅ Ngrok started (PID: {process.pid})")
            
            # Wait for ngrok to initialize
            print("  ⏳ Waiting for ngrok to initialize...")
            time.sleep(5)
            return True
        except Exception as e:
            print(f"  ❌ Failed to start ngrok: {e}")
            return False
    
    def get_ngrok_url(self, max_retries=10):
        """Get ngrok public URL from API"""
        print("🔗 Getting ngrok URL...")
        
        for attempt in range(max_retries):
            try:
                response = requests.get(self.ngrok_api_url, timeout=5)
                response.raise_for_status()
                
                data = response.json()
                tunnels = data.get('tunnels', [])
                
                for tunnel in tunnels:
                    if tunnel.get('proto') == 'https':
                        url = tunnel.get('public_url')
                        if url:
                            print(f"  ✅ Found ngrok URL: {url}")
                            return url
                
                print(f"  ⏳ Attempt {attempt + 1}/{max_retries} - No HTTPS tunnel found, retrying...")
                time.sleep(2)
                
            except requests.exceptions.RequestException as e:
                print(f"  ⏳ Attempt {attempt + 1}/{max_retries} - API not ready, retrying...")
                time.sleep(2)
        
        print("  ❌ Failed to get ngrok URL after all retries")
        return None
    
    def update_env_file(self, ngrok_url):
        """Update .env file with new ngrok URL"""
        print("📝 Updating .env file...")
        
        try:
            # Read current .env content
            with open(self.env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Update WEB_APP_URL line
            updated_lines = []
            url_updated = False
            
            for line in lines:
                if line.startswith('WEB_APP_URL='):
                    updated_lines.append(f'WEB_APP_URL={ngrok_url}\n')
                    url_updated = True
                    print(f"  ✅ Updated WEB_APP_URL to: {ngrok_url}")
                else:
                    updated_lines.append(line)
            
            # If WEB_APP_URL wasn't found, add it
            if not url_updated:
                updated_lines.append(f'\nWEB_APP_URL={ngrok_url}\n')
                print(f"  ✅ Added WEB_APP_URL: {ngrok_url}")
            
            # Write updated content
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
            
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to update .env file: {e}")
            return False
    
    def start_bot(self):
        """Start the Telegram bot"""
        print("🤖 Starting Telegram bot...")
        print("=" * 60)
        print()
        
        try:
            # Check if virtual environment exists
            venv_path = Path("venv")
            if not venv_path.exists():
                print("Creating virtual environment...")
                subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            
            # Determine python executable path
            if os.name == 'nt':  # Windows
                python_exe = venv_path / "Scripts" / "python.exe"
                pip_exe = venv_path / "Scripts" / "pip.exe"
            else:  # Unix-like
                python_exe = venv_path / "bin" / "python"
                pip_exe = venv_path / "bin" / "pip"
            
            # Install requirements
            print("Installing/updating requirements...")
            subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True)
            
            # Run the bot (this will block)
            print("Bot is starting...")
            print("🟢 ALL SERVICES RUNNING - Bot is now active!")
            print("📱 Test your bot in Telegram")
            print("⏹️  Press Ctrl+C to stop all services")
            print()
            
            process = subprocess.run([str(python_exe), "main.py"])
            return process.returncode == 0
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start bot: {e}")
            return False
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal")
            return True
    
    def cleanup(self):
        """Clean up all processes"""
        if self.processes:
            print("\n🧹 Cleaning up processes...")
            for name, process in self.processes:
                try:
                    if process.poll() is None:  # Process is still running
                        print(f"  🛑 Stopping {name}...")
                        process.terminate()
                        # Wait a bit for graceful termination
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            print(f"  💀 Force killing {name}...")
                            process.kill()
                except Exception as e:
                    print(f"  ⚠️  Error stopping {name}: {e}")
            
            print("  ✅ Cleanup complete")
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        print(f"\n🛑 Received signal {signum}")
        sys.exit(0)
    
    def run(self):
        """Main execution flow"""
        self.print_header()
        
        # Check requirements
        if not self.check_requirements():
            print("❌ Requirements check failed. Please fix the issues above.")
            return False
        
        # Start web server
        if not self.start_web_server():
            print("❌ Failed to start web server")
            return False
        
        # Start ngrok
        if not self.start_ngrok():
            print("❌ Failed to start ngrok")
            return False
        
        # Get ngrok URL
        ngrok_url = self.get_ngrok_url()
        if not ngrok_url:
            print("❌ Failed to get ngrok URL")
            return False
        
        # Update .env file
        if not self.update_env_file(ngrok_url):
            print("❌ Failed to update .env file")
            return False
        
        # Start bot
        print()
        return self.start_bot()

def main():
    launcher = CoachAssistantLauncher()
    try:
        success = launcher.run()
        if not success:
            print("\n❌ Startup failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
    finally:
        launcher.cleanup()

if __name__ == "__main__":
    main()
