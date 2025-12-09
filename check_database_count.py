#!/usr/bin/env python3
"""Check how many articles are in the database"""
import sys
import os
sys.path.insert(0, '/Users/kabellatsang/PycharmProjects/ai_code')

import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'count=exact'
}

try:
    # Get articles
    response = requests.get(
        f"{url}/rest/v1/articles?select=date,title,source&limit=10",
        headers=headers
    )
    
    if response.status_code in [200, 206]:
        articles = response.json()
        print(f"✅ Total articles retrieved: {len(articles)}")
        
        if articles:
            print(f"\n📰 Sample articles:")
            for i, article in enumerate(articles[:5], 1):
                print(f"{i}. {article['title'][:60]}...")
                print(f"   Date: {article['date']}, Source: {article['source']}")
        else:
            print("⚠️  No articles found in database")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
