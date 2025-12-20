#!/usr/bin/env python3
"""
Fix DeepSeek API Key Configuration
Helps you update the API key in the .env file
"""

import os
from pathlib import Path

def fix_deepseek_api_key():
    """Guide user through fixing DeepSeek API key"""
    
    print("🔧 DeepSeek API Key Configuration Fix")
    print("=" * 50)
    
    # Check current key
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
        
        if 'DEEPSEEK_API_KEY=' in content:
            # Extract current key
            for line in content.split('\n'):
                if line.startswith('DEEPSEEK_API_KEY='):
                    current_key = line.split('=', 1)[1]
                    print(f"📋 Current API key: {current_key[:15]}...")
                    
                    if current_key in ['your-deepseek-api-key-here', 'placeholder-key']:
                        print("❌ This is a placeholder/invalid key!")
                        print()
                        print("🚀 To fix this:")
                        print("1. Go to: https://platform.deepseek.com/")
                        print("2. Sign up or login to your account")
                        print("3. Navigate to 'API Keys' section")
                        print("4. Create a new API key")
                        print("5. Copy the key (starts with 'sk-')")
                        print()
                        print("6. Then run this command to update:")
                        print("   python fix_deepseek_api_key.py --update YOUR_NEW_API_KEY")
                        print()
                        print("💡 Example:")
                        print("   python fix_deepseek_api_key.py --update sk-1234567890abcdef...")
                        
                    else:
                        print("✅ API key format looks correct")
                        print("🔍 Testing API connection...")
                        
                        # Test the API
                        import requests
                        try:
                            headers = {
                                "Authorization": f"Bearer {current_key}",
                                "Content-Type": "application/json"
                            }
                            
                            data = {
                                "model": "deepseek-chat",
                                "messages": [{"role": "user", "content": "Hello"}],
                                "max_tokens": 10
                            }
                            
                            response = requests.post(
                                "https://api.deepseek.com/v1/chat/completions",
                                headers=headers,
                                json=data,
                                timeout=10
                            )
                            
                            if response.status_code == 200:
                                print("✅ API key is working!")
                                return True
                            else:
                                print(f"❌ API Error: {response.status_code}")
                                print(f"Response: {response.text}")
                                print()
                                print("🔧 Possible issues:")
                                print("- API key is expired")
                                print("- No credits in your DeepSeek account")
                                print("- API key is not activated")
                                print("- Try generating a new API key")
                                
                        except Exception as e:
                            print(f"❌ Connection error: {e}")
                    
                    break
        else:
            print("❌ DEEPSEEK_API_KEY not found in .env file")
    else:
        print("❌ .env file not found")
    
    return False

def update_api_key(new_key: str):
    """Update the API key in .env file"""
    
    if not new_key.startswith('sk-'):
        print("❌ Invalid API key format. DeepSeek API keys should start with 'sk-'")
        return False
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    # Read current content
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update the API key line
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('DEEPSEEK_API_KEY='):
            lines[i] = f'DEEPSEEK_API_KEY={new_key}\n'
            updated = True
            break
    
    if not updated:
        # Add the API key if not found
        lines.append(f'\nDEEPSEEK_API_KEY={new_key}\n')
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ API key updated successfully!")
    print(f"📋 New key: {new_key[:15]}...{new_key[-10:]}")
    
    # Test the new key
    print("🔍 Testing new API key...")
    return fix_deepseek_api_key()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 2 and sys.argv[1] == '--update':
        new_key = sys.argv[2]
        update_api_key(new_key)
    else:
        fix_deepseek_api_key()