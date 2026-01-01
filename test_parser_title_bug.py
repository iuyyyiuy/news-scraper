#!/usr/bin/env python3
"""
Simple test to reproduce the parser title bug.
"""
import requests
from bs4 import BeautifulSoup

def test_title_extraction():
    """Test title extraction for multiple articles."""
    
    # Test articles with known different titles
    test_urls = [
        'https://www.theblockbeats.info/flash/326513',
        'https://www.theblockbeats.info/flash/326512', 
        'https://www.theblockbeats.info/flash/326511'
    ]
    
    print("Testing title extraction from multiple articles...")
    print("=" * 60)
    
    for i, url in enumerate(test_urls):
        print(f"\n[{i+1}] Testing: {url}")
        
        try:
            # Fetch HTML
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract title using different methods
            print("Title extraction methods:")
            
            # Method 1: <title> tag
            title_tag = soup.find('title')
            if title_tag:
                page_title = title_tag.get_text().strip()
                # Remove " - BlockBeats" suffix
                if ' - BlockBeats' in page_title:
                    page_title = page_title.replace(' - BlockBeats', '')
                print(f"  <title> tag: {page_title}")
            
            # Method 2: og:title meta tag
            og_title_meta = soup.find('meta', property='og:title')
            if og_title_meta:
                og_title = og_title_meta.get('content', '').strip()
                print(f"  og:title:    {og_title}")
            
            # Method 3: h1 tags
            h1_tags = soup.find_all('h1')
            if h1_tags:
                for j, h1 in enumerate(h1_tags):
                    h1_text = h1.get_text().strip()
                    if h1_text:
                        print(f"  h1[{j}]:      {h1_text}")
            
            # Method 4: h3 tags (flash news)
            h3_tags = soup.find_all('h3')
            if h3_tags:
                for j, h3 in enumerate(h3_tags[:3]):  # Show first 3
                    h3_text = h3.get_text().strip()
                    if h3_text and len(h3_text) > 10:  # Skip short text
                        print(f"  h3[{j}]:      {h3_text}")
                        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 60)

if __name__ == "__main__":
    test_title_extraction()