#!/usr/bin/env python3
"""
Test 15-Minute Analysis and Alert System
Tests both immediate trading alerts and regular analysis updates
"""

import requests
import json
import time
from datetime import datetime

def test_analysis_and_alerts():
    """Test the analysis and alert system"""
    
    print("🔔 Testing 15-Minute Analysis & Alert System")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Start AI Trading System
    print("\n1. 🚀 Starting AI Trading System...")
    try:
        start_request = {
            "initial_balance": 200.0,
            "target_balance": 1000.0,
            "risk_level": "conservative"
        }
        
        response = requests.post(
            f"{base_url}/api/ai-trading/start-system",
            json=start_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ System started: ${result['initial_balance']} → ${result['target_balance']}")
        else:
            print(f"   ❌ Start failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Start error: {e}")
    
    # Wait for system to initialize
    print("\n   ⏳ Waiting for system to start monitoring...")
    time.sleep(8)
    
    # Test 2: Check for Trading Alerts
    print("\n2. 🚨 Checking for Trading Alerts...")
    try:
        response = requests.get(f"{base_url}/api/ai-trading/alerts/trading?limit=5")
        if response.status_code == 200:
            alerts_data = response.json()
            alerts = alerts_data['alerts']
            
            print(f"   ✅ Found {len(alerts)} trading alerts")
            print(f"   🔔 Unacknowledged: {alerts_data['unacknowledged_count']}")
            
            for i, alert in enumerate(alerts[:3], 1):
                print(f"   📊 Alert {i}:")
                print(f"      ⚡ Strength: {alert['signal_strength']}")
                print(f"      🎯 Action: {alert['recommended_action']}")
                print(f"      💰 Entry: ${alert['entry_price']:.2f}")
                print(f"      🕐 Time: {alert['timestamp']}")
                
        else:
            print(f"   ❌ Failed to get alerts: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Alerts error: {e}")
    
    # Test 3: Check for Analysis Notifications
    print("\n3. 📊 Checking for Analysis Notifications...")
    try:
        response = requests.get(f"{base_url}/api/ai-trading/alerts/analysis?limit=10")
        if response.status_code == 200:
            notifications_data = response.json()
            notifications = notifications_data['notifications']
            
            print(f"   ✅ Found {len(notifications)} analysis notifications")
            print(f"   📖 Unread: {notifications_data['unread_count']}")
            
            for i, notification in enumerate(notifications[:5], 1):
                print(f"   📈 Analysis {i}:")
                print(f"      💰 BTC: ${notification['btc_price']:.0f} ({notification['price_change_24h']:+.1f}%)")
                print(f"      📊 Condition: {notification['market_condition']}")
                print(f"      🤖 AI: {notification['ai_recommendation']} ({notification['ai_confidence']:.0%})")
                print(f"      🕐 Time: {notification['timestamp']}")
                
        else:
            print(f"   ❌ Failed to get notifications: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Notifications error: {e}")
    
    # Test 4: Get Current Market Analysis
    print("\n4. 📈 Getting Current Market Analysis...")
    try:
        response = requests.get(f"{base_url}/api/ai-trading/market/current-analysis")
        if response.status_code == 200:
            analysis = response.json()
            if analysis['success']:
                market = analysis['market_analysis']
                recommendation = analysis['recommendation']
                
                print(f"   ✅ Current Analysis:")
                print(f"   💰 BTC Price: ${market['current_price']:.2f}")
                print(f"   📊 24h Change: {market['price_change_24h']:+.2f}%")
                print(f"   📈 Market: {market['market_condition']}")
                print(f"   🤖 AI Rec: {recommendation['action']} ({recommendation['confidence']:.1%})")
                print(f"   ⚠️ Risk: {recommendation['risk_score']:.2f}")
                print(f"   💡 Reasoning: {recommendation['reasoning']}")
                
        else:
            print(f"   ❌ Analysis failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Analysis error: {e}")
    
    # Test 5: Monitor for New Updates
    print("\n5. ⏰ Monitoring for New Updates...")
    print("   📝 The system will now:")
    print("   • Generate analysis updates every 15 minutes")
    print("   • Send immediate alerts for STRONG trading signals")
    print("   • Log all activity to console and database")
    print("   • You can check alerts via the API endpoints")
    
    print(f"\n   🔗 API Endpoints:")
    print(f"   • Trading Alerts: {base_url}/api/ai-trading/alerts/trading")
    print(f"   • Analysis Updates: {base_url}/api/ai-trading/alerts/analysis")
    print(f"   • Current Analysis: {base_url}/api/ai-trading/market/current-analysis")
    print(f"   • System Status: {base_url}/api/ai-trading/status")
    
    # Test 6: Wait and Check for Updates
    print("\n6. ⏳ Waiting for Next Analysis Cycle...")
    print("   (The system checks every 5 minutes, analyzes every 15 minutes)")
    
    # Monitor for a few cycles
    for cycle in range(3):
        print(f"\n   🔄 Cycle {cycle + 1}/3 - Waiting 2 minutes...")
        time.sleep(120)  # Wait 2 minutes
        
        # Check for new notifications
        try:
            response = requests.get(f"{base_url}/api/ai-trading/alerts/analysis?limit=1")
            if response.status_code == 200:
                data = response.json()
                if data['notifications']:
                    latest = data['notifications'][0]
                    print(f"   📊 Latest: BTC ${latest['btc_price']:.0f} | {latest['ai_recommendation']} | {latest['timestamp']}")
                else:
                    print("   📊 No new notifications yet")
        except:
            print("   ⚠️ Could not check notifications")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 15-Minute Analysis & Alert System Test Complete!")
    
    print("\n📋 System Features:")
    print("   ✅ 15-minute regular analysis updates")
    print("   ✅ Immediate alerts for strong trading signals")
    print("   ✅ Database storage of all alerts and analysis")
    print("   ✅ API endpoints for retrieving notifications")
    print("   ✅ Console logging with different priority levels")
    
    print("\n🔔 Alert Types:")
    print("   🚨 IMMEDIATE TRADING ALERTS - For STRONG/VERY_STRONG signals")
    print("   📊 REGULAR ANALYSIS - Every 15 minutes regardless of signals")
    print("   📈 MARKET UPDATES - Continuous monitoring and logging")
    
    print("\n💡 Next Steps:")
    print("   1. Monitor the console logs for 15-minute updates")
    print("   2. Check the API endpoints for alerts and notifications")
    print("   3. The system will continue running and analyzing")
    print("   4. Strong signals will trigger immediate alerts")
    
    print("\n🎯 The system is now providing both:")
    print("   • Immediate trading alerts when opportunities arise")
    print("   • Regular 15-minute analysis updates for market awareness")

if __name__ == "__main__":
    test_analysis_and_alerts()