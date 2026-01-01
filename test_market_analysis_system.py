#!/usr/bin/env python3
"""
Test Market Analysis System

Test the new market analysis functionality including:
1. MCP CoinEx integration
2. Market monitoring API
3. Manipulation detection algorithms
4. Real-time alert system
"""

import asyncio
import requests
import json
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_MARKETS = ["BTC", "ETH", "SOL"]

def test_api_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """Run market analysis system tests"""
    
    print("=" * 80)
    print("🔍 Market Analysis System Test")
    print("=" * 80)
    
    # Test 1: Check if web server is running
    print("\n1. Testing web server connectivity...")
    result = test_api_endpoint("/api/health")
    if result["success"]:
        print("✅ Web server is running")
        print(f"   Health status: {result['data']}")
    else:
        print("❌ Web server is not accessible")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        return False
    
    # Test 2: Test market analysis page
    print("\n2. Testing market analysis page...")
    result = test_api_endpoint("/market-analysis")
    if result["success"]:
        print("✅ Market analysis page is accessible")
    else:
        print("❌ Market analysis page failed")
        print(f"   Status: {result.get('status_code', 'Unknown')}")
    
    # Test 3: Get available markets
    print("\n3. Testing available markets API...")
    result = test_api_endpoint("/api/market-analysis/markets")
    if result["success"] and result["data"].get("success"):
        markets = result["data"].get("markets", [])
        print(f"✅ Found {len(markets)} available markets")
        for market in markets[:3]:  # Show first 3
            print(f"   - {market['symbol']}: {market['price']}")
    else:
        print("❌ Failed to get available markets")
        print(f"   Error: {result['data'].get('error', 'Unknown error')}")
    
    # Test 4: Test monitoring start
    print("\n4. Testing monitoring start...")
    monitoring_config = {
        "markets": TEST_MARKETS,
        "interval": 5,  # 5 seconds for testing
        "sensitivity": "medium"
    }
    
    result = test_api_endpoint("/api/market-analysis/start", "POST", monitoring_config)
    if result["success"] and result["data"].get("success"):
        print("✅ Monitoring started successfully")
        print(f"   Message: {result['data'].get('message')}")
        
        # Wait a bit for monitoring to collect data
        print("   Waiting 15 seconds for data collection...")
        time.sleep(15)
        
        # Test 5: Check alerts
        print("\n5. Testing alerts retrieval...")
        result = test_api_endpoint("/api/market-analysis/alerts")
        if result["success"] and result["data"].get("success"):
            alerts = result["data"].get("alerts", [])
            scan_count = result["data"].get("scan_count", 0)
            print(f"✅ Retrieved {len(alerts)} alerts after {scan_count} scans")
            
            if alerts:
                print("   Recent alerts:")
                for alert in alerts[:3]:  # Show first 3 alerts
                    print(f"   - {alert['market']}: {alert['title']} ({alert['severity']})")
            else:
                print("   No alerts generated (this is normal for stable markets)")
        else:
            print("❌ Failed to get alerts")
            print(f"   Error: {result['data'].get('error', 'Unknown error')}")
        
        # Test 6: Test monitoring stop
        print("\n6. Testing monitoring stop...")
        result = test_api_endpoint("/api/market-analysis/stop", "POST")
        if result["success"] and result["data"].get("success"):
            print("✅ Monitoring stopped successfully")
        else:
            print("❌ Failed to stop monitoring")
            print(f"   Error: {result['data'].get('error', 'Unknown error')}")
    
    else:
        print("❌ Failed to start monitoring")
        print(f"   Error: {result['data'].get('error', 'Unknown error')}")
    
    # Test 7: Test monitoring status
    print("\n7. Testing monitoring status...")
    result = test_api_endpoint("/api/market-analysis/status")
    if result["success"] and result["data"].get("success"):
        status = result["data"]
        print("✅ Status retrieved successfully")
        print(f"   Active: {status.get('active', False)}")
        print(f"   Scan count: {status.get('scan_count', 0)}")
        print(f"   Alert count: {status.get('alert_count', 0)}")
    else:
        print("❌ Failed to get status")
        print(f"   Error: {result['data'].get('error', 'Unknown error')}")
    
    # Test 8: Test clear alerts
    print("\n8. Testing clear alerts...")
    result = test_api_endpoint("/api/market-analysis/clear-alerts", "POST")
    if result["success"] and result["data"].get("success"):
        print("✅ Alerts cleared successfully")
    else:
        print("❌ Failed to clear alerts")
        print(f"   Error: {result['data'].get('error', 'Unknown error')}")
    
    print("\n" + "=" * 80)
    print("🎉 Market Analysis System Test Complete!")
    print("=" * 80)
    
    print("\n📋 Next Steps:")
    print("1. Visit http://localhost:8000/market-analysis to see the dashboard")
    print("2. Start monitoring to see real-time market analysis")
    print("3. Adjust sensitivity settings based on your risk tolerance")
    print("4. Set up alerts for specific manipulation patterns")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)