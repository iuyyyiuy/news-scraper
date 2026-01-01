#!/usr/bin/env python3
"""
Test CSV Export API Endpoints
"""

import requests
import time
import json
from datetime import date, timedelta

# API base URL
BASE_URL = "http://localhost:8000"

def test_csv_export_basic():
    """Test basic CSV export"""
    print("🧪 Testing basic CSV export...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/export/csv",
            json={
                "max_records": 5,
                "include_content": True
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Basic export successful")
            print(f"   File ID: {data['file_id']}")
            print(f"   Articles: {data['articles_count']}")
            print(f"   Download URL: {data['download_url']}")
            return data['file_id']
        else:
            print(f"❌ Basic export failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Server not running")
        print("   Start server with: python start_dashboard.py")
        return None
    except Exception as e:
        print(f"❌ Basic export error: {str(e)}")
        return None

def test_csv_export_with_filters():
    """Test CSV export with filters"""
    print("\n🧪 Testing CSV export with filters...")
    
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        response = requests.post(
            f"{BASE_URL}/api/export/csv",
            json={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "sources": ["BlockBeats"],
                "keywords": ["攻击", "安全"],
                "max_records": 10,
                "include_content": True
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Filtered export successful")
            print(f"   File ID: {data['file_id']}")
            print(f"   Articles: {data['articles_count']}")
            print(f"   Filters: {data.get('filters_applied', {})}")
            return data['file_id']
        else:
            print(f"❌ Filtered export failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Server not running")
        return None
    except Exception as e:
        print(f"❌ Filtered export error: {str(e)}")
        return None

def test_csv_download(file_id):
    """Test CSV file download"""
    print(f"\n🧪 Testing CSV download for file: {file_id}...")
    
    if not file_id:
        print("⏭️  Skipping download test (no file_id)")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/export/download/{file_id}")
        
        if response.status_code == 200:
            content = response.text
            print(f"✅ Download successful")
            print(f"   Content length: {len(content)} characters")
            print(f"   First line: {content.split(chr(10))[0][:80]}...")
            
            # Verify CSV structure
            lines = content.split('\n')
            if len(lines) > 1 and 'title' in lines[0]:
                print(f"✅ CSV structure valid")
                return True
            else:
                print(f"❌ CSV structure invalid")
                return False
        else:
            print(f"❌ Download failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Download error: {str(e)}")
        return False

def test_csv_status(file_id):
    """Test CSV export status"""
    print(f"\n🧪 Testing export status for file: {file_id}...")
    
    if not file_id:
        print("⏭️  Skipping status test (no file_id)")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/export/csv/status/{file_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status check successful")
            print(f"   Status: {data['status']}")
            print(f"   Message: {data['message']}")
            print(f"   Articles: {data['articles_count']}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Status check error: {str(e)}")
        return False

def test_csv_list():
    """Test listing all exports"""
    print("\n🧪 Testing export list...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/export/csv/list")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ List exports successful")
            print(f"   Total exports: {data['total_count']}")
            
            if data['exports']:
                print(f"   Recent exports:")
                for export in data['exports'][:3]:
                    print(f"     - {export['file_id']}: {export['status']} ({export['articles_count']} articles)")
            
            return True
        else:
            print(f"❌ List exports failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ List exports error: {str(e)}")
        return False

def test_csv_validation():
    """Test API validation"""
    print("\n🧪 Testing API validation...")
    
    try:
        # Test invalid date format
        response = requests.post(
            f"{BASE_URL}/api/export/csv",
            json={
                "start_date": "invalid-date",
                "max_records": 5
            }
        )
        
        if response.status_code == 400 or response.status_code == 422:
            print(f"✅ Invalid date validation working")
        else:
            print(f"❌ Invalid date validation not working")
            return False
        
        # Test invalid source
        response = requests.post(
            f"{BASE_URL}/api/export/csv",
            json={
                "sources": ["InvalidSource"],
                "max_records": 5
            }
        )
        
        if response.status_code == 400 or response.status_code == 422:
            print(f"✅ Invalid source validation working")
        else:
            print(f"❌ Invalid source validation not working")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Validation test error: {str(e)}")
        return False

def test_health_check():
    """Test if server is running"""
    print("🔍 Checking server status...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"⚠️  Server responded with status: {response.status_code}")
            return True  # Server is running but might have issues
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        print("   Start server with: python start_dashboard.py")
        return False
    except Exception as e:
        print(f"⚠️  Health check error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 CSV Export API Tests")
    print("=" * 60)
    
    # Check if server is running
    if not test_health_check():
        print("\n" + "=" * 60)
        print("⚠️  Server not running. Please start the server first:")
        print("   python start_dashboard.py")
        print("=" * 60)
        exit(1)
    
    print("\n" + "=" * 60)
    
    # Run tests
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Basic export
    tests_total += 1
    file_id1 = test_csv_export_basic()
    if file_id1:
        tests_passed += 1
    
    # Test 2: Filtered export
    tests_total += 1
    file_id2 = test_csv_export_with_filters()
    if file_id2:
        tests_passed += 1
    
    # Test 3: Download
    tests_total += 1
    if test_csv_download(file_id1 or file_id2):
        tests_passed += 1
    
    # Test 4: Status
    tests_total += 1
    if test_csv_status(file_id1 or file_id2):
        tests_passed += 1
    
    # Test 5: List
    tests_total += 1
    if test_csv_list():
        tests_passed += 1
    
    # Test 6: Validation
    tests_total += 1
    if test_csv_validation():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("🎉 All CSV API tests PASSED!")
    else:
        print(f"⚠️  {tests_total - tests_passed} tests failed")
    
    print("=" * 60)