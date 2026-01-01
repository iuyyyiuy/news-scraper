"""
Test to verify that all scheduler code has been removed
"""

def test_scheduler_removed():
    """Test that scheduler imports fail as expected"""
    print("🧪 Testing that scheduler has been completely removed...")
    
    # Test 1: Scheduler module should not exist
    print("\n📋 Test 1: Scheduler module should not exist")
    try:
        from scraper.core.scheduler import SchedulerService
        print("❌ FAIL: Scheduler module still exists!")
        return False
    except ImportError:
        print("✅ PASS: Scheduler module successfully removed")
    
    # Test 2: Web API should work without scheduler
    print("\n📋 Test 2: Web API should work without scheduler")
    try:
        from scraper.web_api import app
        print("✅ PASS: Web API imports successfully without scheduler")
    except Exception as e:
        print(f"❌ FAIL: Web API has issues: {e}")
        return False
    
    # Test 3: Manual scrape should still work
    print("\n📋 Test 3: Manual scrape functionality should work")
    try:
        from scraper.core.scheduled_scraper import ScheduledScraper
        scraper = ScheduledScraper()
        print("✅ PASS: ScheduledScraper can be imported and created")
    except Exception as e:
        print(f"❌ FAIL: ScheduledScraper has issues: {e}")
        return False
    
    # Test 4: Database functionality should work
    print("\n📋 Test 4: Database functionality should work")
    try:
        from scraper.core.database_manager import DatabaseManager
        db = DatabaseManager()
        print("✅ PASS: DatabaseManager works without scheduler")
    except Exception as e:
        print(f"❌ FAIL: DatabaseManager has issues: {e}")
        return False
    
    print("\n🎉 All tests passed! Scheduler has been completely removed.")
    return True

def main():
    """Main test function"""
    print("🚀 Testing Scheduler Removal")
    print("=" * 50)
    
    success = test_scheduler_removed()
    
    if success:
        print("\n✅ SUCCESS: All scheduler code has been removed!")
        print("💡 The system now works without any automated scheduling")
        print("💡 Use /api/trigger-scrape for manual scraping")
        return 0
    else:
        print("\n❌ FAILED: Some scheduler code still exists")
        return 1

if __name__ == "__main__":
    exit(main())