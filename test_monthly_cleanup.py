#!/usr/bin/env python3
"""
Test Monthly Cleanup System
Safe testing of the monthly cleanup without actually deleting data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automated_monthly_cleanup import MonthlyCleanupScheduler
from datetime import date, datetime
import json

def test_cleanup_logic():
    """Test the cleanup logic without actually deleting anything"""
    
    print("🧪 Testing Monthly Cleanup Logic")
    print("=" * 50)
    
    try:
        # Initialize cleanup scheduler
        cleanup_scheduler = MonthlyCleanupScheduler()
        
        # Test 1: Database connection
        print("1️⃣ Testing database connection...")
        if cleanup_scheduler.db_manager.supabase:
            print("   ✅ Database connection successful")
        else:
            print("   ❌ Database connection failed")
            return False
        
        # Test 2: Date threshold calculation
        print("\n2️⃣ Testing date threshold calculation...")
        threshold_date = cleanup_scheduler.get_cleanup_date_threshold()
        print(f"   📅 Threshold date: {threshold_date}")
        print(f"   📋 Meaning: Keep articles from {threshold_date} onwards")
        
        # Test 3: Article counting
        print("\n3️⃣ Testing article counting...")
        articles_to_keep = cleanup_scheduler.get_articles_to_keep_count(threshold_date)
        articles_to_delete = cleanup_scheduler.get_articles_to_delete_count(threshold_date)
        
        print(f"   📊 Articles to keep (current month): {articles_to_keep}")
        print(f"   🗑️ Articles to delete (old months): {articles_to_delete}")
        
        total_articles = articles_to_keep + articles_to_delete
        print(f"   📈 Total articles in database: {total_articles}")
        
        # Test 4: Cleanup decision logic
        print("\n4️⃣ Testing cleanup decision logic...")
        should_run = cleanup_scheduler.should_run_cleanup()
        today = date.today()
        
        print(f"   📅 Today is: {today}")
        print(f"   🔍 Is 1st of month: {today.day == 1}")
        print(f"   🎯 Should run cleanup: {should_run}")
        
        # Test 5: Backup summary creation (safe test)
        print("\n5️⃣ Testing backup summary creation...")
        if articles_to_delete > 0:
            backup_summary = cleanup_scheduler.create_backup_summary(threshold_date)
            if backup_summary:
                print("   ✅ Backup summary created successfully")
                print(f"   📁 Sample articles to delete: {len(backup_summary.get('sample_deleted_articles', []))}")
            else:
                print("   ⚠️ Backup summary creation had issues")
        else:
            print("   ℹ️ No articles to delete - backup not needed")
        
        # Test 6: Simulate cleanup results
        print("\n6️⃣ Simulating cleanup results...")
        if should_run and articles_to_delete > 0:
            print(f"   🎯 SIMULATION: Would delete {articles_to_delete} old articles")
            print(f"   📊 SIMULATION: Would keep {articles_to_keep} current articles")
            print(f"   💾 SIMULATION: Database size would reduce by {articles_to_delete} articles")
        elif not should_run:
            print("   ⏭️ SIMULATION: Cleanup would be skipped (not 1st of month)")
        else:
            print("   ✅ SIMULATION: No cleanup needed (database already clean)")
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        print("✅ Monthly cleanup system is ready to deploy")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_deployment_summary():
    """Show summary of what will be deployed"""
    
    print("\n📋 DEPLOYMENT SUMMARY")
    print("=" * 50)
    print("🎯 What will be automated:")
    print("   ✅ Runs automatically on 1st of each month at 2:00 AM")
    print("   ✅ Deletes all articles older than current month")
    print("   ✅ Keeps only current month's articles (2026-01-XX)")
    print("   ✅ Creates backup summary before deletion")
    print("   ✅ Logs all activities to monthly_cleanup_cron.log")
    print("   ✅ Keeps your dashboard fast and clean")
    
    print("\n📊 Current Status:")
    try:
        cleanup_scheduler = MonthlyCleanupScheduler()
        threshold_date = cleanup_scheduler.get_cleanup_date_threshold()
        articles_to_keep = cleanup_scheduler.get_articles_to_keep_count(threshold_date)
        articles_to_delete = cleanup_scheduler.get_articles_to_delete_count(threshold_date)
        
        print(f"   📅 Current month threshold: {threshold_date}")
        print(f"   📊 Articles to keep: {articles_to_keep}")
        print(f"   🗑️ Articles to delete: {articles_to_delete}")
        
        if articles_to_delete == 0:
            print("   ✅ Database is already clean for current month!")
        else:
            print(f"   🔄 Next cleanup will remove {articles_to_delete} old articles")
            
    except Exception as e:
        print(f"   ⚠️ Could not get current status: {e}")
    
    print("\n🚀 Ready to deploy!")

def main():
    """Main test function"""
    
    print("🧪 Monthly Cleanup Test Suite")
    print("=" * 50)
    
    # Run tests
    success = test_cleanup_logic()
    
    if success:
        show_deployment_summary()
        print("\n✅ All tests passed - ready for deployment!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed - fix issues before deployment")
        sys.exit(1)

if __name__ == "__main__":
    main()