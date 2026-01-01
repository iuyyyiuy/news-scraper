#!/usr/bin/env python3
"""
Test the parser fix for title extraction.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from scraper.core.parser import HTMLParser
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def test_parser_fix():
    """Test the parser fix with real articles."""
    
    test_urls = [
        'https://www.theblockbeats.info/flash/326513',
        'https://www.theblockbeats.info/flash/326512',
        'https://www.theblockbeats.info/flash/326511'
    ]
    
    expected_titles = [
        'Bithumb将上线XAUT韩元交易对',
        '张铮文：短期争议终将过去，专注于Neo持续建设和长期发展',
        'Lummis：《负责任金融创新法案》将允许大型银行提供数字资产托管、质押和支付服务'
    ]
    
    parser = HTMLParser()
    
    print("Testing parser fix...")
    print("=" * 80)
    
    for i, (url, expected) in enumerate(zip(test_urls, expected_titles)):
        print(f"\n[{i+1}] Testing: {url}")
        print(f"Expected: {expected}")
        print("-" * 60)
        
        try:
            # Fetch HTML
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; NewsScraperBot/1.0)'
            })
            response.raise_for_status()
            
            # Parse article
            article = parser.parse_article(response.text, url, 'theblockbeats.info')
            
            print(f"Extracted: {article.title}")
            
            # Check if correct
            if article.title == expected:
                print("✅ CORRECT!")
            else:
                print("❌ WRONG!")
                print(f"Expected: {expected}")
                print(f"Got:      {article.title}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("=" * 80)

if __name__ == "__main__":
    test_parser_fix()