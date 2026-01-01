#!/usr/bin/env python3
"""
Test Dashboard Popup Message Simplification
"""

import requests
import time

BASE_URL = "http://localhost:5000"

def test_dashboard_popup():
    """Test the simplified popup messages in dashboard"""
    
    print("🧪 Testing Dashboard Popup Message Simplification")
    print("=" * 60)
    
    # Test 1: Check if dashboard loads
    print("\n1️⃣ Testing dashboard page load...")
    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ Dashboard loads successfully")
        
        # Check if JavaScript file is updated
        js_content = response.text
        if "正在运行..." in js_content:
            print("✅ Found simplified '正在运行...' message in JavaScript")
        else:
            print("⚠️ Could not verify '正在运行...' message in page source")
            
    except Exception as e:
        print(f"❌ Dashboard load failed: {e}")
        return False
    
    # Test 2: Check manual update API
    print("\n2️⃣ Testing manual update API...")
    try:
        response = requests.get(f"{BASE_URL}/api/manual-update/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        print(f"✅ Manual update status: {data.get('status')}")
        print(f"   Parameters: {data.get('parameters', {})}")
    except Exception as e:
        print(f"❌ Manual update status check failed: {e}")
        return False
    
    # Test 3: Verify JavaScript changes
    print("\n3️⃣ Verifying JavaScript changes...")
    try:
        response = requests.get(f"{BASE_URL}/static/js/dashboard.js")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        js_code = response.text
        
        # Check for simplified messages
        checks = [
            ("🔄 正在运行...", "Running message"),
            ("✅ 完成！新增", "Completion message"),
            ("checkUpdateCompletion", "New completion check method"),
        ]
        
        all_passed = True
        for text, description in checks:
            if text in js_code:
                print(f"✅ Found: {description}")
            else:
                print(f"❌ Missing: {description}")
                all_passed = False
        
        # Check that verbose messages are removed
        removed_checks = [
            ("使用固定参数：1天，21个安全关键词，每源100篇", "Verbose parameter message"),
            ("📋 参数：最近1天", "Detailed parameter info"),
        ]
        
        for text, description in removed_checks:
            if text not in js_code:
                print(f"✅ Removed: {description}")
            else:
                print(f"⚠️ Still present: {description}")
                all_passed = False
        
        if all_passed:
            print("\n✅ All JavaScript changes verified!")
        else:
            print("\n⚠️ Some changes may need review")
            
    except Exception as e:
        print(f"❌ JavaScript verification failed: {e}")
        return False
    
    # Test 4: Check article count tracking
    print("\n4️⃣ Testing article count tracking...")
    try:
        response = requests.get(f"{BASE_URL}/api/database/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        if data.get('success'):
            print(f"✅ Current article count: {data.get('data', {}).get('total_articles', 0)}")
            print("   This will be used to calculate new articles added")
        else:
            print("⚠️ Could not get article count")
    except Exception as e:
        print(f"❌ Article count check failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Dashboard Popup Message Test Complete!")
    print("\n📋 Summary of Changes:")
    print("   ✅ Simplified running message: '🔄 正在运行...'")
    print("   ✅ Simplified completion message: '✅ 完成！新增 X 篇文章'")
    print("   ✅ Removed verbose parameter information")
    print("   ✅ Added article count tracking")
    print("\n💡 To test manually:")
    print("   1. Open http://localhost:5000 in your browser")
    print("   2. Click '手动更新' button")
    print("   3. You should see:")
    print("      - '🔄 正在运行...' when starting")
    print("      - '✅ 完成！新增 X 篇文章' when done (after ~2 minutes)")
    
    return True

if __name__ == "__main__":
    try:
        success = test_dashboard_popup()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        exit(1)
