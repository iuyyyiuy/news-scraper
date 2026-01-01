#!/usr/bin/env python3
"""
Test ForesightNews integration with the manual scraper
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from datetime import date, timedelta
from scraper.core.manual_scraper import ManualScraper
from scraper.core.storage import CSVDataStore
import tempfile

def test_foresightnews_integration():
    """Test ForesightNews scraper integration"""
    print("🧪 Testing ForesightNews Integration")
    print("=" * 60)
    
    try:
        # Create temporary CSV file for testing
        temp_file = tempfile.mktemp(suffix='.csv')
        data_store = CSVDataStore(temp_file)
        
        # Create manual scraper
        scraper = ManualScraper()
        
        # Test with small number of articles
        print("🚀 Starting manual update test (2 articles per source)...")
        
        def progress_callback(found, scraped):
            print(f"📊 Progress: {found} found, {scraped} scraped")
        
        # Run manual update
        result = scraper.手动更新(max_articles=2, progress_callback=progress_callback)
        
        print("\n📋 Test Results:")
        print(f"✅ Sources processed: {result['sources_processed']}")
        print(f"📰 Total articles found: {result['total_articles_found']}")
        print(f"💾 Total articles saved: {result['total_articles_saved']}")
        print(f"⏱️  Duration: {result['duration']:.2f} seconds")
        
        # Check individual source results
        for source, source_result in result['source_results'].items():
            print(f"\n📊 {source.upper()} Results:")
            print(f"   Found: {source_result['articles_found']}")
            print(f"   Saved: {source_result['articles_saved']}")
            print(f"   Duration: {source_result['duration']:.2f}s")
            
            if source_result['errors']:
                print(f"   Errors: {len(source_result['errors'])}")
        
        if result['errors']:
            print(f"\n⚠️  Errors encountered: {len(result['errors'])}")
            for error in result['errors'][:3]:
                print(f"   - {error}")
        
        # Check if ForesightNews was processed
        if 'foresightnews' in result['sources_processed']:
            print("\n✅ ForesightNews integration successful!")
        else:
            print("\n❌ ForesightNews was not processed")
        
        # Clean up
        try:
            os.remove(temp_file)
        except:
            pass
        
        return result['total_articles_saved'] > 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_selenium_availability():
    """Test if Selenium and Chrome are available"""
    print("\n🔍 Testing Selenium availability...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        print("✅ Selenium package available")
        
        # Test Chrome driver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.google.com")
        driver.quit()
        
        print("✅ Chrome WebDriver working")
        return True
        
    except ImportError:
        print("❌ Selenium not installed")
        print("💡 Install with: pip install selenium")
        return False
    except Exception as e:
        print(f"❌ Chrome WebDriver issue: {e}")
        print("💡 Make sure Chrome and ChromeDriver are installed")
        return False

if __name__ == "__main__":
    print("🚀 ForesightNews Integration Test")
    print("=" * 60)
    
    # Test Selenium first
    selenium_ok = test_selenium_availability()
    
    if selenium_ok:
        # Test integration
        success = test_foresightnews_integration()
        
        print("\n" + "=" * 60)
        print("🔍 INTEGRATION TEST SUMMARY:")
        print(f"✅ Selenium available: {selenium_ok}")
        print(f"✅ Integration test: {'PASSED' if success else 'FAILED'}")
        
        if success:
            print("\n🎉 ForesightNews is ready for production!")
            print("💡 You can now use manual update with both BlockBeats and ForesightNews")
        else:
            print("\n⚠️  Integration needs attention")
            print("💡 Check error messages above for details")
    else:
        print("\n⚠️  Selenium setup required")
        print("💡 Install Selenium and Chrome to use ForesightNews scraper")
    
    print("=" * 60)