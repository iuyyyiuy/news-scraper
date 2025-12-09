#!/usr/bin/env python3
"""Upload CSV using REST API directly"""
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
print("📤 Upload CSV via REST API")
print("="*60)
print()

headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

total_rows = 0
total_inserted = 0
total_errors = 0

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        total_rows += 1
        
        try:
            # Parse keywords
            keywords = [k.strip() for k in row['matched_keywords'].split(',') if k.strip()]
            
            # Prepare data
            data = {
                'publication_date': row['publication_date'],
                'title': row['title'],
                'body_text': row['body_text'],
                'url': row['url'],
                'source': row['source'],
                'matched_keywords': keywords
            }
            
            # Insert via REST API
            response = requests.post(
                f"{url}/rest/v1/articles",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                total_inserted += 1
                print(f"  ✅ [{total_inserted}] {row['title'][:60]}...")
                time.sleep(0.2)  # Small delay to avoid rate limiting
            elif response.status_code == 409:
                # Duplicate - skip silently
                continue
            else:
                total_errors += 1
                if total_errors <= 3:  # Only show first 3 errors
                    print(f"  ❌ Row {total_rows} Error {response.status_code}")
                    print(f"     Title: {row['title'][:50]}")
                    print(f"     Response: {response.text[:200]}")
                time.sleep(0.5)  # Longer delay after error
                
        except Exception as e:
            total_errors += 1
            print(f"  ❌ Error on row {total_rows}: {e}")
            continue

print()
print("="*60)
print("📊 Upload Summary")
print("="*60)
print(f"📄 Total rows: {total_rows}")
print(f"💾 Articles inserted: {total_inserted}")
print(f"❌ Errors: {total_errors}")
print("="*60)
print()

if total_inserted > 0:
    print("✅ Upload complete!")
else:
    print("⚠️  No articles were inserted")
