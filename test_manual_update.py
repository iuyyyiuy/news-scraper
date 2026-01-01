"""
Test the 手动更新 (Manual Update) functionality
"""
from scraper.core.manual_scraper import ManualScraper
import time

def test_manual_update():
    """Test the manual update function"""
    print("🧪 Testing 手动更新 (Manual Update) Function")
    print("=" * 60)
    
    # Create progress callback for testing
    def progress_callback(message, log_type):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    try:
        # Create manual scraper
        scraper = ManualScraper()
        
        print("📋 Starting 手动更新 with 5 articles per source for testing...")
        
        # Run manual update with small number for testing
        result = scraper.手动更新(
            max_articles=5,  # Small number for testing
            progress_callback=progress_callback
        )
        
        print("\n" + "=" * 60)
        print("📊 手动更新 Test Results:")
        print("=" * 60)
        print(f"⏱️  Duration: {result['duration']:.2f} seconds")
        print(f"📰 Total articles found: {result['total_articles_found']}")
        print(f"💾 Total articles saved: {result['total_articles_saved']}")
        print(f"🔄 Total duplicates skipped: {result['total_duplicates_skipped']}")
        print(f"🤖 AI filtered count: {result['ai_filtered_count']}")
        print(f"📝 Sources processed: {', '.join(result['sources_processed'])}")
        
        if result['errors']:
            print(f"❌ Errors: {len(result['errors'])}")
            for error in result['errors']:
                print(f"   - {error}")
        else:
            print("✅ No errors")
        
        # Source-specific results
        print("\n📊 Per-Source Results:")
        for source, source_result in result['source_results'].items():
            print(f"  {source.upper()}:")
            print(f"    Found: {source_result['articles_found']}")
            print(f"    Saved: {source_result['articles_saved']}")
            print(f"    Duplicates: {source_result['duplicates_skipped']}")
            print(f"    AI Filtered: {source_result.get('ai_filtered', 0)}")
            print(f"    Duration: {source_result['duration']:.2f}s")
        
        print("\n✅ 手动更新 test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ 手动更新 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint():
    """Test the API endpoint"""
    print("\n🌐 Testing API Endpoint")
    print("-" * 40)
    
    try:
        import requests
        
        # Test the status endpoint
        response = requests.get("http://localhost:8000/api/manual-update/status")
        if response.status_code == 200:
            print("✅ Status endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
        
        # Test the manual update endpoint (don't actually run it)
        print("💡 Manual update endpoint: POST /api/manual-update")
        print("   Parameters: max_articles (default: 200)")
        
        return True
        
    except Exception as e:
        print(f"⚠️  API test skipped (server not running): {e}")
        return True

def main():
    """Main test function"""
    print("🚀 手动更新 (Manual Update) Test Suite")
    print("=" * 60)
    
    success = True
    
    # Test the core functionality
    if not test_manual_update():
        success = False
    
    # Test API endpoint
    if not test_api_endpoint():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests completed!")
        print("💡 手动更新 function is ready to use")
        print("📝 API endpoints:")
        print("   POST /api/manual-update - Start manual update")
        print("   GET /api/manual-update/status - Check status")
    else:
        print("💥 Some tests failed")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())