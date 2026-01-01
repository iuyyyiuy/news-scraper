#!/usr/bin/env python3
"""
Test the updated manual scraper with broader keywords.
"""

import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_updated_manual_scraper():
    """Test the updated manual scraper with broader keywords"""
    print("🧪 TESTING UPDATED MANUAL SCRAPER")
    print("=" * 60)
    
    try:
        from scraper.core.manual_scraper import ManualScraper
        
        print("✅ ManualScraper imported successfully")
        
        # Initialize scraper
        scraper = ManualScraper()
        print("✅ ManualScraper initialized")
        
        # Check updated keywords
        print(f"   Keywords count: {len(scraper.KEYWORDS)}")
        print(f"   Updated keywords: {', '.join(scraper.KEYWORDS)}")
        
        # Test with small number for debugging
        print(f"\n🧪 Testing with max_articles=10 for debugging...")
        
        def progress_callback(message, log_type):
            print(f"   Progress: {message}")
        
        # Run a small test
        start_time = datetime.now()
        result = scraper.手动更新(max_articles=10, progress_callback=progress_callback)
        end_time = datetime.now()
        
        print("✅ Updated manual scraper test completed")
        print(f"   Sources processed: {result.get('sources_processed', [])}")
        print(f"   Total articles found: {result.get('total_articles_found', 0)}")
        print(f"   Total articles saved: {result.get('total_articles_saved', 0)}")
        print(f"   Duration: {result.get('duration', 0):.2f} seconds")
        
        if result.get('errors'):
            print("   Errors:")
            for error in result['errors'][:3]:
                print(f"     - {error}")
        
        # Show improvement
        articles_saved = result.get('total_articles_saved', 0)
        if articles_saved > 0:
            print(f"🎉 SUCCESS! Found and saved {articles_saved} articles with broader keywords!")
        else:
            print("⚠️  Still no articles saved. May need further keyword adjustment.")
        
        return result
        
    except Exception as e:
        print(f"❌ Updated manual scraper test error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    test_updated_manual_scraper()

if __name__ == "__main__":
    main()