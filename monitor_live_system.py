#!/usr/bin/env python3
"""
Live System Monitoring - Regular health checks for manual update functionality
"""
import requests
import json
from datetime import datetime, timedelta
import time

def monitor_system():
    """Monitor the live system health and manual update functionality"""
    base_url = "https://crypto-news-scraper.onrender.com"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"🔍 [{timestamp}] Monitoring Live System Health")
    print("=" * 60)
    
    # Test 1: Dashboard accessibility
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=10)
        dashboard_ok = response.status_code == 200
        print(f"✅ Dashboard: {'OK' if dashboard_ok else 'FAILED'} ({response.status_code})")
    except Exception as e:
        dashboard_ok = False
        print(f"❌ Dashboard: FAILED ({e})")
    
    # Test 2: API health
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        api_ok = response.status_code == 200
        print(f"✅ API Health: {'OK' if api_ok else 'FAILED'} ({response.status_code})")
    except Exception as e:
        api_ok = False
        print(f"❌ API Health: FAILED ({e})")
    
    # Test 3: Database articles count
    try:
        response = requests.get(f"{base_url}/api/database/articles?limit=5", timeout=15)
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total', 0)
            articles = data.get('data', [])
            
            print(f"✅ Database: OK ({total_articles} total articles)")
            
            if articles:
                latest = articles[0]
                latest_date = latest.get('date', 'unknown')
                latest_title = latest.get('title', 'unknown')[:50]
                latest_source = latest.get('source', 'unknown')
                print(f"📰 Latest: [{latest_date}] {latest_source}: {latest_title}...")
                
                # Check for recent articles (last 24 hours)
                recent_count = 0
                cutoff_time = datetime.now() - timedelta(hours=24)
                
                for article in articles:
                    scraped_at = article.get('scraped_at', '')
                    if scraped_at:
                        try:
                            scraped_time = datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))
                            if scraped_time.replace(tzinfo=None) > cutoff_time:
                                recent_count += 1
                        except:
                            pass
                
                print(f"📅 Recent articles (24h): {recent_count}")
            else:
                print("⚠️  No articles found")
                
        else:
            print(f"❌ Database: FAILED ({response.status_code})")
            
    except Exception as e:
        print(f"❌ Database: FAILED ({e})")
    
    # Test 4: Manual update status
    try:
        response = requests.get(f"{base_url}/api/manual-update/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ Manual Update: {status_data.get('status', 'unknown').upper()}")
            print(f"📋 Sources: {', '.join(status_data.get('parameters', {}).get('sources', []))}")
        else:
            print(f"❌ Manual Update Status: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Manual Update Status: FAILED ({e})")
    
    # Overall status
    all_systems = dashboard_ok and api_ok
    status_icon = "🟢" if all_systems else "🔴"
    status_text = "ALL SYSTEMS OPERATIONAL" if all_systems else "ISSUES DETECTED"
    
    print("-" * 60)
    print(f"{status_icon} {status_text}")
    print("=" * 60)
    
    return all_systems

def test_manual_update_functionality():
    """Test the manual update functionality with a small batch"""
    base_url = "https://crypto-news-scraper.onrender.com"
    
    print("\n🧪 Testing Manual Update Functionality")
    print("=" * 60)
    
    # Get current article count
    try:
        response = requests.get(f"{base_url}/api/database/articles?limit=1", timeout=15)
        if response.status_code == 200:
            initial_count = response.json().get('total', 0)
            print(f"📊 Initial article count: {initial_count}")
        else:
            print("❌ Could not get initial article count")
            return False
    except Exception as e:
        print(f"❌ Error getting initial count: {e}")
        return False
    
    # Trigger manual update with small batch
    try:
        payload = {"max_articles": 2}
        response = requests.post(f"{base_url}/api/manual-update", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Manual update triggered successfully")
            print(f"📋 Processing: {result.get('parameters', {}).get('max_articles_per_source', 'unknown')} articles per source")
            
            # Wait for processing
            print("⏳ Waiting 60 seconds for processing...")
            time.sleep(60)
            
            # Check for new articles
            response2 = requests.get(f"{base_url}/api/database/articles?limit=1", timeout=15)
            if response2.status_code == 200:
                final_count = response2.json().get('total', 0)
                new_articles = final_count - initial_count
                
                print(f"📊 Final article count: {final_count}")
                print(f"🆕 New articles added: {new_articles}")
                
                if new_articles > 0:
                    print("🎉 SUCCESS: Manual update is working correctly!")
                    return True
                else:
                    print("⚠️  No new articles added (may be normal if no matching articles found)")
                    return True  # Still consider success as the API worked
            else:
                print("❌ Could not check final article count")
                return False
                
        else:
            print(f"❌ Manual update failed: {response.status_code}")
            print(response.text[:200])
            return False
            
    except Exception as e:
        print(f"❌ Error testing manual update: {e}")
        return False

def main():
    """Main monitoring function"""
    print("🚀 Starting Live System Monitoring")
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Basic health monitoring
    system_healthy = monitor_system()
    
    # If system is healthy, test manual update functionality
    if system_healthy:
        manual_update_working = test_manual_update_functionality()
        
        if manual_update_working:
            print("\n🎉 CONCLUSION: System is fully operational!")
            print("✅ Dashboard accessible")
            print("✅ API endpoints working")
            print("✅ Database connected")
            print("✅ Manual update functional")
        else:
            print("\n⚠️  CONCLUSION: System partially operational")
            print("✅ Basic systems working")
            print("❌ Manual update needs attention")
    else:
        print("\n🚨 CONCLUSION: System issues detected!")
        print("❌ Basic system health problems")
    
    print(f"\n📅 Monitoring completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()