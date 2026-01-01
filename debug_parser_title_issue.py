#!/usr/bin/env python3
"""
Debug script to identify why parser is extracting wrong titles.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.http_client import HTTPClient
from scraper.core.parser import HTMLParser
from bs4 import BeautifulSoup
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_title_extraction():
    """Test title extraction for multiple articles."""
    
    # Test articles with known different titles
    test_articles = [
        {
            'id': 326513,
            'expected_title': 'Bithumb将上线XAUT韩元交易对',
            'url': 'https://www.theblockbeats.info/flash/326513'
        },
        {
            'id': 326512, 
            'expected_title': '张铮文：短期争议终将过去，专注于Neo持续建设和长期发展',
            'url': 'https://www.theblockbeats.info/flash/326512'
        },
        {
            'id': 326511,
            'expected_title': 'Lummis：《负责任金融创新法案》将允许大型银行提供数字资产托管、质押和支付服务',
            'url': 'https://www.theblockbeats.info/flash/326511'
        }
    ]
    
    http_client = HTTPClient()
    parser = HTMLParser(debug_mode=True)
    
    print("=" * 80)
    print("DEBUGGING PARSER TITLE EXTRACTION")
    print("=" * 80)
    
    for i, article in enumerate(test_articles):
        print(f"\n[{i+1}] Testing Article ID {article['id']}")
        print(f"URL: {article['url']}")
        print(f"Expected Title: {article['expected_title']}")
        print("-" * 60)
        
        try:
            # Fetch HTML
            response = http_client.fetch_with_retry(article['url'])
            html = response.text
            
            # Parse with BeautifulSoup to check what's actually in the HTML
            soup = BeautifulSoup(html, 'lxml')
            
            # Check title tag
            title_tag = soup.find('title')
            if title_tag:
                page_title = title_tag.get_text().strip()
                print(f"Page <title> tag: {page_title}")
            
            # Check og:title meta tag
            og_title = soup.find('meta', property='og:title')
            if og_title:
                og_title_content = og_title.get('content', '').strip()
                print(f"og:title meta: {og_title_content}")
            
            # Check h1 tags
            h1_tags = soup.find_all('h1')
            print(f"Found {len(h1_tags)} h1 tags:")
            for j, h1 in enumerate(h1_tags):
                h1_text = h1.get_text().strip()
                print(f"  h1[{j}]: {h1_text}")
            
            # Check h3 tags (flash news might use h3)
            h3_tags = soup.find_all('h3')
            print(f"Found {len(h3_tags)} h3 tags:")
            for j, h3 in enumerate(h3_tags[:5]):  # Show first 5
                h3_text = h3.get_text().strip()
                print(f"  h3[{j}]: {h3_text}")
            
            # Now test the parser
            print("\n--- PARSER EXTRACTION ---")
            try:
                parsed_article = parser.parse_article(html, article['url'], 'theblockbeats.info')
                extracted_title = parsed_article.title
                print(f"Parser extracted title: {extracted_title}")
                
                # Check if it matches expected
                if extracted_title == article['expected_title']:
                    print("✅ CORRECT: Parser extracted the right title!")
                else:
                    print("❌ WRONG: Parser extracted wrong title!")
                    print(f"Expected: {article['expected_title']}")
                    print(f"Got:      {extracted_title}")
                    
                    # Try to debug why
                    print("\n--- DEBUGGING TITLE EXTRACTION ---")
                    title_extracted = parser._extract_title_enhanced(soup)
                    print(f"_extract_title_enhanced returned: {title_extracted}")
                    
            except Exception as e:
                print(f"❌ Parser failed: {e}")
                
        except Exception as e:
            print(f"❌ Failed to fetch article: {e}")
        
        print("=" * 80)
    
    http_client.close()

if __name__ == "__main__":
    test_title_extraction()