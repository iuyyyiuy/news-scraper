#!/usr/bin/env python3
"""Test if table structure is correct"""
import sys
sys.path.insert(0, '/Users/kabellatsang/PycharmProjects/ai_code')

from scraper.core.database_manager import DatabaseManager

db = DatabaseManager()

if db.supabase:
    print("✅ Connected to Supabase")
    
    # Try to query the table structure
    try:
        # Try a simple select to see what columns exist
        response = db.supabase.table('articles').select('*').limit(0).execute()
        print("✅ Table 'articles' exists and is accessible")
        print()
        
        # Try to insert a test record
        test_data = {
            'publication_date': '2025/12/5',
            'title': 'Test',
            'body_text': 'Test body',
            'url': 'https://test.com/unique123',
            'source': 'test',
            'matched_keywords': ['test']
        }
        
        print("Attempting to insert test record...")
        response = db.supabase.table('articles').insert(test_data).execute()
        
        if response.data:
            print("✅ SUCCESS! Insert worked!")
            print(f"Inserted record: {response.data}")
        else:
            print("❌ Insert failed - no data returned")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Failed to connect")
