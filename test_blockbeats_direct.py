#!/usr/bin/env python3
"""Test BlockBeats scraper directly"""
import sys
sys.path.insert(0, '.')

from datetime import date, timedelta
from scraper.core import Config
from scraper.core.storage import CSVDataStore
from scraper.core.blockbeats_scraper import BlockBeatsScraper

print("Testing BlockBeats scraper...")

config = Config(
    target_url="https://www.theblockbeats.info/newsflash",
    max_articles=20,
    request_delay=1.0,
    timeout=30,
    max_retries=3
)

data_store = CSVDataStore("test_blockbeats.csv")

end_date = date.today()
start_date = end_date - timedelta(days=1)

print(f"Date range: {start_date} to {end_date}")

scraper = BlockBeatsScraper(
    config=config,
    data_store=data_store,
    start_date=start_date,
    end_date=end_date,
    keywords_filter=["监管", "攻击", "黑客"],
    progress_callback=None,
    log_callback=None
)

print("\nFinding latest article ID...")
latest_id = scraper.find_latest_article_id()
print(f"Latest ID: {latest_id}")

print("\nScraping...")
result = scraper.scrape()

print(f"\nResult:")
print(f"  Total found: {result.total_articles_found}")
print(f"  Scraped: {result.articles_scraped}")
print(f"  Failed: {result.articles_failed}")

articles = data_store.get_all_articles()
print(f"\nArticles in store: {len(articles)}")

if articles:
    print("\nFirst 3 articles:")
    for i, article in enumerate(articles[:3]):
        print(f"  {i+1}. {article.title[:60]}")
        print(f"     Date: {article.date}")
