#!/usr/bin/env python3
"""
Monthly Cleanup Scheduler
Automatically cleans up old articles on the 1st of each month.

This scheduler ensures that only the current month's articles are kept in the database.
Articles from previous months are automatically deleted on the 1st of each month at 00:05.

Usage:
    python monthly_cleanup_scheduler.py              # Run scheduler (production)
    python monthly_cleanup_scheduler.py --test       # Run cleanup immediately (testing)
    python monthly_cleanup_scheduler.py --dry-run    # Preview what would be deleted
"""
import schedule
import time
import logging
from datetime import datetime, timedelta
from scraper.core.database_manager import DatabaseManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monthly_cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def cleanup_last_month(dry_run: bool = False):
    """
    Delete all articles from previous months, keeping only current month's articles.
    
    Args:
        dry_run: If True, only preview what would be deleted without actually deleting
    """
    db = DatabaseManager()
    
    # Get first day of current month
    today = datetime.now()
    first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    logger.info("="*60)
    logger.info(f"🗑️  Monthly Cleanup - {today.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)
    logger.info(f"Cutoff date: {first_day_of_month.date()}")
    logger.info(f"Will delete: Articles before {first_day_of_month.date()}")
    logger.info(f"Will keep: Articles from {first_day_of_month.date()} onwards")
    
    try:
        # Get count of articles before deletion
        total_before = db.get_total_count()
        logger.info(f"Total articles before cleanup: {total_before}")
        
        # Preview articles to be deleted
        try:
            old_articles_response = db.supabase.table('articles').select('id, date, title').lt('date', first_day_of_month.isoformat()).execute()
            old_articles = old_articles_response.data if old_articles_response.data else []
            logger.info(f"Articles to be deleted: {len(old_articles)}")
            
            if old_articles and len(old_articles) > 0:
                logger.info("Preview of articles to be deleted (first 5):")
                for i, article in enumerate(old_articles[:5]):
                    logger.info(f"  {i+1}. {article['date']} - {article['title'][:60]}...")
                if len(old_articles) > 5:
                    logger.info(f"  ... and {len(old_articles) - 5} more")
        except Exception as e:
            logger.warning(f"Could not preview articles: {e}")
        
        if dry_run:
            logger.info("🔍 DRY RUN MODE - No articles will be deleted")
            logger.info(f"Would delete {len(old_articles)} articles")
            logger.info("="*60)
            return 0
        
        # Delete old articles
        deleted_count = db.delete_old_articles(first_day_of_month)
        
        # Get count after deletion
        total_after = db.get_total_count()
        
        logger.info(f"✅ Cleanup complete!")
        logger.info(f"   Articles before: {total_before}")
        logger.info(f"   Articles deleted: {deleted_count}")
        logger.info(f"   Articles after: {total_after}")
        logger.info(f"   Retention: Current month only ({first_day_of_month.strftime('%Y-%m')})")
        logger.info("="*60)
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")
        logger.error("="*60)
        return 0

def calculate_next_cleanup():
    """Calculate when the next cleanup will occur."""
    today = datetime.now()
    
    # Next cleanup is on the 1st of next month at 00:05
    if today.month == 12:
        next_cleanup = datetime(today.year + 1, 1, 1, 0, 5)
    else:
        next_cleanup = datetime(today.year, today.month + 1, 1, 0, 5)
    
    return next_cleanup

def run_scheduler():
    """Run the monthly cleanup scheduler."""
    # Schedule cleanup for 1st of every month at 00:05 (5 minutes after midnight)
    schedule.every().day.at("00:05").do(lambda: cleanup_if_first_of_month())
    
    next_cleanup = calculate_next_cleanup()
    days_until = (next_cleanup - datetime.now()).days
    
    logger.info("="*60)
    logger.info("🗓️  Monthly Cleanup Scheduler Started")
    logger.info("="*60)
    logger.info(f"📅 Cleanup schedule: 1st of every month at 00:05")
    logger.info(f"🗑️  Retention policy: Keep current month only")
    logger.info(f"💾 Articles kept: From 1st of current month onwards")
    logger.info(f"🕐 Next cleanup: {next_cleanup.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"⏳ Days until next cleanup: {days_until}")
    logger.info("="*60)
    logger.info("")
    
    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("\n🛑 Scheduler stopped by user")
    except Exception as e:
        logger.error(f"❌ Scheduler error: {e}")

def cleanup_if_first_of_month():
    """Run cleanup only if today is the 1st of the month."""
    today = datetime.now()
    if today.day == 1:
        logger.info("📅 Today is the 1st of the month - running cleanup")
        cleanup_last_month()
    else:
        logger.debug(f"Not the 1st of month (today is {today.day}), skipping cleanup")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            logger.info("🧪 Running test cleanup (immediate execution)...")
            cleanup_last_month()
        elif sys.argv[1] == "--dry-run":
            logger.info("🔍 Running dry-run (preview only)...")
            cleanup_last_month(dry_run=True)
        elif sys.argv[1] == "--help":
            print(__doc__)
        else:
            logger.error(f"Unknown option: {sys.argv[1]}")
            print(__doc__)
    else:
        run_scheduler()
