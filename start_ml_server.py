#!/usr/bin/env python3
"""
Simple ML Server Startup Script
Start the web server with ML analysis functionality
"""

import subprocess
import sys
import time
import requests
import os
import signal

def kill_existing_servers():
    """Kill any existing servers on port 8000"""
    try:
        # Find and kill processes on port 8000
        result = subprocess.run(['lsof', '-ti:8000'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"🔄 Stopped existing server (PID: {pid})")
                    time.sleep(1)
                except (ValueError, ProcessLookupError):
                    pass
    except FileNotFoundError:
        # Try alternative method
        subprocess.run(['pkill', '-f', 'uvicorn.*scraper.web_api'], capture_output=True)

def test_server():
    """Test if server is working"""
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/api/health", timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        
        if attempt < max_attempts - 1:
            print(f"⏳ Waiting for server... ({attempt + 1}/{max_attempts})")
            time.sleep(2)
    
    return False

def main():
    print("🚀 Starting ML Analysis Server")
    print("=" * 40)
    
    # Step 1: Kill existing servers
    print("🔄 Checking for existing servers...")
    kill_existing_servers()
    
    # Step 2: Start new server
    print("🌐 Starting server on http://localhost:8000...")
    
    try:
        # Start server in background
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn",
            "scraper.web_api:app",
            "--host", "0.0.0.0",
            "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        if test_server():
            print("✅ Server started successfully!")
            
            # Test ML functionality
            try:
                response = requests.get("http://localhost:8000/api/ml-analysis/status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ml_available"):
                        print("✅ ML Analysis: Available")
                    else:
                        print("⚠️  ML Analysis: Limited (dependencies missing)")
                elif response.status_code == 503:
                    print("⚠️  ML Analysis: Service unavailable")
                else:
                    print(f"⚠️  ML Analysis: Status {response.status_code}")
            except:
                print("⚠️  ML Analysis: Could not test")
            
            # Show available pages
            print("\n🎉 Server is running!")
            print("=" * 40)
            print("📱 Available Pages:")
            print("   🏠 Home:           http://localhost:8000/")
            print("   📊 Dashboard:      http://localhost:8000/dashboard")
            print("   📈 Market Analysis: http://localhost:8000/market-analysis")
            print("   🧠 ML Analysis:    http://localhost:8000/ml-analysis")
            print("\n🔧 API Health Check:")
            print("   📡 Health:         http://localhost:8000/api/health")
            print("=" * 40)
            print("\n✨ ML Analysis is ready at: http://localhost:8000/ml-analysis")
            print("⚠️  Server is running in background (PID: {})".format(process.pid))
            print("🛑 To stop: kill {}".format(process.pid))
            
            return True
            
        else:
            print("❌ Server failed to start properly")
            process.terminate()
            return False
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 Next steps:")
        print("1. Open your browser")
        print("2. Go to: http://localhost:8000/ml-analysis")
        print("3. Click 'Start Data Collection' or 'Simulate Data'")
        print("4. Train the ML model and get predictions!")
    else:
        print("\n❌ Server startup failed. Check the error messages above.")
        sys.exit(1)