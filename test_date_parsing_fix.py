#!/usr/bin/env python3
"""
Test the date parsing fix to ensure 2025 dates are not converted to 2026.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.parser import HTMLParser
from datetime import datetime, date

def test_date_parsing_fix():
    """Test that date parsing correctly handles year assignment."""
    
    parser = HTMLParser()
    
    print("Testing date parsing fix...")
    print("=" * 60)
    
    # Test cases for Chinese date formats without year
    test_cases = [
        {
            'body_text': 'BlockBeats 消息，12 月 31 日，这是一个测试新闻',
            'expected_year': 2025,  # Should be 2025, not 2026
            'description': 'December 31st should be 2025 (not future 2026)'
        },
        {
            'body_text': 'BlockBeats 消息，1 月 2 日，这是一个测试新闻',
            'expected_year': 2026,  # Should be 2026 (current year)
            'description': 'January 2nd should be 2026 (current year)'
        },
        {
            'body_text': '12月30日消息，测试新闻内容',
            'expected_year': 2025,  # Should be 2025
            'description': 'December 30th without BlockBeats prefix should be 2025'
        },
        {
            'body_text': '1月5日消息，测试新闻内容',
            'expected_year': 2026,  # Should be 2026
            'description': 'January 5th without BlockBeats prefix should be 2026'
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases):
        print(f"\n[{i+1}] {test_case['description']}")
        print(f"Body text: {test_case['body_text']}")
        
        try:
            # Extract date from body text
            extracted_date = parser._extract_date_from_body(test_case['body_text'])
            
            if extracted_date:
                print(f"Extracted date: {extracted_date}")
                print(f"Expected year: {test_case['expected_year']}")
                print(f"Actual year: {extracted_date.year}")
                
                if extracted_date.year == test_case['expected_year']:
                    print("✅ CORRECT: Year assignment is correct!")
                    success_count += 1
                else:
                    print("❌ WRONG: Year assignment is incorrect!")
            else:
                print("❌ FAILED: No date extracted!")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print("-" * 40)
    
    print(f"\nRESULTS: {success_count}/{len(test_cases)} tests passed")
    
    if success_count == len(test_cases):
        print("🎉 ALL TESTS PASSED - Date parsing fix is working!")
        return True
    else:
        print("⚠️  Some tests failed - Date parsing needs more work")
        return False

def test_smart_year_logic():
    """Test the smart year determination logic directly."""
    
    parser = HTMLParser()
    
    print("\n" + "=" * 60)
    print("Testing smart year determination logic...")
    print("=" * 60)
    
    # Test cases for smart year logic
    test_cases = [
        {'month': 12, 'day': 31, 'expected': 2025, 'description': 'Dec 31 should be 2025'},
        {'month': 1, 'day': 1, 'expected': 2026, 'description': 'Jan 1 should be 2026'},
        {'month': 1, 'day': 15, 'expected': 2026, 'description': 'Jan 15 should be 2026'},
        {'month': 11, 'day': 30, 'expected': 2025, 'description': 'Nov 30 should be 2025'},
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases):
        print(f"\n[{i+1}] {test_case['description']}")
        
        try:
            result_year = parser._determine_smart_year(test_case['month'], test_case['day'])
            print(f"Month: {test_case['month']}, Day: {test_case['day']}")
            print(f"Expected year: {test_case['expected']}")
            print(f"Result year: {result_year}")
            
            if result_year == test_case['expected']:
                print("✅ CORRECT!")
                success_count += 1
            else:
                print("❌ WRONG!")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\nSmart year logic: {success_count}/{len(test_cases)} tests passed")
    return success_count == len(test_cases)

if __name__ == "__main__":
    success1 = test_date_parsing_fix()
    success2 = test_smart_year_logic()
    
    if success1 and success2:
        print("\n🎉 ALL DATE PARSING TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n⚠️  Some date parsing tests failed!")
        sys.exit(1)