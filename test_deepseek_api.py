#!/usr/bin/env python3
"""
Simple test script to validate DeepSeek API key.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_deepseek_api():
    """Test DeepSeek API key directly."""
    
    print("=== DEEPSEEK API KEY TEST ===")
    
    # Get API key
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        return
    
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
                "content": "Hello, this is a test. Please respond with 'API working'."
            }
        ],
        "temperature": 0.1,
        "max_tokens": 10
    }
    
    try:
        print("🔄 Testing API connection...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"✅ API Response: {message}")
            print("🎉 DeepSeek API is working correctly!")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 401:
                print("\n🔧 Troubleshooting:")
                print("1. Check if your API key is correct")
                print("2. Make sure you have credits in your DeepSeek account")
                print("3. Verify the API key is activated")
                print("4. Try generating a new API key")
            
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify the API key format")
        print("3. Make sure DeepSeek API is accessible")
        return False

if __name__ == "__main__":
    test_deepseek_api()