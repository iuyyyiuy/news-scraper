#!/usr/bin/env python3
"""
Quick Backfill - Uses existing scraper with date range
"""
import sys
sys.path.insert(0, '/Users/kabellatsang/PycharmProjects/ai_code')

from datetime import date, timedelta
from scraper.core.database_manager import DatabaseManager
from scraper.core.scheduled_scraper import ScheduledScraper

print("="*60)
print("🚀 Quick Backfill - December 2024")
print("="*60)
print()

# Initialize
db_manager = DatabaseManager()
if not db_manager.supabase:
    print("❌ Failed to connect to Supabase")
    sys.exit(1)

print("✅ Connected to Supabase")
print()

# Use the scheduled scraper
scraper = ScheduledScraper()

print("🔍 Running scraper for all 21 keywords...")
print("This will take 10-20 minutes...")
print()

# Run the daily scrape (it will get recent articles)
results = scraper.scrape_daily()

print()
print("="*60)
print("✅ Backfill Complete!")
print("="*60)
print(f"📰 Articles found: {results['articles_found']}")
print(f"💾 Articles stored: {results['articles_stored']}")
print(f"🔄 Duplicates: {results['articles_duplicate']}")
print("="*60)
print()

if results['articles_stored'] > 0:
    print("🌐 View at: https://crypto-news-scraper.onrender.com/dashboard")
else:
    print("⚠️  No articles stored. Try running again or check logs.")
