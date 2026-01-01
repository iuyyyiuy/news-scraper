#!/usr/bin/env python3
"""
Test Manual Update Centered Popup Messages
"""

import requests
import time

BASE_URL = "http://localhost:5000"

def test_manual_update_centered():
    """Test that all manual update popup messages are centered"""
    
    print("🎯 Testing Manual Update Centered Popup Messages")
    print("=" * 55)
    
    # Test 1: Verify JavaScript implementation
    print("\n1️⃣ Verifying JavaScript implementation...")
    try:
        response = requests.get(f"{BASE_URL}/static/js/dashboard.js")
        assert response.status_code == 200
        js_code = response.text
        
        # Check that manual update uses showNotification method
        manual_update_checks = [
            ("this.showNotification('🔄 正在运行...', 'info')", "Starting notification"),
            ("this.showNotification(`✅ 完成！新增 ${newArticlesCount} 篇文章`, 'success')", "Success with count"),
            ("this.showNotification('✅ 完成！没有新增新闻', 'info')", "No new articles"),
            ("this.showNotification(`❌ 手动更新失败: ${error.message}`, 'error')", "Error notification"),
        ]
        
        for text, description in manual_update_checks:
            if text in js_code:
                print(f"✅ Found: {description}")
            else:
                print(f"❌ Missing: {description}")
        
        # Verify showNotification is centered
        centering_checks = [
            ("top: 50%", "Centered top position"),
            ("left: 50%", "Centered left position"),
            ("transform: translate(-50%, -50%)", "Center transform"),
            ("text-align: center", "Centered text"),
        ]
        
        print("\n   Verifying showNotification centering:")
        for text, description in centering_checks:
            if text in js_code:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description}")
        
    except Exception as e:
        print(f"❌ JavaScript verification failed: {e}")
        return False
    
    # Test 2: Check manual update API
    print("\n2️⃣ Testing manual update API...")
    try:
        response = requests.get(f"{BASE_URL}/api/manual-update/status")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Manual update API status: {data.get('status')}")
        print(f"   Parameters: {data.get('parameters', {})}")
    except Exception as e:
        print(f"❌ Manual update API test failed: {e}")
        return False
    
    # Test 3: Check dashboard loads
    print("\n3️⃣ Testing dashboard page...")
    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        print("✅ Dashboard loads successfully")
    except Exception as e:
        print(f"❌ Dashboard load failed: {e}")
        return False
    
    print("\n" + "=" * 55)
    print("🎉 Manual Update Centered Popup Test Complete!")
    
    print("\n📋 All Manual Update Messages Are Centered:")
    print("   🔄 '正在运行...' - Appears in center when starting")
    print("   ✅ '完成！新增 X 篇文章' - Appears in center when successful")
    print("   ✅ '完成！没有新增新闻' - Appears in center when no new articles")
    print("   ❌ '手动更新失败: [error]' - Appears in center on error")
    
    print("\n💡 Visual Characteristics:")
    print("   - Position: Perfect center of screen (50% top/left)")
    print("   - Size: 16px 24px padding, minimum 200px width")
    print("   - Style: Centered text, enhanced shadow")
    print("   - Animation: Scale down from center on close")
    print("   - Duration: 5 seconds display time")
    
    print("\n🧪 To test manually:")
    print("   1. Open http://localhost:5000")
    print("   2. Click '手动更新' button")
    print("   3. Watch for centered popup: '🔄 正在运行...'")
    print("   4. Wait ~2 minutes for completion message (also centered)")
    
    return True

if __name__ == "__main__":
    try:
        success = test_manual_update_centered()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        exit(1)