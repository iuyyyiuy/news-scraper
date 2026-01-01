#!/usr/bin/env python3
"""
Test CSV formatting with special characters (RFC 4180 compliance)
"""

import os
import sys
import csv
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.csv_exporter import CSVExportService

def test_special_characters_formatting():
    """Test CSV formatting with quotes, commas, newlines"""
    print("🧪 Testing CSV formatting with special characters...")
    
    # Create test articles with special characters
    test_articles = [
        {
            'id': 1,
            'title': 'Article with "quotes" and, commas',
            'body_text': 'Content with\nmultiple\nlines and "quotes"',
            'source': 'TestSource',
            'matched_keywords': ['test', 'special'],
            'url': 'https://example.com/test1',
            'date': '2025/12/20',
            'scraped_at': '2025-12-20T10:00:00'
        },
        {
            'id': 2,
            'title': 'Article with emoji 🚀 and unicode 中文',
            'body_text': 'Multi-line content:\n- Point 1\n- Point 2\n"Quoted text"',
            'source': 'TestSource',
            'matched_keywords': ['emoji', '中文'],
            'url': 'https://example.com/test2',
            'date': '2025/12/20',
            'scraped_at': '2025-12-20T10:01:00'
        },
        {
            'id': 3,
            'title': 'Article, with, many, commas',
            'body_text': 'Content with "nested quotes" and \'single quotes\' and more commas, here, and, there',
            'source': 'TestSource',
            'matched_keywords': ['commas'],
            'url': 'https://example.com/test3',
            'date': '2025/12/20',
            'scraped_at': '2025-12-20T10:02:00'
        }
    ]
    
    try:
        service = CSVExportService()
        
        # Test with content included
        csv_content = service.format_csv(test_articles, include_content=True)
        
        print("✅ CSV formatting completed")
        print(f"📄 Content length: {len(csv_content)} characters")
        
        # Verify CSV can be parsed back correctly
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        parsed_rows = list(csv_reader)
        
        print(f"📊 Parsed {len(parsed_rows)} rows")
        
        # Test specific formatting cases
        success = True
        
        # Test 1: Quotes in title should be escaped
        row1 = parsed_rows[0]
        if 'quotes' in row1['title'] and '"' in row1['title']:
            print("✅ Quotes in title properly handled")
        else:
            print("❌ Quotes in title not properly handled")
            success = False
        
        # Test 2: Multi-line content should be preserved
        if '\n' in row1['content']:
            print("✅ Multi-line content preserved")
        else:
            print("❌ Multi-line content not preserved")
            success = False
        
        # Test 3: Unicode characters should be preserved
        row2 = parsed_rows[1]
        if '🚀' in row2['title'] and '中文' in row2['title']:
            print("✅ Unicode characters preserved")
        else:
            print("❌ Unicode characters not preserved")
            success = False
        
        # Test 4: Commas in content should not break CSV structure
        if len(parsed_rows) == 3:  # Should have exactly 3 rows
            print("✅ Commas properly escaped - CSV structure intact")
        else:
            print(f"❌ CSV structure broken - got {len(parsed_rows)} rows instead of 3")
            success = False
        
        # Test 5: Keywords array should be properly formatted
        if ',' in row1['keywords']:  # Keywords should be comma-separated
            print("✅ Keywords array properly formatted")
        else:
            print("❌ Keywords array not properly formatted")
            success = False
        
        return success
        
    except Exception as e:
        print(f"❌ Special characters test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_rfc4180_compliance():
    """Test RFC 4180 compliance specifically"""
    print("\n🧪 Testing RFC 4180 compliance...")
    
    # Test edge cases for RFC 4180
    test_articles = [
        {
            'id': 1,
            'title': 'Field with "quotes" inside',
            'body_text': 'Field with\r\nCRLF line endings',
            'source': 'Test',
            'matched_keywords': [],
            'url': 'https://test.com',
            'date': '2025/12/20',
            'scraped_at': '2025-12-20T10:00:00'
        },
        {
            'id': 2,
            'title': 'Field with ""double quotes""',
            'body_text': 'Field ending with quote"',
            'source': 'Test',
            'matched_keywords': [],
            'url': 'https://test.com',
            'date': '2025/12/20',
            'scraped_at': '2025-12-20T10:00:00'
        }
    ]
    
    try:
        service = CSVExportService()
        csv_content = service.format_csv(test_articles, include_content=True)
        
        # Parse with standard CSV reader
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)
        
        if len(rows) == 2:
            print("✅ RFC 4180 compliance test passed")
            print(f"📝 Row 1 title: {rows[0]['title']}")
            print(f"📝 Row 2 title: {rows[1]['title']}")
            return True
        else:
            print(f"❌ RFC 4180 compliance failed - got {len(rows)} rows")
            return False
            
    except Exception as e:
        print(f"❌ RFC 4180 compliance error: {str(e)}")
        return False

def test_csv_without_content():
    """Test CSV export without content field"""
    print("\n🧪 Testing CSV export without content...")
    
    test_articles = [
        {
            'id': 1,
            'title': 'Test Article',
            'body_text': 'This content should not appear in CSV',
            'source': 'Test',
            'matched_keywords': ['test'],
            'url': 'https://test.com',
            'date': '2025/12/20',
            'scraped_at': '2025-12-20T10:00:00'
        }
    ]
    
    try:
        service = CSVExportService()
        csv_content = service.format_csv(test_articles, include_content=False)
        
        # Check that content column is not present
        lines = csv_content.split('\n')
        header = lines[0]
        
        if 'content' not in header:
            print("✅ Content column excluded when include_content=False")
            return True
        else:
            print("❌ Content column present when include_content=False")
            return False
            
    except Exception as e:
        print(f"❌ CSV without content error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 CSV Special Characters and RFC 4180 Tests")
    print("=" * 60)
    
    tests = [
        test_special_characters_formatting,
        test_rfc4180_compliance,
        test_csv_without_content
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All CSV special character tests PASSED!")
    else:
        print(f"⚠️  {total - passed} tests failed")
    
    print("=" * 60)