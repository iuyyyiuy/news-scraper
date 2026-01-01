#!/usr/bin/env python3
"""
Test ForesightNews implementation on localhost
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from datetime import date, timedelta
import tempfile
import time

def test_selenium_setup():
    """Test if Selenium and Chrome are working"""
    print("🔍 Testing Selenium Setup...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        print("📱 Starting Chrome WebDriver...")
        driver = webdriver.Chrome(options=chrome_options)
        
        print("🌐 Testing basic navigation...")
        driver.get("https://www.google.com")
        title = driver.title
        
        driver.quit()
        
        print(f"✅ Selenium working! Page title: {title}")
        return True
        
    except Exception as e:
        print(f"❌ Selenium setup issue: {e}")
        print("💡 Make sure Chrome browser is installed")
        return False

def test_foresightnews_scraper_direct():
    """Test ForesightNews scraper directly"""
    print("\n🧪 Testing ForesightNews Scraper Directly...")
    
    try:
        from scraper.core.foresightnews_scraper import ForesightNewsScraper
        from scraper.core.storage import CSVDataStore
        from scraper.core.models import Config
        
        # Create temporary CSV file
        temp_file = tempfile.mktemp(suffix='.csv')
        data_store = CSVDataStore(temp_file)
        
        # Create config
        config = Config(
            target_url="https://foresightnews.pro/news",
            max_articles=50,  # Test with 50 articles
            request_delay=2.0,
            timeout=45,
            max_retries=2
        )
        
        # Date range: last 3 days
        end_date = date.today()
        start_date = end_date - timedelta(days=3)
        
        # Security keywords
        keywords = [
            "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
            "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
            "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
        ]
        
        print(f"📅 Date range: {start_date} to {end_date}")
        print(f"🔍 Keywords: {len(keywords)} security-related terms")
        print(f"📰 Max articles: {config.max_articles}")
        
        # Create scraper
        scraper = ForesightNewsScraper(
            config=config,
            data_store=data_store,
            start_date=start_date,
            end_date=end_date,
            keywords_filter=keywords
        )
        
        print("\n🚀 Starting ForesightNews scraping...")
        start_time = time.time()
        
        # Run scraper
        result = scraper.scrape()
        
        duration = time.time() - start_time
        
        print(f"\n📊 Scraping Results:")
        print(f"✅ Articles found: {result.total_articles_found}")
        print(f"💾 Articles scraped: {result.articles_scraped}")
        print(f"❌ Articles failed: {result.articles_failed}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        if result.errors:
            print(f"⚠️  Errors: {len(result.errors)}")
            for error in result.errors[:3]:
                print(f"   - {error}")
        
        # Check saved articles
        articles = data_store.get_all_articles()
        print(f"\n📋 Saved Articles: {len(articles)}")
        
        for i, article in enumerate(articles):
            print(f"   {i+1}. {article.title[:50]}...")
            print(f"      Source: {article.source_website}")
            print(f"      Date: {article.publication_date}")
            print(f"      URL: {article.url}")
            if hasattr(article, 'matched_keywords'):
                print(f"      Keywords: {article.matched_keywords}")
            print()
        
        # Clean up
        try:
            os.remove(temp_file)
        except:
            pass
        
        return result.articles_scraped > 0
        
    except Exception as e:
        print(f"❌ ForesightNews scraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manual_scraper_integration():
    """Test the manual scraper with ForesightNews integration"""
    print("\n🔧 Testing Manual Scraper Integration...")
    
    try:
        from scraper.core.manual_scraper import ManualScraper
        
        # Create manual scraper
        scraper = ManualScraper()
        
        print("📋 Testing manual update with 50 articles per source...")
        
        def progress_callback(found, scraped):
            print(f"   📊 Progress: {found} found, {scraped} scraped")
        
        # Run manual update
        result = scraper.手动更新(max_articles=50, progress_callback=progress_callback)
        
        print(f"\n📊 Manual Update Results:")
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
                for error in source_result['errors'][:2]:
                    print(f"      - {error}")
        
        if result['errors']:
            print(f"\n⚠️  Global errors: {len(result['errors'])}")
            for error in result['errors'][:3]:
                print(f"   - {error}")
        
        # Check if ForesightNews was processed
        foresightnews_processed = 'foresightnews' in result['sources_processed']
        print(f"\n✅ ForesightNews integration: {'SUCCESS' if foresightnews_processed else 'FAILED'}")
        
        return result['total_articles_saved'] > 0
        
    except Exception as e:
        print(f"❌ Manual scraper integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def start_localhost_server():
    """Start the web server on localhost for testing"""
    print("\n🌐 Starting Localhost Server...")
    
    try:
        import uvicorn
        from scraper.web_api import app
        
        print("🚀 Starting server on http://localhost:8000")
        print("📱 Dashboard will be available at: http://localhost:8000/dashboard")
        print("🔧 API docs at: http://localhost:8000/docs")
        print("\n💡 Press Ctrl+C to stop the server")
        
        # Start server
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server startup failed: {e}")

def main():
    """Main testing function"""
    print("🚀 ForesightNews Localhost Testing")
    print("=" * 60)
    
    # Test 1: Selenium setup
    selenium_ok = test_selenium_setup()
    
    if not selenium_ok:
        print("\n❌ Cannot proceed without Selenium")
        print("💡 Please install Chrome browser and try again")
        return
    
    # Test 2: Direct scraper test
    print("\n" + "=" * 60)
    scraper_ok = test_foresightnews_scraper_direct()
    
    # Test 3: Manual scraper integration
    print("\n" + "=" * 60)
    integration_ok = test_manual_scraper_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("🔍 LOCALHOST TEST SUMMARY:")
    print(f"✅ Selenium setup: {'OK' if selenium_ok else 'FAILED'}")
    print(f"✅ ForesightNews scraper: {'OK' if scraper_ok else 'FAILED'}")
    print(f"✅ Manual scraper integration: {'OK' if integration_ok else 'FAILED'}")
    
    if selenium_ok and scraper_ok and integration_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("💡 ForesightNews is ready for localhost testing")
        
        # Ask if user wants to start server
        print("\n" + "=" * 60)
        response = input("🌐 Start localhost web server? (y/n): ").lower().strip()
        
        if response in ['y', 'yes']:
            start_localhost_server()
        else:
            print("👋 Testing complete. You can start the server manually with:")
            print("   python -m uvicorn scraper.web_api:app --host 0.0.0.0 --port 8000")
    else:
        print("\n⚠️  Some tests failed. Check error messages above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()