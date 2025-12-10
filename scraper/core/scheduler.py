"""
Scheduler Service for News Database Feature
Manages scheduled tasks for daily scraping and monthly cleanup
"""
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from .scheduled_scraper import ScheduledScraper
from .database_manager import DatabaseManager


class SchedulerService:
    """Manages scheduled tasks for automated scraping and cleanup"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Shanghai'))
        self.scheduled_scraper = ScheduledScraper()
        self.db_manager = DatabaseManager()
        self.last_scrape_result = None
    
    def schedule_daily_scrape(self):
        """
        Schedule daily scraping at 11:30 AM UTC+8
        """
        try:
            # TEST: Schedule for 10:55 AM HKT for immediate testing
            self.scheduler.add_job(
                func=self._run_daily_scrape,
                trigger=CronTrigger(hour=10, minute=55, timezone=pytz.timezone('Asia/Shanghai')),
                id='daily_scrape',
                name='Daily News Scraping',
                replace_existing=True
            )
            print("✅ Scheduled daily scrape at 10:55 AM HKT for testing")
            
        except Exception as e:
            print(f"❌ Error scheduling daily scrape: {e}")
    
    def schedule_monthly_cleanup(self):
        """
        Schedule monthly cleanup on the 1st at 00:00 UTC+8
        """
        try:
            # Schedule for 1st of each month at midnight
            self.scheduler.add_job(
                func=self._run_monthly_cleanup,
                trigger=CronTrigger(day=1, hour=0, minute=0, timezone=pytz.timezone('Asia/Shanghai')),
                id='monthly_cleanup',
                name='Monthly Article Cleanup',
                replace_existing=True
            )
            print("✅ Scheduled monthly cleanup on 1st at 00:00 UTC+8")
            
        except Exception as e:
            print(f"❌ Error scheduling monthly cleanup: {e}")
    
    def start_scheduler(self):
        """
        Start the scheduler service
        """
        try:
            if not self.scheduler.running:
                self.schedule_daily_scrape()
                self.schedule_monthly_cleanup()
                self.scheduler.start()
                print("✅ Scheduler service started")
                self._print_scheduled_jobs()
            else:
                print("⚠️  Scheduler is already running")
                
        except Exception as e:
            print(f"❌ Error starting scheduler: {e}")
    
    def stop_scheduler(self):
        """
        Stop the scheduler service
        """
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                print("✅ Scheduler service stopped")
            else:
                print("⚠️  Scheduler is not running")
                
        except Exception as e:
            print(f"❌ Error stopping scheduler: {e}")
    
    def _run_daily_scrape(self):
        """
        Execute daily scraping task
        """
        print("\n" + "="*60)
        print("🤖 SCHEDULED TASK: Daily Scrape")
        print("="*60 + "\n")
        
        try:
            self.last_scrape_result = self.scheduled_scraper.scrape_daily()
            print("\n✅ Daily scrape completed successfully")
            
        except Exception as e:
            print(f"\n❌ Daily scrape failed: {e}")
            self.last_scrape_result = {
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    def _run_monthly_cleanup(self):
        """
        Execute monthly cleanup task
        """
        print("\n" + "="*60)
        print("🗑️  SCHEDULED TASK: Monthly Cleanup")
        print("="*60 + "\n")
        
        try:
            # Calculate first day of current month
            now = datetime.now()
            first_day_of_month = datetime(now.year, now.month, 1)
            
            # Delete articles before this month
            deleted_count = self.db_manager.delete_old_articles(first_day_of_month)
            
            print(f"\n✅ Monthly cleanup completed: {deleted_count} articles deleted")
            
        except Exception as e:
            print(f"\n❌ Monthly cleanup failed: {e}")
    
    def get_next_run_times(self) -> dict:
        """
        Get next scheduled run times for all jobs
        
        Returns:
            Dictionary with job names and next run times
        """
        next_runs = {}
        
        try:
            for job in self.scheduler.get_jobs():
                next_runs[job.name] = job.next_run_time
                
        except Exception as e:
            print(f"❌ Error getting next run times: {e}")
        
        return next_runs
    
    def get_scheduler_status(self) -> dict:
        """
        Get current scheduler status
        
        Returns:
            Dictionary with scheduler information
        """
        status = {
            'running': self.scheduler.running if self.scheduler else False,
            'jobs': [],
            'last_scrape': None
        }
        
        try:
            if self.scheduler and self.scheduler.running:
                for job in self.scheduler.get_jobs():
                    status['jobs'].append({
                        'id': job.id,
                        'name': job.name,
                        'next_run': job.next_run_time.isoformat() if job.next_run_time else None
                    })
            
            # Get last scrape time from database
            last_scrape_time = self.db_manager.get_last_scrape_time()
            if last_scrape_time:
                status['last_scrape'] = last_scrape_time.isoformat()
            
            # Include last scrape result if available
            if self.last_scrape_result:
                status['last_scrape_result'] = self.last_scrape_result
                
        except Exception as e:
            print(f"❌ Error getting scheduler status: {e}")
        
        return status
    
    def _print_scheduled_jobs(self):
        """Print information about scheduled jobs"""
        print("\n📅 Scheduled Jobs:")
        for job in self.scheduler.get_jobs():
            print(f"  - {job.name}")
            print(f"    ID: {job.id}")
            print(f"    Next run: {job.next_run_time}")
        print()
    
    def trigger_scrape_now(self):
        """
        Manually trigger a scrape immediately (for testing)
        """
        print("\n🚀 Manually triggering scrape...")
        self._run_daily_scrape()


# Test when run directly
if __name__ == "__main__":
    print("🧪 Testing Scheduler Service\n")
    
    scheduler_service = SchedulerService()
    
    # Start scheduler
    scheduler_service.start_scheduler()
    
    # Get status
    status = scheduler_service.get_scheduler_status()
    print(f"\n📊 Scheduler Status:")
    print(f"  Running: {status['running']}")
    print(f"  Jobs: {len(status['jobs'])}")
    
    for job in status['jobs']:
        print(f"\n  Job: {job['name']}")
        print(f"    Next run: {job['next_run']}")
    
    print("\n✅ Scheduler test complete!")
    print("⚠️  Note: Scheduler is running in background. Press Ctrl+C to stop.")
    
    # Keep running for testing
    try:
        import time
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping scheduler...")
        scheduler_service.stop_scheduler()
        print("✅ Scheduler stopped")
