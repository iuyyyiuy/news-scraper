#!/usr/bin/env python3
"""
Quick script to check system status and recent errors.
"""

import json
import glob
from datetime import datetime, timedelta

def check_system_status():
    """Check for recent errors and system health."""
    
    print("=== SYSTEM STATUS CHECK ===")
    
    # Check alert logs for errors
    try:
        log_files = glob.glob('alert_logs_*.json')
        recent_errors = []
        recent_criticals = []
        
        # Look at logs from last 24 hours
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for log_file in sorted(log_files, reverse=True):
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                log_entry = json.loads(line)
                                log_time = datetime.fromisoformat(log_entry.get('timestamp', '').replace('Z', '+00:00'))
                                
                                if log_time >= cutoff_time:
                                    if log_entry.get('level') == 'ERROR':
                                        recent_errors.append(log_entry)
                                    elif log_entry.get('level') == 'CRITICAL':
                                        recent_criticals.append(log_entry)
                            except (json.JSONDecodeError, ValueError):
                                continue
            except Exception as e:
                print(f"⚠️ Error reading {log_file}: {e}")
        
        # Report findings
        if recent_criticals:
            print(f"🚨 CRITICAL: {len(recent_criticals)} critical errors in last 24h")
            for error in recent_criticals[-3:]:  # Show last 3
                timestamp = error.get('timestamp', 'Unknown')
                component = error.get('component', 'Unknown')
                message = error.get('message', 'No message')
                print(f"   {timestamp} [{component}]: {message}")
        
        if recent_errors:
            print(f"❌ ERROR: {len(recent_errors)} errors in last 24h")
            for error in recent_errors[-3:]:  # Show last 3
                timestamp = error.get('timestamp', 'Unknown')
                component = error.get('component', 'Unknown')
                message = error.get('message', 'No message')
                print(f"   {timestamp} [{component}]: {message}")
        
        if not recent_errors and not recent_criticals:
            print("✅ No errors or critical issues in last 24 hours")
        
        # Check session stats
        session_files = glob.glob('session_stats_*.json')
        if session_files:
            latest_session_file = sorted(session_files, reverse=True)[0]
            with open(latest_session_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            session = json.loads(line)
                            perf = session.get('performance_metrics', {})
                            success_rate = perf.get('success_rate_percent', 0)
                            
                            print(f"\n📊 Latest Session: {session.get('session_id', 'Unknown')}")
                            print(f"   Success Rate: {success_rate:.1f}%")
                            print(f"   Articles Found: {session.get('articles_found', 0)}")
                            print(f"   Articles Stored: {session.get('articles_stored', 0)}")
                            print(f"   Errors: {session.get('errors_encountered', 0)}")
                            
                            if success_rate < 50:
                                print("   ⚠️ LOW SUCCESS RATE - Check for issues")
                            elif success_rate < 80:
                                print("   ⚠️ MODERATE SUCCESS RATE - Monitor closely")
                            else:
                                print("   ✅ Good success rate")
                            break
                        except json.JSONDecodeError:
                            continue
        
    except Exception as e:
        print(f"❌ Error checking system status: {e}")

if __name__ == "__main__":
    check_system_status()