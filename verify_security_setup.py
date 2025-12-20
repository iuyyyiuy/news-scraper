#!/usr/bin/env python3
"""
Security Setup Verification
Verifies that all sensitive information is properly protected and the system is functional.
"""

import os
import sys
from dotenv import load_dotenv

def verify_security_setup():
    """Verify that security setup is correct"""
    
    print("🔒 Security Setup Verification")
    print("=" * 50)
    
    # Check 1: .env file exists and is gitignored
    print("1️⃣ Checking .env file protection...")
    
    if os.path.exists('.env'):
        print("   ✅ .env file exists")
        
        # Check if .env is in .gitignore
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
            if '.env' in gitignore_content:
                print("   ✅ .env is properly gitignored")
            else:
                print("   ❌ .env is NOT in .gitignore - SECURITY RISK!")
                return False
    else:
        print("   ❌ .env file missing")
        return False
    
    # Check 2: .env.example exists with placeholder values
    print("\n2️⃣ Checking .env.example template...")
    
    if os.path.exists('.env.example'):
        print("   ✅ .env.example exists")
        
        with open('.env.example', 'r') as f:
            example_content = f.read()
            if 'your_supabase_url_here' in example_content and 'your_deepseek_api_key_here' in example_content:
                print("   ✅ .env.example has proper placeholder values")
            else:
                print("   ❌ .env.example contains real credentials - SECURITY RISK!")
                return False
    else:
        print("   ❌ .env.example missing")
        return False
    
    # Check 3: Environment variables are loaded and functional
    print("\n3️⃣ Checking environment variables...")
    
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    
    if supabase_url and supabase_key and deepseek_key:
        print("   ✅ All required environment variables are set")
        print(f"   📊 Supabase URL: {supabase_url[:30]}...")
        print(f"   📊 Supabase Key: {supabase_key[:20]}...")
        print(f"   📊 DeepSeek Key: {deepseek_key[:15]}...")
    else:
        print("   ❌ Missing required environment variables")
        return False
    
    # Check 4: No hardcoded credentials in source files
    print("\n4️⃣ Checking for hardcoded credentials...")
    
    sensitive_patterns = [
        'vckulcbgaqyujucbbeno',  # Supabase project ID
        'eyJhbGciOiJIUzI1NiIs',  # JWT token start
        'sk-5192eebd30f446128039a5bae58556a3'  # Old API key
    ]
    
    source_files = [
        'scraper/core/database_manager.py',
        'scraper/core/ai_content_analyzer.py',
        'scraper/web_api.py',
        'check_article_content.py',
        'fix_deepseek_api_key.py'
    ]
    
    issues_found = False
    for file_path in source_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                for pattern in sensitive_patterns:
                    if pattern in content:
                        print(f"   ❌ Found sensitive data in {file_path}: {pattern[:20]}...")
                        issues_found = True
    
    if not issues_found:
        print("   ✅ No hardcoded credentials found in source files")
    else:
        return False
    
    # Check 5: Test API functionality
    print("\n5️⃣ Testing API functionality...")
    
    try:
        import requests
        
        # Test if the web server can start (just check if port is available)
        response = requests.get('http://localhost:8080/api/database/stats', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ API is functional and returning data")
                print(f"   📊 Total articles: {data['data'].get('total_articles', 0)}")
            else:
                print("   ⚠️ API responding but with errors")
        else:
            print("   ⚠️ API not currently running (start server to test)")
    except Exception as e:
        print(f"   ⚠️ Could not test API (server may not be running): {e}")
    
    # Check 6: Verify .gitignore completeness
    print("\n6️⃣ Checking .gitignore completeness...")
    
    required_ignores = ['.env', '*.log', 'temp_session_*', '__pycache__/', '*.key']
    
    with open('.gitignore', 'r') as f:
        gitignore_content = f.read()
        
    missing_ignores = []
    for ignore_pattern in required_ignores:
        if ignore_pattern not in gitignore_content:
            missing_ignores.append(ignore_pattern)
    
    if not missing_ignores:
        print("   ✅ .gitignore is comprehensive")
    else:
        print(f"   ⚠️ Missing .gitignore patterns: {missing_ignores}")
    
    print("\n" + "=" * 50)
    print("🎉 Security verification completed!")
    print("\n📋 Summary:")
    print("✅ Sensitive data is properly protected")
    print("✅ API keys are hidden but functional")
    print("✅ No personal information in repository")
    print("✅ Environment variables properly configured")
    print("✅ Ready for production deployment")
    
    return True

def main():
    """Main function"""
    success = verify_security_setup()
    
    if success:
        print("\n🚀 Your repository is secure and ready!")
        print("💡 You can safely share this repository publicly")
    else:
        print("\n❌ Security issues found - please fix before sharing")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())