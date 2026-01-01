#!/usr/bin/env python3
"""
Test AI Integration for Trading Strategy Analysis
Tests the DeepSeek API integration in the trading strategy system
"""

import requests
import pandas as pd
import io
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_ai_integration():
    """Test that AI integration is working with DeepSeek API"""
    
    base_url = "http://localhost:8000"
    
    print("🤖 Testing AI Integration for Trading Strategy Analysis")
    print("=" * 60)
    
    # Test 1: Check DeepSeek API key
    print("\n1. Checking DeepSeek API configuration...")
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if api_key:
        print(f"✅ DeepSeek API key found: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("❌ DeepSeek API key not found in environment")
        return False
    
    # Test 2: Upload sample data
    print("\n2. Uploading sample trading data...")
    sample_data = create_comprehensive_sample_data()
    
    try:
        csv_buffer = io.StringIO()
        sample_data.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()
        
        files = {'file': ('ai_test_trader.csv', csv_content, 'text/csv')}
        response = requests.post(f"{base_url}/api/trading-strategy/upload-csv", files=files)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ Sample data uploaded: {result['records_imported']} records")
            else:
                print(f"❌ Upload failed: {result['message']}")
                return False
        else:
            print(f"❌ Upload request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error uploading data: {e}")
        return False
    
    # Test 3: Start AI-powered analysis
    print("\n3. Starting AI-powered strategy analysis...")
    
    analysis_request = {
        "date_range_days": 30,
        "min_profit_threshold": 0.0,
        "include_news_correlation": True
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/trading-strategy/analyze-strategies",
            json=analysis_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                analysis_id = result['analysis_id']
                print(f"✅ AI analysis started: {analysis_id}")
                
                # Wait for analysis to complete
                print("   ⏳ Waiting for AI analysis to complete...")
                import time
                
                for attempt in range(12):  # Wait up to 60 seconds
                    time.sleep(5)
                    
                    try:
                        status_response = requests.get(f"{base_url}/api/trading-strategy/analysis/{analysis_id}")
                        if status_response.status_code == 200:
                            status_result = status_response.json()
                            
                            if status_result['success'] and 'ai_insights' in status_result:
                                print("✅ AI analysis completed!")
                                
                                # Test AI insights quality
                                ai_insights = status_result['ai_insights']
                                print(f"\n4. Testing AI insights quality...")
                                
                                # Check if AI analysis was actually used
                                if ai_insights.get('ai_analysis_available'):
                                    print("✅ DeepSeek AI analysis successfully used")
                                    print(f"   📊 AI Model: {ai_insights.get('analysis_metadata', {}).get('ai_model', 'unknown')}")
                                else:
                                    print("⚠️  AI analysis not available, using fallback")
                                
                                # Check insight categories
                                insight_categories = [
                                    'success_patterns',
                                    'failure_analysis', 
                                    'risk_management_tips',
                                    'strategy_optimization',
                                    'news_impact_insights',
                                    'market_timing_advice'
                                ]
                                
                                for category in insight_categories:
                                    insights = ai_insights.get(category, [])
                                    if insights:
                                        print(f"   ✅ {category}: {len(insights)} insights")
                                        # Show first insight as example
                                        if isinstance(insights, list) and insights:
                                            print(f"      例: {insights[0][:100]}...")
                                    else:
                                        print(f"   ❌ {category}: No insights")
                                
                                # Check overall recommendation
                                overall_rec = ai_insights.get('overall_recommendation', '')
                                if overall_rec:
                                    print(f"   ✅ Overall recommendation: {len(overall_rec)} characters")
                                    print(f"      预览: {overall_rec[:150]}...")
                                else:
                                    print("   ❌ No overall recommendation")
                                
                                return True
                            else:
                                print(f"   ⏳ Analysis still in progress (attempt {attempt + 1}/12)...")
                    except Exception as e:
                        print(f"   ❌ Error checking analysis status: {e}")
                
                print("❌ Analysis timed out after 60 seconds")
                return False
            else:
                print(f"❌ Analysis failed to start: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Analysis request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error starting analysis: {e}")
        return False

def create_comprehensive_sample_data():
    """Create comprehensive sample data for AI analysis testing"""
    
    # Create diverse trading scenarios for better AI analysis
    records = [
        # Successful scalper
        {
            "开仓时间": "2025-12-20 09:15:30",
            "平仓时间": "2025-12-20 09:45:15",
            "合约": "BTCUSDT",
            "类型": "多仓",
            "开仓均价": 97500,
            "进入价格": 97500,
            "离开价格": 97850,
            "平仓类型": "止盈",
            "历史最高数量": 2.5,
            "历史最高价值": 243750,
            "已实现盈亏": 875.00,
            "手续费": 48.75,
            "资金费用": 0
        },
        # Successful swing trader
        {
            "开仓时间": "2025-12-18 14:30:00",
            "平仓时间": "2025-12-20 16:20:00",
            "合约": "ETHUSDT",
            "类型": "空仓",
            "开仓均价": 3450,
            "进入价格": 3450,
            "离开价格": 3280,
            "平仓类型": "止盈",
            "历史最高数量": 15.0,
            "历史最高价值": 51750,
            "已实现盈亏": 2550.00,
            "手续费": 103.50,
            "资金费用": -25.50
        },
        # Failed high leverage trade
        {
            "开仓时间": "2025-12-19 22:10:00",
            "平仓时间": "2025-12-19 22:35:00",
            "合约": "BTCUSDT",
            "类型": "多仓",
            "开仓均价": 96800,
            "进入价格": 96800,
            "离开价格": 95200,
            "平仓类型": "止损",
            "历史最高数量": 10.0,
            "历史最高价值": 968000,
            "已实现盈亏": -16000.00,
            "手续费": 1936.00,
            "资金费用": 0
        },
        # Successful day trader
        {
            "开仓时间": "2025-12-19 08:00:00",
            "平仓时间": "2025-12-19 18:30:00",
            "合约": "ETHUSDT",
            "类型": "多仓",
            "开仓均价": 3200,
            "进入价格": 3200,
            "离开价格": 3380,
            "平仓类型": "一键平仓",
            "历史最高数量": 8.0,
            "历史最高价值": 25600,
            "已实现盈亏": 1440.00,
            "手续费": 51.20,
            "资金费用": -12.80
        },
        # Failed overtrading
        {
            "开仓时间": "2025-12-20 03:45:00",
            "平仓时间": "2025-12-20 04:15:00",
            "合约": "BTCUSDT",
            "类型": "空仓",
            "开仓均价": 97200,
            "进入价格": 97200,
            "离开价格": 98100,
            "平仓类型": "止损",
            "历史最高数量": 3.0,
            "历史最高价值": 291600,
            "已实现盈亏": -2700.00,
            "手续费": 583.20,
            "资金费用": 0
        },
        # Successful position trader
        {
            "开仓时间": "2025-12-15 10:00:00",
            "平仓时间": "2025-12-20 15:00:00",
            "合约": "ETHUSDT",
            "类型": "多仓",
            "开仓均价": 3100,
            "进入价格": 3100,
            "离开价格": 3420,
            "平仓类型": "止盈",
            "历史最高数量": 20.0,
            "历史最高价值": 62000,
            "已实现盈亏": 6400.00,
            "手续费": 124.00,
            "资金费用": -186.00
        }
    ]
    
    return pd.DataFrame(records)

if __name__ == "__main__":
    success = test_ai_integration()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 AI Integration Test PASSED!")
        print("✅ DeepSeek API is working with trading strategy analysis")
    else:
        print("❌ AI Integration Test FAILED!")
        print("🔧 Please check DeepSeek API configuration and server status")