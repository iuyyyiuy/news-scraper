#!/usr/bin/env python3
"""
Stop all AI trading related processes
"""
import subprocess
import os
import signal

def stop_ai_trading():
    """Stop all AI trading processes"""
    print("🛑 Stopping AI trading processes...")
    
    try:
        # Find and kill AI trading processes
        result = subprocess.run(['pgrep', '-f', 'ai_trading'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"✅ Killed AI trading process {pid}")
                except:
                    pass
        
        # Find and kill reinforcement learning processes
        result = subprocess.run(['pgrep', '-f', 'reinforcement'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"✅ Killed reinforcement learning process {pid}")
                except:
                    pass
        
        print("✅ AI trading processes stopped")
        
    except Exception as e:
        print(f"⚠️  Error stopping processes: {e}")

if __name__ == "__main__":
    stop_ai_trading()