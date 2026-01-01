#!/usr/bin/env python3
"""
Verify Enhanced Duplicate Detection Integration
Test that the MultiSourceScraper now uses enhanced duplicate detection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta
from scraper.core.multi_source_scraper import MultiSourceScraper, EnhancedDuplicateDetector
from scraper.core.storage import InMemoryDataStore
from scraper.core import Config

def verify_enhanced_duplicate_integration():
    """Verify that MultiSourceScraper now has enhanced duplicate detection"""
    
    print("🔍 Verifying Enhanced Duplicate Detection Integration")
    print("=" * 60)
    
    # Test 1: Check if EnhancedDuplicateDetector is available
    print("📋 Test 1: EnhancedDuplicateDetector Class")
    try:
        detector = EnhancedDuplicateDetector()
        stats = detector.get_stats()
        print(f"✅ EnhancedDuplicateDetector initialized successfully")
        print(f"   - URLs tracked: {stats['urls_tracked']}")
        print(f"   - Titles tracked: {stats['titles_tracked']}")
        print(f"   - Content hashes tracked: {stats['content_hashes_tracked']}")
    except Exception as e:
        print(f"❌ EnhancedDuplicateDetector failed: {e}")
        return False
    
    print()
    
    # Test 2: Check if MultiSourceScraper has enhanced duplicate detector
    print("📋 Test 2: MultiSourceScraper Integration")
    try:
        config = Config(
            target_url="https://www.theblockbeats.info/newsflash",
            max_articles=5,
            request_delay=1.0,
            timeout=30,
            max_retries=2
        )
        
        data_store = InMemoryDataStore()
        end_date = date.today()
        start_date = end_date - timedelta(days=1)
        keywords = ["安全问题", "黑客", "被盗"]
        
        scraper = MultiSourceScraper(
            config=config,
            data_store=data_store,
            start_date=start_date,
            end_date=end_date,
            keywords_filter=keywords,
            sources=['blockbeats'],
            enable_deduplication=True
        )
        
        # Check if enhanced duplicate detector is initialized
        if hasattr(scraper, 'enhanced_duplicate_detector') and scraper.enhanced_duplicate_detector:
            print("✅ MultiSourceScraper has enhanced_duplicate_detector")
            print(f"   - Type: {type(scraper.enhanced_duplicate_detector).__name__}")
        else:
            print("❌ MultiSourceScraper missing enhanced_duplicate_detector")
            return False
        
        # Check if basic deduplicator is still there
        if hasattr(scraper, 'deduplicator') and scraper.deduplicator:
            print("✅ MultiSourceScraper has basic deduplicator (fallback)")
        else:
            print("⚠️  MultiSourceScraper missing basic deduplicator")
        
    except Exception as e:
        print(f"❌ MultiSourceScraper integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Test 3: Test duplicate detection functionality
    print("📋 Test 3: Duplicate Detection Functionality")
    try:
        # Test with sample article data
        test_articles = [
            {
                'url': 'https://test.com/article1',
                'title': 'Test Article About Security Issue',
                'content': 'This is a test article about security issues in blockchain'
            },
            {
                'url': 'https://test.com/article2',
                'title': 'Test Article About Security Issue',  # Same title
                'content': 'This is a test article about security issues in blockchain'  # Same content
            },
            {
                'url': 'https://test.com/article3',
                'title': 'Different Article About Bitcoin',
                'content': 'This is a different article about Bitcoin price movements'
            }
        ]
        
        detector = EnhancedDuplicateDetector()
        
        # Test first article (should not be duplicate)
        result1 = detector.is_duplicate(test_articles[0])
        print(f"   Article 1: {'Duplicate' if result1['is_duplicate'] else 'Unique'}")
        
        if not result1['is_duplicate']:
            detector.add_article(test_articles[0])
        
        # Test second article (should be duplicate)
        result2 = detector.is_duplicate(test_articles[1])
        print(f"   Article 2: {'Duplicate' if result2['is_duplicate'] else 'Unique'} ({result2['method']})")
        
        # Test third article (should not be duplicate)
        result3 = detector.is_duplicate(test_articles[2])
        print(f"   Article 3: {'Duplicate' if result3['is_duplicate'] else 'Unique'}")
        
        if result2['is_duplicate'] and not result1['is_duplicate'] and not result3['is_duplicate']:
            print("✅ Duplicate detection working correctly")
        else:
            print("❌ Duplicate detection not working as expected")
            return False
        
    except Exception as e:
        print(f"❌ Duplicate detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("🎉 All tests passed! Enhanced duplicate detection is properly integrated.")
    print()
    print("📝 Summary:")
    print("   ✅ EnhancedDuplicateDetector class is working")
    print("   ✅ MultiSourceScraper has enhanced duplicate detection")
    print("   ✅ Duplicate detection functionality is working")
    print("   ✅ Integration is complete and ready for use")
    
    return True

if __name__ == "__main__":
    success = verify_enhanced_duplicate_integration()
    sys.exit(0 if success else 1)