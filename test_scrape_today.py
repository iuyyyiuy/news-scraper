#!/usr/bin/env python3
"""Test scraping today's articles"""
import sys
sys.path.insert(0, '.')

from datetime import date, timedelta
from scraper.core import Config
from scraper.core.storage import CSVDataStore
from scraper.core.multi_source_scraper import MultiSourceScraper

# Keywords
KEYWORDS = [
    "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
    "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
    "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
]

print("Testing scraper for today's articles...")

config = Config(
    target_url="https://www.theblockbeats.info/newsflash",
    max_articles=100,
    request_delay=2.0,
    timeout=30,
    max_retries=3
)

data_store = CSVDataStore("test_today.csv")

# Today only
end_date = date.today()
start_date = end_date

print(f"Scraping date: {start_date}")
print(f"Keywords: {KEYWORDS[:5]}...")

scraper = MultiSourceScraper(
    config=config,
    data_store=data_store,
    start_date=start_date,
    end_date=end_date,
    keywords_filter=KEYWORDS,
    sources=['blockbeats'],
    enable_deduplication=True
)

result = scraper.scrape()
articles = data_store.get_all_articles()

print(f"\nResults:")
print(f"  Articles found: {len(articles)}")
print(f"  Articles scraped: {result.articles_scraped}")

if articles:
    print(f"\nFirst 3 articles:")
    for i, article in enumerate(articles[:3]):
        print(f"  {i+1}. {article.title[:50]}...")
        print(f"     Date: {article.date}")
        print(f"     URL: {article.url}")
