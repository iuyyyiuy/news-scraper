#!/usr/bin/env python3
"""
Debug ML Analysis Page Access
Diagnose why http://localhost:8000/ml-analysis is not accessible
"""

import requests
import json
import time
import subprocess
import sys
import os

def check_server_status():
    """Check if the server is running"""
    print("🔍 Checking Server Status...")
    print("=" * 40)
    
    try:
        # Test basic server connection
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ Server is running on port 8000")
            health_data = response.json()
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   Database: {health_data.get('database', 'unknown')}")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server on port 8000")
        print("   Server is not running or not accessible")
        return False
    except requests.exceptions.Timeout:
        print("❌ Server connection timeout")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def check_ml_routes():
    """Check if ML routes are available"""
    print("\n🧠 Checking ML Routes...")
    print("=" * 30)
    
    routes_to_test = [
        ("/ml-analysis", "ML Analysis Page"),
        ("/api/ml-analysis/status", "ML Status API"),
        ("/market-analysis", "Market Analysis Page"),
        ("/dashboard", "Dashboard Page"),
        ("/", "Home Page")
    ]
    
    results = {}
    
    for route, description in routes_to_test:
        try:
            response = requests.get(f"http://localhost:8000{route}", timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {description}: Available")
                results[route] = True
            elif response.status_code == 503:
                print(f"⚠️  {description}: Service Unavailable (503)")
                results[route] = False
            elif response.status_code == 404:
                print(f"❌ {description}: Not Found (404)")
                results[route] = False
            else:
                print(f"⚠️  {description}: Status {response.status_code}")
                results[route] = False
                
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
            results[route] = False
    
    return results

def check_ml_dependencies():
    """Check if ML dependencies are installed"""
    print("\n📦 Checking ML Dependencies...")
    print("=" * 35)
    
    dependencies = [
        ("tensorflow", "TensorFlow"),
        ("sklearn", "Scikit-learn"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas")
    ]
    
    missing_deps = []
    
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name}: Installed")
        except ImportError:
            print(f"❌ {name}: Missing")
            missing_deps.append(module)
    
    return missing_deps

def check_file_structure():
    """Check if ML files exist"""
    print("\n📁 Checking ML File Structure...")
    print("=" * 35)
    
    files_to_check = [
        ("ml_orderbook_analyzer/btc_deep_analyzer.py", "ML Core Engine"),
        ("ml_orderbook_analyzer/btc_live_collector.py", "Data Collector"),
        ("ml_orderbook_analyzer/ml_integration_api.py", "ML API Integration"),
        ("scraper/templates/ml_analysis.html", "ML Web Interface"),
        ("scraper/static/js/ml_analysis.js", "ML JavaScript"),
        ("scraper/web_api.py", "Main Web API")
    ]
    
    missing_files = []
    
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {description}: Found")
        else:
            print(f"❌ {description}: Missing ({file_path})")
            missing_files.append(file_path)
    
    return missing_files

def check_server_logs():
    """Check for server startup logs"""
    print("\n📋 Checking Server Startup...")
    print("=" * 30)
    
    try:
        # Check if there are any Python processes running on port 8000
        result = subprocess.run(
            ["lsof", "-i", ":8000"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout:
            print("✅ Process found on port 8000:")
            print(f"   {result.stdout.strip()}")
            return True
        else:
            print("❌ No process found on port 8000")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Timeout checking port 8000")
        return False
    except FileNotFoundError:
        print("⚠️  lsof command not available")
        # Try alternative method
        try:
            result = subprocess.run(
                ["netstat", "-tlnp", "|", "grep", ":8000"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stdout:
                print("✅ Port 8000 is in use")
                return True
            else:
                print("❌ Port 8000 is not in use")
                return False
        except:
            print("⚠️  Cannot check port status")
            return False
    except Exception as e:
        print(f"⚠️  Error checking port: {e}")
        return False

def test_ml_api_directly():
    """Test ML API endpoints directly"""
    print("\n🔬 Testing ML API Endpoints...")
    print("=" * 35)
    
    ml_endpoints = [
        "/api/ml-analysis/status",
        "/api/market-analysis/status", 
        "/api/health"
    ]
    
    for endpoint in ml_endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}: Working")
                
                # Show relevant info
                if "ml_available" in data:
                    print(f"   ML Available: {data.get('ml_available', False)}")
                if "success" in data:
                    print(f"   Success: {data.get('success', False)}")
                    
            else:
                print(f"❌ {endpoint}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

def provide_solutions(server_running, ml_routes, missing_deps, missing_files):
    """Provide solutions based on diagnosis"""
    print("\n" + "=" * 50)
    print("🔧 SOLUTIONS & NEXT STEPS")
    print("=" * 50)
    
    if not server_running:
        print("\n❌ PROBLEM: Server is not running")
        print("🔧 SOLUTION:")
        print("   1. Start the server:")
        print("      python3 restart_server_with_market_analysis.py")
        print("   2. Or start manually:")
        print("      python3 -m uvicorn scraper.web_api:app --host 0.0.0.0 --port 8000 --reload")
        print("   3. Wait 10-15 seconds for startup")
        print("   4. Then try: http://localhost:8000/ml-analysis")
        return
    
    if not ml_routes.get("/ml-analysis", False):
        print("\n❌ PROBLEM: ML Analysis page not accessible")
        
        if missing_deps:
            print("🔧 SOLUTION: Install missing ML dependencies")
            print("   pip install tensorflow scikit-learn numpy pandas")
            print("   Then restart the server")
        
        elif missing_files:
            print("🔧 SOLUTION: Missing ML files detected")
            print("   The ML system files may not be properly created")
            print("   Please check the file structure")
        
        else:
            print("🔧 SOLUTION: ML integration issue")
            print("   1. Check server logs for errors")
            print("   2. Try accessing other pages first:")
            print("      http://localhost:8000/dashboard")
            print("      http://localhost:8000/market-analysis")
            print("   3. If those work, the ML route may be disabled")
    
    else:
        print("\n✅ DIAGNOSIS: Everything looks good!")
        print("🎯 TRY THESE URLS:")
        print("   🌐 ML Analysis: http://localhost:8000/ml-analysis")
        print("   📊 Market Analysis: http://localhost:8000/market-analysis") 
        print("   📈 Dashboard: http://localhost:8000/dashboard")
        print("   🏠 Home: http://localhost:8000/")

def main():
    """Main diagnostic function"""
    print("🚨 ML Analysis Access Diagnostic Tool")
    print("=====================================")
    print("Diagnosing why http://localhost:8000/ml-analysis is not accessible...\n")
    
    # Step 1: Check server status
    server_running = check_server_status()
    
    # Step 2: Check ML routes
    ml_routes = check_ml_routes()
    
    # Step 3: Check ML dependencies
    missing_deps = check_ml_dependencies()
    
    # Step 4: Check file structure
    missing_files = check_file_structure()
    
    # Step 5: Check server process
    server_process = check_server_logs()
    
    # Step 6: Test ML API directly
    if server_running:
        test_ml_api_directly()
    
    # Step 7: Provide solutions
    provide_solutions(server_running, ml_routes, missing_deps, missing_files)
    
    # Final summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    print(f"Server Running: {'✅' if server_running else '❌'}")
    print(f"ML Page Access: {'✅' if ml_routes.get('/ml-analysis', False) else '❌'}")
    print(f"ML Dependencies: {'✅' if not missing_deps else f'❌ Missing {len(missing_deps)}'}")
    print(f"ML Files: {'✅' if not missing_files else f'❌ Missing {len(missing_files)}'}")
    print(f"Server Process: {'✅' if server_process else '❌'}")
    
    if server_running and ml_routes.get('/ml-analysis', False):
        print("\n🎉 ML Analysis should be accessible!")
        print("🌐 Try: http://localhost:8000/ml-analysis")
    else:
        print("\n🔧 Follow the solutions above to fix the issues")

if __name__ == "__main__":
    main()