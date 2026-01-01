#!/usr/bin/env python3
"""
Debug ForesightNews scraper on localhost to see what's happening
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import time

def debug_foresightnews_access():
    """Debug ForesightNews access and content extraction"""
    print("🔍 Debugging ForesightNews Access")
    print("=" * 50)
    
    try:
        # Setup Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        print("1️⃣ Loading ForesightNews main page...")
        driver.get("https://foresightnews.pro/news")
        time.sleep(5)
        
        print(f"Page title: {driver.title}")
        print(f"Page URL: {driver.current_url}")
        
        # Check for article links
        print("\n2️⃣ Looking for article links...")
        article_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/news/detail/"]')
        print(f"Found {len(article_links)} article links")
        
        if article_links:
            print("\nFirst 5 article links:")
            for i, link in enumerate(article_links[:5]):
                href = link.get_attribute('href')
                text = link.text.strip()
                print(f"  {i+1}. {href}")
                print(f"     Text: {text[:80]}...")
                
                # Extract article ID
                match = re.search(r'/detail/(\d+)', href)
                if match:
                    article_id = match.group(1)
                    print(f"     ID: {article_id}")
                print()
            
            # Test accessing the first article
            first_article_url = article_links[0].get_attribute('href')
            print(f"3️⃣ Testing article access: {first_article_url}")
            
            driver.get(first_article_url)
            time.sleep(3)
            
            # Parse content
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Look for title
            title_selectors = ['h1', '.title', '[class*="title"]']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 5:
                        print(f"📰 Title: {title}")
                        break
            
            # Look for content
            content_selectors = ['.content', '.article-content', '[class*="content"]', 'article', 'main']
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(strip=True)
                    if len(content) > 50:
                        print(f"📝 Content preview: {content[:200]}...")
                        break
            
            # Check for security keywords
            print("\n4️⃣ Checking for security keywords...")
            keywords = [
                "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
                "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
                "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
            ]
            
            full_text = f"{title} {content}".lower()
            matched_keywords = [kw for kw in keywords if kw.lower() in full_text]
            
            print(f"🔍 Matched keywords: {matched_keywords}")
            
            if matched_keywords:
                print("✅ This article would be saved!")
            else:
                print("❌ This article would be filtered out (no keyword matches)")
                
                # Show some sample text to see what we're working with
                print(f"\n📄 Sample text for keyword matching:")
                print(f"Title: {title}")
                print(f"Content sample: {content[:300]}...")
        
        else:
            print("❌ No article links found")
            print("📄 Page source sample:")
            print(driver.page_source[:1000])
        
        driver.quit()
        return len(article_links) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_manual_update():
    """Test a simple manual update without keyword filtering"""
    print("\n🧪 Testing Simple Manual Update (No Keyword Filter)")
    print("=" * 50)
    
    try:
        from scraper.core.manual_scraper import ManualScraper
        
        # Create manual scraper
        scraper = ManualScraper()
        
        # Temporarily modify keywords to be more inclusive
        original_keywords = scraper.KEYWORDS
        scraper.KEYWORDS = ["区块链", "加密", "币", "crypto", "blockchain", "bitcoin", "ethereum"]  # More common terms
        
        print("📋 Testing with broader keywords...")
        print(f"🔍 Keywords: {scraper.KEYWORDS}")
        
        def progress_callback(message, log_type):
            if log_type in ['info', 'success', 'error']:
                print(f"   📊 {message}")
        
        # Run manual update with just ForesightNews
        result = scraper._process_source_sequential('foresightnews', 2, progress_callback)
        
        print(f"\n📊 Results:")
        print(f"✅ Articles found: {result['articles_found']}")
        print(f"💾 Articles saved: {result['articles_saved']}")
        print(f"⏱️  Duration: {result['duration']:.2f}s")
        
        if result['errors']:
            print(f"⚠️  Errors: {len(result['errors'])}")
            for error in result['errors'][:3]:
                print(f"   - {error}")
        
        # Restore original keywords
        scraper.KEYWORDS = original_keywords
        
        return result['articles_found'] > 0
        
    except Exception as e:
        print(f"❌ Simple manual update failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main debug function"""
    print("🚀 ForesightNews Localhost Debug")
    print("=" * 50)
    
    # Test 1: Debug access
    access_ok = debug_foresightnews_access()
    
    # Test 2: Simple manual update
    if access_ok:
        manual_ok = test_simple_manual_update()
    else:
        manual_ok = False
    
    print("\n" + "=" * 50)
    print("🔍 DEBUG SUMMARY:")
    print(f"✅ ForesightNews access: {'OK' if access_ok else 'FAILED'}")
    print(f"✅ Manual update test: {'OK' if manual_ok else 'FAILED'}")
    
    if access_ok and manual_ok:
        print("\n🎉 ForesightNews is working!")
        print("💡 The issue might be with keyword matching")
        print("💡 Try running the localhost server to test manually")
    elif access_ok:
        print("\n⚠️  ForesightNews access works but scraper needs tuning")
        print("💡 May need to adjust keyword matching or content extraction")
    else:
        print("\n❌ ForesightNews access issues")
        print("💡 Check network connection and anti-bot protection")
    
    print("=" * 50)

if __name__ == "__main__":
    main()