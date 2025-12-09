#!/usr/bin/env python3
"""
Debug the query issue
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

supabase = create_client(url, key)

print("Testing different query methods:\n")

# Method 1: Direct select all
print("1. Direct select all:")
response1 = supabase.table('articles').select('*').execute()
print(f"   Returned: {len(response1.data)} articles")

# Method 2: With order by
print("\n2. With order by date desc:")
response2 = supabase.table('articles').select('*').order('date', desc=True).execute()
print(f"   Returned: {len(response2.data)} articles")

# Method 3: With order and range (like the API)
print("\n3. With order and range(0, 49):")
response3 = supabase.table('articles').select('*').order('date', desc=True).range(0, 49).execute()
print(f"   Returned: {len(response3.data)} articles")

# Method 4: With order and limit
print("\n4. With order and limit(50):")
response4 = supabase.table('articles').select('*').order('date', desc=True).limit(50).execute()
print(f"   Returned: {len(response4.data)} articles")

# Check what dates we have
print("\n5. Checking dates in database:")
dates = {}
for article in response1.data:
    date = article['date']
    dates[date] = dates.get(date, 0) + 1

for date in sorted(dates.keys(), reverse=True):
    print(f"   {date}: {dates[date]} articles")
