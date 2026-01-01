#!/usr/bin/env python3
"""Test if parser can extract content from BlockBeats"""
import sys
sys.path.insert(0, '.')

from scraper.core.parser import HTMLParser
from scraper.core.http_client import HTTPClient

print("Testing parser fix...")

http_client = HTTPClient(timeout=30, request_delay=1.0, max_retries=3)
parser = HTMLParser()

# Test with a recent article
article_url = "https://www.theblockbeats.info/flash/323657"
print(f"Fetching: {article_url}")

response = http_client.fetch_with_retry(article_url)
print(f"Got response: {len(response.text)} bytes")

try:
    article = parser.parse_article(response.text, article_url, "theblockbeats.info")
    print(f"\n✅ SUCCESS!")
    print(f"Title: {article.title}")
    print(f"Body: {article.body_text[:200]}...")
    print(f"Date: {article.publication_date}")
except Exception as e:
    print(f"\n❌ FAILED: {e}")
