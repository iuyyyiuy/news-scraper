#!/usr/bin/env python3
"""
Simple test to check if parser works correctly.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.parser import HTMLParser
from bs4 import BeautifulSoup

def test_parser():
    """Test parser with sample HTML."""
    
    # Sample HTML with different titles
    html_samples = [
        {
            'name': 'Sample 1',
            'html': '''
            <html>
            <head>
                <title>Bithumb将上线XAUT韩元交易对 - BlockBeats</title>
                <meta property="og:title" content="Bithumb将上线XAUT韩元交易对" />
            </head>
            <body>
                <h1>Bithumb将上线XAUT韩元交易对</h1>
                <p>BlockBeats 消息，1 月 1 日，Bithumb 将上线黄金代币 Tether Gold(XAUT) 韩元交易对。</p>
            </body>
            </html>
            '''
        },
        {
            'name': 'Sample 2', 
            'html': '''
            <html>
            <head>
                <title>张铮文：短期争议终将过去，专注于Neo持续建设和长期发展 - BlockBeats</title>
                <meta property="og:title" content="张铮文：短期争议终将过去，专注于Neo持续建设和长期发展" />
            </head>
            <body>
                <h1>张铮文：短期争议终将过去，专注于Neo持续建设和长期发展</h1>
                <p>BlockBeats 消息，1 月 1 日，Neo 两大创始人之一的张铮文发文表示...</p>
            </body>
            </html>
            '''
        }
    ]
    
    parser = HTMLParser()
    
    print("Testing parser with different HTML samples...")
    print("=" * 60)
    
    for sample in html_samples:
        print(f"\nTesting {sample['name']}:")
        
        try:
            soup = BeautifulSoup(sample['html'], 'lxml')
            title = parser._extract_title_enhanced(soup)
            print(f"Extracted title: {title}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 40)

if __name__ == "__main__":
    test_parser()