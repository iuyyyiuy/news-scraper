#!/usr/bin/env python3
"""
Restart Server with Market Analysis
Quick script to restart the web server with the new market analysis functionality
"""

import subprocess
import sys
import time
import requests
import signal
import os

def find_and_kill_existing_server():
    """Find and kill any existing server processes"""
    try:
        # Find processes using port 8000
        result = subprocess.run(['lsof', '-ti:8000'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"✅ Killed existing server process {pid}")
                    time.sleep(1)
                except (ValueError, ProcessLookupError):
                    pass
    except FileNotFoundError:
        # lsof not available, try alternative method
        try:
            result = subprocess.run(['pkill', '-f', 'uvicorn.*scraper.web_api'], capture_output=True)
            if result.returncode == 0:
                print("✅ Killed existing server processes")
                time.sleep(2)
        except FileNotFoundError:
            print("⚠️  Could not check for existing processes")

def start_server():
    """Start the web server with market analysis"""
    print("🚀 Starting Web Server with Market Analysis...")
    
    # Kill any existing servers
    find_and_kill_existing_server()
    
    # Start the server
    try:
        print("⏳ Starting server on http://localhost:8000...")
        
        # Use uvicorn to start the server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "scraper.web_api:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"  # Enable auto-reload for development
        ])
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Test if server is responding
        try:
            response = requests.get("http://localhost:8000/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully!")
                
                # Test market analysis
                response = requests.get("http://localhost:8000/api/market-analysis/markets", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"✅ Market analysis working! Found {len(data.get('markets', []))} markets")
                    else:
                        print(f"⚠️  Market analysis API issue: {data.get('error')}")
                else:
                    print(f"⚠️  Market analysis API returned {response.status_code}")
                
                print("\n🎉 Server is running with Market Analysis!")
                print("=" * 60)
                print("📱 Available Pages:")
                print("   🏠 Home (News Search):     http://localhost:8000/")
                print("   📊 Dashboard:              http://localhost:8000/dashboard")
                print("   📈 Market Analysis:        http://localhost:8000/market-analysis")
                print("   🔍 Monitoring:             http://localhost:8000/monitoring")
                print("\n🔧 API Endpoints:")
                print("   📡 Health Check:           http://localhost:8000/api/health")
                print("   📈 Market Analysis API:    http://localhost:8000/api/market-analysis/markets")
                print("=" * 60)
                print("\n⚠️  Press Ctrl+C to stop the server")
                
                # Keep the process running
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Stopping server...")
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    print("✅ Server stopped")
                
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                process.terminate()
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Server not responding: {e}")
            process.terminate()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

if __name__ == "__main__":
    try:
        success = start_server()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Startup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Startup failed with error: {e}")
        sys.exit(1)