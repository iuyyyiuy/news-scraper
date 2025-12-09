#!/usr/bin/env python3
"""Test that scheduled scraper can insert articles correctly"""
import sys
sys.path.insert(0, '/Users/kabellatsang/PycharmProjects/ai_code')

from datetime import datetime
from scraper.core.database_manager import DatabaseManager

# Create a test article in the format the scraper produces
test_article = {
    'publication_date': '2025/12/5',
    'title': 'Test Scheduled Article',
    'body_text': 'This is a test article from the scheduled scraper',
    'url': 'https://test.com/scheduled-test-' + str(datetime.now().timestamp()),
    'source': 'test_scheduler',
    'matched_keywords': ['test', 'scheduled']
}

print("Testing scheduled scraper database insert...")
print(f"Article: {test_article['title']}")
print()

db = DatabaseManager()

if db.supabase:
    try:
        result = db.insert_article(test_article)
        if result:
            print("✅ SUCCESS! Scheduled scraper format works correctly")
            print("   The daily scraper will be able to save articles to the database")
        else:
            print("❌ Insert failed")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ Could not connect to database")
