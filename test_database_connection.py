"""
Test script for News Database Feature
Tests database connection and basic operations
"""
from scraper.core.database_manager import DatabaseManager
from datetime import datetime


def test_connection():
    """Test database connection"""
    print("="*60)
    print("🧪 Testing Database Connection")
    print("="*60 + "\n")
    
    db = DatabaseManager()
    
    if not db.supabase:
        print("❌ Failed to connect to database")
        return False
    
    print("✅ Successfully connected to Supabase\n")
    return True


def test_insert_sample_article():
    """Test inserting a sample article"""
    print("="*60)
    print("🧪 Testing Article Insertion")
    print("="*60 + "\n")
    
    db = DatabaseManager()
    
    # Create sample article
    sample_article = {
        'title': '测试文章：某交易所发现安全漏洞',
        'url': f'https://test.example.com/article-{datetime.now().timestamp()}',
        'date': datetime.now(),
        'source': 'Test',
        'content': '这是一篇测试文章的内容。某交易所发现了严重的安全漏洞，已经及时修复。',
        'matched_keywords': ['安全问题', '漏洞']
    }
    
    success = db.insert_article(sample_article)
    
    if success:
        print("✅ Successfully inserted test article\n")
        return True
    else:
        print("❌ Failed to insert test article\n")
        return False


def test_retrieve_articles():
    """Test retrieving articles"""
    print("="*60)
    print("🧪 Testing Article Retrieval")
    print("="*60 + "\n")
    
    db = DatabaseManager()
    
    # Get all articles
    articles = db.get_all_articles(limit=5)
    print(f"📰 Found {len(articles)} articles (showing max 5)")
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article['title'][:50]}...")
        print(f"   Source: {article['source']}")
        print(f"   Date: {article['date']}")
        print(f"   Keywords: {', '.join(article['matched_keywords'])}")
    
    print("\n✅ Successfully retrieved articles\n")
    return True


def test_keyword_filtering():
    """Test filtering by keyword"""
    print("="*60)
    print("🧪 Testing Keyword Filtering")
    print("="*60 + "\n")
    
    db = DatabaseManager()
    
    # Get keyword counts
    keywords = db.get_all_keywords_with_counts()
    
    if keywords:
        print(f"🔑 Found {len(keywords)} unique keywords:\n")
        for keyword, count in list(keywords.items())[:10]:
            print(f"   {keyword}: {count} articles")
        
        # Test filtering by first keyword
        first_keyword = list(keywords.keys())[0]
        filtered_articles = db.get_articles_by_keyword(first_keyword, limit=3)
        print(f"\n📰 Articles with keyword '{first_keyword}': {len(filtered_articles)}")
        
        print("\n✅ Successfully tested keyword filtering\n")
    else:
        print("⚠️  No keywords found (database might be empty)\n")
    
    return True


def test_statistics():
    """Test getting statistics"""
    print("="*60)
    print("🧪 Testing Statistics")
    print("="*60 + "\n")
    
    db = DatabaseManager()
    
    total_count = db.get_total_count()
    last_scrape = db.get_last_scrape_time()
    
    print(f"📊 Database Statistics:")
    print(f"   Total articles: {total_count}")
    print(f"   Last scrape: {last_scrape if last_scrape else 'Never'}")
    
    print("\n✅ Successfully retrieved statistics\n")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 News Database Feature - Connection Test")
    print("="*60 + "\n")
    
    tests = [
        ("Connection", test_connection),
        ("Insert Sample Article", test_insert_sample_article),
        ("Retrieve Articles", test_retrieve_articles),
        ("Keyword Filtering", test_keyword_filtering),
        ("Statistics", test_statistics)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with error: {e}\n")
            results.append((test_name, False))
    
    # Print summary
    print("="*60)
    print("📊 Test Summary")
    print("="*60 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 All tests passed! Database is ready to use.\n")
    else:
        print("⚠️  Some tests failed. Please check the errors above.\n")


if __name__ == "__main__":
    main()
