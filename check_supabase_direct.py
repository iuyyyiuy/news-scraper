#!/usr/bin/env python3
"""
Direct Supabase check to see what's really in the database
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

supabase = create_client(url, key)

# Get total count
response = supabase.table('articles').select('*', count='exact').execute()
print(f"✅ Total articles in Supabase: {response.count}")
print(f"✅ Articles returned: {len(response.data)}")

# Show first 5
print("\n📰 First 5 articles:")
for i, article in enumerate(response.data[:5], 1):
    print(f"{i}. {article['title'][:60]}...")
    print(f"   Date: {article['date']}, Source: {article['source']}")

# Check for duplicates
urls = [a['url'] for a in response.data]
print(f"\n📊 Unique URLs: {len(set(urls))}")
print(f"📊 Total articles: {len(urls)}")
if len(urls) != len(set(urls)):
    print("⚠️  WARNING: Duplicate URLs found!")
