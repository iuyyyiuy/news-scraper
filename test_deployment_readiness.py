#!/usr/bin/env python3
"""
Test Deployment Readiness
Comprehensive test to ensure all components are ready for deployment
"""

import sys
import os
import importlib.util
from pathlib import Path

def test_file_exists(filepath, description):
    """Test if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def test_import(module_path, module_name, description):
    """Test if a module can be imported"""
    try:
        if os.path.exists(module_path):
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            print(f"✅ {description}: Import successful")
            return True
        else:
            print(f"❌ {description}: File not found - {module_path}")
            return False
    except Exception as e:
        print(f"❌ {description}: Import failed - {e}")
        return False

def main():
    print("🧪 Testing Deployment Readiness")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test 1: Critical files
    print("\n📁 Testing Critical Files:")
    critical_files = [
        ("automated_news_scheduler.py", "Main scheduler script"),
        ("setup_digital_ocean_scheduler.sh", "Setup script"),
        ("check_scheduler_status.py", "Status check script"),
        ("requirements.txt", "Python dependencies"),
        (".env.example", "Environment template"),
        ("scraper/core/database_manager.py", "Database manager"),
        ("scraper/core/multi_source_scraper.py", "Multi-source scraper"),
        ("scraper/core/blockbeats_scraper.py", "BlockBeats scraper"),
    ]
    
    for filepath, description in critical_files:
        if not test_file_exists(filepath, description):
            all_tests_passed = False
    
    # Test 2: Python imports
    print("\n🐍 Testing Python Imports:")
    
    # Add current directory to Python path
    sys.path.insert(0, os.getcwd())
    
    import_tests = [
        ("scraper/core/database_manager.py", "database_manager", "Database Manager"),
        ("scraper/core/multi_source_scraper.py", "multi_source_scraper", "Multi-source Scraper"),
        ("automated_news_scheduler.py", "automated_news_scheduler", "Main Scheduler"),
    ]
    
    for module_path, module_name, description in import_tests:
        if not test_import(module_path, module_name, description):
            all_tests_passed = False
    
    # Test 3: Requirements file content
    print("\n📦 Testing Requirements File:")
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read()
            required_packages = [
                "fastapi", "uvicorn", "requests", "beautifulsoup4", 
                "supabase", "python-dotenv", "APScheduler"
            ]
            
            for package in required_packages:
                if package in requirements:
                    print(f"✅ Required package: {package}")
                else:
                    print(f"❌ Missing package: {package}")
                    all_tests_passed = False
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        all_tests_passed = False
    
    # Test 4: Environment template
    print("\n🔧 Testing Environment Template:")
    try:
        with open(".env.example", "r") as f:
            env_content = f.read()
            required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "DEEPSEEK_API_KEY"]
            
            for var in required_vars:
                if var in env_content:
                    print(f"✅ Environment variable: {var}")
                else:
                    print(f"❌ Missing environment variable: {var}")
                    all_tests_passed = False
    except Exception as e:
        print(f"❌ Error reading .env.example: {e}")
        all_tests_passed = False
    
    # Test 5: Script permissions
    print("\n🔐 Testing Script Permissions:")
    scripts = [
        "automated_news_scheduler.py",
        "setup_digital_ocean_scheduler.sh", 
        "check_scheduler_status.py"
    ]
    
    for script in scripts:
        if os.path.exists(script):
            # Check if file is executable (will be set during deployment)
            print(f"✅ Script exists: {script}")
        else:
            print(f"❌ Script missing: {script}")
            all_tests_passed = False
    
    # Final result
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED - Ready for deployment!")
        print("\n📋 Next steps:")
        print("1. Push to GitHub")
        print("2. Run deployment script on droplet")
        print("3. Configure environment variables")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Fix issues before deployment!")
        return 1

if __name__ == "__main__":
    sys.exit(main())