#!/usr/bin/env python3
"""Check Supabase connection and status"""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

print(f"Supabase URL: {url}")
print(f"API Key (first 20 chars): {key[:20]}...")
print()

# Try a direct HTTP request to see what's happening
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

# Try to access the articles table
test_url = f"{url}/rest/v1/articles?limit=1"
print(f"Testing URL: {test_url}")
print()

try:
    response = requests.get(test_url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
