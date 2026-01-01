#!/usr/bin/env python3
"""
Test the live manual update API directly
"""
import requests
import json
import time
from datetime import datetime

def test_manual_update_api():
    """Test the manual update API on the live server"""
    base_url = "https://crypto-news-scraper.onrender.com"
    
    print("🧪 Testing Live Manual Update API")
    print("=" * 50)
    print(f"🌐 Server: {base_url}")
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test with a small number of articles first
    test_payload = {
        "max_articles": 10  # Small test
    }
    
    print("📋 Test payload:", json.dumps(test_payload, indent=2))
    print()
    
    try:
        print("🚀 Sending manual update request...")
        response = requests.post(
            f"{base_url}/api/manual-update",
            json=test_payload,
            timeout=30  # 30 second timeout
        )
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Manual update started successfully!")
                print("📊 Response data:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                # Check if the process started
                if result.get('success'):
                    print("\n⏳ Manual update is running in background...")
                    print("💡 Check the dashboard for progress updates")
                    
                    # Wait a bit and check articles count
                    print("\n⏱️  Waiting 10 seconds to check for new articles...")
                    time.sleep(10)
                    
                    # Check articles endpoint
                    try:
                        articles_response = requests.get(f"{base_url}/api/articles?limit=5", timeout=10)
                        if articles_response.status_code == 200:
                            articles_data = articles_response.json()
                            print(f"📰 Current article count: {articles_data.get('total_count', 'unknown')}")
                        else:
                            print(f"⚠️  Could not check articles: {articles_response.status_code}")
                    except Exception as e:
                        print(f"⚠️  Error checking articles: {e}")
                        
                else:
                    print("❌ Manual update failed to start")
                    
            except json.JSONDecodeError:
                print("⚠️  Response is not valid JSON:")
                print(response.text[:500])
                
        elif response.status_code == 500:
            print("❌ Server error occurred")
            try:
                error_data = response.json()
                print("🔍 Error details:")
                print(json.dumps(error_data, indent=2))
            except:
                print("🔍 Error response:")
                print(response.text[:500])
                
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            print("🔍 Response content:")
            print(response.text[:500])
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - this might be normal for manual update")
        print("💡 The process may still be running in the background")
        
    except Exception as e:
        print(f"❌ Request failed: {e}")
        
    print("\n" + "=" * 50)

def check_recent_articles():
    """Check if there are recent articles in the database"""
    base_url = "https://crypto-news-scraper.onrender.com"
    
    print("📰 Checking recent articles...")
    
    try:
        # Try different endpoints to get articles
        endpoints_to_try = [
            "/api/articles",
            "/api/articles?limit=10",
            "/api/database/articles",
            "/api/database/articles?limit=10"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                print(f"📡 {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        articles = data.get('articles', [])
                        total = data.get('total_count', len(articles))
                        
                        print(f"✅ Found {total} total articles")
                        
                        if articles:
                            latest = articles[0]
                            print(f"📅 Latest article date: {latest.get('date', 'unknown')}")
                            print(f"📰 Latest title: {latest.get('title', 'unknown')[:60]}...")
                            print(f"🏷️  Source: {latest.get('source', 'unknown')}")
                        
                        return True
                        
                    except json.JSONDecodeError:
                        print("⚠️  Response not JSON")
                        
            except Exception as e:
                print(f"⚠️  {endpoint} failed: {e}")
                
        print("❌ Could not access articles from any endpoint")
        return False
        
    except Exception as e:
        print(f"❌ Error checking articles: {e}")
        return False

if __name__ == "__main__":
    # First check current articles
    check_recent_articles()
    print()
    
    # Then test manual update
    test_manual_update_api()
    
    print("\n💡 Next steps:")
    print("1. Check the Render deployment logs for any errors")
    print("2. Verify the latest code is deployed")
    print("3. Test the manual update button on the dashboard")
    print("4. Monitor for new articles after manual update")