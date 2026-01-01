"""
Simple Scheduler Service - Clean and Easy to Monitor
Focused on hourly news scraping with real-time status updates
"""
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleSchedulerService:
    """Simple, clean scheduler for automated news scraping"""
    
    def __init__(self, test_mode=False):
        logger.info(f"🚀 Initializing SimpleSchedulerService (test_mode={test_mode})")
        
        # Configuration
        self.test_mode = test_mode
        self.interval_minutes = 5 if test_mode else 60  # 5 min for testing, 60 for production
        
        # State
        self.is_running = False
        self.is_scheduled = False
        self.current_operation = "idle"
        self.last_run_time = None
        self.next_run_time = None
        
        # Threading
        self.scheduler_thread = None
        self.stop_event = threading.Event()
        
        # Status callbacks for real-time updates
        self.status_callbacks: List[Callable] = []
        
        # Mock scraper for testing (will be replaced with real scraper)
        self.mock_scraper_result = {
            'articles_found': 0,
            'articles_saved': 0,
            'duration': 0,
            'errors': []
        }
        
        logger.info(f"✅ SimpleSchedulerService initialized (interval: {self.interval_minutes} minutes)")
    
    def start(self) -> bool:
        """Start the scheduler service"""
        logger.info("🔧 Starting scheduler service...")
        
        if self.is_running:
            logger.warning("⚠️  Scheduler is already running")
            return False
        
        try:
            self.is_running = True
            self.stop_event.clear()
            
            # Start the scheduler thread
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            
            logger.info("✅ Scheduler service started successfully")
            self._broadcast_status()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
            self.is_running = False
            return False
    
    def stop(self) -> bool:
        """Stop the scheduler service"""
        logger.info("🛑 Stopping scheduler service...")
        
        if not self.is_running:
            logger.warning("⚠️  Scheduler is not running")
            return False
        
        try:
            # Signal stop
            self.stop_event.set()
            self.is_running = False
            self.is_scheduled = False
            self.current_operation = "stopped"
            
            # Wait for thread to finish
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            logger.info("✅ Scheduler service stopped successfully")
            self._broadcast_status()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop scheduler: {e}")
            return False
    
    def start_schedule(self) -> bool:
        """Start the automated scheduling"""
        logger.info(f"⏰ Starting automated schedule (every {self.interval_minutes} minutes)...")
        
        if not self.is_running:
            logger.error("❌ Cannot start schedule - scheduler service is not running")
            return False
        
        if self.is_scheduled:
            logger.warning("⚠️  Schedule is already active")
            return False
        
        self.is_scheduled = True
        self._calculate_next_run_time()
        
        interval_desc = f"{self.interval_minutes}-minute" if self.test_mode else "hourly"
        logger.info(f"✅ {interval_desc} schedule started - next run: {self.next_run_time}")
        self._broadcast_status()
        return True
    
    def stop_schedule(self) -> bool:
        """Stop the automated scheduling"""
        logger.info("🛑 Stopping automated schedule...")
        
        if not self.is_scheduled:
            logger.warning("⚠️  Schedule is not active")
            return False
        
        self.is_scheduled = False
        self.next_run_time = None
        self.current_operation = "idle"
        
        logger.info("✅ Automated schedule stopped")
        self._broadcast_status()
        return True
    
    def trigger_now(self) -> bool:
        """Manually trigger a scrape immediately"""
        logger.info("🚀 Manually triggering scrape...")
        
        if not self.is_running:
            logger.error("❌ Cannot trigger scrape - scheduler service is not running")
            return False
        
        # Run scrape in separate thread to avoid blocking
        scrape_thread = threading.Thread(target=self._run_scrape, args=("manual",), daemon=True)
        scrape_thread.start()
        
        return True
    
    def get_status(self) -> Dict:
        """Get current scheduler status"""
        return {
            'service_running': self.is_running,
            'schedule_active': self.is_scheduled,
            'current_operation': self.current_operation,
            'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
            'next_run_time': self.next_run_time.isoformat() if self.next_run_time else None,
            'interval_minutes': self.interval_minutes,
            'test_mode': self.test_mode,
            'last_result': self.mock_scraper_result
        }
    
    def register_status_callback(self, callback: Callable):
        """Register a callback for status updates"""
        if callback not in self.status_callbacks:
            self.status_callbacks.append(callback)
            logger.info(f"📡 Registered status callback: {callback.__name__}")
    
    def unregister_status_callback(self, callback: Callable):
        """Unregister a status callback"""
        if callback in self.status_callbacks:
            self.status_callbacks.remove(callback)
            logger.info(f"📡 Unregistered status callback: {callback.__name__}")
    
    def _scheduler_loop(self):
        """Main scheduler loop - runs in separate thread"""
        logger.info("🔄 Scheduler loop started")
        
        while not self.stop_event.is_set():
            try:
                # Check if we should run a scheduled scrape
                if self.is_scheduled and self.next_run_time:
                    now = datetime.now()
                    
                    if now >= self.next_run_time:
                        logger.info(f"⏰ Scheduled run time reached: {self.next_run_time}")
                        self._run_scrape("scheduled")
                        self._calculate_next_run_time()
                
                # Sleep for 10 seconds before checking again
                self.stop_event.wait(10)
                
            except Exception as e:
                logger.error(f"❌ Error in scheduler loop: {e}")
                time.sleep(10)  # Wait before retrying
        
        logger.info("🔄 Scheduler loop stopped")
    
    def _run_scrape(self, trigger_type: str):
        """Run a scraping operation"""
        start_time = datetime.now()
        logger.info(f"🤖 Starting scrape (trigger: {trigger_type}) at {start_time}")
        
        self.current_operation = f"scraping ({trigger_type})"
        self._broadcast_status()
        
        try:
            # Simulate scraping work (replace with real scraper later)
            logger.info("📰 Processing BlockBeats...")
            time.sleep(2)  # Simulate work
            
            logger.info("📰 Processing Jinse...")
            time.sleep(2)  # Simulate work
            
            # Update mock results
            self.mock_scraper_result = {
                'articles_found': 5,
                'articles_saved': 3,
                'duration': (datetime.now() - start_time).total_seconds(),
                'errors': [],
                'trigger': trigger_type,
                'timestamp': start_time.isoformat()
            }
            
            self.last_run_time = start_time
            self.current_operation = "idle"
            
            logger.info(f"✅ Scrape completed successfully in {self.mock_scraper_result['duration']:.1f}s")
            
        except Exception as e:
            logger.error(f"❌ Scrape failed: {e}")
            self.mock_scraper_result = {
                'articles_found': 0,
                'articles_saved': 0,
                'duration': (datetime.now() - start_time).total_seconds(),
                'errors': [str(e)],
                'trigger': trigger_type,
                'timestamp': start_time.isoformat()
            }
            self.current_operation = "error"
        
        finally:
            self._broadcast_status()
    
    def _calculate_next_run_time(self):
        """Calculate the next scheduled run time"""
        if not self.is_scheduled:
            self.next_run_time = None
            return
        
        now = datetime.now()
        
        if self.test_mode:
            # For testing: next run is in X minutes from now
            self.next_run_time = now + timedelta(minutes=self.interval_minutes)
        else:
            # For production: next run is at the top of the next hour
            next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            self.next_run_time = next_hour
        
        logger.info(f"📅 Next run scheduled for: {self.next_run_time}")
    
    def _broadcast_status(self):
        """Broadcast status to all registered callbacks"""
        status = self.get_status()
        
        for callback in self.status_callbacks.copy():
            try:
                callback(status)
            except Exception as e:
                logger.error(f"❌ Error in status callback: {e}")


# Test function
def test_simple_scheduler():
    """Test the simple scheduler"""
    print("🧪 Testing Simple Scheduler")
    print("=" * 50)
    
    def status_callback(status):
        print(f"📊 Status Update: {status['current_operation']} | "
              f"Next: {status['next_run_time']}")
    
    # Create scheduler in test mode
    scheduler = SimpleSchedulerService(test_mode=True)
    scheduler.register_status_callback(status_callback)
    
    try:
        # Start the service
        print("1. Starting scheduler service...")
        scheduler.start()
        time.sleep(1)
        
        # Start the schedule
        print("2. Starting automated schedule...")
        scheduler.start_schedule()
        time.sleep(1)
        
        # Trigger manual scrape
        print("3. Triggering manual scrape...")
        scheduler.trigger_now()
        time.sleep(5)
        
        # Show status
        status = scheduler.get_status()
        print(f"4. Current status: {status}")
        
        # Wait a bit more
        print("5. Waiting 10 seconds...")
        time.sleep(10)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        print("6. Stopping scheduler...")
        scheduler.stop()


if __name__ == "__main__":
    success = test_simple_scheduler()
    print(f"\n{'✅ Test passed!' if success else '❌ Test failed!'}")