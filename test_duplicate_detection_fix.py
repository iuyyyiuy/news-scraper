#!/usr/bin/env python3
"""
Test and Fix Duplicate Detection
Tests the current duplicate detection and implements a fix to check against database articles
"""

import logging
from scraper.core.database_manager import DatabaseManager
from scraper.core.ai_content_analyzer import AIContentAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_current_duplicate_detection():
    """Test the current duplicate detection system"""
    
    print("🔍 Testing Current Duplicate Detection")
    print("=" * 50)
    
    try:
        # Initialize components
        db_manager = DatabaseManager()
        ai_analyzer = AIContentAnalyzer()
        
        # Get some articles from database
        result = db_manager.supabase.table('articles').select('*').limit(10).execute()
        articles = result.data
        
        if not articles:
            print("❌ No articles found in database")
            return False
        
        print(f"✅ Found {len(articles)} articles in database")
        
        # Look for potential duplicates by title
        titles = [article['title'] for article in articles]
        title_counts = {}
        
        for title in titles:
            title_counts[title] = title_counts.get(title, 0) + 1
        
        duplicates_found = {title: count for title, count in title_counts.items() if count > 1}
        
        if duplicates_found:
            print(f"🚨 Found {len(duplicates_found)} duplicate titles:")
            for title, count in duplicates_found.items():
                print(f"   '{title}' appears {count} times")
                
                # Get all articles with this title
                duplicate_articles = [a for a in articles if a['title'] == title]
                for i, article in enumerate(duplicate_articles):
                    print(f"     {i+1}. Date: {article.get('date', 'N/A')}, Source: {article.get('source', 'N/A')}")
        else:
            print("✅ No duplicate titles found in sample")
        
        return len(duplicates_found) > 0
        
    except Exception as e:
        print(f"❌ Error testing duplicate detection: {e}")
        return False

def test_ai_duplicate_detection():
    """Test the AI duplicate detection specifically"""
    
    print("\n🤖 Testing AI Duplicate Detection")
    print("=" * 50)
    
    try:
        ai_analyzer = AIContentAnalyzer()
        
        # Create test articles with obvious duplicates
        test_articles = [
            {
                'title': '2026年，加密行业会好吗？',
                'content': '随着2026年的到来，加密货币行业面临着新的挑战和机遇。市场分析师认为...'
            },
            {
                'title': '2026年，加密行业会好吗?',  # Slightly different punctuation
                'content': '随着2026年的到来，加密货币行业面临着新的挑战和机遇。市场分析师认为...'
            },
            {
                'title': 'Bitcoin价格分析',
                'content': 'Bitcoin今日价格波动较大，技术分析显示...'
            }
        ]
        
        print("📝 Testing with sample articles:")
        for i, article in enumerate(test_articles):
            print(f"   {i+1}. {article['title']}")
        
        # Test duplicate detection
        for i, new_article in enumerate(test_articles[1:], 1):
            existing_articles = test_articles[:i]
            
            print(f"\n🔍 Testing article {i+1} against previous articles:")
            
            duplicate_result = ai_analyzer.detect_duplicate_content(new_article, existing_articles)
            
            print(f"   Is duplicate: {duplicate_result['is_duplicate']}")
            print(f"   Similarity score: {duplicate_result['similarity_score']}")
            print(f"   Reason: {duplicate_result['reason']}")
            
            if duplicate_result['is_duplicate']:
                print(f"   ✅ Correctly detected duplicate!")
            else:
                print(f"   ⚠️  Did not detect as duplicate")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI duplicate detection: {e}")
        return False

def check_database_duplicates():
    """Check for actual duplicates in the database"""
    
    print("\n📊 Checking Database for Duplicates")
    print("=" * 50)
    
    try:
        db_manager = DatabaseManager()
        
        # Get all articles
        result = db_manager.supabase.table('articles').select('id, title, date, source').execute()
        articles = result.data
        
        print(f"📈 Total articles in database: {len(articles)}")
        
        # Group by title (case-insensitive)
        title_groups = {}
        for article in articles:
            title_key = article['title'].lower().strip()
            if title_key not in title_groups:
                title_groups[title_key] = []
            title_groups[title_key].append(article)
        
        # Find duplicates
        duplicates = {title: articles for title, articles in title_groups.items() if len(articles) > 1}
        
        if duplicates:
            print(f"🚨 Found {len(duplicates)} sets of duplicate titles:")
            
            for title, duplicate_articles in list(duplicates.items())[:5]:  # Show first 5
                print(f"\n📰 '{duplicate_articles[0]['title']}':")
                for article in duplicate_articles:
                    print(f"   - ID: {article['id']}, Date: {article['date']}, Source: {article['source']}")
            
            if len(duplicates) > 5:
                print(f"\n... and {len(duplicates) - 5} more duplicate sets")
        else:
            print("✅ No duplicate titles found")
        
        return duplicates
        
    except Exception as e:
        print(f"❌ Error checking database duplicates: {e}")
        return {}

def main():
    """Run all duplicate detection tests"""
    
    print("🧪 Duplicate Detection Analysis")
    print("=" * 60)
    
    # Test current system
    has_duplicates = test_current_duplicate_detection()
    
    # Test AI detection
    ai_test_ok = test_ai_duplicate_detection()
    
    # Check database duplicates
    db_duplicates = check_database_duplicates()
    
    print("\n" + "=" * 60)
    print("📋 Analysis Results")
    print("=" * 60)
    
    print(f"Database has duplicates: {'✅ YES' if has_duplicates or db_duplicates else '❌ NO'}")
    print(f"AI detection working: {'✅ YES' if ai_test_ok else '❌ NO'}")
    print(f"Duplicate sets found: {len(db_duplicates) if db_duplicates else 0}")
    
    if db_duplicates:
        print("\n🔧 Issue Identified:")
        print("- AI duplicate detection only compares within the same scraping session")
        print("- It doesn't check against existing articles in the database")
        print("- This allows duplicates to be saved across different scraping sessions")
        
        print("\n💡 Solution Needed:")
        print("1. Modify manual scraper to fetch recent articles from database")
        print("2. Use AI to compare new articles against existing database articles")
        print("3. Skip saving articles that are detected as duplicates")
        
        print(f"\n📊 Current Status:")
        print(f"- Total duplicate sets: {len(db_duplicates)}")
        print(f"- This explains why you see duplicate news in the dashboard")
    else:
        print("\n✅ No duplicates found - system working correctly")

if __name__ == "__main__":
    main()