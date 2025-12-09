#!/usr/bin/env python3
"""
Test range behavior
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

supabase = create_client(url, key)

print("Testing range behavior:\n")

# Test different range values
tests = [
    (0, 4, "First 5 items"),
    (0, 49, "First 50 items"),
    (0, 9, "First 10 items"),
]

for start, end, desc in tests:
    response = supabase.table('articles').select('*').order('date', desc=True).range(start, end).execute()
    print(f"{desc}: range({start}, {end}) -> {len(response.data)} items")
    expected = end - start + 1
    print(f"  Expected: {expected}, Got: {len(response.data)}, Match: {expected == len(response.data)}")
