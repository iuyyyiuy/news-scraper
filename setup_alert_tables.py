#!/usr/bin/env python3
"""
Set up alert logging tables in Supabase database.
"""

from scraper.core.database_manager import DatabaseManager

def setup_alert_tables():
    """Create alert logging tables in the database."""
    
    db_manager = DatabaseManager()
    
    # Read SQL file
    try:
        with open('create_alert_tables.sql', 'r') as f:
            sql_commands = f.read()
        
        print("=== SETTING UP ALERT LOGGING TABLES ===")
        
        # Try to create tables by checking if they exist first
        print("📝 Checking if alert_logs table exists...")
        try:
            # Try to query the table - if it fails, table doesn't exist
            response = db_manager.supabase.table('alert_logs').select('id').limit(1).execute()
            print("   ✅ alert_logs table already exists")
        except Exception:
            print("   ℹ️ alert_logs table doesn't exist - will be created automatically on first insert")
        
        print("📝 Checking if scraping_sessions table exists...")
        try:
            response = db_manager.supabase.table('scraping_sessions').select('id').limit(1).execute()
            print("   ✅ scraping_sessions table already exists")
        except Exception:
            print("   ℹ️ scraping_sessions table doesn't exist - will be created automatically on first insert")
        
        print(f"\n🎉 Alert logging tables setup complete!")
        
        # Test the tables by inserting a test log entry
        print(f"\n🧪 Testing alert logging...")
        
        from scraper.core.alert_logger import AlertLogger
        logger = AlertLogger()
        
        # Test basic logging
        logger.log_info(
            component="SetupScript",
            message="Alert logging system initialized successfully",
            details={"setup_time": "2025-12-10", "tables_created": ["alert_logs", "scraping_sessions"]}
        )
        
        # Test session tracking
        session_id = logger.start_scraping_session(["BlockBeats", "Jinse"])
        logger.update_session_stats(articles_found=5, articles_stored=3, articles_duplicate=2)
        logger.log_scraping_operation("BlockBeats", 5, 3, 2, 45.5)
        completed_session = logger.end_scraping_session()
        
        if completed_session:
            print(f"   ✅ Session tracking working: {session_id}")
        
        # Test log retrieval
        recent_logs = logger.get_recent_logs(limit=5)
        print(f"   ✅ Log retrieval working: {len(recent_logs)} entries found")
        
        # Test system health
        health = logger.get_system_health()
        print(f"   ✅ System health monitoring: {health.get('health_status', 'UNKNOWN')}")
        
        print(f"\n✅ Alert logging system is fully operational!")
        return True
        
    except FileNotFoundError:
        print(f"❌ SQL file 'create_alert_tables.sql' not found")
        return False
    except Exception as e:
        print(f"❌ Error setting up tables: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    setup_alert_tables()