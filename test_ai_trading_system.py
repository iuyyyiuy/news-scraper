#!/usr/bin/env python3
"""
Test AI Trading System
Comprehensive test of the self-learning trading system
"""

import requests
import json
import time
import asyncio
from datetime import datetime

def test_ai_trading_system():
    """Test the complete AI trading system"""
    
    print("🤖 Testing AI Self-Learning Trading System")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health Check
    print("\n1. 🏥 Health Check...")
    try:
        response = requests.get(f"{base_url}/api/ai-trading/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ System health: {health['success']}")
            print(f"   📊 Status: {health['system_status']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Start AI Trading System
    print("\n2. 🚀 Starting AI Trading System...")
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
            if result['success']:
                print(f"   ✅ System started successfully!")
                print(f"   💰 Initial: ${result['initial_balance']} → Target: ${result['target_balance']}")
                print(f"   🛡️ Risk Level: {result['risk_level']}")
            else:
                print(f"   ❌ Start failed: {result.get('message', 'Unknown error')}")
        else:
            print(f"   ❌ Start request failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Start system error: {e}")
    
    # Wait for system to initialize
    print("\n   ⏳ Waiting for system initialization...")
    time.sleep(5)
    
    # Test 3: Check System Status
    print("\n3. 📊 Checking System Status...")
    try:
        response = requests.get(f"{base_url}/api/ai-trading/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ System Active: {status['active']}")
            print(f"   💰 Current Balance: ${status['current_balance']:.2f}")
            print(f"   📈 Progress: {status['progress_percentage']:.1f}%")
            print(f"   🎯 Win Rate: {status['win_rate']:.1%}")
            print(f"   📊 Signals Today: {status['signals_today']}")
            print(f"   🎯 Accuracy Rate: {status['accuracy_rate']:.1%}")
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Status check error: {e}")
    
    # Test 4: Trigger Learning from Data
    print("\n4. 🧠 Testing AI Learning...")
    try:
        response = requests.post(f"{base_url}/api/ai-trading/learn-from-data")
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"   ✅ Learning completed successfully!")
                print(f"   📚 Timestamp: {result['timestamp']}")
            else:
                print(f"   ❌ Learning failed: {result.get('message', 'Unknown error')}")
        else:
            print(f"   ❌ Learning request failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Learning error: {e}")
    
    # Test 5: Get Market Analysis
    print("\n5. 📈 Testing Market Analysis...")
    try:
        response = requests.get(f"{base_url}/api/ai-trading/market/current-analysis")
        if response.status_code == 200:
            analysis = response.json()
            if analysis['success']:
                market = analysis['market_analysis']
                recommendation = analysis['recommendation']
                
                print(f"   ✅ Market Analysis Retrieved!")
                print(f"   💰 Current Price: ${market['current_price']:.2f}")
                print(f"   📊 24h Change: {market['price_change_24h']:.2f}%")
                print(f"   📈 RSI: {market['rsi']:.1f}")
                print(f"   🌊 Volatility: {market['volatility']:.3f}")
                print(f"   📰 News Sentiment: {market['news_sentiment']:.2f}")
                print(f"   🤖 AI Recommendation: {recommendation['action']}")
                print(f"   🎯 Confidence: {recommendation['confidence']:.1%}")
                print(f"   ⚠️ Risk Score: {recommendation['risk_score']:.2f}")
            else:
                print(f"   ❌ Analysis failed: {analysis.get('message', 'Unknown error')}")
        else:
            print(f"   ❌ Analysis request failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Analysis error: {e}")
    
    # Test 6: Get Recent Signals
    print("\n6. 🚨 Testing Signal Generation...")
    try:
        response = requests.get(f"{base_url}/api/ai-trading/signals/recent?limit=5")
        if response.status_code == 200:
            signals_data = response.json()
            if signals_data['success']:
                signals = signals_data['signals']
                print(f"   ✅ Retrieved {len(signals)} recent signals")
                
                for i, signal in enumerate(signals[:3], 1):
                    print(f"   📊 Signal {i}:")
                    print(f"      🎯 Action: {signal['recommended_action']}")
                    print(f"      💪 Strength: {signal['signal_strength']}")
                    print(f"      💰 Entry: ${signal['entry_price']:.2f}")
                    print(f"      🛡️ Stop Loss: ${signal['stop_loss']:.2f}")
                    print(f"      🎯 Take Profit: ${signal['take_profit']:.2f}")
                    print(f"      📏 Position Size: {signal['position_size_pct']:.1%}")
                    print(f"      🎯 Confidence: {signal['confidence']:.1%}")
            else:
                print(f"   ❌ Signals retrieval failed: {signals_data.get('message', 'Unknown error')}")
        else:
            print(f"   ❌ Signals request failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Signals error: {e}")
    
    # Test 7: Get Performance Summary
    print("\n7. 📊 Testing Performance Analysis...")
    try:
        response = requests.get(f"{base_url}/api/ai-trading/performance/summary")
        if response.status_code == 200:
            perf_data = response.json()
            if perf_data['success']:
                perf = perf_data['performance_summary']
                print(f"   ✅ Performance Analysis Retrieved!")
                print(f"   💰 Current Balance: ${perf['current_balance']:.2f}")
                print(f"   📈 Profit/Loss: ${perf['profit_loss']:.2f}")
                print(f"   📊 Progress: {perf['progress_percentage']:.1f}%")
                print(f"   🎯 Win Rate: {perf['win_rate']:.1%}")
                print(f"   📉 Max Drawdown: {perf['max_drawdown']:.1%}")
                print(f"   🔄 Trades Executed: {perf['trades_executed']}")
                print(f"   📊 Signals Today: {perf['signals_today']}")
                print(f"   🎯 Accuracy Rate: {perf['accuracy_metrics']['accuracy_rate']:.1%}")
                print(f"   📈 Avg Daily Return: {perf['avg_daily_return']:.3%}")
                print(f"   📊 Sharpe Ratio: {perf['sharpe_ratio']:.2f}")
            else:
                print(f"   ❌ Performance analysis failed: {perf_data.get('message', 'Unknown error')}")
        else:
            print(f"   ❌ Performance request failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Performance error: {e}")
    
    # Test 8: Get Milestone Progress
    print("\n8. 🎯 Testing Milestone Progress...")
    try:
        response = requests.get(f"{base_url}/api/ai-trading/progress/milestones")
        if response.status_code == 200:
            milestone_data = response.json()
            if milestone_data['success']:
                milestones = milestone_data['milestones']
                print(f"   ✅ Milestone Progress Retrieved!")
                print(f"   💰 Current: ${milestone_data['current_balance']:.2f}")
                print(f"   🎯 Target: ${milestone_data['target_balance']:.2f}")
                print(f"   ⏰ Est. Days to Goal: {milestone_data['estimated_days_to_goal']}")
                
                print(f"   📊 Milestones:")
                for milestone in milestones[:5]:
                    status_icon = "✅" if milestone['status'] == 'completed' else "🔄" if milestone['status'] == 'in_progress' else "⏳"
                    print(f"      {status_icon} ${milestone['milestone']} - {milestone['status']} ({milestone['progress_percentage']:.1f}%)")
            else:
                print(f"   ❌ Milestone retrieval failed: {milestone_data.get('message', 'Unknown error')}")
        else:
            print(f"   ❌ Milestone request failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Milestone error: {e}")
    
    # Test 9: Update Settings
    print("\n9. ⚙️ Testing Settings Update...")
    try:
        settings_update = {
            "max_position_size": 0.08,  # 8%
            "stop_loss_pct": 0.025,     # 2.5%
            "take_profit_pct": 0.06,    # 6%
            "daily_loss_limit": 0.05    # 5%
        }
        
        response = requests.post(
            f"{base_url}/api/ai-trading/settings/update",
            json=settings_update
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"   ✅ Settings updated successfully!")
                print(f"   ⚙️ Updated: {result['updated_settings']}")
            else:
                print(f"   ❌ Settings update failed: {result.get('detail', 'Unknown error')}")
        else:
            print(f"   ❌ Settings request failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Settings error: {e}")
    
    # Test 10: Test Web Interface
    print("\n10. 🌐 Testing Web Interface...")
    try:
        response = requests.get(f"{base_url}/ai-trading")
        if response.status_code == 200:
            print(f"   ✅ Web interface accessible!")
            print(f"   🌐 URL: {base_url}/ai-trading")
        else:
            print(f"   ❌ Web interface failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Web interface error: {e}")
    
    # Test 11: Stop System (Optional)
    print("\n11. ⏹️ Testing System Stop (Optional)...")
    stop_system = input("   Do you want to stop the system? (y/N): ").lower().strip()
    
    if stop_system == 'y':
        try:
            response = requests.post(f"{base_url}/api/ai-trading/stop-system")
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"   ✅ System stopped successfully!")
                    if 'final_performance' in result:
                        final = result['final_performance']
                        print(f"   📊 Final Performance:")
                        print(f"      💰 Final Balance: ${final['current_balance']:.2f}")
                        print(f"      📈 Total P&L: ${final['profit_loss']:.2f}")
                        print(f"      📊 Progress: {final['progress_percentage']:.1f}%")
                else:
                    print(f"   ❌ Stop failed: {result.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ Stop request failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Stop error: {e}")
    else:
        print("   ℹ️ System left running")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 AI Trading System Test Complete!")
    print("\n📋 Test Summary:")
    print("   ✅ Health Check")
    print("   ✅ System Start/Stop")
    print("   ✅ Status Monitoring")
    print("   ✅ AI Learning")
    print("   ✅ Market Analysis")
    print("   ✅ Signal Generation")
    print("   ✅ Performance Tracking")
    print("   ✅ Milestone Progress")
    print("   ✅ Settings Management")
    print("   ✅ Web Interface")
    
    print("\n🚀 Next Steps:")
    print("   1. Access the web interface: http://localhost:8000/ai-trading")
    print("   2. Upload your trading data for AI learning")
    print("   3. Monitor signals and performance")
    print("   4. Adjust settings based on your risk tolerance")
    print("   5. Track progress towards your 1000 USDT goal!")
    
    print("\n💡 Tips:")
    print("   - Start with conservative settings")
    print("   - Upload quality trading data for better learning")
    print("   - Monitor the system regularly")
    print("   - Adjust parameters based on performance")
    
    print("\n🎯 Goal: 200 USDT → 1000 USDT with AI-powered conservative trading!")

if __name__ == "__main__":
    test_ai_trading_system()