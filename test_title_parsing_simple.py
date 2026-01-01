#!/usr/bin/env python3
"""
Simple test of title parsing with direct requests
"""

import requests
from bs4 import BeautifulSoup
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.parser import HTMLParser

def test_title_extraction():
    """Test title extraction methods"""
    
    print("🔍 Testing Title Extraction Methods")
    print("=" * 50)
    
    # Test with a recent article
    url = "https://www.theblockbeats.info/flash/326535"
    
    try:
        # Fetch with requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to fetch {url}: {response.status_code}")
            return
        
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        
        print(f"📄 Testing URL: {url}")
        print("-" * 40)
        
        # Method 1: og:title meta tag
        og_title = soup.find('meta', property='og:title')
        og_title_content = og_title.get('content') if og_title else None
        print(f"1️⃣ og:title: {og_title_content}")
        
        # Method 2: page title
        title_tag = soup.find('title')
        page_title = title_tag.get_text().strip() if title_tag else None
        print(f"2️⃣ page title: {page_title}")
        
        # Method 3: All h1 tags
        h1_tags = soup.find_all('h1')
        print(f"3️⃣ h1 tags found: {len(h1_tags)}")
        for i, h1 in enumerate(h1_tags):
            text = h1.get_text().strip()
            print(f"   h1[{i}]: {text}")
        
        # Method 4: All h3 tags (flash news often use h3)
        h3_tags = soup.find_all('h3')
        print(f"4️⃣ h3 tags found: {len(h3_tags)}")
        for i, h3 in enumerate(h3_tags):
            text = h3.get_text().strip()
            if text and len(text) > 5:
                print(f"   h3[{i}]: {text}")
        
        # Method 5: Flash-specific selectors
        flash_selectors = [
            '.flash-top',
            '.flash-content', 
            '.flash-item',
            '.news-title',
            '.article-title'
        ]
        
        print("5️⃣ Flash-specific elements:")
        for selector in flash_selectors:
            elements = soup.select(selector)
            print(f"   {selector}: {len(elements)} found")
            for i, elem in enumerate(elements[:2]):  # Show first 2
                text = elem.get_text().strip()[:100]  # First 100 chars
                print(f"      [{i}]: {text}")
        
        # Method 6: Test current parser
        print("6️⃣ Current parser result:")
        try:
            parser = HTMLParser()
            article = parser.parse_article(html, url, "theblockbeats.info")
            print(f"   Parser title: {article.title}")
        except Exception as e:
            print(f"   Parser failed: {e}")
        
        # Method 7: Look for the actual content structure
        print("7️⃣ Page structure analysis:")
        
        # Find elements with substantial text that could be titles
        all_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'div', 'span', 'p'])
        potential_titles = []
        
        for elem in all_elements:
            text = elem.get_text().strip()
            # Look for text that could be a title (10-200 chars, no line breaks)
            if 10 <= len(text) <= 200 and '\n' not in text and text not in potential_titles:
                potential_titles.append(text)
        
        print(f"   Found {len(potential_titles)} potential titles:")
        for i, title in enumerate(potential_titles[:10]):  # Show first 10
            print(f"      [{i}]: {title}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_title_extraction()