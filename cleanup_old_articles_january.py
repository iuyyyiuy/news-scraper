#!/usr/bin/env python3
"""
Clean up old articles - Keep only January 2026 articles
Remove all articles from before 2026-01-01 to speed up dashboard
"""

import os
import sys
from datetime import datetime, date
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def cleanup_old_articles():
    """Remove all articles before January 2026"""
    
    print("🧹 Cleaning up old articles - Keep only January 2026")
    print("=" * 60)
    
    # Initialize Supabase client
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: Supabase credentials not found")
        return False
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print(f"✅ Connected to Supabase: {supabase_url}")
        
        # First, check current article count
        print("\n📊 Current database status:")
        
        # Count total articles
        total_response = supabase.table('articles').select('id', count='exact').execute()
        total_count = len(total_response.data) if total_response.data else 0
        print(f"   Total articles: {total_count}")
        
        # Count articles from January 2026
        january_response = supabase.table('articles').select('id', count='exact').gte('date', '2026-01-01').execute()
        january_count = len(january_response.data) if january_response.data else 0
        print(f"   January 2026 articles: {january_count}")
        
        # Count articles to be deleted (before 2026-01-01)
        old_count = total_count - january_count
        print(f"   Articles to delete: {old_count}")
        
        if old_count == 0:
            print("\n✅ No old articles to delete - database is already clean!")
            return True
        
        # Confirm deletion
        print(f"\n⚠️  This will DELETE {old_count} articles from before 2026-01-01")
        print("   Only January 2026 articles will remain")
        
        # Delete old articles
        print(f"\n🗑️  Deleting {old_count} old articles...")
        
        delete_response = supabase.table('articles').delete().lt('date', '2026-01-01').execute()
        
        if delete_response.data is not None:
            deleted_count = len(delete_response.data)
            print(f"✅ Successfully deleted {deleted_count} old articles")
        else:
            print("✅ Old articles deleted successfully")
        
        # Verify cleanup
        print("\n📊 After cleanup:")
        final_response = supabase.table('articles').select('id', count='exact').execute()
        final_count = len(final_response.data) if final_response.data else 0
        print(f"   Remaining articles: {final_count}")
        
        # Show sample of remaining articles
        sample_response = supabase.table('articles').select('date, title, source').order('date', desc=True).limit(5).execute()
        
        if sample_response.data:
            print("\n📰 Sample of remaining articles:")
            for i, article in enumerate(sample_response.data, 1):
                print(f"   {i}. {article['date']} - {article['title'][:60]}... ({article['source']})")
        
        print(f"\n🎉 Cleanup completed successfully!")
        print(f"📈 Database size reduced by {old_count} articles")
        print(f"⚡ Dashboard should load faster now")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")
        return False

def verify_cleanup():
    """Verify that only January 2026 articles remain"""
    
    print("\n🔍 Verifying cleanup results...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Check date range
        response = supabase.table('articles').select('date').order('date', desc=False).limit(1).execute()
        
        if response.data:
            oldest_date = response.data[0]['date']
            print(f"   Oldest article date: {oldest_date}")
            
            if oldest_date >= '2026-01-01':
                print("✅ Verification passed - all articles are from January 2026 or later")
                return True
            else:
                print(f"⚠️  Warning: Found articles older than 2026-01-01")
                return False
        else:
            print("ℹ️  No articles found in database")
            return True
            
    except Exception as e:
        print(f"❌ Verification error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧹 JANUARY 2026 ARTICLE CLEANUP")
    print("=" * 60)
    print("This will remove all articles from before 2026-01-01")
    print("Only current month (January 2026) articles will remain")
    print("This will speed up the dashboard significantly")
    print("=" * 60)
    
    if cleanup_old_articles():
        if verify_cleanup():
            print("\n✅ SUCCESS: Old articles cleaned up successfully")
            print("📱 Dashboard should now load faster")
            print("🔄 Refresh your dashboard to see the results")
        else:
            print("\n⚠️  Cleanup completed but verification failed")
    else:
        print("\n❌ FAILED: Cleanup was not successful")
        sys.exit(1)