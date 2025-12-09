#!/usr/bin/env python3
"""Test the scheduled scraper immediately"""
import sys
sys.path.insert(0, '/Users/kabellatsang/PycharmProjects/ai_code')

from datetime import datetime, timedelta
from scraper.core.scheduled_scraper import ScheduledScraper

print("="*60)
print("🧪 Testing Scheduled Scraper")
print("="*60)
print()

# Create scraper instance
scraper = ScheduledScraper()

# Run a scrape for the last 2 days
end_date = datetime.now()
start_date = end_date - timedelta(days=2)

print(f"📅 Scraping from {start_date.date()} to {end_date.date()}")
print()

# Run the scrape
results = scraper.scrape_daily()

print()
print("="*60)
print("📊 Test Results")
print("="*60)
print(f"Total articles scraped: {results.get('total_articles', 0)}")
print(f"Articles stored in database: {results.get('articles_stored', 0)}")
print(f"Duplicates skipped: {results.get('duplicates', 0)}")
print(f"Keywords processed: {results.get('keywords_processed', 0)}")
print("="*60)
print()

if results.get('articles_stored', 0) > 0:
    print("✅ SUCCESS! Scheduled scraper is working and saving to database")
else:
    print("⚠️  No articles were stored (might be due to Supabase API issues)")
