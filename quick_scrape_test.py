#!/usr/bin/env python3
"""Quick test to scrape and store today's articles"""
import sys
sys.path.insert(0, '.')

from scraper.core.scheduled_scraper import ScheduledScraper
from scraper.core.database_manager import DatabaseManager

print("Before scrape:")
db = DatabaseManager()
before_count = db.get_total_count()
print(f"  Total articles: {before_count}")

print("\nRunning scraper...")
scraper = ScheduledScraper()
result = scraper.scrape_daily()

print("\nAfter scrape:")
after_count = db.get_total_count()
print(f"  Total articles: {after_count}")
print(f"  New articles: {after_count - before_count}")
print(f"\nResult: {result}")
