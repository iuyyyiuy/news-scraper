#!/usr/bin/env python3
"""
Monthly Cleanup Scheduler
Automatically cleans up old articles on the 1st of each month
"""
import schedule
import time
from datetime import datetime, timedelta
from scraper.core.database_manager import DatabaseManager

def cleanup_last_month():
    """Delete all articles from the previous month"""
    db = DatabaseManager()
    
    # Get first day of current month
    today = datetime.now()
    first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    print(f"\n{'='*60}")
    print(f"🗑️  Monthly Cleanup - {today.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    print(f"Deleting articles before: {first_day_of_month.date()}")
    
    # Delete old articles
    deleted_count = db.delete_old_articles(first_day_of_month)
    
    print(f"✅ Cleanup complete! Deleted {deleted_count} articles")
    print(f"{'='*60}\n")

def run_scheduler():
    """Run the monthly cleanup scheduler"""
    # Schedule cleanup for 1st of every month at 00:05 (5 minutes after midnight)
    schedule.every().month.at("00:05").do(cleanup_last_month)
    
    print("="*60)
    print("🗓️  Monthly Cleanup Scheduler Started")
    print("="*60)
    print("📅 Cleanup runs on: 1st of every month at 00:05")
    print("🗑️  Deletes: All articles from previous months")
    print("💾 Keeps: Current month's articles")
    print("="*60)
    print()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    # For testing: run cleanup immediately
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("🧪 Running test cleanup...")
        cleanup_last_month()
    else:
        run_scheduler()
