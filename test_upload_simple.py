#!/usr/bin/env python3
"""Simple test to upload one article"""
import sys
sys.path.insert(0, '/Users/kabellatsang/PycharmProjects/ai_code')

from scraper.core.database_manager import DatabaseManager

# Test data matching CSV structure
test_article = {
    'publication_date': '2025/12/5',
    'title': 'Test Article',
    'body_text': 'This is a test article body text',
    'url': 'https://test.com/article123',
    'source': 'test_source',
    'matched_keywords': '黑客, 被盗'
}

print("Testing database upload...")
print(f"Article data: {test_article}")
print()

db = DatabaseManager()

if db.supabase:
    print("✅ Connected to database")
    print()
    
    try:
        result = db.insert_article(test_article)
        if result:
            print("✅ SUCCESS! Article uploaded")
        else:
            print("❌ Failed to upload")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Failed to connect to database")
