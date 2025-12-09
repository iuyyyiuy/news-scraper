#!/usr/bin/env python3
"""
Debug the database manager
"""
from scraper.core.database_manager import DatabaseManager

db = DatabaseManager()

print("Testing DatabaseManager methods:\n")

# Test 1: get_all_articles with default params
print("1. get_all_articles(limit=50, offset=0):")
articles1 = db.get_all_articles(limit=50, offset=0)
print(f"   Returned: {len(articles1)} articles")
if articles1:
    print(f"   First article: {articles1[0]['title'][:50]}...")
    print(f"   Last article: {articles1[-1]['title'][:50]}...")

# Test 2: get_all_articles with higher limit
print("\n2. get_all_articles(limit=100, offset=0):")
articles2 = db.get_all_articles(limit=100, offset=0)
print(f"   Returned: {len(articles2)} articles")

# Test 3: get_total_count
print("\n3. get_total_count():")
total = db.get_total_count()
print(f"   Total: {total} articles")

# Test 4: Check if there's a filter issue
print("\n4. get_all_articles with no filters:")
articles3 = db.get_all_articles(limit=50, offset=0, keyword=None, source=None)
print(f"   Returned: {len(articles3)} articles")
