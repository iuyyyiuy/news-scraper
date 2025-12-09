#!/usr/bin/env python3
"""
Verify the scheduler is set correctly for UTC+8 (Hong Kong Time)
"""
from datetime import datetime
import pytz
from scraper.core.scheduler import SchedulerService

# Get current Hong Kong time
hk_tz = pytz.timezone('Asia/Shanghai')  # Same as Hong Kong
now_hk = datetime.now(hk_tz)

print("="*60)
print("⏰ Schedule Verification")
print("="*60)
print(f"Current Hong Kong Time: {now_hk.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"Scheduled scrape time: 11:30 AM HKT (UTC+8)")
print()

# Calculate time until next scrape
target_time = now_hk.replace(hour=11, minute=30, second=0, microsecond=0)
if now_hk.time() > target_time.time():
    # If past 11:30 today, schedule for tomorrow
    from datetime import timedelta
    target_time = target_time + timedelta(days=1)

time_diff = target_time - now_hk
minutes_until = int(time_diff.total_seconds() / 60)

print(f"Next scheduled run: {target_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"Time until next run: {minutes_until} minutes")
print()

# Start scheduler to verify
print("Starting scheduler service...")
scheduler = SchedulerService()
scheduler.start_scheduler()

print()
print("📅 Scheduled Jobs:")
for job in scheduler.scheduler.get_jobs():
    print(f"  - {job.name}")
    print(f"    Next run: {job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Calculate minutes until this job runs
    time_to_job = job.next_run_time - datetime.now(hk_tz)
    mins_to_job = int(time_to_job.total_seconds() / 60)
    print(f"    In {mins_to_job} minutes")
    print()

print("="*60)
print("✅ Verification complete!")
print("="*60)

scheduler.stop_scheduler()
