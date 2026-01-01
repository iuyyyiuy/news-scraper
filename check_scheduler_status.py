#!/usr/bin/env python3
"""
Check News Scheduler Status
Monitors the automated news scheduler and reports status
"""

import subprocess
import sys
import os
from datetime import datetime, timedelta

def check_systemd_timer():
    """Check if systemd timer is active"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'news-scheduler.timer'], 
                              capture_output=True, text=True)
        return result.returncode == 0 and result.stdout.strip() == 'active'
    except:
        return False

def check_recent_logs():
    """Check if scheduler has run recently"""
    log_file = '/var/log/news-scraper/scheduler.log'
    if not os.path.exists(log_file):
        return False, "Log file not found"
    
    try:
        # Check if there's a log entry in the last 5 hours
        cutoff_time = datetime.now() - timedelta(hours=5)
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
            
        for line in reversed(lines[-100:]):  # Check last 100 lines
            if 'Starting scheduled scrape' in line:
                # Extract timestamp (assuming format: YYYY-MM-DD HH:MM:SS)
                try:
                    timestamp_str = line.split(' - ')[0]
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                    if timestamp > cutoff_time:
                        return True, f"Last run: {timestamp_str}"
                except:
                    continue
        
        return False, "No recent runs found"
    except Exception as e:
        return False, f"Error reading logs: {e}"

def main():
    print("🔍 News Scheduler Status Check")
    print("=" * 40)
    
    # Check systemd timer
    timer_active = check_systemd_timer()
    print(f"Systemd Timer: {'✅ Active' if timer_active else '❌ Inactive'}")
    
    # Check recent logs
    recent_run, message = check_recent_logs()
    print(f"Recent Activity: {'✅' if recent_run else '❌'} {message}")
    
    # Check next scheduled run
    try:
        result = subprocess.run(['systemctl', 'list-timers', 'news-scheduler.timer'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'news-scheduler.timer' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        next_run = f"{parts[0]} {parts[1]}"
                        print(f"Next Scheduled: ⏰ {next_run}")
                    break
    except:
        print("Next Scheduled: ❓ Unable to determine")
    
    print("=" * 40)
    
    # Overall status
    if timer_active and recent_run:
        print("✅ Scheduler is working properly")
        return 0
    elif timer_active:
        print("⚠️  Timer active but no recent activity")
        return 1
    else:
        print("❌ Scheduler is not running")
        return 2

if __name__ == "__main__":
    sys.exit(main())