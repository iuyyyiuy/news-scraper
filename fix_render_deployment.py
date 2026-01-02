#!/usr/bin/env python3
"""
Fix Render deployment issues and ensure synchronization with Digital Ocean
"""

import os
import sys
import subprocess
from pathlib import Path

def check_git_status():
    """Check current git status"""
    print("🔍 Checking git status...")
    
    try:
        # Check if there are uncommitted changes
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("⚠️  Uncommitted changes found:")
            print(result.stdout)
            return False
        else:
            print("✅ Git working directory is clean")
            return True
            
    except Exception as e:
        print(f"❌ Error checking git status: {e}")
        return False

def check_render_requirements():
    """Check if all required files for Render deployment exist"""
    print("\n🔍 Checking Render deployment requirements...")
    
    required_files = [
        'requirements.txt',
        'render.yaml',
        'scraper/web_api.py',
        'scraper/core/ai_content_analyzer.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path} exists")
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True

def fix_render_yaml():
    """Ensure render.yaml is properly configured"""
    print("\n🔧 Checking render.yaml configuration...")
    
    render_yaml_path = Path('render.yaml')
    if not render_yaml_path.exists():
        print("❌ render.yaml not found")
        return False
    
    with open(render_yaml_path, 'r') as f:
        content = f.read()
    
    # Check for required configurations
    required_configs = [
        'services:',
        'name: crypto-news-scraper',
        'env: python',
        'buildCommand:',
        'startCommand:'
    ]
    
    missing_configs = []
    for config in required_configs:
        if config not in content:
            missing_configs.append(config)
    
    if missing_configs:
        print(f"⚠️  Missing configurations in render.yaml: {missing_configs}")
    else:
        print("✅ render.yaml properly configured")
    
    return len(missing_configs) == 0

def create_deployment_script():
    """Create a deployment script for Render"""
    
    deployment_script = """#!/bin/bash

echo "🚀 Render Deployment Script"
echo "=========================="

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check environment variables
echo "🔑 Checking environment variables..."
if [ -z "$SUPABASE_URL" ]; then
    echo "❌ SUPABASE_URL not set"
    exit 1
fi

if [ -z "$SUPABASE_KEY" ]; then
    echo "❌ SUPABASE_KEY not set"
    exit 1
fi

if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ DEEPSEEK_API_KEY not set"
    exit 1
fi

echo "✅ All environment variables set"

# Test database connection
echo "🔍 Testing database connection..."
python3 -c "
import os
from supabase import create_client
try:
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
    response = supabase.table('articles').select('id').limit(1).execute()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

echo "🎉 Deployment checks passed"
"""
    
    with open('deploy_render.sh', 'w') as f:
        f.write(deployment_script)
    
    # Make it executable
    os.chmod('deploy_render.sh', 0o755)
    
    print("✅ Created deploy_render.sh")
    return True

def force_render_redeploy():
    """Force a new deployment on Render by creating a deployment trigger"""
    print("\n🔄 Forcing Render redeploy...")
    
    try:
        # Create a small change to trigger redeploy
        trigger_file = Path('RENDER_DEPLOY_TRIGGER.txt')
        
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        
        with open(trigger_file, 'w') as f:
            f.write(f"Deployment triggered at: {timestamp}\n")
            f.write("This file triggers Render auto-deploy\n")
            f.write("AI analyzer fix deployed\n")
            f.write("Monthly cleanup system deployed\n")
        
        # Add and commit the trigger file
        subprocess.run(['git', 'add', 'RENDER_DEPLOY_TRIGGER.txt'], check=True)
        subprocess.run(['git', 'commit', '-m', f'Trigger Render redeploy - {timestamp}'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print("✅ Deployment trigger pushed to git")
        print("🔄 Render should automatically redeploy within 1-2 minutes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error triggering redeploy: {e}")
        return False

def verify_deployment_status():
    """Provide instructions to verify deployment"""
    print("\n📋 Deployment Verification Steps:")
    print("=" * 50)
    print("1. 🌐 Check Render dashboard for deployment status")
    print("2. 📱 Visit your dashboard URL to verify it's working")
    print("3. 🔍 Check if new articles appear (wait 1-2 hours)")
    print("4. 📊 Monitor system status with check_system_status.py")
    
    print("\n🔗 Useful Links:")
    print("- Render Dashboard: https://dashboard.render.com/")
    print("- Your App URL: Check Render dashboard for the URL")
    
    print("\n⏰ Timeline:")
    print("- Render redeploy: 1-2 minutes")
    print("- AI analyzer active: Immediately after deploy")
    print("- New articles: Next scheduled run (every 4 hours)")

if __name__ == "__main__":
    print("🔧 RENDER DEPLOYMENT FIX")
    print("=" * 50)
    print("Fixing Render deployment issues and ensuring synchronization")
    print("=" * 50)
    
    success = True
    
    # Check git status
    if not check_git_status():
        print("⚠️  Git working directory has uncommitted changes")
        success = False
    
    # Check Render requirements
    if not check_render_requirements():
        print("❌ Missing required files for Render deployment")
        success = False
    
    # Check render.yaml
    if not fix_render_yaml():
        print("⚠️  render.yaml configuration issues")
    
    # Create deployment script
    if not create_deployment_script():
        print("❌ Failed to create deployment script")
        success = False
    
    if success:
        # Force redeploy
        if force_render_redeploy():
            print("\n🎉 SUCCESS!")
            print("=" * 50)
            print("✅ Render deployment triggered")
            print("✅ AI analyzer fix will be deployed")
            print("✅ Monthly cleanup system will be deployed")
            
            verify_deployment_status()
        else:
            print("\n❌ Failed to trigger redeploy")
            sys.exit(1)
    else:
        print("\n❌ FAILED!")
        print("Please fix the issues above before redeploying")
        sys.exit(1)