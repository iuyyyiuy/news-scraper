#!/usr/bin/env python3
"""
Test Dashboard Network Issues
Tests network calls and timing to diagnose why articles aren't loading.
"""

import requests
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_api_timing():
    """Test API response times"""
    print("🔍 Testing API response times...")
    
    base_url = "http://localhost:8080"
    endpoints = [
        "/api/database/articles",
        "/api/database/keywords", 
        "/api/database/stats"
    ]
    
    for endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ {endpoint} - {response_time:.0f}ms")
                else:
                    print(f"❌ {endpoint} - API error: {data.get('message')}")
            else:
                print(f"❌ {endpoint} - HTTP {response.status_code} in {response_time:.0f}ms")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def test_browser_network():
    """Test dashboard in browser and monitor network calls"""
    print("\n🔍 Testing dashboard network calls in browser...")
    
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--log-level=0")
        
        # Create driver
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            print("📱 Loading dashboard...")
            driver.get("http://localhost:8080/dashboard")
            
            # Wait a bit for JavaScript to execute
            time.sleep(3)
            
            # Check console logs for network activity
            logs = driver.get_log('browser')
            
            print("📊 Browser console logs:")
            for log in logs:
                if 'api' in log['message'].lower() or 'fetch' in log['message'].lower():
                    print(f"   {log['level']}: {log['message']}")
            
            # Check if loading state persists
            try:
                tbody = driver.find_element(By.ID, "articles-tbody")
                rows = tbody.find_elements(By.TAG_NAME, "tr")
                
                if rows:
                    first_row_text = rows[0].text
                    print(f"📋 Table state: {first_row_text}")
                    
                    if "加载中" in first_row_text:
                        print("⚠️ Still in loading state after 3 seconds")
                        
                        # Wait longer and check again
                        time.sleep(5)
                        tbody = driver.find_element(By.ID, "articles-tbody")
                        rows = tbody.find_elements(By.TAG_NAME, "tr")
                        if rows:
                            first_row_text = rows[0].text
                            print(f"📋 Table state after 8 seconds: {first_row_text}")
                    else:
                        print(f"✅ Data loaded: {len(rows)} rows")
                else:
                    print("❌ No table rows found")
                    
            except Exception as e:
                print(f"❌ Error checking table: {e}")
            
            # Check article count display
            try:
                count_element = driver.find_element(By.ID, "article-count")
                count_text = count_element.text
                print(f"📊 Article count: {count_text}")
            except Exception as e:
                print(f"❌ Error checking article count: {e}")
            
            # Check last update display
            try:
                update_element = driver.find_element(By.ID, "last-update")
                update_text = update_element.text
                print(f"📅 Last update: {update_text}")
            except Exception as e:
                print(f"❌ Error checking last update: {e}")
            
            return True
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"❌ Browser network test failed: {e}")
        return False

def test_cors_and_headers():
    """Test CORS and headers"""
    print("\n🔍 Testing CORS and headers...")
    
    try:
        response = requests.get("http://localhost:8080/api/database/articles", 
                              headers={'Origin': 'http://localhost:8080'})
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response headers:")
        for header, value in response.headers.items():
            if 'cors' in header.lower() or 'access-control' in header.lower():
                print(f"   {header}: {value}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Data received: {len(data.get('data', []))} articles")
        
    except Exception as e:
        print(f"❌ CORS test failed: {e}")

def main():
    """Main test function"""
    print("🧪 Testing Dashboard Network Issues")
    print("=" * 50)
    
    # Test API timing
    test_api_timing()
    
    # Test CORS
    test_cors_and_headers()
    
    # Test in browser
    try:
        test_browser_network()
    except Exception as e:
        print(f"\n⚠️ Browser test failed: {e}")
    
    print("\n💡 Troubleshooting Tips:")
    print("1. Check if JavaScript console shows any errors")
    print("2. Check Network tab in browser dev tools")
    print("3. Verify API endpoints are accessible")
    print("4. Check if there are any CORS issues")
    print("5. Try refreshing the page")

if __name__ == "__main__":
    main()