#!/usr/bin/env python3
"""Manually add a test article for today"""
import sys
sys.path.insert(0, '.')

from datetime import date
from scraper.core.database_manager import DatabaseManager

db = DatabaseManager()

# Add a test article for today
article_data = {
    'publication_date': '2025/12/09',
    'title': 'TEST: 加密货币交易所遭受黑客攻击',
    'body_text': '测试文章：某交易所今日遭受黑客攻击，损失惨重。这是一个测试文章。',
    'url': f'https://test.com/article-{date.today().isoformat()}',
    'source': 'BlockBeats',
    'matched_keywords': ['黑客', '攻击']
}

print("Adding test article for 2025/12/09...")
success = db.insert_article(article_data)

if success:
    print("✅ Article added successfully!")
    total = db.get_total_count()
    print(f"Total articles now: {total}")
else:
    print("❌ Failed to add article")
