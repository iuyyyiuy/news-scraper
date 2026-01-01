#!/usr/bin/env python3
"""
Test DeepSeek API Connection
Simple test to verify DeepSeek API is working
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_deepseek_api():
    """Test direct connection to DeepSeek API"""
    
    print("🤖 Testing DeepSeek API Connection")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test API call
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": "请用中文简单介绍一下加密货币交易策略分析的重要性。回答控制在100字以内。"
            }
        ],
        "temperature": 0.1,
        "max_tokens": 200
    }
    
    try:
        print("\n🔄 Testing API call...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            print("✅ API call successful!")
            print(f"🤖 AI Response: {ai_response}")
            
            # Test usage info
            if 'usage' in result:
                usage = result['usage']
                print(f"📊 Token usage: {usage.get('total_tokens', 0)} tokens")
            
            return True
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ API call timed out (30 seconds)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_ai_analyzer_class():
    """Test the AIContentAnalyzer class"""
    
    print("\n🧪 Testing AIContentAnalyzer Class")
    print("=" * 40)
    
    try:
        from scraper.core.ai_content_analyzer import AIContentAnalyzer
        
        # Initialize analyzer
        analyzer = AIContentAnalyzer()
        print("✅ AIContentAnalyzer initialized successfully")
        
        # Test simple API call
        test_prompt = "请简单分析一下这个交易策略：高频交易，平均持仓时间30分钟，胜率65%，平均盈利2%。"
        
        print("🔄 Testing analyzer API call...")
        response = analyzer._call_deepseek_api(test_prompt)
        
        if response:
            print("✅ Analyzer API call successful!")
            print(f"🤖 Response preview: {response[:200]}...")
            return True
        else:
            print("❌ Analyzer API call failed")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing analyzer: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DeepSeek API Connection Test\n")
    
    # Test 1: Direct API call
    api_success = test_deepseek_api()
    
    # Test 2: AI Analyzer class
    analyzer_success = test_ai_analyzer_class()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"   Direct API: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"   AI Analyzer: {'✅ PASS' if analyzer_success else '❌ FAIL'}")
    
    if api_success and analyzer_success:
        print("\n🎉 All tests passed! DeepSeek API is ready for trading analysis.")
    else:
        print("\n❌ Some tests failed. Please check your configuration.")
        print("\n🔧 Troubleshooting:")
        print("   1. Verify DEEPSEEK_API_KEY in .env file")
        print("   2. Check internet connection")
        print("   3. Verify API key is valid and has credits")
        print("   4. Check if DeepSeek API service is available")