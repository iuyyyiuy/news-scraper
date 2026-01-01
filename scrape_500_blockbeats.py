#!/usr/bin/env python3
"""
Scrape the latest 500 news articles from BlockBeats.
Uses the improved content extraction for clean, structured data.
"""

import os
import sys
import time
from datetime import datetime
from scraper.core.scheduled_scraper import ScheduledScraper
from scraper.core.database_manager import DatabaseManager

def scrape_500_blockbeats():
    """Scrape the latest 500 articles from BlockBeats."""
    
    print("=" * 60)
    print("🚀 Scraping Latest 500 Articles from BlockBeats")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    try:
        # Test database connection
        print("🔗 Testing database connection...")
        try:
            current_count = db_manager.get_total_count()
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return
        
        print(f"📊 Current articles in database: {current_count}")
        
        # Initialize scraper with larger limits
        scraper = ScheduledScraper()
        
        # Configure for larger batch
        print("⚙️ Configuring scraper for 500 articles...")
        
        # Start scraping with increased limits
        print("\n🔍 Starting BlockBeats scrape...")
        print("   Target: 500 articles")
        print("   Source: BlockBeats (theblockbeats.info)")
        print("   Keywords: Security-related terms")
        
        start_time = time.time()
        
        # Run the scraper with 500 articles
        print("\n🔍 Starting single batch scrape for 500 articles...")
        
        try:
            # Run the daily scraper with 500 articles
            result = scraper.scrape_daily(max_articles=500)
            
            if result:
                total_scraped = result.get('articles_found', 0)
                total_stored = result.get('articles_stored', 0)
                total_duplicates = result.get('articles_duplicate', 0)
                
                print(f"📰 Found: {total_scraped}")
                print(f"💾 Stored: {total_stored}")
                print(f"🔄 Duplicates: {total_duplicates}")
                
            else:
                print("❌ Scraping failed")
                total_scraped = 0
                total_stored = 0
                
        except Exception as e:
            print(f"❌ Scraping error: {e}")
            import traceback
            traceback.print_exc()
            total_scraped = 0
            total_stored = 0
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Get final article count
        final_count = db_manager.get_total_count()
        new_articles = final_count - current_count
        
        print("\n" + "=" * 60)
        print("📊 SCRAPING SUMMARY")
        print("=" * 60)
        print(f"⏱️  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"📰 Total articles found: {total_scraped}")
        print(f"💾 Total articles stored: {total_stored}")
        print(f"📈 Database growth: {current_count} → {final_count} (+{new_articles})")
        print(f"🎯 Target: 500 articles")
        print(f"📊 Achievement: {(new_articles/500)*100:.1f}% of target")
        
        if new_articles >= 400:
            print("🎉 Excellent! Got close to 500 articles")
        elif new_articles >= 200:
            print("✅ Good progress! Got substantial number of articles")
        elif new_articles >= 50:
            print("👍 Moderate success! Got some new articles")
        else:
            print("ℹ️ Limited new articles - database may be up to date")
        
        print("=" * 60)
        
        # Show sample of newly scraped articles
        print("\n📰 Sample of newly scraped articles:")
        try:
            recent_articles = db_manager.get_all_articles(limit=5)
            for i, article in enumerate(recent_articles, 1):
                title = article.get('title', 'No title')[:60]
                date = article.get('date', 'No date')
                print(f"{i}. {title}...")
                print(f"   📅 {date}")
        except Exception as e:
            print(f"❌ Error fetching sample articles: {e}")
        
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if 'db_manager' in locals():
            try:
                db_manager.close()
            except:
                pass

if __name__ == "__main__":
    scrape_500_blockbeats()