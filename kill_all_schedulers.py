#!/usr/bin/env python3
"""
Kill all remaining scheduler processes
Use this if you see scheduler errors again
"""
import subprocess
import sys

def kill_scheduler_processes():
    """Kill all scheduler-related processes"""
    print("🔍 Looking for scheduler processes...")
    
    # Commands to kill various scheduler processes
    kill_commands = [
        ["pkill", "-f", "test_scheduler"],
        ["pkill", "-f", "test_5_minute"],
        ["pkill", "-f", "APScheduler"],
        ["pkill", "-f", "python.*scheduler"],
        ["pkill", "-f", "BackgroundScheduler"],
    ]
    
    killed_any = False
    
    for cmd in kill_commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Killed processes matching: {' '.join(cmd[2:])}")
                killed_any = True
        except Exception as e:
            print(f"⚠️  Error running {' '.join(cmd)}: {e}")
    
    if not killed_any:
        print("✅ No scheduler processes found running")
    
    # Check what's still running
    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        scheduler_lines = [line for line in result.stdout.split('\n') 
                          if 'scheduler' in line.lower() and 'grep' not in line.lower()]
        
        if scheduler_lines:
            print(f"\n⚠️  Still found {len(scheduler_lines)} scheduler-related processes:")
            for line in scheduler_lines:
                print(f"   {line}")
        else:
            print("\n✅ No scheduler processes remaining")
            
    except Exception as e:
        print(f"⚠️  Error checking processes: {e}")

def main():
    print("🛑 Scheduler Process Killer")
    print("=" * 40)
    
    kill_scheduler_processes()
    
    print("\n💡 If you still see scheduler errors:")
    print("   1. Run this script again")
    print("   2. Restart your terminal")
    print("   3. Reboot your computer if necessary")
    
    return 0

if __name__ == "__main__":
    exit(main())