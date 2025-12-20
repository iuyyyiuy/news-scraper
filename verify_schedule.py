#!/usr/bin/env python3
"""
Scheduler verification disabled - scheduler has been removed
"""
from datetime import datetime
import pytz

# Get current Hong Kong time
hk_tz = pytz.timezone('Asia/Shanghai')  # Same as Hong Kong
now_hk = datetime.now(hk_tz)

print("="*60)
print("⏰ Schedule Verification (DISABLED)")
print("="*60)
print(f"Current Hong Kong Time: {now_hk.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print()
print("❌ Scheduler has been removed from the system")
print("💡 Use manual scraping via API: /api/trigger-scrape")
print()
print("="*60)
