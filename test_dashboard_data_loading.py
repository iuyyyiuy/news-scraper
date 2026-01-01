#!/usr/bin/env python3
"""
Test Dashboard Data Loading
Tests if the dashboard is properly loading and displaying data from the API.
"""

import requests
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_api_endpoints():
    """Test all API endpoints"""
    print("🔍 Testing API endpoints...")
    
    base_url = "http://localhost:8080"
    endpoints = [
        "/api/database/articles",
        "/api/database/keywords", 
        "/api/database/stats"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ {endpoint} - Working")
                    if endpoint == "/api/database/articles":
                        print(f"   📊 Articles: {len(data.get('data', []))}")
                    elif endpoint == "/api/database/keywords":
                        print(f"   📊 Keywords: {len(data.get('data', []))}")
                    elif endpoint == "/api/database/stats":
                        stats = data.get('data', {})
                        print(f"   📊 Total articles: {stats.get('total_articles', 0)}")
                else:
                    print(f"❌ {endpoint} - API error: {data.get('message')}")
            else:
                print(f"❌ {endpoint} - HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def test_dashboard_html():
    """Test if dashboard HTML loads correctly"""
    print("\n🔍 Testing dashboard HTML...")
    
    try:
        response = requests.get("http://localhost:8080/dashboard", timeout=5)
        if response.status_code == 200:
            html = response.text
            
            # Check for key elements
            checks = [
                ("articles-tbody", "Articles table body"),
                ("article-count", "Article count element"),
                ("last-update", "Last update element"),
                ("keyword-filter", "Keyword filter"),
                ("source-filter", "Source filter"),
                ("dashboard.js", "Dashboard JavaScript")
            ]
            
            for element, description in checks:
                if element in html:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} missing")
                    
            return True
        else:
            print(f"❌ Dashboard not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def test_javascript_loading():
    """Test if JavaScript is loading and executing"""
    print("\n🔍 Testing JavaScript loading...")
    
    try:
        response = requests.get("http://localhost:8080/static/js/dashboard.js", timeout=5)
        if response.status_code == 200:
            js_content = response.text
            
            # Check for key JavaScript functions
            js_checks = [
                ("DashboardController", "Main controller class"),
                ("loadArticles", "Load articles method"),
                ("loadKeywords", "Load keywords method"),
                ("loadStats", "Load stats method"),
                ("renderArticles", "Render articles method")
            ]
            
            for check, description in js_checks:
                if check in js_content:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} missing")
                    
            return True
        else:
            print(f"❌ JavaScript not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ JavaScript test failed: {e}")
        return False

def test_browser_console():
    """Test dashboard in browser and check for console errors"""
    print("\n🔍 Testing dashboard in browser...")
    
    try:
        # Setup Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Create driver
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Load dashboard
            driver.get("http://localhost:8080/dashboard")
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "articles-tbody"))
            )
            
            # Check for console errors
            logs = driver.get_log('browser')
            errors = [log for log in logs if log['level'] == 'SEVERE']
            
            if errors:
                print("❌ Browser console errors found:")
                for error in errors:
                    print(f"   {error['message']}")
            else:
                print("✅ No browser console errors")
            
            # Check if articles are loaded
            tbody = driver.find_element(By.ID, "articles-tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            
            if len(rows) > 1:  # More than just loading row
                print(f"✅ Articles loaded: {len(rows)} rows")
            else:
                row_text = rows[0].text if rows else "No rows"
                print(f"❌ Articles not loaded. Row text: {row_text}")
            
            # Check article count
            try:
                count_element = driver.find_element(By.ID, "article-count")
                count_text = count_element.text
                print(f"📊 Article count display: {count_text}")
            except:
                print("❌ Article count element not found")
            
            return True
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"❌ Browser test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Dashboard Data Loading")
    print("=" * 50)
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test dashboard HTML
    test_dashboard_html()
    
    # Test JavaScript loading
    test_javascript_loading()
    
    # Test in browser (requires Chrome/Chromium)
    try:
        test_browser_console()
    except Exception as e:
        print(f"\n⚠️ Browser test skipped (Chrome not available): {e}")
        print("💡 To run browser tests, install Chrome/Chromium and selenium:")
        print("   pip install selenium")
    
    print("\n📋 Manual Testing:")
    print("1. Open http://localhost:8080/dashboard in your browser")
    print("2. Open Developer Tools (F12)")
    print("3. Check Console tab for JavaScript errors")
    print("4. Check Network tab to see if API calls are successful")
    print("5. Verify that articles are loading and displaying")

if __name__ == "__main__":
    main()