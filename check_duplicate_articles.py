#!/usr/bin/env python3
"""
Check for duplicate articles in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.database_manager import DatabaseManager
from collections import defaultdict

def check_duplicate_articles():
    """Check for duplicate articles in the database"""
    
    print("🔍 Checking for Duplicate Articles in Database")
    print("=" * 60)
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Get all articles
        print("1. Retrieving all articles from database...")
        result = db_manager.supabase.table('articles').select(
            'id, title, body_text, url, source, date, scraped_at'
        ).order('scraped_at', desc=True).execute()
        
        articles = result.data
        print(f"   Found {len(articles)} total articles")
        
        # Group by title to find duplicates
        print("\n2. Analyzing for duplicate titles...")
        title_groups = defaultdict(list)
        
        for article in articles:
            title = article['title'].strip()
            title_groups[title].append(article)
        
        # Find duplicates
        duplicates = {title: articles for title, articles in title_groups.items() if len(articles) > 1}
        
        print(f"   Found {len(duplicates)} duplicate title groups")
        
        if duplicates:
            print("\n3. Duplicate Articles Found:")
            print("-" * 60)
            
            total_duplicate_count = 0
            for title, duplicate_articles in duplicates.items():
                print(f"\n📰 Title: {title[:80]}...")
                print(f"   Duplicate Count: {len(duplicate_articles)}")
                total_duplicate_count += len(duplicate_articles) - 1  # -1 because one is original
                
                for i, article in enumerate(duplicate_articles):
                    print(f"   [{i+1}] ID: {article['id'][:8]}... | Source: {article['source']} | Date: {article['date']} | Scraped: {article['scraped_at'][:19]}")
                
                # Show content comparison for first few
                if len(duplicate_articles) >= 2:
                    content1 = duplicate_articles[0].get('body_text', '')[:200]
                    content2 = duplicate_articles[1].get('body_text', '')[:200]
                    
                    if content1 == content2:
                        print(f"   ⚠️  Content is IDENTICAL")
                    else:
                        print(f"   ℹ️  Content differs")
            
            print(f"\n📊 Summary:")
            print(f"   Total duplicate groups: {len(duplicates)}")
            print(f"   Total duplicate articles: {total_duplicate_count}")
            print(f"   Percentage of duplicates: {(total_duplicate_count/len(articles)*100):.1f}%")
        else:
            print("✅ No duplicate articles found!")
        
        # Check for similar content (same first 100 characters)
        print("\n4. Checking for similar content...")
        content_groups = defaultdict(list)
        
        for article in articles:
            content_start = article.get('body_text', '')[:100].strip()
            if content_start:
                content_groups[content_start].append(article)
        
        similar_content = {content: articles for content, articles in content_groups.items() if len(articles) > 1}
        
        if similar_content:
            print(f"   Found {len(similar_content)} groups with similar content")
            
            for content_start, similar_articles in list(similar_content.items())[:3]:  # Show first 3
                print(f"\n📝 Content starts with: {content_start[:50]}...")
                print(f"   Similar articles: {len(similar_articles)}")
                for article in similar_articles[:3]:  # Show first 3
                    print(f"   - {article['title'][:60]}... ({article['source']})")
        else:
            print("✅ No articles with similar content found!")
        
        print("\n" + "=" * 60)
        print("🎯 Duplicate Check Complete")
        
        return len(duplicates) > 0
        
    except Exception as e:
        print(f"❌ Error checking duplicates: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_duplicate_articles()