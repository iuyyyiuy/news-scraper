"""
Quick test for Jinse scraper
Run this to verify Jinse is working correctly
"""
from datetime import date, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.core.config import Config
from scraper.core.storage import CSVDataStore
from scraper.core.jinse_scraper import JinseScraper

print("=" * 60)
print("Testing Jinse (金色财经) Scraper")
print("=" * 60)
print()

# Setup
end_date = date.today()
start_date = end_date - timedelta(days=2)  # Last 2 days
keywords = ['BTC', 'Bitcoin', '比特币', '以太坊', 'ETH']

print(f"Date range: {start_date} to {end_date}")
print(f"Keywords: {keywords}")
print(f"Will check: 20 articles")
print()

# Create config
config = Config(
    target_url="https://www.jinse.cn/lives",
    max_articles=20,  # Check 20 articles
    request_delay=1.0,
    output_format="csv",
    output_path="jinse_test_output.csv"
)

# Create data store
data_store = CSVDataStore("jinse_test_output.csv")

# Create scraper with detailed logging
def log_callback(message, log_type='info', source=None):
    print(f"[{log_type.upper()}] {message}")

scraper = JinseScraper(
    config=config,
    data_store=data_store,
    start_date=start_date,
    end_date=end_date,
    keywords_filter=keywords,
    log_callback=log_callback
)

# Run scraper
print("Starting scrape...")
print("-" * 60)
result = scraper.scrape()

# Print results
print()
print("=" * 60)
print("Results:")
print("=" * 60)
print(f"✅ Articles checked: {result.total_articles_found}")
print(f"✅ Articles scraped: {result.articles_scraped}")
print(f"❌ Articles failed: {result.articles_failed}")
print(f"⏱️  Duration: {result.duration_seconds:.2f} seconds")
print()

if result.articles_scraped > 0:
    print(f"✅ SUCCESS! Jinse scraper is working!")
    print(f"📄 Output saved to: jinse_test_output.csv")
else:
    print("⚠️  No articles found. This could mean:")
    print("   1. No articles match your keywords in the date range")
    print("   2. The website structure changed")
    print("   3. Network issues")
    
if result.errors:
    print()
    print("Errors encountered:")
    for error in result.errors[:5]:
        print(f"  - {error}")

print("=" * 60)
