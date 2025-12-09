#!/usr/bin/env python3
"""
Backfill Historical Data Script
Scrapes news from December 1st to today and stores in Supabase
"""
import sys
import os
sys.path.insert(0, '/Users/kabellatsang/PycharmProjects/ai_code')

from datetime import datetime, date, timedelta
from scraper.core.database_manager import DatabaseManager
from scraper.core import Config
from scraper.core.storage import CSVDataStore
from scraper.core.multi_source_scraper import MultiSourceScraper
import tempfile

# Security keywords to search for
KEYWORDS = [
    "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
    "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
    "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
]

def backfill_data():
    """Backfill historical data from Dec 1 to today"""
    
    print("="*60)
    print("🔄 Historical Data Backfill")
    print("="*60)
    print(f"📅 Date Range: 2024-12-01 to {date.today()}")
    print(f"🔑 Keywords: {len(KEYWORDS)} security-related terms")
    print(f"📰 Sources: BlockBeats, Jinse")
    print("="*60)
    print()
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    if not db_manager.supabase:
        print("❌ Failed to connect to database. Check your .env file.")
        return False
    
    # Date range
    start_date = date(2024, 12, 1)
    end_date = date.today()
    
    print(f"📊 Starting backfill...")
    print()
    
    total_found = 0
    total_stored = 0
    total_duplicate = 0
    
    # Create temporary directory for CSV storage
    temp_dir = tempfile.mkdtemp()
    
    # Process each keyword
    for i, keyword in enumerate(KEYWORDS, 1):
        print(f"[{i}/{len(KEYWORDS)}] 🔍 Scraping keyword: {keyword}")
        
        try:
            # Create config
            config = Config(
                target_url="https://www.theblockbeats.info/newsflash",
                max_articles=200,  # Get more articles for historical data
                request_delay=2.0,
                timeout=30,
                max_retries=3
            )
            
            # Create temporary data store
            temp_file = os.path.join(temp_dir, f"temp_{keyword}.csv")
            data_store = CSVDataStore(temp_file)
            
            # Create scraper
            scraper = MultiSourceScraper(
                config=config,
                data_store=data_store,
                start_date=start_date,
                end_date=end_date,
                keywords_filter=[keyword],
                sources=['blockbeats', 'jinse'],
                enable_deduplication=True
            )
            
            # Scrape
            articles = scraper.scrape_all_sources()
            
            found = len(articles)
            stored = 0
            duplicate = 0
            
            # Store each article
            for article in articles:
                # Check if exists
                if db_manager.check_article_exists(article['url']):
                    duplicate += 1
                    continue
                
                # Prepare article data
                article_data = {
                    'title': article['title'],
                    'url': article['url'],
                    'date': article['date'],
                    'source': article['source'],
                    'content': article.get('content', article['title']),
                    'matched_keywords': [keyword]
                }
                
                # Insert
                if db_manager.insert_article(article_data):
                    stored += 1
                else:
                    duplicate += 1
            
            total_found += found
            total_stored += stored
            total_duplicate += duplicate
            
            print(f"  ✅ Found: {found}, Stored: {stored}, Duplicate: {duplicate}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue
        
        print()
    
    # Cleanup temp directory
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Print summary
    print("="*60)
    print("📊 Backfill Summary")
    print("="*60)
    print(f"🔑 Keywords processed: {len(KEYWORDS)}")
    print(f"📰 Articles found: {total_found}")
    print(f"💾 Articles stored: {total_stored}")
    print(f"🔄 Duplicates skipped: {total_duplicate}")
    print("="*60)
    print()
    
    if total_stored > 0:
        print(f"✅ Successfully backfilled {total_stored} articles!")
        print()
        print("🌐 View them at:")
        print("   Local: http://localhost:8000/dashboard")
        print("   Render: https://crypto-news-scraper.onrender.com/dashboard")
    else:
        print("⚠️  No new articles were stored.")
        print("   This might mean:")
        print("   - All articles already exist in database")
        print("   - No articles matched the keywords in date range")
        print("   - There was an error during scraping")
    
    print()
    return total_stored > 0


if __name__ == "__main__":
    print()
    print("🚀 Starting Historical Data Backfill")
    print()
    print("This will scrape news from December 1st to today")
    print("and store all security-related articles in Supabase.")
    print()
    
    # Confirm
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("❌ Cancelled")
        sys.exit(0)
    
    print()
    success = backfill_data()
    
    if success:
        print("🎉 Backfill complete!")
        sys.exit(0)
    else:
        print("❌ Backfill failed or no data stored")
        sys.exit(1)
