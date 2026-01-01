#!/usr/bin/env python3
"""
Debug API Issues: DeepSeek API and Jinse News Fetching
"""

import os
import requests
import json
from datetime import datetime
import sys

def debug_deepseek_api():
    """Debug DeepSeek API authentication issues"""
    print("🔍 DEBUGGING DEEPSEEK API")
    print("=" * 50)
    
    # Check environment variable
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test API call
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": "Hello, test message"}
            ],
            "max_tokens": 10
        }
        
        print("🔄 Testing API connection...")
        response = requests.post(
            'https://api.deepseek.com/chat/completions',
            headers=headers,
            json=data,
            timeout=10
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ DeepSeek API is working!")
            result = response.json()
            print(f"📝 Response: {result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Provide specific troubleshooting
            if response.status_code == 401:
                print("\n🔧 AUTHENTICATION ERROR - Possible fixes:")
                print("1. API key is invalid or expired")
                print("2. Account has no credits")
                print("3. API key not activated")
                print("4. Need to generate a new API key")
                print("5. Check https://platform.deepseek.com/api_keys")
            elif response.status_code == 429:
                print("\n🔧 RATE LIMIT ERROR - Possible fixes:")
                print("1. Too many requests")
                print("2. Account quota exceeded")
                print("3. Wait and try again")
            
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def debug_jinse_scraping():
    """Debug Jinse news fetching issues"""
    print("\n🔍 DEBUGGING JINSE NEWS FETCHING")
    print("=" * 50)
    
    # Test basic Jinse connectivity
    try:
        print("🔄 Testing Jinse main page...")
        response = requests.get('https://www.jinse.cn/', timeout=10)
        print(f"📡 Main page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Jinse main page accessible")
        else:
            print(f"❌ Jinse main page error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Jinse main page connection error: {e}")
        return False
    
    # Test Jinse API endpoints
    test_urls = [
        'https://www.jinse.cn/api/noah/v2/lives',
        'https://www.jinse.cn/lives/492457.html',  # This was failing in logs
        'https://api.jinse.cn/noah/v2/lives'
    ]
    
    for url in test_urls:
        try:
            print(f"\n🔄 Testing: {url}")
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            print(f"📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ URL accessible")
                # Try to parse JSON if it's an API endpoint
                if 'api' in url:
                    try:
                        data = response.json()
                        print(f"📊 JSON data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    except:
                        print("📄 Response is not JSON")
            else:
                print(f"❌ URL error: {response.status_code}")
                if response.status_code == 404:
                    print("   → URL not found (404)")
                elif response.status_code == 403:
                    print("   → Access forbidden (403)")
                elif response.status_code == 429:
                    print("   → Rate limited (429)")
                    
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    return True

def check_scraper_configuration():
    """Check scraper configuration and recent logs"""
    print("\n🔍 CHECKING SCRAPER CONFIGURATION")
    print("=" * 50)
    
    # Check if scraper files exist
    scraper_files = [
        'scraper/core/manual_scraper.py',
        'scraper/core/ai_content_analyzer.py',
        'scraper/core/parser.py'
    ]
    
    for file_path in scraper_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
    
    # Check recent server logs
    print("\n📋 Recent Issues from Server Logs:")
    print("1. DeepSeek API authentication fails (401 error)")
    print("2. Jinse URL 404 errors: https://www.jinse.cn/lives/492457.html")
    print("3. Poor success rate in scraping operations")
    
    return True

def provide_solutions():
    """Provide solutions for identified issues"""
    print("\n🔧 RECOMMENDED SOLUTIONS")
    print("=" * 50)
    
    print("🎯 DeepSeek API Issues:")
    print("1. Get a new API key from https://platform.deepseek.com/api_keys")
    print("2. Check account balance and credits")
    print("3. Verify API key is activated")
    print("4. Update .env file with new API key")
    
    print("\n🎯 Jinse Scraping Issues:")
    print("1. Update Jinse URL patterns (some URLs return 404)")
    print("2. Add better error handling for missing articles")
    print("3. Implement retry logic with exponential backoff")
    print("4. Add User-Agent headers to avoid blocking")
    
    print("\n🎯 General Improvements:")
    print("1. Add fallback mechanisms when APIs fail")
    print("2. Implement graceful degradation")
    print("3. Add better logging and monitoring")
    print("4. Create health check endpoints")

def main():
    """Main debugging function"""
    print("🐛 API ISSUES DEBUGGING TOOL")
    print("=" * 60)
    print(f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Debug DeepSeek API
    deepseek_ok = debug_deepseek_api()
    
    # Debug Jinse scraping
    jinse_ok = debug_jinse_scraping()
    
    # Check configuration
    config_ok = check_scraper_configuration()
    
    # Provide solutions
    provide_solutions()
    
    print("\n" + "=" * 60)
    print("📊 DEBUGGING SUMMARY")
    print(f"DeepSeek API: {'✅ Working' if deepseek_ok else '❌ Issues found'}")
    print(f"Jinse Scraping: {'✅ Working' if jinse_ok else '❌ Issues found'}")
    print(f"Configuration: {'✅ OK' if config_ok else '❌ Issues found'}")
    
    if not deepseek_ok or not jinse_ok:
        print("\n⚠️ Issues detected! Please follow the recommended solutions above.")
        return False
    else:
        print("\n🎉 All systems appear to be working!")
        return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Debugging interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Debugging failed with error: {e}")
        sys.exit(1)