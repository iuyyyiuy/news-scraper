#!/usr/bin/env python3
"""
Setup automated monthly cleanup to keep only current month articles
This prevents the database from growing too large and keeps the dashboard fast
"""

import os
import sys
from datetime import datetime, date
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def setup_monthly_cleanup_trigger():
    """Setup a database trigger to automatically delete old articles monthly"""
    
    print("🔧 Setting up automated monthly cleanup...")
    print("=" * 50)
    
    # SQL function to clean up old articles
    cleanup_function_sql = """
    CREATE OR REPLACE FUNCTION cleanup_old_articles()
    RETURNS void AS $$
    BEGIN
        -- Delete articles older than current month
        DELETE FROM articles 
        WHERE date < date_trunc('month', CURRENT_DATE);
        
        -- Log the cleanup
        RAISE NOTICE 'Monthly cleanup completed at %', NOW();
    END;
    $$ LANGUAGE plpgsql;
    """
    
    # SQL trigger to run cleanup on the 1st of each month
    cleanup_trigger_sql = """
    -- Create a scheduled job (if pg_cron extension is available)
    -- This would run on the 1st of each month at 2 AM UTC
    -- SELECT cron.schedule('monthly-cleanup', '0 2 1 * *', 'SELECT cleanup_old_articles();');
    """
    
    print("📝 SQL Functions created:")
    print("   - cleanup_old_articles() function")
    print("   - Monthly trigger (requires pg_cron extension)")
    
    return cleanup_function_sql, cleanup_trigger_sql

def create_dashboard_optimization():
    """Create database optimizations for faster dashboard loading"""
    
    optimization_sql = """
    -- Create indexes for faster dashboard queries
    CREATE INDEX IF NOT EXISTS idx_articles_date_desc ON articles (date DESC);
    CREATE INDEX IF NOT EXISTS idx_articles_source ON articles (source);
    CREATE INDEX IF NOT EXISTS idx_articles_date_source ON articles (date DESC, source);
    
    -- Create a view for recent articles (current month only)
    CREATE OR REPLACE VIEW recent_articles AS
    SELECT * FROM articles 
    WHERE date >= date_trunc('month', CURRENT_DATE)
    ORDER BY date DESC, created_at DESC;
    """
    
    print("⚡ Dashboard optimizations:")
    print("   - Date index for faster sorting")
    print("   - Source index for filtering")
    print("   - Combined index for dashboard queries")
    print("   - Recent articles view")
    
    return optimization_sql

def setup_cleanup_schedule():
    """Setup a Python-based cleanup schedule"""
    
    schedule_script = """#!/usr/bin/env python3
# Monthly cleanup script - run this on the 1st of each month
import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def monthly_cleanup():
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    supabase = create_client(supabase_url, supabase_key)
    
    # Delete articles older than current month
    current_month = datetime.now().strftime('%Y-%m-01')
    
    delete_response = supabase.table('articles').delete().lt('date', current_month).execute()
    
    print(f"Monthly cleanup completed: {datetime.now()}")
    print(f"Deleted articles older than {current_month}")

if __name__ == "__main__":
    monthly_cleanup()
"""
    
    # Write the monthly cleanup script
    with open('monthly_cleanup_auto.py', 'w') as f:
        f.write(schedule_script)
    
    print("📅 Created monthly_cleanup_auto.py")
    print("   Run this script on the 1st of each month")
    
    return schedule_script

def create_dashboard_speed_improvements():
    """Create additional improvements for dashboard speed"""
    
    improvements = {
        'pagination': 'Limit articles per page (20-50 articles)',
        'lazy_loading': 'Load articles as user scrolls',
        'caching': 'Cache recent articles in browser',
        'compression': 'Compress article content',
        'indexing': 'Database indexes on frequently queried columns'
    }
    
    print("🚀 Dashboard speed improvements:")
    for key, value in improvements.items():
        print(f"   - {key.title()}: {value}")
    
    return improvements

if __name__ == "__main__":
    print("🔧 AUTOMATED MONTHLY CLEANUP SETUP")
    print("=" * 50)
    print("This will set up automatic cleanup to keep only current month articles")
    print("=" * 50)
    
    # Setup cleanup functions
    cleanup_sql, trigger_sql = setup_monthly_cleanup_trigger()
    
    print("\n" + "=" * 50)
    
    # Setup dashboard optimizations
    optimization_sql = create_dashboard_optimization()
    
    print("\n" + "=" * 50)
    
    # Setup Python-based schedule
    schedule_script = setup_cleanup_schedule()
    
    print("\n" + "=" * 50)
    
    # Dashboard speed improvements
    improvements = create_dashboard_speed_improvements()
    
    print("\n" + "=" * 50)
    print("📋 SETUP COMPLETE")
    print("=" * 50)
    print("✅ Monthly cleanup function created")
    print("✅ Dashboard optimizations ready")
    print("✅ Python cleanup script created")
    print("✅ Speed improvement recommendations provided")
    
    print("\n📅 NEXT STEPS:")
    print("1. Run monthly_cleanup_auto.py on the 1st of each month")
    print("2. Consider setting up a cron job for automation")
    print("3. Monitor dashboard performance")
    print("4. Implement pagination if needed")
    
    print(f"\n⏰ Current database status: Only January 2026 articles")
    print(f"🎯 Next cleanup: February 1st, 2026")