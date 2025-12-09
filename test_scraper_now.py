#!/usr/bin/env python3
"""
Test the scraper immediately to verify the schedule change
"""
from scraper.core.scheduled_scraper import ScheduledScraper
from datetime import datetime

print("="*60)
print("🧪 Testing Scraper - Manual Run")
print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)
print()

scraper = ScheduledScraper()
result = scraper.scrape_daily()

print()
print("="*60)
print("✅ Test Complete!")
print(f"📊 Articles scraped: {result.get('total_articles', 0)}")
print("="*60)
