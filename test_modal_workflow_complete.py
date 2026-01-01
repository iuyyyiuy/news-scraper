#!/usr/bin/env python3
"""
Complete Modal Workflow Test
Tests the complete workflow of the new modal-based article count selection.
"""

import requests
import time
import json

def test_complete_workflow():
    """Test the complete modal workflow"""
    print("🧪 Testing Complete Modal Workflow")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Test 1: Dashboard Access
    print("1️⃣ Testing dashboard access...")
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard accessible")
            
            # Check for modal elements
            html = response.text
            modal_checks = [
                ("manual-update-modal", "Manual update modal"),
                ("article-count-select", "Article count select"),
                ("showManualUpdateModal", "Show modal function"),
                ("closeManualUpdateModal", "Close modal function"),
                ("confirmManualUpdate", "Confirm update function")
            ]
            
            for element, description in modal_checks:
                if element in html:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} missing")
                    return False
        else:
            print(f"❌ Dashboard not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False
    
    # Test 2: Manual Update API with Different Article Counts
    print("\n2️⃣ Testing manual update API with different article counts...")
    test_counts = [100, 300, 500, 1000, 2000]
    
    for count in test_counts:
        try:
            print(f"   Testing {count} articles per source...")
            response = requests.post(
                f"{base_url}/api/manual-update",
                json={"max_articles": count},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    params = result.get("parameters", {})
                    actual_count = params.get("max_articles_per_source")
                    if actual_count == count:
                        print(f"   ✅ {count} articles - API accepts and processes correctly")
                    else:
                        print(f"   ❌ {count} articles - Expected {count}, got {actual_count}")
                        return False
                else:
                    print(f"   ❌ {count} articles - API error: {result.get('message')}")
                    return False
            else:
                print(f"   ❌ {count} articles - HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ {count} articles - Request failed: {e}")
            return False
    
    # Test 3: Check JavaScript Functions
    print("\n3️⃣ Testing JavaScript implementation...")
    try:
        response = requests.get(f"{base_url}/static/js/dashboard.js", timeout=5)
        if response.status_code == 200:
            js_content = response.text
            
            js_checks = [
                ("showManualUpdateModal()", "Show modal method"),
                ("closeManualUpdateModal()", "Close modal method"),
                ("confirmManualUpdate()", "Confirm update method"),
                ("startManualUpdate(maxArticles", "Updated startManualUpdate method"),
                ("getElementById('article-count-select')", "Article count select access"),
                ("parseInt(articleCountSelect.value)", "Article count parsing")
            ]
            
            for check, description in js_checks:
                if check in js_content:
                    print(f"   ✅ {description} implemented")
                else:
                    print(f"   ❌ {description} missing")
                    return False
        else:
            print(f"   ❌ JavaScript file not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ JavaScript test failed: {e}")
        return False
    
    # Test 4: Verify Old Dropdown Removal
    print("\n4️⃣ Verifying old dropdown removal...")
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=5)
        html = response.text
        
        # Check that old filter dropdown is NOT present
        old_elements = [
            ('id="article-count-filter"', "Old article count filter"),
            ('label>抓取数量:', "Old article count label in filter section")
        ]
        
        for element, description in old_elements:
            if element in html:
                print(f"   ❌ {description} still present (should be removed)")
                return False
            else:
                print(f"   ✅ {description} successfully removed")
                
    except Exception as e:
        print(f"   ❌ Dropdown removal test failed: {e}")
        return False
    
    print("\n✅ All tests passed!")
    print("\n📋 Manual Testing Instructions:")
    print("=" * 50)
    print("1. Open http://localhost:8080/dashboard in your browser")
    print("2. Verify that there is NO article count dropdown in the filter section")
    print("3. Click the '手动更新' button")
    print("4. Verify that a modal appears with:")
    print("   - Title: '手动更新设置'")
    print("   - Dropdown with options: 100, 300, 500, 1000, 2000 articles")
    print("   - Default selection: 500 articles")
    print("   - Cancel and Start Update buttons")
    print("5. Select different article counts and click 'Start Update'")
    print("6. Verify that the modal closes and manual update starts")
    print("7. Check that the progress notification shows the selected count")
    
    return True

if __name__ == "__main__":
    success = test_complete_workflow()
    if success:
        print("\n🎉 Implementation completed successfully!")
    else:
        print("\n❌ Implementation has issues that need to be fixed.")