#!/usr/bin/env python3
"""
Test title parsing with live BlockBeats articles to debug the issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.http_client import HTTPClient
from scraper.core.parser import HTMLParser
import requests

def test_live_title_parsing():
    """Test title parsing with current live articles"""
    
    print("🔍 Testing Live Title Parsing")
    print("=" * 50)
    
    # Test URLs from your screenshot
    test_urls = [
        "https://www.theblockbeats.info/flash/326535",
        "https://www.theblockbeats.info/flash/326534", 
        "https://www.theblockbeats.info/flash/326533",
        "https://www.theblockbeats.info/flash/326532",
        "https://www.theblockbeats.info/flash/326531"
    ]
    
    http_client = HTTPClient()
    parser = HTMLParser(debug_mode=True)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}️⃣ Testing: {url}")
        print("-" * 40)
        
        try:
            # Fetch the page
            response = http_client.fetch(url)
            if not response.success:
                print(f"❌ Failed to fetch: {response.error}")
                continue
            
            html = response.content
            
            # Test different title extraction methods
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'lxml')
            
            # Method 1: og:title meta tag
            og_title = soup.find('meta', property='og:title')
            og_title_content = og_title.get('content') if og_title else None
            
            # Method 2: page title
            title_tag = soup.find('title')
            page_title = title_tag.get_text() if title_tag else None
            
            # Method 3: h1 tags
            h1_tags = soup.find_all('h1')
            h1_texts = [h1.get_text().strip() for h1 in h1_tags if h1.get_text().strip()]
            
            # Method 4: Flash-specific selectors
            flash_title_selectors = [
                '.flash-top h3',
                '.flash-item h3', 
                '.flash-content h3',
                '.flash-top .title',
                '.flash-item .title',
                '.flash-content .title'
            ]
            
            flash_titles = []
            for selector in flash_title_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    text = elem.get_text().strip()
                    if text and len(text) > 10:  # Meaningful title
                        flash_titles.append(text)
            
            # Method 5: Use the parser
            try:
                article = parser.parse_article(html, url, "theblockbeats.info")
                parser_title = article.title
            except Exception as e:
                parser_title = f"Parser failed: {e}"
            
            # Display results
            print(f"🏷️  og:title: {og_title_content}")
            print(f"📄 page title: {page_title}")
            print(f"📰 h1 tags: {h1_texts}")
            print(f"⚡ flash titles: {flash_titles}")
            print(f"🔧 parser result: {parser_title}")
            
            # Determine what should be the correct title
            if flash_titles:
                correct_title = flash_titles[0]
                print(f"✅ SHOULD BE: {correct_title}")
            elif og_title_content and len(og_title_content) > 10:
                correct_title = og_title_content
                print(f"✅ SHOULD BE: {correct_title}")
            else:
                print("❓ Could not determine correct title")
                
        except Exception as e:
            print(f"❌ Error testing {url}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_live_title_parsing()