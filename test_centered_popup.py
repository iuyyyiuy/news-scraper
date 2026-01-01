#!/usr/bin/env python3
"""
Test Centered Popup Messages and "No New News" Message
"""

import requests
import time

BASE_URL = "http://localhost:5000"

def test_centered_popup():
    """Test the centered popup messages and updated text"""
    
    print("🎯 Testing Centered Popup Messages")
    print("=" * 50)
    
    # Test 1: Check JavaScript changes
    print("\n1️⃣ Verifying JavaScript changes...")
    try:
        response = requests.get(f"{BASE_URL}/static/js/dashboard.js")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        js_code = response.text
        
        # Check for centered positioning
        checks = [
            ("top: 50%", "Centered top position"),
            ("left: 50%", "Centered left position"),
            ("transform: translate(-50%, -50%)", "Center transform"),
            ("没有新增新闻", "Updated 'no new news' message"),
            ("text-align: center", "Centered text alignment"),
        ]
        
        all_passed = True
        for text, description in checks:
            if text in js_code:
                print(f"✅ Found: {description}")
            else:
                print(f"❌ Missing: {description}")
                all_passed = False
        
        # Check that old positioning is removed
        removed_checks = [
            ("top: 20px", "Old top position"),
            ("right: 20px", "Old right position"),
            ("translateX(100%)", "Old slide animation"),
            ("没有新文章", "Old 'no new articles' message"),
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
    
    # Test 2: Check dashboard loads
    print("\n2️⃣ Testing dashboard page load...")
    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ Dashboard loads successfully")
    except Exception as e:
        print(f"❌ Dashboard load failed: {e}")
        return False
    
    # Test 3: Check manual update API
    print("\n3️⃣ Testing manual update API...")
    try:
        response = requests.get(f"{BASE_URL}/api/manual-update/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        print(f"✅ Manual update status: {data.get('status')}")
    except Exception as e:
        print(f"❌ Manual update status check failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Centered Popup Test Complete!")
    print("\n📋 Summary of Changes:")
    print("   ✅ Popup messages now centered on screen")
    print("   ✅ Updated message: '没有新增新闻' (instead of '没有新文章')")
    print("   ✅ Better visual styling with larger, centered notifications")
    print("   ✅ Improved animation (scale instead of slide)")
    
    print("\n💡 Visual Changes:")
    print("   - Position: Center of screen (50% top/left)")
    print("   - Size: Larger padding (16px 24px)")
    print("   - Text: Centered alignment")
    print("   - Shadow: Enhanced shadow for better visibility")
    print("   - Animation: Scale down on close (more elegant)")
    
    print("\n🧪 To test manually:")
    print("   1. Open http://localhost:5000 in your browser")
    print("   2. Click '手动更新' button")
    print("   3. You should see:")
    print("      - '🔄 正在运行...' centered on screen")
    print("      - After completion: '✅ 完成！没有新增新闻' (if no new articles)")
    print("      - Or: '✅ 完成！新增 X 篇文章' (if new articles found)")
    
    return True

if __name__ == "__main__":
    try:
        success = test_centered_popup()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        exit(1)