"""
Test the cleaned up scheduler with no automatic jobs
"""
from unittest.mock import Mock, patch
from scraper.core.scheduler import HourlySchedulerService

def test_clean_scheduler():
    """Test that scheduler starts clean with no jobs"""
    print("🧪 Testing Clean Scheduler")
    print("=" * 40)
    
    # Mock external dependencies
    with patch('scraper.core.scheduler.ScheduledScraper') as mock_scraper_class, \
         patch('scraper.core.scheduler.DatabaseManager') as mock_db_class:
        
        # Setup mocks
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper
        mock_db = Mock()
        mock_db_class.return_value = mock_db
        
        try:
            # Test 1: Create scheduler in test mode
            print("\n📋 Test 1: Create scheduler")
            scheduler = HourlySchedulerService(test_mode=True)
            print("   ✅ Scheduler created")
            
            # Test 2: Start scheduler (should have no jobs)
            print("\n📋 Test 2: Start empty scheduler")
            scheduler.start_scheduler()
            
            jobs = scheduler.scheduler.get_jobs()
            assert len(jobs) == 0, f"Expected 0 jobs, got {len(jobs)}"
            print(f"   ✅ Scheduler started with {len(jobs)} jobs")
            
            # Test 3: Add 5-minute schedule
            print("\n📋 Test 3: Add 5-minute schedule")
            success = scheduler.start_hourly_schedule()
            assert success, "Failed to start hourly schedule"
            
            jobs = scheduler.scheduler.get_jobs()
            assert len(jobs) == 1, f"Expected 1 job, got {len(jobs)}"
            print(f"   ✅ Added 5-minute schedule, now {len(jobs)} job(s)")
            
            # Test 4: Check job details
            job = jobs[0]
            print(f"   📅 Job: {job.name}")
            print(f"   🆔 ID: {job.id}")
            print(f"   ⏰ Next run: {job.next_run_time}")
            
            # Test 5: Clear all jobs
            print("\n📋 Test 4: Clear all jobs")
            scheduler.clear_all_jobs()
            
            jobs = scheduler.scheduler.get_jobs()
            assert len(jobs) == 0, f"Expected 0 jobs after clear, got {len(jobs)}"
            print(f"   ✅ All jobs cleared, now {len(jobs)} jobs")
            
            # Test 6: Get status
            print("\n📋 Test 5: Check status")
            status = scheduler.get_scheduler_status()
            print(f"   Running: {status['running']}")
            print(f"   Hourly running: {status['hourly_running']}")
            print(f"   Test mode: {scheduler.test_mode}")
            print(f"   Interval: {scheduler.schedule_interval_minutes} minutes")
            
            print("\n🎉 All tests passed!")
            print("✅ Clean scheduler works correctly")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            # Cleanup
            try:
                if scheduler.scheduler.running:
                    scheduler.stop_scheduler()
            except:
                pass

if __name__ == "__main__":
    success = test_clean_scheduler()
    exit(0 if success else 1)