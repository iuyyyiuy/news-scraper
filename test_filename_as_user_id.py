#!/usr/bin/env python3
"""
Test that CSV filename is used as user ID in trading strategy analysis
"""

import requests
import pandas as pd
import io
from datetime import datetime

def test_filename_as_user_id():
    """Test that the CSV filename becomes the user ID"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Filename as User ID")
    print("=" * 50)
    
    # Test 1: Create sample data with a specific filename
    print("\n1. Creating sample trading data...")
    sample_data = create_sample_data()
    print(f"✅ Created {len(sample_data)} sample records")
    
    # Test 2: Upload with specific filename
    test_filename = "trader_john_doe.csv"
    print(f"\n2. Testing upload with filename: {test_filename}")
    
    try:
        # Convert to CSV
        csv_buffer = io.StringIO()
        sample_data.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()
        
        # Upload via API with specific filename
        files = {'file': (test_filename, csv_content, 'text/csv')}
        response = requests.post(f"{base_url}/api/trading-strategy/upload-csv", files=files)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ Upload successful: {result['records_imported']} records imported")
                print(f"   Message: {result['message']}")
                
                # Check if the message contains the expected user ID
                expected_user_id = test_filename.replace('.csv', '')
                if expected_user_id in result['message']:
                    print(f"✅ Filename correctly used as user ID: {expected_user_id}")
                else:
                    print(f"❌ User ID not found in message. Expected: {expected_user_id}")
            else:
                print(f"❌ Upload failed: {result['message']}")
                return False
        else:
            print(f"❌ Upload request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error uploading CSV: {e}")
        return False
    
    # Test 3: Verify user ID in data summary
    print(f"\n3. Verifying user ID in data summary...")
    try:
        response = requests.get(f"{base_url}/api/trading-strategy/data-summary")
        if response.status_code == 200:
            summary = response.json()
            if summary['success']:
                print("✅ Data summary retrieved successfully")
                
                # Check top performers for the correct user ID
                if summary.get('top_performers'):
                    top_performer = summary['top_performers'][0]
                    actual_user_id = top_performer['user_id']
                    expected_user_id = test_filename.replace('.csv', '')
                    
                    if actual_user_id == expected_user_id:
                        print(f"✅ User ID correctly set: {actual_user_id}")
                        print(f"   Total PnL: ${top_performer['total_pnl']:.2f}")
                        print(f"   Win Rate: {top_performer['win_rate']:.1f}%")
                    else:
                        print(f"❌ User ID mismatch. Expected: {expected_user_id}, Got: {actual_user_id}")
                        return False
                else:
                    print("❌ No top performers found in summary")
                    return False
            else:
                print("❌ Failed to get data summary")
                return False
        else:
            print(f"❌ Data summary request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting data summary: {e}")
        return False
    
    # Test 4: Test with another filename
    print(f"\n4. Testing with different filename...")
    test_filename2 = "2282678.csv"  # Your actual file
    
    try:
        files = {'file': (test_filename2, csv_content, 'text/csv')}
        response = requests.post(f"{base_url}/api/trading-strategy/upload-csv", files=files)
        
        if response.status_code == 200:
            result = response.json()
            expected_user_id2 = test_filename2.replace('.csv', '')
            if expected_user_id2 in result['message']:
                print(f"✅ Second filename test passed: {expected_user_id2}")
            else:
                print(f"❌ Second filename test failed")
        else:
            print(f"❌ Second upload failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in second test: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Filename as User ID Test Complete!")
    
    return True

def create_sample_data():
    """Create sample trading data"""
    
    records = [
        {
            "开仓时间": "2025-12-18 20:07:45",
            "平仓时间": "2025-12-18 21:44:39", 
            "合约": "BTCUSDT",
            "类型": "空仓",
            "开仓均价": 84998,
            "进入价格": 84998,
            "离开价格": 85371,
            "平仓类型": "一键平仓",
            "历史最高数量": 5.7622,
            "历史最高价值": 489775.4756,
            "已实现盈亏": -2541.980701,
            "手续费": 392.6801007,
            "资金费用": 0
        },
        {
            "开仓时间": "2025-12-18 19:36:03",
            "平仓时间": "2025-12-18 19:45:34",
            "合约": "BTCUSDT", 
            "类型": "多仓",
            "开仓均价": 85481,
            "进入价格": 85481,
            "离开价格": 84702,
            "平仓类型": "一键平仓",
            "历史最高数量": 2.8616,
            "历史最高价值": 244612.4296,
            "已实现盈亏": -2375.50802,
            "手续费": 146.3216205,
            "资金费用": 0
        },
        {
            "开仓时间": "2025-12-16 20:01:42",
            "平仓时间": "2025-12-17 15:18:47",
            "合约": "ETHUSDT",
            "类型": "多仓",
            "开仓均价": 2949.11,
            "进入价格": 2949.11,
            "离开价格": 3019.82,
            "平仓类型": "一键平仓",
            "历史最高数量": 135.137,
            "历史最高价值": 398533.8781,
            "已实现盈亏": 9195.383669,
            "手续费": 322.6493174,
            "资金费用": -37.50428376
        }
    ]
    
    return pd.DataFrame(records)

if __name__ == "__main__":
    test_filename_as_user_id()