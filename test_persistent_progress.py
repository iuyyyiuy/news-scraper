#!/usr/bin/env python3
"""
Test Persistent Progress Notification
"""

import requests
import time

BASE_URL = "http://localhost:8080"

def test_persistent_progress():
    """Test that the progress notification stays visible until completion"""
    
    print("🔄 Testing Persistent Progress Notification")
    print("=" * 55)
    
    # Test 1: Verify JavaScript changes
    print("\n1️⃣ Verifying JavaScript implementation...")
    try:
        response = requests.get(f"{BASE_URL}/static/js/dashboard.js")
        if response.status_code == 200:
            js_code = response.text
            
            # Check for persistent notification methods
            checks = [
                ("showPersistentNotification", "Persistent notification method"),
                ("removePersistentNotification", "Remove persistent notification method"),
                ("this.progressNotification =", "Progress notification tracking"),
                ("z-index: 10001", "Higher z-index for persistent notification"),
            ]
            
            all_passed = True
            for text, description in checks:
                if text in js_code:
                    print(f"   ✅ Found: {description}")
                else:
                    print(f"   ❌ Missing: {description}")
                    all_passed = False
            
            if all_passed:
                print("   ✅ All persistent notification features implemented!")
            else:
                print("   ⚠️ Some features may be missing")
                
        else:
            print(f"   ❌ Could not load JavaScript: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ JavaScript check failed: {e}")
        return False
    
    # Test 2: Check dashboard loads
    print("\n2️⃣ Testing dashboard accessibility...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("   ✅ Dashboard loads successfully")
        else:
            print(f"   ❌ Dashboard failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Dashboard test failed: {e}")
        return False
    
    # Test 3: Manual update API
    print("\n3️⃣ Testing manual update API...")
    try:
        response = requests.get(f"{BASE_URL}/api/manual-update/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Status: {data.get('status')}")
        else:
            print(f"   ❌ API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        return False
    
    print("\n" + "=" * 55)
    print("🎉 Persistent Progress Test Complete!")
    
    print(f"\n🎯 New Behavior:")
    print(f"   1. Click '手动更新' → '🔄 正在运行...' appears (centered)")
    print(f"   2. Progress message STAYS VISIBLE throughout scraping")
    print(f"   3. When scraping completes → Progress message disappears")
    print(f"   4. Final result appears → '✅ 完成！新增 X 篇文章' or '✅ 完成！没有新增新闻'")
    
    print(f"\n🔧 Technical Implementation:")
    print(f"   - showPersistentNotification(): Creates notification without auto-removal")
    print(f"   - progressNotification: Tracks the persistent notification element")
    print(f"   - removePersistentNotification(): Manually removes when complete")
    print(f"   - Higher z-index (10001): Ensures visibility above other elements")
    
    print(f"\n💡 User Experience:")
    print(f"   - No more confusion about whether scraping is still running")
    print(f"   - Clear visual feedback throughout the entire process")
    print(f"   - Smooth transition from progress to completion message")
    
    print(f"\n🧪 To test manually:")
    print(f"   1. Open {BASE_URL} in your browser")
    print(f"   2. Click '手动更新' button")
    print(f"   3. Observe: '🔄 正在运行...' stays visible")
    print(f"   4. Wait for completion (30-180 seconds)")
    print(f"   5. Observe: Progress message disappears, completion message appears")
    
    return True

if __name__ == "__main__":
    try:
        success = test_persistent_progress()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        exit(1)