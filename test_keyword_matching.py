#!/usr/bin/env python3
"""
Test script to check what articles are available and what keywords they contain.
This will help us understand why the manual update returns 0 articles.
"""

import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from scraper.core.http_client import HTTPClient
from scraper.core.parser import HTMLParser
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KeywordMatchingTester:
    """Test keyword matching with recent articles"""
    
    def __init__(self):
        self.http_client = HTTPClient(timeout=30, request_delay=1.0, max_retries=3)
        self.parser = HTMLParser()
        
        # Current security keywords used by the system
        self.security_keywords = [
            "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
            "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
            "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
        ]
        
        # Broader set of crypto-related keywords for comparison
        self.broader_keywords = [
            "比特币", "以太坊", "加密货币", "区块链", "DeFi", "NFT", "交易所",
            "币安", "Binance", "USDT", "BTC", "ETH", "代币", "挖矿",
            "智能合约", "去中心化", "数字货币", "虚拟货币", "加密", "区块"
        ]
    
    def test_recent_blockbeats_articles(self, count=10):
        """Test recent BlockBeats articles for keyword matching"""
        print("=" * 60)
        print(f"TESTING RECENT BLOCKBEATS ARTICLES (last {count})")
        print("=" * 60)
        
        try:
            # Get latest article ID
            response = self.http_client.fetch_with_retry("https://www.theblockbeats.info/")
            pattern = r'/flash/(\d+)'
            matches = re.findall(pattern, response.text)
            
            if not matches:
                print("❌ No article IDs found")
                return
            
            latest_id = max(int(id_str) for id_str in matches)
            print(f"Latest article ID: {latest_id}")
            
            articles_tested = 0
            security_matches = 0
            broader_matches = 0
            
            for i in range(count):
                article_id = latest_id - i
                article_url = f"https://www.theblockbeats.info/flash/{article_id}"
                
                try:
                    response = self.http_client.fetch_with_retry(article_url)
                    article = self.parser.parse_article(response.text, article_url, "theblockbeats.info")
                    
                    articles_tested += 1
                    
                    # Test content
                    full_text = f"{article.title} {article.body_text}".lower()
                    
                    # Check security keywords
                    security_matched = [kw for kw in self.security_keywords if kw.lower() in full_text]
                    broader_matched = [kw for kw in self.broader_keywords if kw.lower() in full_text]
                    
                    if security_matched:
                        security_matches += 1
                    if broader_matched:
                        broader_matches += 1
                    
                    print(f"\n--- Article {article_id} ---")
                    print(f"Title: {article.title[:80]}...")
                    print(f"Content: {article.body_text[:100]}...")
                    print(f"Security keywords matched: {security_matched}")
                    print(f"Broader keywords matched: {broader_matched[:5]}{'...' if len(broader_matched) > 5 else ''}")
                    
                except Exception as e:
                    print(f"❌ Error testing article {article_id}: {e}")
            
            print(f"\n--- SUMMARY ---")
            print(f"Articles tested: {articles_tested}")
            print(f"Security keyword matches: {security_matches}/{articles_tested} ({security_matches/articles_tested*100:.1f}%)")
            print(f"Broader keyword matches: {broader_matches}/{articles_tested} ({broader_matches/articles_tested*100:.1f}%)")
            
        except Exception as e:
            print(f"❌ Error testing BlockBeats articles: {e}")
    
    def test_recent_jinse_articles(self, count=10):
        """Test recent Jinse articles for keyword matching"""
        print("=" * 60)
        print(f"TESTING RECENT JINSE ARTICLES (last {count})")
        print("=" * 60)
        
        try:
            # Get latest article ID
            response = self.http_client.fetch_with_retry("https://www.jinse.cn/lives")
            pattern = r'/lives/(\d+)\.html'
            matches = re.findall(pattern, response.text)
            
            if not matches:
                print("❌ No article IDs found")
                return
            
            latest_id = max(int(id_str) for id_str in matches)
            print(f"Latest article ID: {latest_id}")
            
            articles_tested = 0
            security_matches = 0
            broader_matches = 0
            
            for i in range(count):
                article_id = latest_id - i
                article_url = f"https://www.jinse.cn/lives/{article_id}.html"
                
                try:
                    response = self.http_client.fetch_with_retry(article_url)
                    
                    # Use Jinse-specific parser
                    from scraper.core.jinse_scraper import JinseScraper
                    from scraper.core import Config
                    from scraper.core.storage import CSVDataStore
                    from datetime import date
                    import tempfile
                    
                    # Create temporary scraper to use its parser
                    config = Config(target_url="", max_articles=1)
                    temp_file = tempfile.mktemp(suffix='.csv')
                    data_store = CSVDataStore(temp_file)
                    
                    jinse_scraper = JinseScraper(
                        config=config,
                        data_store=data_store,
                        start_date=date.today(),
                        end_date=date.today(),
                        keywords_filter=[]
                    )
                    
                    article = jinse_scraper._parse_jinse_article(response.text, article_url)
                    
                    articles_tested += 1
                    
                    # Test content
                    full_text = f"{article.title} {article.body_text}".lower()
                    
                    # Check security keywords
                    security_matched = [kw for kw in self.security_keywords if kw.lower() in full_text]
                    broader_matched = [kw for kw in self.broader_keywords if kw.lower() in full_text]
                    
                    if security_matched:
                        security_matches += 1
                    if broader_matched:
                        broader_matches += 1
                    
                    print(f"\n--- Article {article_id} ---")
                    print(f"Title: {article.title[:80]}...")
                    print(f"Content: {article.body_text[:100]}...")
                    print(f"Security keywords matched: {security_matched}")
                    print(f"Broader keywords matched: {broader_matched[:5]}{'...' if len(broader_matched) > 5 else ''}")
                    
                    # Clean up
                    try:
                        import os
                        os.unlink(temp_file)
                    except:
                        pass
                    
                except Exception as e:
                    print(f"❌ Error testing article {article_id}: {e}")
            
            print(f"\n--- SUMMARY ---")
            print(f"Articles tested: {articles_tested}")
            print(f"Security keyword matches: {security_matches}/{articles_tested} ({security_matches/articles_tested*100:.1f}%)")
            print(f"Broader keyword matches: {broader_matches}/{articles_tested} ({broader_matches/articles_tested*100:.1f}%)")
            
        except Exception as e:
            print(f"❌ Error testing Jinse articles: {e}")
    
    def suggest_keyword_improvements(self):
        """Suggest improvements to keyword matching"""
        print("=" * 60)
        print("KEYWORD MATCHING SUGGESTIONS")
        print("=" * 60)
        
        print("Current security keywords are very specific and may miss relevant articles.")
        print("Consider these options:")
        print()
        print("1. **Expand security keywords** to include:")
        print("   - General terms: '风险', '警告', '注意', '提醒'")
        print("   - Exchange names: 'Coinbase', 'OKX', 'Huobi', 'Kraken'")
        print("   - Security events: '暂停', '维护', '升级', '更新'")
        print()
        print("2. **Add broader crypto keywords** for general news:")
        print("   - Core terms: '比特币', '以太坊', 'BTC', 'ETH', 'USDT'")
        print("   - Market terms: '价格', '涨跌', '交易量', '市值'")
        print("   - Tech terms: 'DeFi', 'NFT', '智能合约', '区块链'")
        print()
        print("3. **Use flexible matching**:")
        print("   - Allow articles with ANY keyword match (not just security)")
        print("   - Use OR logic instead of requiring specific security terms")
        print("   - Consider content relevance scoring")
    
    def run_full_test(self):
        """Run complete keyword matching test"""
        print("🔍 KEYWORD MATCHING ANALYSIS")
        print("=" * 60)
        
        # Test BlockBeats
        self.test_recent_blockbeats_articles(10)
        
        print("\n")
        
        # Test Jinse
        self.test_recent_jinse_articles(10)
        
        print("\n")
        
        # Suggestions
        self.suggest_keyword_improvements()
        
        print("\n🏁 ANALYSIS COMPLETE")

def main():
    """Main function"""
    tester = KeywordMatchingTester()
    try:
        tester.run_full_test()
    finally:
        tester.http_client.close()

if __name__ == "__main__":
    main()