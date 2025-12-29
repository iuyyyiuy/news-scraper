#!/usr/bin/env python3
"""
Debug the live manual update issue on Render deployment
"""
import requests
import json
from datetime import datetime
import time

def test_live_deployment():
    """Test the live deployment manual update functionality"""
    base_url = "https://crypto-news-scraper.onrender.com"
    
    print("🔍 Debugging Live Manual Update Issue")
    print("=" * 60)
    print(f"🌐 Testing: {base_url}")
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Check if the site is accessible
    print("1️⃣ Testing site accessibility...")
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=10)
        print(f"✅ Dashboard accessible: {response.status_code}")
        
        # Check if manual update button exists
        if '手动更新' in response.text:
            print("✅ Manual update button found in HTML")
        else:
            print("❌ Manual update button NOT found in HTML")
            
    except Exception as e:
        print(f"❌ Dashboard access failed: {e}")
        return False
    
    # Test 2: Check API health
    print("\n2️⃣ Testing API health...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"✅ Health endpoint accessible: {response.status_code}")
        
        if response.status_code == 200:
            try:
                health_data = response.json()
                print(f"📊 Health status: {health_data.get('status', 'unknown')}")
                print(f"🗄️  Database: {health_data.get('database', 'unknown')}")
                
                env_vars = health_data.get('env_vars', {})
                print(f"🔑 SUPABASE_URL: {env_vars.get('SUPABASE_URL', 'missing')}")
                print(f"🔑 SUPABASE_KEY: {env_vars.get('SUPABASE_KEY', 'missing')}")
            except:
                print("⚠️  Could not parse health response as JSON")
                
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 3: Check manual update status endpoint
    print("\n3️⃣ Testing manual update status...")
    try:
        response = requests.get(f"{base_url}/api/manual-update/status", timeout=10)
        print(f"✅ Manual update status accessible: {response.status_code}")
        
        if response.status_code == 200:
            try:
                status_data = response.json()
                print(f"📊 Status: {status_data.get('status', 'unknown')}")
                print(f"📝 Message: {status_data.get('message', 'no message')}")
                
                # Check parameters
                params = status_data.get('parameters', {})
                print(f"📰 Max articles per source: {params.get('max_articles_per_source', 'unknown')}")
                print(f"🔍 Sources: {params.get('sources', 'unknown')}")
                
            except:
                print("⚠️  Could not parse status response as JSON")
                
    except Exception as e:
        print(f"❌ Manual update status failed: {e}")
    
    # Test 4: Test manual update API (without actually running it)
    print("\n4️⃣ Testing manual update API endpoint...")
    try:
        # Just check if the endpoint exists (don't actually trigger it)
        response = requests.options(f"{base_url}/api/manual-update", timeout=10)
        print(f"✅ Manual update endpoint exists: {response.status_code}")
        
        # Check allowed methods
        allowed_methods = response.headers.get('Allow', 'unknown')
        print(f"📋 Allowed methods: {allowed_methods}")
        
    except Exception as e:
        print(f"❌ Manual update endpoint test failed: {e}")
    
    # Test 5: Check recent articles in database
    print("\n5️⃣ Testing database articles...")
    try:
        response = requests.get(f"{base_url}/api/articles", timeout=10)
        print(f"✅ Articles endpoint accessible: {response.status_code}")
        
        if response.status_code == 200:
            try:
                articles_data = response.json()
                articles = articles_data.get('articles', [])
                total_count = articles_data.get('total_count', 0)
                
                print(f"📊 Total articles in database: {total_count}")
                
                if articles:
                    latest_article = articles[0]
                    print(f"📰 Latest article date: {latest_article.get('date', 'unknown')}")
                    print(f"📰 Latest article title: {latest_article.get('title', 'unknown')[:50]}...")
                    print(f"📰 Latest article source: {latest_article.get('source', 'unknown')}")
                else:
                    print("⚠️  No articles found in database")
                    
            except:
                print("⚠️  Could not parse articles response as JSON")
                
    except Exception as e:
        print(f"❌ Articles endpoint test failed: {e}")
    
    # Test 6: Check if Jinse domain is accessible from Render
    print("\n6️⃣ Testing Jinse accessibility from deployment...")
    try:
        # Test if we can reach Jinse from the deployment
        response = requests.get(f"{base_url}/api/test-jinse-access", timeout=15)
        if response.status_code == 404:
            print("⚠️  Test endpoint not available (expected)")
        else:
            print(f"📡 Jinse test response: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Jinse test endpoint not available: {e}")
    
    print("\n" + "=" * 60)
    print("🔍 Debug Summary:")
    print("1. Check if the deployment has the latest code")
    print("2. Verify environment variables are set correctly")
    print("3. Check if Jinse domain is accessible from Render servers")
    print("4. Monitor server logs for errors during manual update")
    print("=" * 60)
    
    return True

def create_monitoring_script():
    """Create a monitoring script for regular checks"""
    monitoring_script = '''#!/usr/bin/env python3
"""
Regular monitoring script for manual update functionality
Run this every 30 minutes to check system health
"""
import requests
import json
from datetime import datetime
import time

def monitor_system():
    base_url = "https://crypto-news-scraper.onrender.com"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"🔍 [{timestamp}] Monitoring manual update system...")
    
    # Quick health checks
    checks = {
        "dashboard": False,
        "health_api": False,
        "manual_update_status": False,
        "articles_api": False
    }
    
    # Test dashboard
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=10)
        checks["dashboard"] = response.status_code == 200
    except:
        pass
    
    # Test health API
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        checks["health_api"] = response.status_code == 200
    except:
        pass
    
    # Test manual update status
    try:
        response = requests.get(f"{base_url}/api/manual-update/status", timeout=10)
        checks["manual_update_status"] = response.status_code == 200
    except:
        pass
    
    # Test articles API
    try:
        response = requests.get(f"{base_url}/api/articles", timeout=10)
        checks["articles_api"] = response.status_code == 200
    except:
        pass
    
    # Report results
    all_good = all(checks.values())
    status = "✅ ALL SYSTEMS OK" if all_good else "⚠️  ISSUES DETECTED"
    
    print(f"📊 {status}")
    for check, result in checks.items():
        icon = "✅" if result else "❌"
        print(f"   {icon} {check}: {'OK' if result else 'FAILED'}")
    
    if not all_good:
        print("🚨 Manual intervention may be required!")
    
    print()
    return all_good

if __name__ == "__main__":
    monitor_system()
'''
    
    with open("monitor_live_system.py", "w") as f:
        f.write(monitoring_script)
    
    print("✅ Created monitoring script: monitor_live_system.py")

if __name__ == "__main__":
    test_live_deployment()
    create_monitoring_script()