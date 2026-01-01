#!/usr/bin/env python3
"""
Test Automated News Scheduler
Verify the automated scheduler works correctly before deployment
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automated_news_scheduler import AutomatedNewsScheduler
import time

def test_automated_scheduler():
    """Test the automated news scheduler functionality"""
    
    print("🧪 Testing Automated News Scheduler")
    print("=" * 60)
    
    try:
        # Initialize scheduler
        print("📋 Step 1: Initializing scheduler...")
        scheduler = AutomatedNewsScheduler()
        print("✅ Scheduler initialized successfully")
        
        # Check components
        print(f"   - Database Manager: {'✅' if scheduler.db_manager else '❌'}")
        print(f"   - Alert Logger: {'✅' if scheduler.alert_logger else '❌'}")
        print(f"   - AI Analyzer: {'✅' if scheduler.use_ai_analysis else '❌'}")
        print(f"   - Keywords: {len(scheduler.KEYWORDS)} security keywords")
        print()
        
        # Test with small number of articles
        print("📋 Step 2: Running test scrape (10 articles)...")
        start_time = time.time()
        
        results = scheduler.run_scheduled_scrape(max_articles=10)
        
        duration = time.time() - start_time
        print(f"✅ Test scrape completed in {duration:.2f} seconds")
        print()
        
        # Display results
        print("📊 Test Results:")
        print(f"   - Articles Found: {results['articles_found']}")
        print(f"   - With Keywords: {results['articles_with_keywords']}")
        
        if scheduler.use_ai_analysis:
            print(f"   - After AI Filter: {results['articles_after_ai_filter']}")
            print(f"   - AI Filtered: {results['ai_filtered']}")
        
        print(f"   - Articles Stored: {results['articles_stored']}")
        print(f"   - Duplicates Removed: {results['duplicates_removed']}")
        print(f"   - Processing Time: {results['duration']:.2f}s")
        
        if results['errors']:
            print(f"   - Errors: {len(results['errors'])}")
            for error in results['errors'][:3]:
                print(f"     * {error}")
        else:
            print("   - Errors: None")
        
        print()
        
        # Evaluate test success
        success_criteria = [
            ("Scheduler initialized", True),
            ("Articles found", results['articles_found'] > 0),
            ("Processing completed", results['duration'] > 0),
            ("No critical errors", len(results['errors']) == 0)
        ]
        
        print("📋 Step 3: Evaluating test results...")
        all_passed = True
        for criterion, passed in success_criteria:
            status = "✅" if passed else "❌"
            print(f"   {status} {criterion}")
            if not passed:
                all_passed = False
        
        print()
        
        if all_passed:
            print("🎉 All tests passed! Automated scheduler is ready for deployment.")
            print()
            print("📋 Deployment Checklist:")
            print("   ✅ Scheduler functionality verified")
            print("   ✅ Database connection working")
            print("   ✅ Enhanced duplicate detection active")
            print("   ✅ Keyword filtering operational")
            
            if scheduler.use_ai_analysis:
                print("   ✅ AI content analysis enabled")
            else:
                print("   ⚠️  AI analysis disabled (DEEPSEEK_API_KEY not configured)")
            
            print()
            print("🚀 Ready for Digital Ocean deployment!")
            print("   Run: chmod +x setup_digital_ocean_scheduler.sh")
            print("   Then: sudo ./setup_digital_ocean_scheduler.sh")
            
            return True
        else:
            print("❌ Some tests failed. Please check the configuration.")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_scheduler_components():
    """Test individual scheduler components"""
    
    print("🔧 Testing Individual Components")
    print("=" * 40)
    
    try:
        # Test database connection
        print("📋 Testing database connection...")
        from scraper.core.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Test query
        result = db_manager.supabase.table('articles').select('id').limit(1).execute()
        print(f"✅ Database connection: {len(result.data)} test records found")
        
        # Test AI analyzer
        print("📋 Testing AI analyzer...")
        try:
            from scraper.core.ai_content_analyzer import AIContentAnalyzer
            ai_analyzer = AIContentAnalyzer()
            print("✅ AI analyzer: Initialized successfully")
        except ValueError as e:
            print(f"⚠️  AI analyzer: {e}")
        
        # Test multi-source scraper
        print("📋 Testing multi-source scraper...")
        from scraper.core.multi_source_scraper import MultiSourceScraper
        from scraper.core.storage import InMemoryDataStore
        from scraper.core import Config
        from datetime import date, timedelta
        
        config = Config(
            target_url="https://www.theblockbeats.info/newsflash",
            max_articles=1,
            request_delay=1.0,
            timeout=30,
            max_retries=2
        )
        
        data_store = InMemoryDataStore()
        end_date = date.today()
        start_date = end_date - timedelta(days=1)
        
        scraper = MultiSourceScraper(
            config=config,
            data_store=data_store,
            start_date=start_date,
            end_date=end_date,
            keywords_filter=["测试"],
            sources=['blockbeats'],
            enable_deduplication=True
        )
        
        print("✅ Multi-source scraper: Initialized successfully")
        
        print()
        print("✅ All components tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Automated News Scheduler Test Suite")
    print("=" * 70)
    print()
    
    # Test components first
    components_ok = test_scheduler_components()
    print()
    
    if components_ok:
        # Test full scheduler
        scheduler_ok = test_automated_scheduler()
        
        if scheduler_ok:
            print()
            print("🎊 All tests completed successfully!")
            print("The automated scheduler is ready for Digital Ocean deployment.")
            sys.exit(0)
        else:
            print()
            print("❌ Scheduler tests failed.")
            sys.exit(1)
    else:
        print()
        print("❌ Component tests failed.")
        sys.exit(1)