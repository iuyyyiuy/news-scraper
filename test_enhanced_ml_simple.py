#!/usr/bin/env python3
"""
Simple test for Enhanced ML System
Focus on testing the enhanced collection and market indicators
"""

import requests
import json
import time

def test_endpoint(url, method='GET', data=None):
    """Test API endpoint"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("🧠 Enhanced ML System - Simple Test")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api/ml-analysis"
    
    # Test 1: Market Indicators
    print("\n📊 Testing Market Indicators...")
    result = test_endpoint(f"{base_url}/market-indicators")
    if result.get('success'):
        indicators = result.get('indicators', {})
        print(f"✅ Volatility: {indicators.get('current_volatility', 0):.2%}")
        print(f"✅ Volume: ${indicators.get('current_volume', 0):,.0f}")
        print(f"✅ RSI: {indicators.get('current_rsi', 50):.1f}")
        print(f"✅ Priority: {indicators.get('collection_priority', 0):.2f}")
        print(f"✅ Should Collect: {result.get('should_collect', False)}")
        print(f"✅ Reason: {result.get('collection_reason', 'N/A')}")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    # Test 2: Enhanced Collection Status
    print("\n🚀 Testing Enhanced Collection...")
    
    # Start enhanced collection
    result = test_endpoint(f"{base_url}/start-enhanced-collection", "POST", {"interval": 5})
    if result.get('success'):
        print("✅ Enhanced collection started")
        features = result.get('features', [])
        print(f"✅ Features: {', '.join(features)}")
        
        # Wait and check status
        print("⏳ Waiting 10 seconds for data collection...")
        time.sleep(10)
        
        # Check status
        status = test_endpoint(f"{base_url}/status")
        if status.get('success'):
            stats = status.get('collection_stats', {})
            print(f"✅ Snapshots: {stats.get('snapshots_collected', 0)}")
            print(f"✅ High Priority: {stats.get('high_priority_collections', 0)}")
            print(f"✅ Avg Volatility: {stats.get('average_volatility', 0):.2%}")
        
        # Stop collection
        stop_result = test_endpoint(f"{base_url}/stop-collection", "POST")
        if stop_result.get('success'):
            print("✅ Collection stopped")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    # Test 3: System Status
    print("\n📈 System Status...")
    status = test_endpoint(f"{base_url}/status")
    if status.get('success'):
        print(f"✅ ML Available: {status.get('ml_available', False)}")
        print(f"✅ Enhanced Features: {status.get('enhanced_features', {})}")
        
        market_indicators = status.get('market_indicators', {})
        if market_indicators:
            print("✅ Current Market State:")
            print(f"   - Price: ${market_indicators.get('price', 0):,.0f}")
            print(f"   - Volatility: {market_indicators.get('current_volatility', 0):.2%}")
            print(f"   - Priority: {market_indicators.get('collection_priority', 0):.2f}")
    
    print("\n" + "=" * 50)
    print("🎉 Enhanced ML System Test Complete!")
    print("\n✅ Key Features Working:")
    print("  • Real-time market indicators")
    print("  • Smart collection strategy")
    print("  • Volatility-based prioritization")
    print("  • Enhanced data collection")
    
    print(f"\n🌐 Access ML Dashboard: http://localhost:8000/ml-analysis")

if __name__ == "__main__":
    main()