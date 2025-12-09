#!/usr/bin/env python3
"""
Fix Supabase header issues in database_manager.py
"""

db_manager_path = "/Users/kabellatsang/PycharmProjects/ai_code/scraper/core/database_manager.py"

with open(db_manager_path, 'r', encoding='utf-8') as f:
    content = f.read()

# The issue is that supabase 1.0.3 might have issues with the key format
# Let's ensure the key is properly stripped and validated
new_connect_method = '''    def connect_to_supabase(self) -> bool:
        """
        Connect to Supabase database
        Returns True if successful, False otherwise
        """
        try:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')
            
            if not url or not key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
            
            # Clean the credentials
            url = url.strip()
            key = key.strip()
            
            # Validate URL format
            if not url.startswith('https://'):
                raise ValueError(f"Invalid SUPABASE_URL format: {url}")
            
            # Validate key format (should start with eyJ for JWT)
            if not key.startswith('eyJ'):
                raise ValueError("Invalid SUPABASE_KEY format")
            
            # Create client
            self.supabase = create_client(url, key)
            
            # Test connection by making a simple query
            self.supabase.table('articles').select('id').limit(1).execute()
            
            print(f"✅ Connected to Supabase: {url}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            return False'''

# Find and replace the connect method
import re
pattern = r'    def connect_to_supabase\(self\) -> bool:.*?return False'
content = re.sub(pattern, new_connect_method, content, flags=re.DOTALL)

with open(db_manager_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed database_manager.py")
print("\nNow run:")
print("cd /Users/kabellatsang/PycharmProjects/ai_code")
print("git add scraper/core/database_manager.py")
print('git commit -m "Fix Supabase header validation"')
print("git push origin main")
