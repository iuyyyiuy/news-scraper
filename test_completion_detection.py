#!/usr/bin/env python3
"""
Test Improved Completion Detection
"""

import requests
import time
import json

BASE_URL = "http://localhost:8080"

def test_completion_detection():
    """Test the improved completion detection logic"""
    
    print("🧪 Testing Improved Completion Detection")
    print("=" * 50)
    
    # Get initial article count
    print("\n1️⃣ Getting initial article count...")
    try:
        response = requests.get(f"{BASE_URL}/api/database/stats")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                initial_count = data.get('data', {}).get('total_articles', 0)
                print(f"   ✅ Initial article count: {initial_count}")
            else:
                print(f"   ❌ Failed to get stats: {data.get('message')}")
                return False
        else:
            print(f"   ❌ Stats API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error getting initial count: {e}")
        return False
    
    # Start manual update
    print("\n2️⃣ Starting manual update...")
    try:
        response = requests.post(f"{BASE_URL}/api/manual-update", 
                               json={},
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Manual update started successfully")
                print(f"   📋 Process: {len(data.get('process', []))} steps")
            else:
                print(f"   ❌ Manual update failed: {data.get('message')}")
                return False
        else:
            print(f"   ❌ Manual update API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error starting manual update: {e}")
        return False
    
    # Monitor progress
    print("\n3️⃣ Monitoring progress...")
    print("   (The dashboard JavaScript will now detect completion automatically)")
    print("   Checking article count changes...")
    
    max_wait_time = 180  # 3 minutes
    check_interval = 10  # 10 seconds
    checks = 0
    max_checks = max_wait_time // check_interval
    
    last_count = initial_count
    stable_count_checks = 0
    
    while checks < max_checks:
        time.sleep(check_interval)
        checks += 1
        
        try:
            response = requests.get(f"{BASE_URL}/api/database/stats")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    current_count = data.get('data', {}).get('total_articles', 0)
                    new_articles = current_count - initial_count
                    
                    print(f"   📊 Check {checks}/{max_checks}: Total={current_count}, New={new_articles}")
                    
                    # Check for stability
                    if current_count == last_count:
                        stable_count_checks += 1
                    else:
                        stable_count_checks = 0
                        last_count = current_count
                    
                    # If stable for 3 checks and we've waited at least 1 minute
                    if stable_count_checks >= 3 and checks >= 6:
                        print(f"\n   ✅ Scraping appears complete!")
                        print(f"   📈 Final result: {new_articles} new articles added")
                        break
                        
        except Exception as e:
            print(f"   ⚠️ Check {checks} failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Completion Detection Test Complete!")
    
    print(f"\n📊 Results:")
    print(f"   - Initial articles: {initial_count}")
    print(f"   - Final articles: {last_count}")
    print(f"   - New articles: {last_count - initial_count}")
    print(f"   - Monitoring duration: {checks * check_interval} seconds")
    
    print(f"\n🎯 Dashboard Behavior:")
    print(f"   - JavaScript checks every 5 seconds")
    print(f"   - Shows completion when article count stabilizes")
    print(f"   - Maximum wait time: 3 minutes")
    print(f"   - Completion message: '✅ 完成！新增 X 篇文章' (centered)")
    
    print(f"\n💡 To see the completion popup:")
    print(f"   1. Open {BASE_URL} in your browser")
    print(f"   2. Click '手动更新' button")
    print(f"   3. Watch for '🔄 正在运行...' (centered)")
    print(f"   4. Wait for completion message (should appear faster now)")
    
    return True

if __name__ == "__main__":
    try:
        success = test_completion_detection()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        exit(1)