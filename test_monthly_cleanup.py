#!/usr/bin/env python3
"""
Test script for monthly cleanup functionality.
Tests the monthly cleanup system that keeps articles for one month.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.core.database_manager import DatabaseManager

def test_monthly_cleanup():
    """Test the monthly cleanup functionality."""
    
    print("🧪 Testing Monthly Cleanup System")
    print("=" * 60)
    
    # Initialize database manager
    db = DatabaseManager()
    
    if not db.supabase:
        print("❌ Failed to connect to database")
        return False
    
    # Get current article count
    total_articles = db.get_total_count()
    print(f"📊 Current total articles: {total_articles}")
    
    # Calculate cleanup date (first day of current month)
    today = datetime.now()
    first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    print(f"📅 Current date: {today.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🗑️  Cleanup cutoff: {first_day_of_month.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💾 Will keep: Articles from {first_day_of_month.strftime('%Y-%m-%d')} onwards")
    print(f"🗑️  Will delete: Articles before {first_day_of_month.strftime('%Y-%m-%d')}")
    
    # Get articles that would be deleted (for preview)
    try:
        # Query articles before the cutoff date
        old_articles_response = db.supabase.table('articles').select('id, date, title').lt('date', first_day_of_month.isoformat()).execute()
        old_articles = old_articles_response.data if old_articles_response.data else []
        
        print(f"\n📋 Articles that would be deleted: {len(old_articles)}")
        
        if old_articles:
            print("   Preview (first 5):")
            for i, article in enumerate(old_articles[:5]):
                print(f"   {i+1}. {article['date']} - {article['title'][:50]}...")
            
            if len(old_articles) > 5:
                print(f"   ... and {len(old_articles) - 5} more")
        
        # Get articles that would be kept
        current_articles_response = db.supabase.table('articles').select('id, date, title').gte('date', first_day_of_month.isoformat()).execute()
        current_articles = current_articles_response.data if current_articles_response.data else []
        
        print(f"\n💾 Articles that would be kept: {len(current_articles)}")
        
        if current_articles:
            print("   Preview (first 5):")
            for i, article in enumerate(current_articles[:5]):
                print(f"   {i+1}. {article['date']} - {article['title'][:50]}...")
            
            if len(current_articles) > 5:
                print(f"   ... and {len(current_articles) - 5} more")
        
    except Exception as e:
        print(f"❌ Error querying articles: {e}")
        return False
    
    # Ask for confirmation before actual cleanup
    print(f"\n⚠️  Monthly Cleanup Preview Complete")
    print(f"   Total articles: {total_articles}")
    print(f"   Would delete: {len(old_articles)} articles")
    print(f"   Would keep: {len(current_articles)} articles")
    
    # For testing, we'll do a dry run unless explicitly requested
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        print(f"\n🚨 EXECUTING ACTUAL CLEANUP...")
        
        # Perform the actual cleanup
        deleted_count = db.delete_old_articles(first_day_of_month)
        
        # Verify results
        new_total = db.get_total_count()
        
        print(f"\n✅ Cleanup Results:")
        print(f"   Articles before: {total_articles}")
        print(f"   Articles deleted: {deleted_count}")
        print(f"   Articles after: {new_total}")
        print(f"   Expected after: {len(current_articles)}")
        
        if new_total == len(current_articles):
            print(f"✅ Cleanup successful! Article count matches expected.")
            return True
        else:
            print(f"⚠️  Article count mismatch. Expected {len(current_articles)}, got {new_total}")
            return False
    
    else:
        print(f"\n💡 This was a DRY RUN. No articles were deleted.")
        print(f"   To execute actual cleanup, run: python test_monthly_cleanup.py --execute")
        return True

def show_cleanup_schedule():
    """Show when the next cleanup would occur."""
    
    print("\n📅 Monthly Cleanup Schedule")
    print("=" * 40)
    
    today = datetime.now()
    
    # Calculate next cleanup date
    if today.day == 1:
        # If today is the 1st, next cleanup is next month
        if today.month == 12:
            next_cleanup = datetime(today.year + 1, 1, 1, 0, 5)  # January 1st next year
        else:
            next_cleanup = datetime(today.year, today.month + 1, 1, 0, 5)
    else:
        # Next cleanup is the 1st of next month
        if today.month == 12:
            next_cleanup = datetime(today.year + 1, 1, 1, 0, 5)  # January 1st next year
        else:
            next_cleanup = datetime(today.year, today.month + 1, 1, 0, 5)
    
    days_until = (next_cleanup - today).days
    
    print(f"🗓️  Current date: {today.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🕐 Next cleanup: {next_cleanup.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏳ Days until cleanup: {days_until}")
    
    # Show what would be kept after next cleanup
    next_cutoff = next_cleanup.replace(hour=0, minute=0, second=0, microsecond=0)
    print(f"💾 After next cleanup, will keep articles from: {next_cutoff.strftime('%Y-%m-%d')} onwards")

if __name__ == "__main__":
    print("🗑️  Monthly News Database Cleanup System")
    print("=" * 60)
    
    # Show schedule information
    show_cleanup_schedule()
    
    # Run cleanup test
    success = test_monthly_cleanup()
    
    if success:
        print(f"\n✅ Monthly Cleanup Test Complete!")
    else:
        print(f"\n❌ Monthly Cleanup Test Failed!")
    
    print("=" * 60)