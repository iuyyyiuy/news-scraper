#!/usr/bin/env python3
"""
Simple test to verify the parser fix works correctly.
Run this on the Digital Ocean server to test the fix.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.http_client import HTTPClient
from scraper.core.parser import HTMLParser

def test_parser_fix():
    """Test that parser extracts correct titles for different articles."""
    
    test_cases = [
        {
            'url': 'https://www.theblockbeats.info/flash/326513',
            'expected_title': 'Bithumb将上线XAUT韩元交易对'
        },
        {
            'url': 'https://www.theblockbeats.info/flash/326512', 
            'expected_title': '张铮文：短期争议终将过去，专注于Neo持续建设和长期发展'
        }
    ]
    
    http_client = HTTPClient()
    parser = HTMLParser()
    
    print("Testing parser fix...")
    print("=" * 60)
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases):
        print(f"\n[{i+1}] Testing: {test_case['url']}")
        
        try:
            # Fetch and parse
            response = http_client.fetch_with_retry(test_case['url'])
            article = parser.parse_article(response.text, test_case['url'], 'theblockbeats.info')
            
            print(f"Expected: {test_case['expected_title']}")
            print(f"Got:      {article.title}")
            
            if article.title == test_case['expected_title']:
                print("✅ SUCCESS: Correct title extracted!")
                success_count += 1
            else:
                print("❌ FAILED: Wrong title extracted!")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {success_count}/{len(test_cases)} tests passed")
    
    if success_count == len(test_cases):
        print("🎉 ALL TESTS PASSED - Parser fix is working!")
        return True
    else:
        print("⚠️  Some tests failed - Parser needs more work")
        return False
    
    http_client.close()

if __name__ == "__main__":
    success = test_parser_fix()
    sys.exit(0 if success else 1)