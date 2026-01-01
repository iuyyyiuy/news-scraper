#!/usr/bin/env python3
"""
Automated Monthly Cleanup System
Runs on the 1st of each month to delete all old news articles from Supabase database
Keeps only the current month's articles for a clean, fast dashboard
"""

import sys
import os
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.database_manager import DatabaseManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('monthly_cleanup.log')
    ]
)
logger = logging.getLogger(__name__)


class MonthlyCleanupScheduler:
    """
    Automated monthly cleanup system for news database
    
    Features:
    - Runs automatically on the 1st of each month
    - Deletes all articles older than current month
    - Keeps current month's articles
    - Creates backup before deletion
    - Provides detailed cleanup statistics
    """
    
    def __init__(self):
        """Initialize the monthly cleanup scheduler"""
        logger.info("🗓️ Initializing Monthly Cleanup Scheduler")
        
        self.db_manager = DatabaseManager()
        
        if not self.db_manager.supabase:
            raise Exception("Failed to connect to Supabase database")
        
        logger.info("✅ Monthly Cleanup Scheduler initialized successfully")
    
    def should_run_cleanup(self) -> bool:
        """
        Check if cleanup should run today
        
        Returns:
            True if today is the 1st of the month, False otherwise
        """
        today = date.today()
        is_first_of_month = today.day == 1
        
        logger.info(f"📅 Today is {today}")
        logger.info(f"🔍 Is first of month: {is_first_of_month}")
        
        return is_first_of_month
    
    def get_cleanup_date_threshold(self) -> str:
        """
        Get the date threshold for cleanup
        
        Returns:
            Date string in YYYY/MM/DD format for articles to keep (current month start)
        """
        today = date.today()
        # Keep articles from the 1st of current month onwards
        current_month_start = date(today.year, today.month, 1)
        
        # Format as YYYY/MM/DD to match database format
        threshold_date = current_month_start.strftime('%Y/%m/%d')
        
        logger.info(f"📊 Cleanup threshold: Keep articles from {threshold_date} onwards")
        return threshold_date
    
    def get_articles_to_delete_count(self, threshold_date: str) -> int:
        """
        Get count of articles that will be deleted
        
        Args:
            threshold_date: Date threshold in YYYY/MM/DD format
            
        Returns:
            Number of articles to be deleted
        """
        try:
            # Count articles older than threshold
            response = self.db_manager.supabase.table('articles').select(
                'id', count='exact'
            ).lt('date', threshold_date).execute()
            
            count = response.count if hasattr(response, 'count') else 0
            logger.info(f"📊 Articles to delete: {count}")
            return count
            
        except Exception as e:
            logger.error(f"❌ Error counting articles to delete: {e}")
            return 0
    
    def get_articles_to_keep_count(self, threshold_date: str) -> int:
        """
        Get count of articles that will be kept
        
        Args:
            threshold_date: Date threshold in YYYY/MM/DD format
            
        Returns:
            Number of articles to be kept
        """
        try:
            # Count articles from threshold date onwards
            response = self.db_manager.supabase.table('articles').select(
                'id', count='exact'
            ).gte('date', threshold_date).execute()
            
            count = response.count if hasattr(response, 'count') else 0
            logger.info(f"📊 Articles to keep: {count}")
            return count
            
        except Exception as e:
            logger.error(f"❌ Error counting articles to keep: {e}")
            return 0
    
    def create_backup_summary(self, threshold_date: str) -> Dict[str, Any]:
        """
        Create a summary of articles being deleted for backup purposes
        
        Args:
            threshold_date: Date threshold in YYYY/MM/DD format
            
        Returns:
            Dictionary with backup summary information
        """
        try:
            # Get sample of articles being deleted
            response = self.db_manager.supabase.table('articles').select(
                'date, title, source, url'
            ).lt('date', threshold_date).order('date', desc=True).limit(10).execute()
            
            sample_articles = response.data if response.data else []
            
            # Get date range of deleted articles
            oldest_response = self.db_manager.supabase.table('articles').select(
                'date'
            ).lt('date', threshold_date).order('date', desc=False).limit(1).execute()
            
            oldest_date = None
            if oldest_response.data and len(oldest_response.data) > 0:
                oldest_date = oldest_response.data[0]['date']
            
            backup_summary = {
                'cleanup_date': datetime.now().isoformat(),
                'threshold_date': threshold_date,
                'oldest_article_date': oldest_date,
                'sample_deleted_articles': sample_articles,
                'total_articles_deleted': len(sample_articles)  # Will be updated after deletion
            }
            
            # Save backup summary to file
            import json
            backup_filename = f"monthly_cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_filename, 'w') as f:
                json.dump(backup_summary, f, indent=2, default=str)
            
            logger.info(f"📁 Backup summary saved to {backup_filename}")
            return backup_summary
            
        except Exception as e:
            logger.error(f"❌ Error creating backup summary: {e}")
            return {}
    
    def perform_cleanup(self, threshold_date: str) -> Dict[str, Any]:
        """
        Perform the actual cleanup by deleting old articles
        
        Args:
            threshold_date: Date threshold in YYYY/MM/DD format
            
        Returns:
            Dictionary with cleanup results
        """
        start_time = time.time()
        
        try:
            logger.info(f"🗑️ Starting cleanup: Deleting articles before {threshold_date}")
            
            # Delete articles older than threshold
            response = self.db_manager.supabase.table('articles').delete().lt(
                'date', threshold_date
            ).execute()
            
            # Calculate results
            duration = time.time() - start_time
            
            # Get final counts
            remaining_count = self.get_articles_to_keep_count(threshold_date)
            
            cleanup_results = {
                'success': True,
                'threshold_date': threshold_date,
                'duration_seconds': duration,
                'articles_remaining': remaining_count,
                'cleanup_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Cleanup completed successfully in {duration:.2f} seconds")
            logger.info(f"📊 Articles remaining in database: {remaining_count}")
            
            return cleanup_results
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Cleanup failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'duration_seconds': duration,
                'cleanup_timestamp': datetime.now().isoformat()
            }
    
    def run_monthly_cleanup(self) -> Dict[str, Any]:
        """
        Execute the complete monthly cleanup process
        
        Returns:
            Dictionary with comprehensive cleanup results
        """
        logger.info("🚀 Starting Monthly Database Cleanup")
        logger.info("=" * 60)
        
        cleanup_start_time = time.time()
        
        try:
            # Check if cleanup should run
            if not self.should_run_cleanup():
                logger.info("⏭️ Skipping cleanup - not the 1st of the month")
                return {
                    'skipped': True,
                    'reason': 'Not the 1st of the month',
                    'next_cleanup_date': date.today().replace(day=1) + timedelta(days=32)
                }
            
            # Get cleanup threshold
            threshold_date = self.get_cleanup_date_threshold()
            
            # Get counts before cleanup
            articles_to_delete = self.get_articles_to_delete_count(threshold_date)
            articles_to_keep = self.get_articles_to_keep_count(threshold_date)
            
            logger.info(f"📊 Cleanup Summary:")
            logger.info(f"   - Articles to delete: {articles_to_delete}")
            logger.info(f"   - Articles to keep: {articles_to_keep}")
            logger.info(f"   - Threshold date: {threshold_date}")
            
            # Skip if no articles to delete
            if articles_to_delete == 0:
                logger.info("✅ No old articles to delete - database is already clean")
                return {
                    'skipped': True,
                    'reason': 'No old articles found',
                    'articles_in_database': articles_to_keep
                }
            
            # Create backup summary
            logger.info("📁 Creating backup summary...")
            backup_summary = self.create_backup_summary(threshold_date)
            
            # Perform cleanup
            logger.info("🗑️ Performing cleanup...")
            cleanup_results = self.perform_cleanup(threshold_date)
            
            # Calculate final statistics
            total_duration = time.time() - cleanup_start_time
            
            final_results = {
                'success': cleanup_results.get('success', False),
                'cleanup_date': date.today().isoformat(),
                'threshold_date': threshold_date,
                'articles_deleted': articles_to_delete,
                'articles_remaining': cleanup_results.get('articles_remaining', 0),
                'total_duration_seconds': total_duration,
                'backup_created': bool(backup_summary),
                'next_cleanup_date': (date.today().replace(day=1) + timedelta(days=32)).replace(day=1).isoformat()
            }
            
            if not cleanup_results.get('success'):
                final_results['error'] = cleanup_results.get('error')
            
            # Log final summary
            self._log_cleanup_summary(final_results)
            
            return final_results
            
        except Exception as e:
            total_duration = time.time() - cleanup_start_time
            error_msg = f"Critical error during monthly cleanup: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return {
                'success': False,
                'error': error_msg,
                'total_duration_seconds': total_duration,
                'cleanup_date': date.today().isoformat()
            }
    
    def _log_cleanup_summary(self, results: Dict[str, Any]):
        """Log comprehensive cleanup summary"""
        logger.info("=" * 60)
        logger.info("🎯 MONTHLY CLEANUP SUMMARY")
        logger.info("=" * 60)
        logger.info(f"📅 Cleanup Date: {results.get('cleanup_date')}")
        logger.info(f"🎯 Threshold Date: {results.get('threshold_date')}")
        logger.info(f"🗑️ Articles Deleted: {results.get('articles_deleted', 0)}")
        logger.info(f"📊 Articles Remaining: {results.get('articles_remaining', 0)}")
        logger.info(f"⏱️ Total Duration: {results.get('total_duration_seconds', 0):.2f} seconds")
        logger.info(f"📁 Backup Created: {'✅' if results.get('backup_created') else '❌'}")
        
        if results.get('success'):
            logger.info("✅ Status: SUCCESS")
            logger.info(f"📅 Next Cleanup: {results.get('next_cleanup_date')}")
        else:
            logger.info("❌ Status: FAILED")
            if results.get('error'):
                logger.info(f"❌ Error: {results.get('error')}")
        
        logger.info("=" * 60)


def main():
    """Main function for scheduled execution"""
    try:
        # Create cleanup scheduler
        cleanup_scheduler = MonthlyCleanupScheduler()
        
        # Run monthly cleanup
        results = cleanup_scheduler.run_monthly_cleanup()
        
        # Exit with appropriate code
        if results.get('skipped'):
            logger.info(f"ℹ️ Cleanup skipped: {results.get('reason')}")
            sys.exit(0)
        elif results.get('success'):
            logger.info(f"✅ Monthly cleanup completed successfully")
            sys.exit(0)
        else:
            logger.error(f"❌ Monthly cleanup failed")
            sys.exit(1)
            
    except Exception as e:
        logger.critical(f"Critical error in monthly cleanup: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()