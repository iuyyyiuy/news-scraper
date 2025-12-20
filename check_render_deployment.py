#!/usr/bin/env python3
"""
Render Deployment Status Check
Verifies that the application is ready for Render auto-deployment.
"""

import os
import sys
import yaml
import requests
from dotenv import load_dotenv

def check_render_deployment():
    """Check if the application is ready for Render deployment"""
    
    print("🚀 Render Deployment Status Check")
    print("=" * 50)
    
    # Check 1: Render configuration
    print("1️⃣ Checking Render configuration...")
    
    if os.path.exists('render.yaml'):
        print("   ✅ render.yaml exists")
        
        with open('render.yaml', 'r') as f:
            render_config = yaml.safe_load(f)
            
        if render_config.get('services'):
            service = render_config['services'][0]
            if service.get('autoDeploy'):
                print("   ✅ Auto-deploy is enabled")
            else:
                print("   ⚠️ Auto-deploy is disabled")
                
            if service.get('healthCheckPath') == '/api/health':
                print("   ✅ Health check path configured")
            else:
                print("   ❌ Health check path missing or incorrect")
                
            print(f"   📊 Service name: {service.get('name', 'N/A')}")
            print(f"   📊 Build command: {service.get('buildCommand', 'N/A')}")
            print(f"   📊 Start command: {service.get('startCommand', 'N/A')}")
        else:
            print("   ❌ No services configured in render.yaml")
            return False
    else:
        print("   ❌ render.yaml missing")
        return False
    
    # Check 2: Requirements file
    print("\n2️⃣ Checking requirements.txt...")
    
    if os.path.exists('requirements.txt'):
        print("   ✅ requirements.txt exists")
        
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
            
        required_packages = ['fastapi', 'uvicorn', 'supabase', 'python-dotenv']
        missing_packages = []
        
        for package in required_packages:
            if package not in requirements:
                missing_packages.append(package)
        
        if not missing_packages:
            print("   ✅ All required packages are listed")
        else:
            print(f"   ❌ Missing packages: {missing_packages}")
            return False
    else:
        print("   ❌ requirements.txt missing")
        return False
    
    # Check 3: Environment variables setup
    print("\n3️⃣ Checking environment variables...")
    
    load_dotenv()
    
    required_env_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'DEEPSEEK_API_KEY']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if not missing_vars:
        print("   ✅ All required environment variables are set locally")
        print("   💡 Remember to set these in Render dashboard:")
        for var in required_env_vars:
            print(f"      - {var}")
    else:
        print(f"   ❌ Missing environment variables: {missing_vars}")
        return False
    
    # Check 4: Health check endpoint
    print("\n4️⃣ Checking health check endpoint...")
    
    try:
        # Try to test locally if server is running
        response = requests.get('http://localhost:8080/api/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Health check endpoint working locally")
            print(f"   📊 Status: {data.get('status', 'N/A')}")
        else:
            print(f"   ⚠️ Health check returned status {response.status_code}")
    except requests.exceptions.RequestException:
        print("   ⚠️ Cannot test health check (server not running locally)")
        print("   💡 This is OK - Render will test it during deployment")
    
    # Check 5: Static files
    print("\n5️⃣ Checking static files...")
    
    static_paths = [
        'scraper/static/js/dashboard.js',
        'scraper/templates/dashboard.html'
    ]
    
    missing_static = []
    for path in static_paths:
        if not os.path.exists(path):
            missing_static.append(path)
    
    if not missing_static:
        print("   ✅ All static files present")
    else:
        print(f"   ❌ Missing static files: {missing_static}")
        return False
    
    # Check 6: Git status
    print("\n6️⃣ Checking Git status...")
    
    import subprocess
    
    try:
        # Check if there are uncommitted changes
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print("   ⚠️ There are uncommitted changes:")
                print(f"   {result.stdout.strip()}")
                print("   💡 Commit and push to trigger Render deployment")
            else:
                print("   ✅ No uncommitted changes")
                
                # Check if we're ahead of origin
                result = subprocess.run(['git', 'status', '-b', '--porcelain'], 
                                      capture_output=True, text=True)
                if 'ahead' in result.stdout:
                    print("   ⚠️ Local branch is ahead of origin")
                    print("   💡 Push to GitHub to trigger Render deployment")
                else:
                    print("   ✅ Local branch is up to date with origin")
        else:
            print("   ❌ Git status check failed")
            return False
            
    except FileNotFoundError:
        print("   ❌ Git not found")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Render deployment check completed!")
    
    return True

def main():
    """Main function"""
    success = check_render_deployment()
    
    if success:
        print("\n🚀 Your application is ready for Render deployment!")
        print("\n📋 Next steps:")
        print("1. Ensure your Render service is connected to your GitHub repo")
        print("2. Set environment variables in Render dashboard:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_KEY") 
        print("   - DEEPSEEK_API_KEY")
        print("3. Render will auto-deploy when you push to GitHub")
        print("4. Check deployment logs in Render dashboard")
        print("\n🌐 Your app will be available at: https://your-app-name.onrender.com")
    else:
        print("\n❌ Issues found - please fix before deploying")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())