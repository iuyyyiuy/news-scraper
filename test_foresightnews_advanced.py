#!/usr/bin/env python3
"""
Advanced ForesightNews scraper with human-like behavior to bypass anti-bot protection
"""
import requests
import time
import random
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from datetime import datetime

class HumanLikeForesightNewsScraper:
    """Advanced scraper that mimics human behavior"""
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """Setup session with human-like headers and behavior"""
        # Rotate user agents
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        self.session.headers.update(headers)
        
    def human_delay(self, min_seconds=1, max_seconds=3):
        """Add human-like random delays"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        
    def test_with_selenium(self):
        """Use Selenium to bypass JavaScript-based protection"""
        print("🤖 Testing with Selenium (browser automation)...")
        
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Create driver
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Test main page
            print("📱 Loading ForesightNews main page...")
            driver.get("https://foresightnews.pro/news")
            
            # Wait for page to load
            time.sleep(5)
            
            # Check if we got past the protection
            page_source = driver.page_source
            print(f"Page length: {len(page_source)}")
            
            if 'aliyun_waf' in page_source.lower():
                print("❌ Still blocked by WAF")
            elif len(page_source) > 50000:  # Reasonable page size
                print("✅ Successfully loaded page!")
                
                # Look for article links
                article_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/news/detail/"]')
                print(f"Found {len(article_links)} article links")
                
                if article_links:
                    for i, link in enumerate(article_links[:5]):
                        href = link.get_attribute('href')
                        text = link.text.strip()
                        print(f"  {i+1}. {href} - {text[:50]}...")
                        
                    # Test accessing a specific article
                    first_article = article_links[0].get_attribute('href')
                    print(f"\\n📰 Testing article: {first_article}")
                    
                    driver.get(first_article)
                    time.sleep(3)
                    
                    article_source = driver.page_source
                    if len(article_source) > 10000:
                        print("✅ Article loaded successfully!")
                        
                        # Try to extract content
                        soup = BeautifulSoup(article_source, 'html.parser')
                        
                        # Look for title
                        title_selectors = ['h1', '.title', '[class*="title"]', 'title']
                        for selector in title_selectors:
                            title_elem = soup.select_one(selector)
                            if title_elem and title_elem.get_text(strip=True):
                                title = title_elem.get_text(strip=True)
                                if len(title) > 10 and 'ForesightNews' not in title:
                                    print(f"📰 Title: {title[:100]}...")
                                    break
                        
                        # Look for content
                        content_selectors = ['.content', '.article-content', '[class*="content"]', 'article', 'main']
                        for selector in content_selectors:
                            content_elem = soup.select_one(selector)
                            if content_elem:
                                content = content_elem.get_text(strip=True)
                                if len(content) > 100:
                                    print(f"📝 Content preview: {content[:150]}...")
                                    break
                        
                        return True
                    else:
                        print("❌ Article page blocked")
            else:
                print("❌ Page appears to be blocked")
                
            driver.quit()
            return False
            
        except Exception as e:
            print(f"❌ Selenium error: {e}")
            return False
    
    def test_with_session_cookies(self):
        """Try to get past protection by handling cookies and JavaScript challenges"""
        print("🍪 Testing with cookie and session handling...")
        
        try:
            # First request to get initial cookies
            print("1️⃣ Getting initial cookies...")
            response = self.session.get("https://foresightnews.pro/news", timeout=15)
            print(f"Initial response: {response.status_code}, cookies: {len(response.cookies)}")
            
            # Look for JavaScript challenge in response
            if 'aliyun_waf' in response.text:
                print("🔍 Detected Aliyun WAF challenge...")
                
                # Try to extract challenge parameters
                challenge_match = re.search(r'arg1=\'([^\']+)\'', response.text)
                if challenge_match:
                    arg1 = challenge_match.group(1)
                    print(f"Found challenge arg1: {arg1[:20]}...")
                    
                    # Simulate solving the challenge (this is a simplified approach)
                    # In reality, you'd need to execute the JavaScript
                    challenge_cookie = f"acw_sc__v2={arg1[:32]}"
                    
                    # Add the challenge cookie
                    self.session.cookies.set('acw_sc__v2', arg1[:32])
                    
                    # Wait a bit (human-like)
                    self.human_delay(2, 4)
                    
                    # Try again with the cookie
                    print("2️⃣ Retrying with challenge cookie...")
                    response2 = self.session.get("https://foresightnews.pro/news", timeout=15)
                    print(f"Second response: {response2.status_code}, length: {len(response2.text)}")
                    
                    if 'aliyun_waf' not in response2.text and len(response2.text) > 50000:
                        print("✅ Successfully bypassed WAF!")
                        return self.extract_articles_from_response(response2)
                    else:
                        print("❌ Still blocked after cookie attempt")
            
            return False
            
        except Exception as e:
            print(f"❌ Session error: {e}")
            return False
    
    def extract_articles_from_response(self, response):
        """Extract article information from successful response"""
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for article links
            article_patterns = [
                r'/news/detail/(\d+)',
                r'href="([^"]*news/detail/[^"]*)"'
            ]
            
            articles_found = []
            
            for pattern in article_patterns:
                matches = re.findall(pattern, response.text)
                if matches:
                    print(f"✅ Found {len(matches)} articles with pattern: {pattern}")
                    
                    for match in matches[:10]:  # Test first 10
                        if pattern.endswith(r'(\d+)'):
                            article_id = match
                            article_url = f"https://foresightnews.pro/news/detail/{article_id}"
                        else:
                            article_url = match if match.startswith('http') else f"https://foresightnews.pro{match}"
                            article_id = re.search(r'/detail/(\d+)', article_url)
                            article_id = article_id.group(1) if article_id else 'unknown'
                        
                        articles_found.append({
                            'id': article_id,
                            'url': article_url
                        })
                    
                    break
            
            if articles_found:
                print(f"📰 Testing article access...")
                
                # Test accessing the first article
                test_article = articles_found[0]
                self.human_delay(1, 2)
                
                article_response = self.session.get(test_article['url'], timeout=15)
                print(f"Article response: {article_response.status_code}")
                
                if article_response.status_code == 200 and len(article_response.text) > 10000:
                    print("✅ Article access successful!")
                    
                    # Parse article content
                    article_soup = BeautifulSoup(article_response.text, 'html.parser')
                    
                    # Extract title
                    title_elem = article_soup.find('h1') or article_soup.find('title')
                    title = title_elem.get_text(strip=True) if title_elem else "No title"
                    
                    print(f"📰 Article title: {title[:100]}...")
                    
                    return True
                else:
                    print("❌ Article access failed")
            
            return len(articles_found) > 0
            
        except Exception as e:
            print(f"❌ Extraction error: {e}")
            return False
    
    def test_api_discovery(self):
        """Try to find API endpoints that might not be protected"""
        print("🔍 Testing API endpoint discovery...")
        
        api_endpoints = [
            "https://foresightnews.pro/api/articles",
            "https://foresightnews.pro/api/news/list",
            "https://foresightnews.pro/api/v1/articles",
            "https://foresightnews.pro/_next/data/articles.json",
            "https://foresightnews.pro/sitemap.xml",
            "https://foresightnews.pro/rss.xml",
            "https://foresightnews.pro/feed.xml"
        ]
        
        for endpoint in api_endpoints:
            try:
                print(f"🌐 Testing: {endpoint}")
                response = self.session.get(endpoint, timeout=10)
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')
                    print(f"  Content-Type: {content_type}")
                    
                    if 'json' in content_type:
                        try:
                            data = response.json()
                            print(f"  ✅ JSON response with keys: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
                        except:
                            print(f"  ⚠️  Invalid JSON")
                    elif 'xml' in content_type:
                        print(f"  ✅ XML response, length: {len(response.text)}")
                    else:
                        print(f"  📄 Text response, length: {len(response.text)}")
                        
                    if len(response.text) > 1000 and 'aliyun_waf' not in response.text:
                        print(f"  🎉 Potential working endpoint!")
                        return endpoint
                
                self.human_delay(0.5, 1)
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        return None

def main():
    """Main testing function"""
    print("🚀 Advanced ForesightNews Scraper Test")
    print("=" * 60)
    
    scraper = HumanLikeForesightNewsScraper()
    
    # Test 1: API Discovery
    working_api = scraper.test_api_discovery()
    
    # Test 2: Session with cookies
    session_success = scraper.test_with_session_cookies()
    
    # Test 3: Selenium (if available)
    try:
        selenium_success = scraper.test_with_selenium()
    except Exception as e:
        print(f"⚠️  Selenium not available: {e}")
        selenium_success = False
    
    print("\n" + "=" * 60)
    print("🔍 ADVANCED ANALYSIS RESULTS:")
    print(f"✅ API Discovery: {'Success' if working_api else 'Failed'}")
    print(f"✅ Session/Cookie Method: {'Success' if session_success else 'Failed'}")
    print(f"✅ Selenium Method: {'Success' if selenium_success else 'Failed'}")
    
    if working_api or session_success or selenium_success:
        print("\n🎉 RECOMMENDATION:")
        print("✅ ForesightNews CAN be scraped with advanced techniques!")
        print("💡 Implementation approach:")
        if selenium_success:
            print("   - Use Selenium WebDriver for JavaScript execution")
        if session_success:
            print("   - Use session cookies and challenge solving")
        if working_api:
            print(f"   - Use API endpoint: {working_api}")
        print("   - Add human-like delays and behavior")
        print("   - Rotate user agents and headers")
    else:
        print("\n⚠️  RECOMMENDATION:")
        print("❌ ForesightNews protection is very strong")
        print("💡 Consider PANews as alternative (already tested working)")
    
    print("=" * 60)

if __name__ == "__main__":
    main()