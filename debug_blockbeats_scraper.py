#!/usr/bin/env python3
"""
Diagnostic script to test BlockBeats article parsing.
This script will:
1. Test the latest article ID detection mechanism
2. Test individual article URL parsing with current selectors
3. Identify specific parsing failures and HTML structure changes
"""

import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from scraper.core.http_client import HTTPClient
from scraper.core.parser import HTMLParser
from scraper.core.models import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BlockBeatsDebugger:
    """Debug BlockBeats scraper issues"""
    
    def __init__(self):
        self.http_client = HTTPClient(timeout=30, request_delay=1.0, max_retries=3)
        self.parser = HTMLParser()
        self.base_url = "https://www.theblockbeats.info/flash/"
        
    def test_latest_article_id_detection(self):
        """Test finding the latest article ID from the main page"""
        print("=" * 60)
        print("TESTING LATEST ARTICLE ID DETECTION")
        print("=" * 60)
        
        try:
            # Test main page
            main_url = "https://www.theblockbeats.info/"
            print(f"Fetching main page: {main_url}")
            
            response = self.http_client.fetch_with_retry(main_url)
            print(f"Response status: {response.status_code}")
            print(f"Response size: {len(response.text)} characters")
            
            # Look for flash article links
            pattern = r'/flash/(\d+)'
            matches = re.findall(pattern, response.text)
            
            print(f"Found {len(matches)} flash article IDs")
            if matches:
                unique_ids = sorted(set(int(id_str) for id_str in matches), reverse=True)
                print(f"Latest 10 IDs found: {unique_ids[:10]}")
                latest_id = unique_ids[0]
                print(f"Latest article ID: {latest_id}")
                return latest_id
            else:
                print("❌ No flash article IDs found!")
                # Let's examine the HTML structure
                print("\nExamining HTML structure...")
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for any links containing 'flash'
                flash_links = soup.find_all('a', href=re.compile(r'flash'))
                print(f"Found {len(flash_links)} links containing 'flash'")
                for i, link in enumerate(flash_links[:5]):
                    print(f"  {i+1}. {link.get('href')} - {link.get_text()[:50]}...")
                
                # Look for any numeric IDs in links
                all_links = soup.find_all('a', href=True)
                numeric_links = [link for link in all_links if re.search(r'\d+', link.get('href', ''))]
                print(f"Found {len(numeric_links)} links with numbers")
                for i, link in enumerate(numeric_links[:10]):
                    print(f"  {i+1}. {link.get('href')} - {link.get_text()[:30]}...")
                
                return None
                
        except Exception as e:
            print(f"❌ Error fetching main page: {e}")
            return None
    
    def test_article_parsing(self, article_id: int):
        """Test parsing a specific article"""
        print("=" * 60)
        print(f"TESTING ARTICLE PARSING - ID {article_id}")
        print("=" * 60)
        
        article_url = f"{self.base_url}{article_id}"
        print(f"Testing article URL: {article_url}")
        
        try:
            # Fetch the article
            response = self.http_client.fetch_with_retry(article_url)
            print(f"Response status: {response.status_code}")
            print(f"Response size: {len(response.text)} characters")
            
            # Parse with BeautifulSoup to examine structure
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Test title extraction
            print("\n--- TITLE EXTRACTION ---")
            title_selectors = [
                'h1',
                'h1.article-title',
                '.article-title',
                'title'
            ]
            
            for selector in title_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"✅ Selector '{selector}' found {len(elements)} elements:")
                    for i, elem in enumerate(elements[:3]):
                        text = elem.get_text().strip()[:100]
                        print(f"   {i+1}. {text}...")
                else:
                    print(f"❌ Selector '{selector}' found no elements")
            
            # Test meta tags
            print("\n--- META TAGS ---")
            og_title = soup.find('meta', property='og:title')
            if og_title:
                print(f"✅ og:title: {og_title.get('content', '')[:100]}...")
            else:
                print("❌ No og:title found")
            
            page_title = soup.find('title')
            if page_title:
                print(f"✅ page title: {page_title.get_text()[:100]}...")
            else:
                print("❌ No page title found")
            
            # Test body content extraction
            print("\n--- BODY CONTENT EXTRACTION ---")
            body_selectors = [
                '.flash-top',
                '.flash-top-border',
                'article .article-body',
                '.article-content',
                'article',
                '.content'
            ]
            
            for selector in body_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"✅ Selector '{selector}' found {len(elements)} elements:")
                    for i, elem in enumerate(elements[:2]):
                        text = elem.get_text().strip()[:200]
                        print(f"   {i+1}. {text}...")
                else:
                    print(f"❌ Selector '{selector}' found no elements")
            
            # Test meta description
            print("\n--- META DESCRIPTION ---")
            og_desc = soup.find('meta', property='og:description')
            if og_desc:
                print(f"✅ og:description: {og_desc.get('content', '')[:200]}...")
            else:
                print("❌ No og:description found")
            
            desc_meta = soup.find('meta', attrs={'name': 'description'})
            if desc_meta:
                print(f"✅ description meta: {desc_meta.get('content', '')[:200]}...")
            else:
                print("❌ No description meta found")
            
            # Test date extraction
            print("\n--- DATE EXTRACTION ---")
            date_selectors = [
                'time[datetime]',
                '.article-date',
                '.entry-date',
                'time'
            ]
            
            for selector in date_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"✅ Selector '{selector}' found {len(elements)} elements:")
                    for i, elem in enumerate(elements[:2]):
                        datetime_attr = elem.get('datetime', '')
                        text = elem.get_text().strip()
                        print(f"   {i+1}. datetime='{datetime_attr}' text='{text}'")
                else:
                    print(f"❌ Selector '{selector}' found no elements")
            
            # Try to parse with current parser
            print("\n--- CURRENT PARSER TEST ---")
            try:
                article = self.parser.parse_article(response.text, article_url, "theblockbeats.info")
                print("✅ Parser succeeded!")
                print(f"   Title: {article.title[:100]}...")
                print(f"   Body: {article.body_text[:200]}...")
                print(f"   Date: {article.publication_date}")
                print(f"   Author: {article.author}")
            except Exception as parse_error:
                print(f"❌ Parser failed: {parse_error}")
            
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"❌ Article not found (404) - ID {article_id} doesn't exist")
            else:
                print(f"❌ HTTP error: {e}")
            return False
        except Exception as e:
            print(f"❌ Error testing article: {e}")
            return False
    
    def test_multiple_articles(self, start_id: int, count: int = 5):
        """Test parsing multiple articles to find patterns"""
        print("=" * 60)
        print(f"TESTING MULTIPLE ARTICLES - Starting from ID {start_id}")
        print("=" * 60)
        
        successful_parses = 0
        failed_parses = 0
        not_found = 0
        
        for i in range(count):
            article_id = start_id - i
            print(f"\n--- Testing Article ID {article_id} ---")
            
            try:
                result = self.test_article_parsing(article_id)
                if result:
                    successful_parses += 1
                else:
                    failed_parses += 1
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    not_found += 1
                    print(f"Article {article_id} not found (404)")
                else:
                    failed_parses += 1
                    print(f"HTTP error for article {article_id}: {e}")
            except Exception as e:
                failed_parses += 1
                print(f"Error testing article {article_id}: {e}")
        
        print("\n" + "=" * 60)
        print("MULTIPLE ARTICLES TEST SUMMARY")
        print("=" * 60)
        print(f"Successful parses: {successful_parses}")
        print(f"Failed parses: {failed_parses}")
        print(f"Not found (404): {not_found}")
        print(f"Total tested: {count}")
    
    def run_full_diagnosis(self):
        """Run complete BlockBeats diagnosis"""
        print("🔍 BLOCKBEATS SCRAPER DIAGNOSIS")
        print("=" * 60)
        
        # Step 1: Test latest ID detection
        latest_id = self.test_latest_article_id_detection()
        
        if latest_id:
            # Step 2: Test parsing recent articles
            self.test_multiple_articles(latest_id, 5)
        else:
            # Fallback: test with known recent IDs
            print("\n⚠️  Could not find latest ID, testing with fallback IDs...")
            fallback_ids = [320000, 319000, 318000]  # Adjust based on current BlockBeats
            
            for test_id in fallback_ids:
                print(f"\n--- Testing fallback ID {test_id} ---")
                if self.test_article_parsing(test_id):
                    print(f"✅ Fallback ID {test_id} works!")
                    self.test_multiple_articles(test_id, 3)
                    break
        
        print("\n🏁 DIAGNOSIS COMPLETE")

def main():
    """Main function to run BlockBeats diagnosis"""
    debugger = BlockBeatsDebugger()
    try:
        debugger.run_full_diagnosis()
    finally:
        debugger.http_client.close()

if __name__ == "__main__":
    main()