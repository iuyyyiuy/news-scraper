#!/usr/bin/env python3
"""
Check if the live deployment has the latest code and is working correctly
"""
import requests
import json
import time
from datetime import datetime

def check_deployment_status():
    """Check the deployment status and recent articles"""
    base_url = "https://crypto-news-scraper.onrender.com"
    
    print("🔍 Checking Live Deployment Status")
    print("=" * 50)
    print(f"🌐 Server: {base_url}")
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check 1: Get current articles from correct endpoint
    print("1️⃣ Checking current articles in database...")
    try:
        response = requests.get(f"{base_url}/api/database/articles?limit=10", timeout=15)
        print(f"📡 Articles endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('data', [])
            total = data.get('total', 0)
            
            print(f"📊 Total articles in database: {total}")
            
            if articles:
                print("📰 Recent articles:")
                for i, article in enumerate(articles[:5]):
                    date = article.get('date', 'unknown')
                    title = article.get('title', 'unknown')[:50]
                    source = article.get('source', 'unknown')
                    print(f"   {i+1}. [{date}] {source}: {title}...")
                    
                # Check if we have recent articles (today or yesterday)
                today = datetime.now().strftime('%Y-%m-%d')
                yesterday = (datetime.now().replace(day=datetime.now().day-1)).strftime('%Y-%m-%d')
                
                recent_articles = [a for a in articles if a.get('date', '').startswith(today) or a.get('date', '').startswith(yesterday)]
                print(f"📅 Recent articles (today/yesterday): {len(recent_articles)}")
                
            else:
                print("⚠️  No articles found in database")
                
        else:
            print(f"❌ Failed to get articles: {response.status_code}")
            print(response.text[:200])
            
    except Exception as e:
        print(f"❌ Error checking articles: {e}")
    
    # Check 2: Test manual update with very small number
    print("\n2️⃣ Testing manual update with 5 articles...")
    try:
        payload = {"max_articles": 5}
        response = requests.post(
            f"{base_url}/api/manual-update",
            json=payload,
            timeout=30
        )
        
        print(f"📡 Manual update status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Manual update started successfully")
                print(f"📋 Processing: {result.get('parameters', {}).get('max_articles_per_source', 'unknown')} articles per source")
                
                # Wait and check for new articles
                print("⏳ Waiting 30 seconds for processing...")
                time.sleep(30)
                
                # Check articles again
                response2 = requests.get(f"{base_url}/api/database/articles?limit=5", timeout=15)
                if response2.status_code == 200:
                    data2 = response2.json()
                    new_total = data2.get('total', 0)
                    print(f"📊 Articles after manual update: {new_total}")
                    
                    if new_total > total:
                        print(f"🎉 SUCCESS! Added {new_total - total} new articles")
                        
                        # Show the newest articles
                        new_articles = data2.get('data', [])[:3]
                        print("📰 Newest articles:")
                        for i, article in enumerate(new_articles):
                            date = article.get('date', 'unknown')
                            title = article.get('title', 'unknown')[:50]
                            source = article.get('source', 'unknown')
                            print(f"   {i+1}. [{date}] {source}: {title}...")
                            
                    else:
                        print("⚠️  No new articles were added")
                        print("💡 This could mean:")
                        print("   - No articles matched the security keywords")
                        print("   - All found articles were duplicates")
                        print("   - AI filtered out articles as not relevant")
                        
                else:
                    print("❌ Could not check articles after update")
                    
            else:
                print("❌ Manual update failed to start")
                print(result)
                
        else:
            print(f"❌ Manual update request failed: {response.status_code}")
            print(response.text[:200])
            
    except Exception as e:
        print(f"❌ Error testing manual update: {e}")
    
    # Check 3: Test Jinse domain accessibility
    print("\n3️⃣ Testing Jinse domain accessibility...")
    try:
        # Test if we can access Jinse from our local machine
        response = requests.get("https://www.jinse.com.cn/lives", timeout=10)
        print(f"📡 Jinse accessibility (local): {response.status_code}")
        
        if response.status_code == 200:
            # Look for article IDs
            import re
            pattern = r'/lives/(\d+)\.html'
            matches = re.findall(pattern, response.text)
            
            if matches:
                latest_id = max(int(id_str) for id_str in matches)
                print(f"📰 Latest Jinse article ID: {latest_id}")
                
                # Test accessing a specific article
                test_url = f"https://www.jinse.com.cn/lives/{latest_id}.html"
                article_response = requests.get(test_url, timeout=10)
                print(f"📰 Specific article access: {article_response.status_code}")
                
            else:
                print("⚠️  No article IDs found in Jinse main page")
                
        else:
            print("❌ Cannot access Jinse main page")
            
    except Exception as e:
        print(f"❌ Error testing Jinse: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 Diagnosis Summary:")
    print("1. Check if articles are being saved to database")
    print("2. Verify manual update is processing articles")
    print("3. Check if Jinse domain is accessible from Render servers")
    print("4. Monitor for keyword matching and AI filtering")
    print("=" * 50)

if __name__ == "__main__":
    check_deployment_status()