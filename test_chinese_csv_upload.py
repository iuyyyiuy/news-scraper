#!/usr/bin/env python3
"""
Test Chinese CSV Format Upload
Tests the trading strategy system with the actual Chinese CSV format
"""

import requests
import pandas as pd
import io
from datetime import datetime, timedelta

def test_chinese_csv_upload():
    """Test uploading the actual Chinese CSV format"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Chinese CSV Format Upload")
    print("=" * 50)
    
    # Test 1: Create sample Chinese CSV data
    print("\n1. Creating sample Chinese CSV data...")
    sample_data = create_chinese_sample_data()
    print(f"✅ Created {len(sample_data)} sample records")
    
    # Test 2: Upload Chinese CSV
    print("\n2. Testing Chinese CSV upload...")
    try:
        # Convert to CSV
        csv_buffer = io.StringIO()
        sample_data.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()
        
        print("📄 Sample CSV content:")
        print(csv_content[:500] + "..." if len(csv_content) > 500 else csv_content)
        
        # Upload via API
        files = {'file': ('chinese_trading_data.csv', csv_content, 'text/csv')}
        response = requests.post(f"{base_url}/api/trading-strategy/upload-csv", files=files)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ Chinese CSV upload successful: {result['records_imported']} records imported")
                print(f"   Message: {result['message']}")
            else:
                print(f"❌ Upload failed: {result['message']}")
                return False
        else:
            print(f"❌ Upload request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error uploading Chinese CSV: {e}")
        return False
    
    # Test 3: Check data summary
    print("\n3. Testing data summary after Chinese upload...")
    try:
        response = requests.get(f"{base_url}/api/trading-strategy/data-summary")
        if response.status_code == 200:
            summary = response.json()
            if summary['success']:
                print("✅ Data summary retrieved successfully")
                print(f"   - Total trades: {summary['summary']['total_trades']}")
                print(f"   - Unique traders: {summary['summary']['unique_traders']}")
                print(f"   - Win rate: {summary['summary']['win_rate']}%")
                print(f"   - Average PnL: ${summary['summary']['avg_pnl']}")
                
                # Show top performers
                if summary.get('top_performers'):
                    print(f"   - Top performer: {summary['top_performers'][0]['user_id']} (${summary['top_performers'][0]['total_pnl']:.2f})")
            else:
                print("❌ Failed to get data summary")
                return False
        else:
            print(f"❌ Data summary request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting data summary: {e}")
        return False
    
    # Test 4: Test with actual file format
    print("\n4. Testing with actual 2282678.csv format...")
    try:
        # Read the actual file if it exists
        try:
            with open('2282678.csv', 'r', encoding='utf-8') as f:
                actual_csv_content = f.read()
            
            files = {'file': ('2282678.csv', actual_csv_content, 'text/csv')}
            response = requests.post(f"{base_url}/api/trading-strategy/upload-csv", files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"✅ Actual CSV upload successful: {result['records_imported']} records imported")
                else:
                    print(f"❌ Actual CSV upload failed: {result['message']}")
            else:
                print(f"❌ Actual CSV upload request failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except FileNotFoundError:
            print("⚠️  2282678.csv file not found, skipping actual file test")
    except Exception as e:
        print(f"❌ Error testing actual CSV: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Chinese CSV Format Test Complete!")
    
    return True

def create_chinese_sample_data():
    """Create sample data in Chinese CSV format"""
    
    # Sample data matching the Chinese format
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
            "开仓时间": "2025-12-18 16:49:03",
            "平仓时间": "2025-12-18 17:19:36",
            "合约": "ETHUSDT",
            "类型": "空仓", 
            "开仓均价": 2948.19,
            "进入价格": 2948.19,
            "离开价格": 2832.13,
            "平仓类型": "一键平仓",
            "历史最高数量": 50.275,
            "历史最高价值": 148220.2523,
            "已实现盈亏": 5776.795382,
            "手续费": 58.1211176,
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
        },
        {
            "开仓时间": "2025-12-15 17:48:14",
            "平仓时间": "2025-12-16 03:33:27",
            "合约": "BTCUSDT",
            "类型": "空仓",
            "开仓均价": 85885,
            "进入价格": 85885,
            "离开价格": 85538,
            "平仓类型": "止盈",
            "历史最高数量": 11.5298,
            "历史最高价值": 990236.873,
            "已实现盈亏": 3718.595243,
            "手续费": 790.5891622,
            "资金费用": 508.3438054
        },
        {
            "开仓时间": "2025-12-15 15:37:11",
            "平仓时间": "2025-12-15 16:51:30",
            "合约": "BTCUSDT",
            "类型": "空仓",
            "开仓均价": 86852,
            "进入价格": 86852,
            "离开价格": 86426,
            "平仓类型": "一键平仓",
            "历史最高数量": 14.6659,
            "历史最高价值": 1273762.747,
            "已实现盈亏": 5329.852229,
            "手续费": 1016.511128,
            "资金费用": 98.68995745
        }
    ]
    
    return pd.DataFrame(records)

if __name__ == "__main__":
    test_chinese_csv_upload()