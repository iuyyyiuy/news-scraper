#!/usr/bin/env python3
"""
Investigate live duplicate detection issues
Check what's happening during the scraping process
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.database_manager import DatabaseManager
from scraper.core.ai_content_analyzer import AIContentAnalyzer
from collections import defaultdict

def investigate_live_duplicates():
    """Investigate why duplicates are appearing in live scraping"""
    
    print("🔍 Investigating Live Duplicate Detection Issues")
    print("=" * 60)
    
    try:
        # Initialize components
        db_manager = DatabaseManager()
        ai_analyzer = AIContentAnalyzer()
        
        # Get recent articles (last 24 hours)
        print("1. Checking recent articles for duplicates...")
        result = db_manager.supabase.table('articles').select(
            'id, title, body_text, url, source, date, scraped_at'
        ).gte(
            'scraped_at', '2026-01-01T00:00:00'
        ).order('scraped_at', desc=True).execute()
        
        articles = result.data
        print(f"   Found {len(articles)} articles from today")
        
        # Group by title to find duplicates
        title_groups = defaultdict(list)
        for article in articles:
            title = article['title'].strip()
            title_groups[title].append(article)
        
        # Find duplicates
        duplicates = {title: articles for title, articles in title_groups.items() if len(articles) > 1}
        
        if duplicates:
            print(f"\n2. Found {len(duplicates)} duplicate title groups:")
            
            for title, duplicate_articles in duplicates.items():
                print(f"\n📰 Title: {title}")
                print(f"   Occurrences: {len(duplicate_articles)}")
                
                # Check if content is actually identical
                contents = [art.get('body_text', '') for art in duplicate_articles]
                unique_contents = set(contents)
                
                if len(unique_contents) == 1:
                    print(f"   ⚠️  IDENTICAL CONTENT - True duplicates!")
                else:
                    print(f"   ℹ️  Different content - Same title, different articles")
                
                # Show scraping times
                for i, article in enumerate(duplicate_articles):
                    print(f"   [{i+1}] {article['scraped_at']} | {article['source']} | ID: {article['id'][:8]}...")
                
                # Test AI duplicate detection on these
                if len(duplicate_articles) >= 2:
                    print(f"\n   🤖 Testing AI duplicate detection:")
                    
                    new_article = {
                        'title': duplicate_articles[0]['title'],
                        'content': duplicate_articles[0].get('body_text', '')
                    }
                    
                    existing_articles = [{
                        'title': art['title'],
                        'content': art.get('body_text', '')
                    } for art in duplicate_articles[1:]]
                    
                    ai_result = ai_analyzer.detect_duplicate_content(new_article, existing_articles)
                    
                    print(f"      AI Result: is_duplicate={ai_result['is_duplicate']}")
                    print(f"      Similarity Score: {ai_result['similarity_score']}")
                    print(f"      Reason: {ai_result.get('explanation', ai_result.get('reason', 'No reason'))}")
        
        # Check database constraint
        print(f"\n3. Checking database constraints...")
        
        # Check if there are URL duplicates (should be prevented by unique constraint)
        url_groups = defaultdict(list)
        for article in articles:
            url = article['url']
            url_groups[url].append(article)
        
        url_duplicates = {url: articles for url, articles in url_groups.items() if len(articles) > 1}
        
        if url_duplicates:
            print(f"   ⚠️  Found {len(url_duplicates)} URL duplicates (database constraint issue!)")
            for url, dups in url_duplicates.items():
                print(f"      URL: {url}")
                print(f"      Count: {len(dups)}")
        else:
            print(f"   ✅ No URL duplicates found (database constraint working)")
        
        # Check the manual scraper logic
        print(f"\n4. Analyzing manual scraper duplicate prevention...")
        
        # Look at the _store_article_realtime method
        from scraper.core.manual_scraper import ManualScraper
        manual_scraper = ManualScraper()
        
        # Test the check_article_exists method
        if duplicates:
            sample_duplicate = list(duplicates.values())[0][0]
            exists = manual_scraper.db_manager.check_article_exists(sample_duplicate['url'])
            print(f"   Sample URL exists check: {exists}")
            print(f"   Sample URL: {sample_duplicate['url']}")
        
        print(f"\n5. Recommendations:")
        
        if duplicates:
            print(f"   🔧 Issues found:")
            print(f"      - {len(duplicates)} duplicate groups in database")
            print(f"      - AI detection may not be running during live scraping")
            print(f"      - Database constraint may not be working properly")
            
            print(f"\n   💡 Suggested fixes:")
            print(f"      1. Strengthen URL uniqueness constraint")
            print(f"      2. Add title+content hash checking")
            print(f"      3. Improve AI integration in real-time scraping")
            print(f"      4. Add pre-save duplicate checking")
        else:
            print(f"   ✅ No duplicates found - system working correctly")
        
        print("\n" + "=" * 60)
        print("🎯 Investigation Complete")
        
        return len(duplicates) > 0
        
    except Exception as e:
        print(f"❌ Error investigating duplicates: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    investigate_live_duplicates()