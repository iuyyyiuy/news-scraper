#!/usr/bin/env python3
"""
Clean up duplicate articles from the database
Keep the most recent version of each duplicate
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.database_manager import DatabaseManager
from collections import defaultdict
from datetime import datetime

def cleanup_duplicate_articles():
    """Remove duplicate articles from database, keeping the most recent"""
    
    print("🧹 Cleaning Up Duplicate Articles")
    print("=" * 50)
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Get all articles
        print("1. Retrieving all articles...")
        result = db_manager.supabase.table('articles').select(
            'id, title, body_text, url, source, date, scraped_at'
        ).order('scraped_at', desc=True).execute()
        
        articles = result.data
        print(f"   Found {len(articles)} total articles")
        
        # Group by title to find duplicates
        print("\n2. Identifying duplicates...")
        title_groups = defaultdict(list)
        
        for article in articles:
            title = article['title'].strip()
            title_groups[title].append(article)
        
        # Find duplicates
        duplicates = {title: articles for title, articles in title_groups.items() if len(articles) > 1}
        
        if not duplicates:
            print("✅ No duplicates found!")
            return True
        
        print(f"   Found {len(duplicates)} duplicate groups")
        
        # Clean up duplicates
        print("\n3. Removing duplicate articles...")
        
        total_removed = 0
        
        for title, duplicate_articles in duplicates.items():
            print(f"\n📰 Processing: {title[:60]}...")
            print(f"   Found {len(duplicate_articles)} copies")
            
            # Sort by scraped_at to keep the most recent
            sorted_articles = sorted(duplicate_articles, key=lambda x: x['scraped_at'], reverse=True)
            
            # Keep the first (most recent), remove the rest
            keep_article = sorted_articles[0]
            remove_articles = sorted_articles[1:]
            
            print(f"   Keeping: ID {keep_article['id'][:8]}... (scraped: {keep_article['scraped_at'][:19]})")
            
            for article in remove_articles:
                try:
                    # Delete the duplicate article
                    delete_result = db_manager.supabase.table('articles').delete().eq('id', article['id']).execute()
                    
                    if delete_result.data:
                        print(f"   ✅ Removed: ID {article['id'][:8]}... (scraped: {article['scraped_at'][:19]})")
                        total_removed += 1
                    else:
                        print(f"   ❌ Failed to remove: ID {article['id'][:8]}...")
                        
                except Exception as e:
                    print(f"   ❌ Error removing ID {article['id'][:8]}...: {e}")
        
        print(f"\n📊 Cleanup Summary:")
        print(f"   Duplicate groups processed: {len(duplicates)}")
        print(f"   Articles removed: {total_removed}")
        
        # Verify cleanup
        print("\n4. Verifying cleanup...")
        result_after = db_manager.supabase.table('articles').select('id, title').execute()
        articles_after = result_after.data
        
        title_groups_after = defaultdict(list)
        for article in articles_after:
            title = article['title'].strip()
            title_groups_after[title].append(article)
        
        duplicates_after = {title: articles for title, articles in title_groups_after.items() if len(articles) > 1}
        
        print(f"   Articles remaining: {len(articles_after)}")
        print(f"   Duplicate groups remaining: {len(duplicates_after)}")
        
        if len(duplicates_after) == 0:
            print("✅ All duplicates successfully removed!")
        else:
            print(f"⚠️  {len(duplicates_after)} duplicate groups still remain")
        
        print("\n" + "=" * 50)
        print("🎯 Duplicate Cleanup Complete")
        
        return len(duplicates_after) == 0
        
    except Exception as e:
        print(f"❌ Error cleaning up duplicates: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    cleanup_duplicate_articles()