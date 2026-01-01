#!/usr/bin/env python3
"""
Test ForesightNews scraper to understand the structure and accessibility
"""
import requests
import time
import re
from bs4 import BeautifulSoup
from datetime import datetime

def test_foresightnews_access():
    """Test different methods to access ForesightNews"""
    print("🔍 Testing ForesightNews Access Methods")
    print("=" * 60)
    
    # Different headers to try
    headers_list = [
        {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        },
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
    ]
    
    urls_to_test = [
        'https://foresightnews.pro/news',
        'https://foresightnews.pro/news/detail/94132',
        'https://foresightnews.pro/news/detail/94130',
        'https://foresightnews.pro/news/detail/94100'
    ]
    
    for i, headers in enumerate(headers_list):
        print(f"\n{i+1}️⃣ Testing with headers set {i+1}...")
        
        for url in urls_to_test:
            try:
                print(f"\n🌐 Testing: {url}")
                
                session = requests.Session()
                session.headers.update(headers)
                
                response = session.get(url, timeout=15, allow_redirects=True)
                print(f"Status: {response.status_code}")
                print(f"Final URL: {response.url}")
                print(f"Content length: {len(response.text)}")
                
                # Check if we got past the anti-bot protection
                if 'aliyun_waf' in response.text.lower():
                    print("❌ Blocked by Aliyun WAF")
                elif len(response.text) < 1000:
                    print("❌ Very short response - likely blocked")
                elif 'foresightnews' in response.text.lower() or '前瞻' in response.text:
                    print("✅ Looks like real ForesightNews content!")
                    
                    # Try to extract article IDs
                    patterns = [
                        r'/news/detail/(\d+)',
                        r'/detail/(\d+)',
                        r'newsId["\']?\s*:\s*["\']?(\d+)',
                        r'id["\']?\s*:\s*["\']?(\d{5,})'
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, response.text)
                        if matches:
                            print(f"📰 Found article IDs with pattern {pattern}: {matches[:5]}")
                            
                    # Show sample content
                    print("📄 Content sample:")
                    print(response.text[:500])
                    
                    # If this is an article page, try to parse it
                    if '/detail/' in url:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Look for title
                        title_selectors = ['h1', '.title', '.article-title', '[class*="title"]']
                        for selector in title_selectors:
                            title_elem = soup.select_one(selector)
                            if title_elem and title_elem.get_text(strip=True):
                                print(f"📰 Title: {title_elem.get_text(strip=True)[:100]}...")
                                break
                        
                        # Look for content
                        content_selectors = ['.content', '.article-content', '[class*="content"]', 'article']
                        for selector in content_selectors:
                            content_elem = soup.select_one(selector)
                            if content_elem and content_elem.get_text(strip=True):
                                print(f"📝 Content: {content_elem.get_text(strip=True)[:100]}...")
                                break
                    
                    return True  # Found working method
                else:
                    print("⚠️  Unknown response format")
                    
                time.sleep(2)  # Be respectful
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    return False

def test_api_endpoints():
    """Test if ForesightNews has API endpoints"""
    print("\n🔍 Testing Potential API Endpoints")
    print("=" * 60)
    
    api_urls = [
        'https://foresightnews.pro/api/news',
        'https://foresightnews.pro/api/articles',
        'https://api.foresightnews.pro/news',
        'https://foresightnews.pro/api/v1/news',
        'https://foresightnews.pro/news.json'
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }
    
    for url in api_urls:
        try:
            print(f"\n🌐 Testing API: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
                print(f"Content length: {len(response.text)}")
                
                # Try to parse as JSON
                try:
                    import json
                    data = response.json()
                    print("✅ Valid JSON response!")
                    print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
                except:
                    print("📄 Text response:")
                    print(response.text[:300])
                    
        except Exception as e:
            print(f"❌ Error: {e}")

def test_article_id_range():
    """Test a range of article IDs to find the pattern"""
    print("\n🔍 Testing Article ID Range")
    print("=" * 60)
    
    # Test recent IDs around 94132
    test_ids = [94132, 94131, 94130, 94129, 94128, 94120, 94110, 94100]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    working_ids = []
    
    for article_id in test_ids:
        try:
            url = f"https://foresightnews.pro/news/detail/{article_id}"
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"ID {article_id}: Status {response.status_code}")
            
            if response.status_code == 200 and len(response.text) > 1000:
                if 'aliyun_waf' not in response.text.lower():
                    working_ids.append(article_id)
                    print(f"  ✅ Working ID: {article_id}")
                else:
                    print(f"  ❌ Blocked by WAF")
            
            time.sleep(1)  # Be respectful
            
        except Exception as e:
            print(f"ID {article_id}: Error - {e}")
    
    if working_ids:
        print(f"\n✅ Working IDs found: {working_ids}")
        print(f"Latest working ID: {max(working_ids)}")
        return max(working_ids)
    else:
        print("\n❌ No working IDs found")
        return None

if __name__ == "__main__":
    print("🚀 ForesightNews Scraper Analysis")
    print("=" * 60)
    
    # Test basic access
    access_working = test_foresightnews_access()
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test article ID range
    latest_id = test_article_id_range()
    
    print("\n" + "=" * 60)
    print("🔍 ANALYSIS SUMMARY:")
    print(f"✅ Basic access working: {access_working}")
    print(f"🎯 Latest working ID: {latest_id}")
    
    if access_working and latest_id:
        print("\n💡 RECOMMENDATION:")
        print("✅ ForesightNews can be implemented as a news source")
        print("📋 Implementation approach:")
        print("   1. Use article ID iteration (similar to BlockBeats)")
        print("   2. Start from latest working ID and iterate backwards")
        print("   3. Handle anti-bot protection with proper headers")
        print("   4. Add delays between requests")
    else:
        print("\n⚠️  RECOMMENDATION:")
        print("❌ ForesightNews may be difficult to scrape reliably")
        print("💡 Consider alternative sources or wait for better access")
    
    print("=" * 60)