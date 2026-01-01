#!/usr/bin/env python3
"""
Test Server Access
Quick test to verify the server starts and dashboard is accessible
"""

import subprocess
import time
import requests
import sys
from threading import Thread

def start_server():
    """Start the server in a separate thread"""
    try:
        subprocess.run([
            "python", "-m", "uvicorn", "scraper.web_api:app", 
            "--host", "0.0.0.0", "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

def test_server_access():
    """Test if the server is accessible"""
    print("🧪 Testing Server Access")
    print("=" * 40)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    try:
        # Test health endpoint
        print("🔍 Testing health endpoint...")
        health_response = requests.get("http://localhost:8000/api/health", timeout=5)
        
        if health_response.status_code == 200:
            print("✅ Health endpoint accessible")
            health_data = health_response.json()
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   Database: {health_data.get('database', 'unknown')}")
        else:
            print(f"❌ Health endpoint failed: {health_response.status_code}")
            return False
        
        # Test dashboard endpoint
        print("🌐 Testing dashboard endpoint...")
        dashboard_response = requests.get("http://localhost:8000/dashboard", timeout=5)
        
        if dashboard_response.status_code == 200:
            print("✅ Dashboard accessible")
            
            # Check for key elements
            content = dashboard_response.text
            if 'article-count-select' in content:
                print("✅ Article count filter present")
            if '手动更新' in content:
                print("✅ Manual update button present")
            if 'dashboard.js' in content:
                print("✅ Dashboard JavaScript loaded")
                
            return True
        else:
            print(f"❌ Dashboard failed: {dashboard_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - server may not be running")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Server Access Test")
    print("=" * 40)
    
    # Start server in background thread
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Test server access
    success = test_server_access()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("✅ Server is running and accessible")
        print("🌐 Dashboard: http://localhost:8000/dashboard")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\n🧪 Test the Progress Notification Fix:")
        print("1. Open http://localhost:8000/dashboard in your browser")
        print("2. Select an article count (e.g., 100篇/源)")
        print("3. Click '手动更新' button")
        print("4. Observe that the progress notification stays visible")
        print("5. Watch it transform to show completion message")
        print("6. Notice it stays visible for 10 seconds")
        
        print("\n⚠️  Press Ctrl+C to stop the server when done testing")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            sys.exit(0)
    else:
        print("\n❌ FAILED!")
        print("Server access test failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()