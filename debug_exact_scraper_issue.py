#!/usr/bin/env python3
"""
Debug script that replicates exactly what the scraper is doing.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.http_client import HTTPClient
from scraper.core.parser import HTMLParser
import logging

# Setup logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_scraper_issue():
    """Debug the exact issue the scraper is having."""
    
    # Test the same articles that are failing
    test_articles = [
        'https://www.theblockbeats.info/flash/326513',
        'https://www.theblockbeats.info/flash/326512', 
        'https://www.theblockbeats.info/flash/326511'
    ]
    
    # Use the same components as the scraper
    http_client = HTTPClient(
        timeout=30,
        request_delay=2.0,
        max_retries=3
    )
    
    parser = HTMLParser(selectors={})  # No custom selectors, use defaults
    
    print("=" * 80)
    print("DEBUGGING EXACT SCRAPER ISSUE")
    print("=" * 80)
    
    for i, url in enumerate(test_articles):
        print(f"\n[{i+1}] Processing: {url}")
        print("-" * 60)
        
        try:
            # Step 1: Fetch HTML (exactly like scraper)
            print("Step 1: Fetching HTML...")
            response = http_client.fetch_with_retry(url)
            print(f"✅ Fetched successfully (status: {response.status_code})")
            print(f"Content length: {len(response.text)} characters")
            
            # Step 2: Parse article (exactly like scraper)
            print("\nStep 2: Parsing article...")
            article = parser.parse_article(
                response.text,
                url,
                "theblockbeats.info"
            )
            
            print(f"✅ Parsed successfully")
            print(f"Title: {article.title}")
            print(f"Body preview: {article.body_text[:100]}...")
            
            # Step 3: Check if title looks correct
            if "永续合约前传" in article.title:
                print("❌ WRONG TITLE DETECTED!")
                print("This is the problematic title that appears for all articles")
                
                # Let's debug further
                print("\n--- DEBUGGING TITLE EXTRACTION ---")
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Check what's actually in the HTML
                title_tag = soup.find('title')
                if title_tag:
                    print(f"Actual <title> tag: {title_tag.get_text()}")
                
                og_title = soup.find('meta', property='og:title')
                if og_title:
                    print(f"Actual og:title: {og_title.get('content')}")
                
                # Try manual title extraction
                manual_title = parser._extract_title_enhanced(soup)
                print(f"Manual title extraction: {manual_title}")
                
            else:
                print("✅ Title looks correct!")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("=" * 80)
    
    http_client.close()

if __name__ == "__main__":
    debug_scraper_issue()