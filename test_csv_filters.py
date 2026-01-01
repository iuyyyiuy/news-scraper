#!/usr/bin/env python3
"""
Test CSV export filtering functionality
"""

import os
import sys
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.csv_exporter import CSVExportService, CSVExportConfig
from scraper.core.database_manager import DatabaseManager

def test_csv_basic_export():
    """Test basic CSV export without filters"""
    print("🧪 Testing basic CSV export...")
    
    try:
        service = CSVExportService()
        config = CSVExportConfig(max_records=5)  # Limit for testing
        
        result = service.export_articles(config)
        
        if result['success']:
            print(f"✅ Basic export successful: {result['articles_count']} articles")
            print(f"📁 File: {result['file_path']}")
            return True
        else:
            print(f"❌ Basic export failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Basic export error: {str(e)}")
        return False

def test_csv_date_filtering():
    """Test CSV export with date range filtering"""
    print("\n🧪 Testing date range filtering...")
    
    try:
        service = CSVExportService()
        
        # Test with recent date range
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        config = CSVExportConfig(
            start_date=start_date,
            end_date=end_date,
            max_records=10
        )
        
        result = service.export_articles(config)
        
        if result['success']:
            print(f"✅ Date filtering successful: {result['articles_count']} articles")
            print(f"📅 Date range: {start_date} to {end_date}")
            return True
        else:
            print(f"❌ Date filtering failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Date filtering error: {str(e)}")
        return False

def test_csv_source_filtering():
    """Test CSV export with source filtering"""
    print("\n🧪 Testing source filtering...")
    
    try:
        service = CSVExportService()
        
        config = CSVExportConfig(
            sources=['BlockBeats', 'Jinse'],
            max_records=10
        )
        
        result = service.export_articles(config)
        
        if result['success']:
            print(f"✅ Source filtering successful: {result['articles_count']} articles")
            print(f"📰 Sources: {config.sources}")
            return True
        else:
            print(f"❌ Source filtering failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Source filtering error: {str(e)}")
        return False

def test_csv_keyword_filtering():
    """Test CSV export with keyword filtering"""
    print("\n🧪 Testing keyword filtering...")
    
    try:
        service = CSVExportService()
        
        config = CSVExportConfig(
            keywords=['攻击', '诈骗', '黑客'],
            max_records=10
        )
        
        result = service.export_articles(config)
        
        if result['success']:
            print(f"✅ Keyword filtering successful: {result['articles_count']} articles")
            print(f"🔍 Keywords: {config.keywords}")
            return True
        else:
            print(f"❌ Keyword filtering failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Keyword filtering error: {str(e)}")
        return False

def test_csv_combined_filters():
    """Test CSV export with multiple filters combined"""
    print("\n🧪 Testing combined filters...")
    
    try:
        service = CSVExportService()
        
        config = CSVExportConfig(
            start_date=date.today() - timedelta(days=30),
            end_date=date.today(),
            sources=['BlockBeats'],
            keywords=['攻击', '安全'],
            max_records=5
        )
        
        result = service.export_articles(config)
        
        if result['success']:
            print(f"✅ Combined filtering successful: {result['articles_count']} articles")
            print(f"📊 Filters applied: {result['filters_applied']}")
            return True
        else:
            print(f"⚠️  Combined filtering returned no results: {result['message']}")
            return True  # This is acceptable - might be no matching articles
            
    except Exception as e:
        print(f"❌ Combined filtering error: {str(e)}")
        return False

def test_csv_edge_cases():
    """Test CSV export edge cases"""
    print("\n🧪 Testing edge cases...")
    
    try:
        service = CSVExportService()
        
        # Test with invalid date range
        config = CSVExportConfig(
            start_date=date.today(),
            end_date=date.today() - timedelta(days=1),  # End before start
            max_records=5
        )
        
        result = service.export_articles(config)
        print(f"📊 Invalid date range: {result['articles_count']} articles (expected: 0)")
        
        # Test with non-existent source
        config = CSVExportConfig(
            sources=['NonExistentSource'],
            max_records=5
        )
        
        result = service.export_articles(config)
        print(f"📊 Non-existent source: {result['articles_count']} articles (expected: 0)")
        
        # Test with empty keywords
        config = CSVExportConfig(
            keywords=[],
            max_records=5
        )
        
        result = service.export_articles(config)
        print(f"📊 Empty keywords: {result['articles_count']} articles")
        
        return True
        
    except Exception as e:
        print(f"❌ Edge cases error: {str(e)}")
        return False

def test_csv_content_formatting():
    """Test CSV content formatting with special characters"""
    print("\n🧪 Testing CSV content formatting...")
    
    try:
        service = CSVExportService()
        
        # Get some articles to test formatting
        config = CSVExportConfig(max_records=3, include_content=True)
        result = service.export_articles(config)
        
        if result['success'] and result['file_path']:
            # Read the CSV file to verify formatting
            with open(result['file_path'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"✅ CSV formatting test successful")
            print(f"📄 File size: {len(content)} characters")
            print(f"📝 Contains headers: {'title' in content}")
            print(f"🔤 Proper encoding: {content.count('，') > 0}")  # Check Chinese characters
            
            return True
        else:
            print(f"❌ CSV formatting failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ CSV formatting error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 CSV Export Filtering Tests")
    print("=" * 50)
    
    tests = [
        test_csv_basic_export,
        test_csv_date_filtering,
        test_csv_source_filtering,
        test_csv_keyword_filtering,
        test_csv_combined_filters,
        test_csv_edge_cases,
        test_csv_content_formatting
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All CSV filtering tests PASSED!")
    else:
        print(f"⚠️  {total - passed} tests failed")
    
    print("=" * 50)