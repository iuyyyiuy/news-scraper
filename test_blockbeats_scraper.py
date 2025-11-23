"""
Test script for the BlockBeats scraper.
"""
from datetime import date
from scraper.core import Config, BlockBeatsScraper
from scraper.core.storage import JSONDataStore

# Create config
config = Config(
    target_url="https://www.theblockbeats.info/",
    max_articles=100,  # Limit for testing
    request_delay=1.0,  # Be nice to the server
    output_format="json",
    output_path="test_blockbeats_output.json",
    timeout=30,
    max_retries=3,
    selectors={},
    keywords=["安全问题", "黑客", "被盗", "漏洞", "攻击"]
)

# Create data store
data_store = JSONDataStore(config.output_path)

# Create scraper
scraper = BlockBeatsScraper(
    config=config,
    data_store=data_store,
    start_date=date(2025, 11, 1),
    end_date=date(2025, 11, 13),
    keywords_filter=config.keywords,
    progress_callback=lambda found, scraped: print(f"Progress: {scraped} articles scraped (checked {found})")
)

# Run scraper
print("Starting BlockBeats scraper test...")
print(f"Date range: 2025-11-01 to 2025-11-13")
print(f"Keywords: {config.keywords}")
print("-" * 60)

result = scraper.scrape()

print("\n" + "=" * 60)
print("RESULTS:")
print(f"Articles checked: {result.total_articles_found}")
print(f"Articles scraped: {result.articles_scraped}")
print(f"Articles failed: {result.articles_failed}")
print(f"Duration: {result.duration_seconds:.2f} seconds")
print("=" * 60)

# Show some sample articles
articles = data_store.get_all_articles()
if articles:
    print(f"\nSample articles (showing first 5):")
    for i, article in enumerate(articles[:5], 1):
        print(f"\n{i}. {article.title}")
        print(f"   Date: {article.publication_date}")
        print(f"   URL: {article.url}")
        print(f"   Keywords: {article.matched_keywords}")
