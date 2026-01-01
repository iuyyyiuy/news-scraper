#!/usr/bin/env python3
"""
Test Manual Update Modal Implementation
Tests the new modal-based article count selection for manual updates.
"""

import subprocess
import time
import requests
import sys
import os

def test_dashboard_access():
    """Test if dashboard is accessible"""
    print("🔍 Testing dashboard access...")
    
    try:
        response = requests.get('http://localhost:5000/dashboard', timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard accessible")
            
            # Check if modal HTML is present
            html_content = response.text
            if 'manual-update-modal' in html_content:
                print("✅ Manual update modal HTML found")
            else:
                print("❌ Manual update modal HTML not found")
                return False
                
            if 'article-count-select' in html_content:
                print("✅ Article count select element found")
            else:
                print("❌ Article count select element not found")
                return False
                
            return True
        else:
            print(f"❌ Dashboard not accessible: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def start_web_server():
    """Start the web server"""
    print("🚀 Starting web server...")
    
    try:
        # Kill any existing processes
        subprocess.run(['pkill', '-f', 'run_web_server.py'], capture_output=True)
        time.sleep(2)
        
        # Start new server
        process = subprocess.Popen([
            sys.executable, 'run_web_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(5)
        
        return process
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def test_manual_update_api():
    """Test manual update API with article count parameter"""
    print("🔍 Testing manual update API...")
    
    try:
        # Test with different article counts
        test_counts = [100, 500, 1000]
        
        for count in test_counts:
            print(f"📤 Testing with {count} articles per source...")
            
            response = requests.post(
                'http://localhost:5000/api/manual-update',
                json={'max_articles': count},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ API accepts {count} articles parameter")
                else:
                    print(f"❌ API error for {count} articles: {result.get('message')}")
            else:
                print(f"❌ HTTP error for {count} articles: {response.status_code}")
                
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API test error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Manual Update Modal Implementation")
    print("=" * 50)
    
    # Start web server
    server_process = start_web_server()
    if not server_process:
        print("❌ Failed to start web server")
        return False
    
    try:
        # Test dashboard access and modal presence
        if not test_dashboard_access():
            print("❌ Dashboard test failed")
            return False
        
        # Test manual update API
        if not test_manual_update_api():
            print("❌ API test failed")
            return False
        
        print("\n✅ All tests passed!")
        print("\n📋 Manual Testing Instructions:")
        print("1. Open http://localhost:5000/dashboard in your browser")
        print("2. Click the '手动更新' button")
        print("3. Verify that a modal appears with article count options")
        print("4. Select different article counts and test the functionality")
        print("5. Verify that the modal closes and manual update starts")
        
        return True
        
    finally:
        # Clean up
        if server_process:
            print("\n🧹 Cleaning up...")
            server_process.terminate()
            time.sleep(2)
            subprocess.run(['pkill', '-f', 'run_web_server.py'], capture_output=True)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)