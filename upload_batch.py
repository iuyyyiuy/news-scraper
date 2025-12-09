#!/usr/bin/env python3
"""Upload CSV in batches to reduce API calls"""
import sys
import os
sys.path.insert(0, '/Users/kabellatsang/PycharmProjects/ai_code')

import csv
import requests
import time
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

csv_file = "/Users/kabellatsang/PycharmProjects/ai_code/crypto_news_20251205_072237.csv"

print("="*60)
print("📤 Upload CSV in Batches")
print("="*60)
print()

headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal,resolution=ignore-duplicates'
}

# Read all data first
all_data = []
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        keywords = [k.strip() for k in row['matched_keywords'].split(',') if k.strip()]
        all_data.append({
            'publication_date': row['publication_date'],
            'title': row['title'],
            'body_text': row['body_text'],
            'url': row['url'],
            'source': row['source'],
            'matched_keywords': keywords
        })

print(f"📄 Total articles to upload: {len(all_data)}")
print()

# Upload in batches of 10
batch_size = 10
total_inserted = 0
total_errors = 0

for i in range(0, len(all_data), batch_size):
    batch = all_data[i:i+batch_size]
    batch_num = (i // batch_size) + 1
    
    try:
        response = requests.post(
            f"{url}/rest/v1/articles",
            headers=headers,
            json=batch,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            total_inserted += len(batch)
            print(f"  ✅ Batch {batch_num}: Uploaded {len(batch)} articles (Total: {total_inserted})")
        else:
            total_errors += len(batch)
            print(f"  ❌ Batch {batch_num}: Error {response.status_code}")
            if batch_num <= 2:
                print(f"     Response: {response.text[:200]}")
        
        time.sleep(1)  # Wait 1 second between batches
        
    except Exception as e:
        total_errors += len(batch)
        print(f"  ❌ Batch {batch_num}: Exception - {e}")

print()
print("="*60)
print("📊 Upload Summary")
print("="*60)
print(f"📄 Total articles: {len(all_data)}")
print(f"💾 Articles inserted: {total_inserted}")
print(f"❌ Errors: {total_errors}")
print("="*60)
print()

if total_inserted > 0:
    print("✅ Upload complete!")
else:
    print("⚠️  No articles were inserted")
