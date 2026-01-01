#!/usr/bin/env python3
"""
Backfill script for missing news from 2026-01-01 to 2026-01-10
Scrapes articles from both BlockBeats and Jinse for the specified date range
"""

import sys
import os
from datetime import datetime, date, timedelta
from typing import List, Dict

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.core.database_manager import DatabaseManager
from scraper.core.manual_scraper import ManualScraper
from scraper.core.multi_source_scraper import MultiSourceScraper
from scraper.core import Config
from scraper.core.storage import CSVDataStore
import tempfile
import time

def backfill_missing_news():
    """Backfill news from 2026-01-01 to 2026-01-10"""
    
    print("🔄 Backfilling Missing News: 2026-01-01 to 2026-01-10")
    print("=" * 60)
    
    # Initialize database manager
    db = DatabaseManager()
    
    if not db.supabase:
        print("❌ Failed to connect to database")
        return False
    
    # Check current database state
    total_before = db.get_total_count()
    print(f"📊 Current articles in database: {total_before}")
    
    # Define date range
    start_date = date(2026, 1, 1)
    end_date = date(2026, 1, 10)
    
    print(f"📅 Target date range: {start_date} to {end_date}")
    
    # Security keywords for filtering
    keywords = [
        "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
        "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
        "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
    ]
    
    # Process each source
    sources = ['blockbeats', 'jinse']
    total_articles_saved = 0
    
    for source in sources:
        print(f"\n📰 Processing {source.upper()}...")
        print("-" * 40)
        
        try:
            # Create temporary directory and file
            temp_dir = tempfile.mkdtemp()
            temp_file = os.path.join(temp_dir, f"backfill_{source}_{int(time.time())}.csv")
            
            # Create config for this source
            config = Config(
                target_url="https://www.theblockbeats.info/newsflash" if source == 'blockbeats' else "https://www.jinse.cn/lives",
                max_articles=2000,  # Large number to ensure we get all articles in date range
                request_delay=1.0,
                timeout=30,
                max_retries=3
            )
            
            # Create data store
            data_store = CSVDataStore(temp_file)
            
            print(f"🔍 {source.upper()}: Creating scraper for date range...")
            
            # Create scraper
            scraper = MultiSourceScraper(
                config=config,
                data_store=data_store,
                start_date=start_date,
                end_date=end_date,
                keywords_filter=keywords,
                sources=[source],
                enable_deduplication=True
            )
            
            print(f"📥 {source.upper()}: Starting scrape...")
            
            # Run scraper
            scraper.scrape()
            articles = data_store.get_all_articles()
            
            print(f"📊 {source.upper()}: Found {len(articles)} articles")
            
            # Filter articles by date range and save to database
            articles_saved = 0
            duplicates_skipped = 0
            
            print(f"💾 {source.upper()}: Saving articles to database...")
            
            for i, article in enumerate(articles):
                try:
                    # Check if article is in our target date range
                    article_date = None
                    if hasattr(article, 'publication_date') and article.publication_date:
                        if hasattr(article.publication_date, 'date'):
                            article_date = article.publication_date.date()
                        else:
                            # Try to parse date string
                            try:
                                if isinstance(article.publication_date, str):
                                    if '/' in article.publication_date:
                                        # Format: YYYY/MM/DD
                                        date_parts = article.publication_date.split('/')
                                        article_date = date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
                                    else:
                                        # Try other formats
                                        article_date = datetime.strptime(article.publication_date, '%Y-%m-%d').date()
                            except:
                                article_date = None
                    
                    # Skip if not in target date range
                    if article_date and (article_date < start_date or article_date > end_date):
                        continue
                    
                    # Check if article already exists
                    if db.check_article_exists(article.url):
                        duplicates_skipped += 1
                        continue
                    
                    # Find matched keywords
                    title_lower = article.title.lower()
                    body_lower = getattr(article, 'body_text', '').lower()
                    matched_keywords = [kw for kw in keywords if kw.lower() in title_lower or kw.lower() in body_lower]
                    
                    if matched_keywords:
                        # Prepare article data
                        if article_date:
                            pub_date_str = article_date.strftime('%Y/%m/%d')
                        else:
                            pub_date_str = datetime.now().strftime('%Y/%m/%d')
                        
                        article_data = {
                            'publication_date': pub_date_str,
                            'title': article.title,
                            'body_text': getattr(article, 'body_text', article.title),
                            'url': article.url,
                            'source': 'BlockBeats' if source == 'blockbeats' else 'Jinse',
                            'matched_keywords': matched_keywords
                        }
                        
                        # Save to database
                        if db.insert_article(article_data):
                            articles_saved += 1
                            
                            # Progress update every 10 articles
                            if articles_saved % 10 == 0:
                                print(f"   💾 Saved {articles_saved} articles so far...")
                
                except Exception as e:
                    print(f"   ❌ Error processing article: {e}")
                    continue
            
            print(f"✅ {source.upper()} completed:")
            print(f"   📊 Articles found: {len(articles)}")
            print(f"   💾 Articles saved: {articles_saved}")
            print(f"   🔄 Duplicates skipped: {duplicates_skipped}")
            
            total_articles_saved += articles_saved
            
            # Cleanup temp files
            try:
                os.remove(temp_file)
                os.rmdir(temp_dir)
            except:
                pass
                
        except Exception as e:
            print(f"❌ Error processing {source}: {e}")
            continue
    
    # Final summary
    total_after = db.get_total_count()
    
    print(f"\n🎉 Backfill Complete!")
    print("=" * 60)
    print(f"📊 Articles before: {total_before}")
    print(f"📊 Articles after: {total_after}")
    print(f"📊 New articles added: {total_after - total_before}")
    print(f"📊 Articles saved by scraper: {total_articles_saved}")
    print(f"📅 Date range covered: {start_date} to {end_date}")
    print("=" * 60)
    
    if total_articles_saved > 0:
        print("✅ Success! New articles should now appear in the dashboard.")
        print("🔄 Refresh your dashboard to see the updated news.")
    else:
        print("⚠️  No new articles were added. This could mean:")
        print("   - Articles from this date range were already in the database")
        print("   - No articles matched the security keywords")
        print("   - The websites don't have articles for this date range")
    
    return total_articles_saved > 0

if __name__ == "__main__":
    success = backfill_missing_news()
    
    if success:
        print(f"\n🚀 Next steps:")
        print(f"   1. Refresh your dashboard to see new articles")
        print(f"   2. Check the date filter to view articles from Dec 10-20")
        print(f"   3. Verify the articles appear correctly")
    else:
        print(f"\n🔍 If no articles were found, you can:")
        print(f"   1. Check if the websites have articles for Dec 10-20")
        print(f"   2. Run the manual update from the dashboard")
        print(f"   3. Check the database directly for existing articles")