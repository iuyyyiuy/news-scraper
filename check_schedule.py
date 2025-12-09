#!/usr/bin/env python3
"""
Simple schedule check
"""
from datetime import datetime, timedelta
import pytz

# Hong Kong timezone
hk_tz = pytz.timezone('Asia/Shanghai')
now = datetime.now(hk_tz)

print("="*60)
print("⏰ Scraper Schedule Check")
print("="*60)
print(f"Current time (HKT): {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Scheduled time: 11:30 AM HKT every day")
print()

# Calculate next run
if now.hour < 11 or (now.hour == 11 and now.minute < 30):
    # Today at 11:30
    next_run = now.replace(hour=11, minute=30, second=0, microsecond=0)
else:
    # Tomorrow at 11:30
    next_run = (now + timedelta(days=1)).replace(hour=11, minute=30, second=0, microsecond=0)

time_diff = next_run - now
minutes = int(time_diff.total_seconds() / 60)
hours = minutes // 60
mins = minutes % 60

print(f"Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S HKT')}")
print(f"Time until run: {hours}h {mins}m ({minutes} minutes)")
print()
print("="*60)
