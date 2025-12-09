#!/usr/bin/env python3
"""Normalize date format in database to YYYY/MM/DD"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

print("Fetching all articles...")
response = requests.get(f"{url}/rest/v1/articles?select=id,date", headers=headers)
articles = response.json()

print(f"Found {len(articles)} articles")
print("Normalizing dates...")

updated = 0
for article in articles:
    date_str = article['date']
    
    # Parse and normalize to YYYY/MM/DD
    try:
        parts = date_str.split('/')
        if len(parts) == 3:
            year, month, day = parts
            normalized = f"{year}/{month.zfill(2)}/{day.zfill(2)}"
            
            if normalized != date_str:
                # Update in database
                update_response = requests.patch(
                    f"{url}/rest/v1/articles?id=eq.{article['id']}",
                    headers=headers,
                    json={'date': normalized}
                )
                if update_response.status_code in [200, 204]:
                    updated += 1
                    print(f"  ✅ {date_str} → {normalized}")
    except:
        continue

print(f"\n✅ Updated {updated} dates")
print("Dates are now normalized!")
