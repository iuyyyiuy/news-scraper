#!/usr/bin/env python3
"""
Setup Monthly Cleanup Cron Job
Configures automatic monthly cleanup to run on the 1st of each month at 2 AM
"""

import os
import subprocess
import sys
from pathlib import Path

def setup_monthly_cleanup_cron():
    """Setup cron job for monthly cleanup"""
    
    print("🗓️ Setting up Monthly Cleanup Cron Job")
    print("=" * 50)
    
    # Get current directory (where the script is located)
    current_dir = Path(__file__).parent.absolute()
    script_path = current_dir / "automated_monthly_cleanup.py"
    
    print(f"📁 Script location: {script_path}")
    
    # Create the cron job command
    # Run on 1st of every month at 2:00 AM
    cron_command = f"0 2 1 * * cd {current_dir} && source venv/bin/activate && python {script_path} >> monthly_cleanup_cron.log 2>&1"
    
    print(f"⏰ Cron schedule: 1st of every month at 2:00 AM")
    print(f"📝 Cron command: {cron_command}")
    
    # Check if cron job already exists
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_crontab = result.stdout
        
        if 'automated_monthly_cleanup.py' in current_crontab:
            print("⚠️ Monthly cleanup cron job already exists")
            print("Current crontab:")
            print(current_crontab)
            
            response = input("Do you want to replace it? (y/n): ").lower()
            if response != 'y':
                print("❌ Setup cancelled")
                return False
    
    except subprocess.CalledProcessError:
        # No existing crontab
        current_crontab = ""
    
    # Add the new cron job
    try:
        # Remove any existing monthly cleanup jobs
        lines = current_crontab.split('\n')
        filtered_lines = [line for line in lines if 'automated_monthly_cleanup.py' not in line and line.strip()]
        
        # Add the new job
        filtered_lines.append(cron_command)
        
        # Write back to crontab
        new_crontab = '\n'.join(filtered_lines) + '\n'
        
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_crontab)
        
        if process.returncode == 0:
            print("✅ Monthly cleanup cron job added successfully!")
            print("\n📋 Cron job details:")
            print(f"   - Schedule: 1st of every month at 2:00 AM")
            print(f"   - Script: {script_path}")
            print(f"   - Log file: {current_dir}/monthly_cleanup_cron.log")
            print(f"   - Next run: Next 1st of the month")
            
            # Verify the cron job was added
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if 'automated_monthly_cleanup.py' in result.stdout:
                print("✅ Verification: Cron job is active")
            else:
                print("⚠️ Warning: Could not verify cron job")
            
            return True
        else:
            print("❌ Failed to add cron job")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up cron job: {e}")
        return False

def test_monthly_cleanup():
    """Test the monthly cleanup script"""
    
    print("\n🧪 Testing Monthly Cleanup Script")
    print("=" * 40)
    
    try:
        # Import and test the cleanup script
        from automated_monthly_cleanup import MonthlyCleanupScheduler
        
        cleanup_scheduler = MonthlyCleanupScheduler()
        print("✅ Monthly cleanup script imports successfully")
        
        # Test database connection
        if cleanup_scheduler.db_manager.supabase:
            print("✅ Database connection working")
        else:
            print("❌ Database connection failed")
            return False
        
        # Test date threshold calculation
        threshold_date = cleanup_scheduler.get_cleanup_date_threshold()
        print(f"✅ Date threshold calculation: {threshold_date}")
        
        # Test article counting (without actually deleting)
        articles_to_keep = cleanup_scheduler.get_articles_to_keep_count(threshold_date)
        articles_to_delete = cleanup_scheduler.get_articles_to_delete_count(threshold_date)
        
        print(f"📊 Current database status:")
        print(f"   - Articles to keep (current month): {articles_to_keep}")
        print(f"   - Articles to delete (old): {articles_to_delete}")
        
        print("✅ Monthly cleanup script is ready!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing cleanup script: {e}")
        return False

def show_manual_test_command():
    """Show command to manually test the cleanup"""
    
    current_dir = Path(__file__).parent.absolute()
    
    print("\n🔧 Manual Testing Commands")
    print("=" * 40)
    print("To manually test the cleanup (safe - checks only):")
    print(f"cd {current_dir}")
    print("source venv/bin/activate")
    print("python automated_monthly_cleanup.py")
    print("\nTo check cron job status:")
    print("crontab -l | grep monthly_cleanup")
    print("\nTo view cleanup logs:")
    print("tail -f monthly_cleanup_cron.log")

def main():
    """Main setup function"""
    
    print("🚀 Monthly Cleanup Setup")
    print("=" * 50)
    
    # Test the cleanup script first
    if not test_monthly_cleanup():
        print("❌ Cleanup script test failed - fix issues before setting up cron")
        sys.exit(1)
    
    # Setup cron job
    if setup_monthly_cleanup_cron():
        print("\n🎉 SUCCESS: Monthly cleanup is now automated!")
        print("\n📋 What happens next:")
        print("✅ Every 1st of the month at 2:00 AM:")
        print("   - Script will automatically run")
        print("   - Delete all articles older than current month")
        print("   - Keep only current month's articles")
        print("   - Create backup summary before deletion")
        print("   - Log all activities")
        
        show_manual_test_command()
        
    else:
        print("❌ Failed to setup monthly cleanup")
        sys.exit(1)

if __name__ == "__main__":
    main()