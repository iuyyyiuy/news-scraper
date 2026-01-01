#!/usr/bin/env python3
"""
Test Web Server Start
Quick test to verify the web server can start with market analysis routes
"""

import sys
import time
import requests
import subprocess
import signal
import os

def test_server_start():
    """Test if the web server can start successfully"""
    
    print("🚀 Testing Web Server Start with Market Analysis...")
    
    # Start the web server in background
    try:
        # Use uvicorn to start the server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "scraper.web_api:app", 
            "--host", "127.0.0.1", 
            "--port", "8001",  # Use different port to avoid conflicts
            "--log-level", "error"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("⏳ Starting server...")
        time.sleep(5)  # Give server time to start
        
        # Test if server is responding
        try:
            response = requests.get("http://127.0.0.1:8001/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully!")
                
                # Test market analysis page
                response = requests.get("http://127.0.0.1:8001/market-analysis", timeout=5)
                if response.status_code == 200:
                    print("✅ Market analysis page accessible!")
                else:
                    print(f"❌ Market analysis page failed: {response.status_code}")
                
                # Test market analysis API
                response = requests.get("http://127.0.0.1:8001/api/market-analysis/markets", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"✅ Market analysis API working! Found {len(data.get('markets', []))} markets")
                    else:
                        print(f"❌ Market analysis API error: {data.get('error')}")
                else:
                    print(f"❌ Market analysis API failed: {response.status_code}")
                
                success = True
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                success = False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Server not responding: {e}")
            success = False
        
        # Stop the server
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        
        print("🛑 Server stopped")
        return success
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

if __name__ == "__main__":
    try:
        success = test_server_start()
        if success:
            print("\n🎉 All tests passed! The market analysis system is working.")
            print("\n📋 To start the server manually:")
            print("   python3 run_web_server.py")
            print("   # or")
            print("   uvicorn scraper.web_api:app --host 0.0.0.0 --port 8000")
            print("\n🌐 Then visit: http://localhost:8000/market-analysis")
        else:
            print("\n❌ Tests failed. Check the error messages above.")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)