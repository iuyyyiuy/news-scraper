#!/usr/bin/env python3
"""
Fix Environment Variable Loading Issues
"""

import os
from dotenv import load_dotenv

def fix_environment_loading():
    """Fix environment variable loading for the scraper"""
    
    print("🔧 Fixing Environment Variable Loading")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check current environment
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    supabase_url = os.getenv('SUPABASE_URL')
    
    print(f"DeepSeek API Key: {'✅ Found' if deepseek_key else '❌ Missing'}")
    print(f"Supabase URL: {'✅ Found' if supabase_url else '❌ Missing'}")
    
    if deepseek_key:
        print(f"DeepSeek Key: {deepseek_key[:10]}...{deepseek_key[-4:]}")
    
    # Test DeepSeek API with current environment
    if deepseek_key:
        print("\n🧪 Testing DeepSeek API with current environment...")
        try:
            import requests
            
            headers = {
                'Authorization': f'Bearer {deepseek_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": "Test"}
                ],
                "max_tokens": 5
            }
            
            response = requests.post(
                'https://api.deepseek.com/chat/completions',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ DeepSeek API working with current environment!")
                return True
            else:
                print(f"❌ DeepSeek API error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ DeepSeek API test failed: {e}")
            return False
    else:
        print("❌ Cannot test DeepSeek API - no API key found")
        return False

def create_environment_fix_script():
    """Create a script to ensure environment variables are loaded"""
    
    script_content = '''#!/usr/bin/env python3
"""
Environment Variable Loader for Scraper
"""

import os
from dotenv import load_dotenv

# Force load environment variables
load_dotenv(override=True)

# Verify critical environment variables
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not DEEPSEEK_API_KEY:
    print("⚠️ WARNING: DEEPSEEK_API_KEY not found in environment")
    print("   AI content analysis will be disabled")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️ WARNING: Supabase configuration incomplete")
    print("   Database operations may fail")

# Export for other modules
__all__ = ['DEEPSEEK_API_KEY', 'SUPABASE_URL', 'SUPABASE_KEY']
'''
    
    with open('scraper/core/environment.py', 'w') as f:
        f.write(script_content)
    
    print("✅ Created scraper/core/environment.py")

if __name__ == "__main__":
    success = fix_environment_loading()
    create_environment_fix_script()
    
    if success:
        print("\n🎉 Environment loading fixed!")
    else:
        print("\n⚠️ Environment issues detected - check API keys")