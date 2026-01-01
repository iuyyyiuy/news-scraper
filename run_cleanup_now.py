#!/usr/bin/env python3
"""
Run Monthly Cleanup NOW - Delete 2025 articles immediately
Forces the cleanup to run regardless of date
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automated_monthly_cleanup import MonthlyCleanupScheduler

def force_cleanup_now():
    """Force run the cleanup immediately, bypassing date checks"""
    
    print("🚀 FORCING MONTHLY CLEANUP TO RUN NOW")
    print("=" * 60)
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Target: Delete all 2025 articles, keep only 2026-01-XX articles")
    print("=" * 60)
    
    try:
        # Create cleanup scheduler
        cleanup_scheduler = MonthlyCleanupScheduler()
        
        # Override the date check by directly calling cleanup methods
        print("📊 Getting current database status...")
        
        # Get cleanup threshold (2026/01/01)
        threshold_date = cleanup_scheduler.get_cleanup_date_threshold()
        print(f"📅 Cleanup threshold: {threshold_date}")
        
        # Get counts before cleanup
        articles_to_delete = cleanup_scheduler.get_articles_to_delete_count(threshold_date)
        articles_to_keep = cleanup_scheduler.get_articles_to_keep_count(threshold_date)
        
        print(f"📊 Current Status:")
        print(f"   🗑️  Articles to DELETE: {articles_to_delete} (2025 and older)")
        print(f"   💾 Articles to KEEP: {articles_to_keep} (2026-01-XX)")
        print(f"   📈 Total articles: {articles_to_delete + articles_to_keep}")
        
        if articles_to_delete == 0:
            print("✅ No old articles to delete - database is already clean!")
            return True
        
        # Confirm deletion
        print("\n" + "⚠️ " * 20)
        print("⚠️  WARNING: This will PERMANENTLY DELETE articles!")
        print(f"⚠️  {articles_to_delete} articles from 2025 will be removed")
        print("⚠️ " * 20)
        
        confirm = input(f"\nType 'DELETE {articles_to_delete}' to confirm deletion: ")
        
        if confirm != f"DELETE {articles_to_delete}":
            print("❌ Deletion cancelled - confirmation text didn't match")
            return False
        
        print("\n🔄 Starting cleanup process...")
        
        # Create backup summary
        print("📁 Creating backup summary...")
        backup_summary = cleanup_scheduler.create_backup_summary(threshold_date)
        
        if backup_summary:
            print("✅ Backup summary created successfully")
        else:
            print("⚠️ Backup summary creation failed, but continuing...")
        
        # Perform the actual cleanup
        print(f"🗑️ DELETING {articles_to_delete} articles...")
        cleanup_results = cleanup_scheduler.perform_cleanup(threshold_date)
        
        if cleanup_results.get('success'):
            print("\n" + "🎉" * 20)
            print("🎉 CLEANUP COMPLETED SUCCESSFULLY!")
            print("🎉" * 20)
            print(f"✅ Deleted: {articles_to_delete} old articles")
            print(f"✅ Remaining: {cleanup_results.get('articles_remaining', 0)} current articles")
            print(f"✅ Duration: {cleanup_results.get('duration_seconds', 0):.2f} seconds")
            print(f"✅ Your dashboard is now clean and fast!")
            
            return True
        else:
            print("❌ CLEANUP FAILED!")
            print(f"❌ Error: {cleanup_results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Critical error during cleanup: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    success = force_cleanup_now()
    
    if success:
        print("\n📋 SUMMARY:")
        print("✅ Old articles deleted successfully")
        print("✅ Database now contains only 2026-01-XX articles")
        print("✅ Dashboard will load faster")
        print("✅ Monthly auto-cleanup still scheduled for future months")
        sys.exit(0)
    else:
        print("\n❌ Cleanup failed - please check errors above")
        sys.exit(1)

if __name__ == "__main__":
    main()