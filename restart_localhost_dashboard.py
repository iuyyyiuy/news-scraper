#!/usr/bin/env python3
"""
Restart localhost dashboard with latest fixes
"""

import subprocess
import sys
import os
import time
import signal
import psutil

def kill_existing_servers():
    """Kill any existing Python servers on common ports"""
    
    print("🔍 Checking for existing servers...")
    
    # Common ports used by the dashboard
    ports_to_check = [8000, 5000, 3000, 8080]
    killed_processes = []
    
    for port in ports_to_check:
        try:
            # Find processes using the port
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # Check if process is using the port
                    connections = proc.connections()
                    for conn in connections:
                        if conn.laddr.port == port:
                            print(f"🔪 Killing process {proc.pid} using port {port}: {proc.name()}")
                            proc.kill()
                            killed_processes.append(proc.pid)
                            time.sleep(1)
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            print(f"⚠️ Error checking port {port}: {e}")
    
    # Also kill any Python processes that might be running web servers
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.name() == 'python' or proc.name() == 'python3':
                    cmdline = ' '.join(proc.cmdline())
                    # Look for web server related commands
                    if any(keyword in cmdline.lower() for keyword in ['web_api', 'dashboard', 'flask', 'run_web', 'start_dashboard']):
                        print(f"🔪 Killing Python web server process {proc.pid}: {cmdline}")
                        proc.kill()
                        killed_processes.append(proc.pid)
                        time.sleep(1)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        print(f"⚠️ Error killing Python processes: {e}")
    
    if killed_processes:
        print(f"✅ Killed {len(killed_processes)} existing server processes")
        time.sleep(2)  # Give processes time to fully terminate
    else:
        print("✅ No existing servers found")

def start_dashboard_server():
    """Start the dashboard server with latest fixes"""
    
    print("🚀 Starting fresh dashboard server...")
    
    # Check if we have the web API file
    if os.path.exists('scraper/web_api.py'):
        print("📄 Found scraper/web_api.py - starting Flask server")
        
        try:
            # Start the Flask web server
            process = subprocess.Popen([
                sys.executable, 'scraper/web_api.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            # Give it a moment to start
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                print("✅ Dashboard server started successfully!")
                print("🌐 Access your dashboard at: http://localhost:8000")
                print("📊 Features available:")
                print("   - View latest news articles")
                print("   - Manual scraping")
                print("   - CSV export")
                print("   - Database statistics")
                print("   - All latest fixes applied!")
                print("")
                print("🔧 Server is running in the background...")
                print("💡 To stop the server, use Ctrl+C or run this script again")
                
                return process
            else:
                print("❌ Server failed to start")
                return None
                
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return None
    
    elif os.path.exists('run_web_server.py'):
        print("📄 Found run_web_server.py - starting server")
        
        try:
            process = subprocess.Popen([
                sys.executable, 'run_web_server.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            time.sleep(3)
            
            if process.poll() is None:
                print("✅ Dashboard server started successfully!")
                print("🌐 Access your dashboard at: http://localhost:8000")
                return process
            else:
                print("❌ Server failed to start")
                return None
                
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return None
    
    else:
        print("❌ No web server file found!")
        print("📋 Available files:")
        for file in os.listdir('.'):
            if 'web' in file.lower() or 'server' in file.lower() or 'dashboard' in file.lower():
                print(f"   - {file}")
        return None

def main():
    """Main function"""
    
    print("🔄 Restarting Localhost Dashboard")
    print("=" * 40)
    
    # Step 1: Kill existing servers
    kill_existing_servers()
    
    # Step 2: Start fresh server
    process = start_dashboard_server()
    
    if process:
        try:
            # Keep the server running and show output
            print("📋 Server output:")
            print("-" * 30)
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            process.terminate()
            process.wait()
            print("✅ Server stopped")
    else:
        print("❌ Failed to start dashboard server")
        sys.exit(1)

if __name__ == "__main__":
    main()