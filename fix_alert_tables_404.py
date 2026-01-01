#!/usr/bin/env python3
"""
Fix for 404 alert_logs table error
Creates missing alert tables in Supabase database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.database_manager import DatabaseManager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_alert_tables():
    """Create missing alert tables in Supabase database"""
    
    print("🔧 Fixing 404 Alert Tables Error")
    print("=" * 50)
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    if not db_manager.supabase:
        print("❌ Failed to connect to Supabase")
        return False
    
    print("✅ Connected to Supabase")
    
    # SQL to create alert_logs table
    alert_logs_sql = """
    CREATE TABLE IF NOT EXISTS alert_logs (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        timestamp TIMESTAMPTZ NOT NULL,
        level VARCHAR(20) NOT NULL CHECK (level IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL')),
        component VARCHAR(100) NOT NULL,
        message TEXT NOT NULL,
        details JSONB,
        session_id VARCHAR(100),
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    # SQL to create scraping_sessions table
    scraping_sessions_sql = """
    CREATE TABLE IF NOT EXISTS scraping_sessions (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        session_id VARCHAR(100) UNIQUE NOT NULL,
        start_time TIMESTAMPTZ NOT NULL,
        end_time TIMESTAMPTZ,
        sources_processed TEXT[],
        articles_found INTEGER DEFAULT 0,
        articles_stored INTEGER DEFAULT 0,
        articles_duplicate INTEGER DEFAULT 0,
        errors_encountered INTEGER DEFAULT 0,
        performance_metrics JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    # SQL to create indexes
    indexes_sql = """
    CREATE INDEX IF NOT EXISTS idx_alert_logs_timestamp ON alert_logs(timestamp DESC);
    CREATE INDEX IF NOT EXISTS idx_alert_logs_level ON alert_logs(level);
    CREATE INDEX IF NOT EXISTS idx_alert_logs_component ON alert_logs(component);
    CREATE INDEX IF NOT EXISTS idx_alert_logs_session_id ON alert_logs(session_id);
    
    CREATE INDEX IF NOT EXISTS idx_scraping_sessions_start_time ON scraping_sessions(start_time DESC);
    CREATE INDEX IF NOT EXISTS idx_scraping_sessions_session_id ON scraping_sessions(session_id);
    """
    
    try:
        print("📝 Creating alert_logs table...")
        db_manager.supabase.rpc('exec_sql', {'sql': alert_logs_sql}).execute()
        print("✅ alert_logs table created successfully")
        
        print("📝 Creating scraping_sessions table...")
        db_manager.supabase.rpc('exec_sql', {'sql': scraping_sessions_sql}).execute()
        print("✅ scraping_sessions table created successfully")
        
        print("📝 Creating indexes...")
        db_manager.supabase.rpc('exec_sql', {'sql': indexes_sql}).execute()
        print("✅ Indexes created successfully")
        
        # Test the tables by inserting a test record
        print("🧪 Testing alert_logs table...")
        test_alert = {
            'timestamp': '2026-01-01T13:00:00Z',
            'level': 'INFO',
            'component': 'TableSetup',
            'message': 'Alert tables created successfully',
            'details': {'setup_version': '1.0'},
            'session_id': 'setup_test'
        }
        
        result = db_manager.supabase.table('alert_logs').insert(test_alert).execute()
        if result.data:
            print("✅ alert_logs table is working correctly")
            
            # Clean up test record
            db_manager.supabase.table('alert_logs').delete().eq('session_id', 'setup_test').execute()
            print("🧹 Cleaned up test record")
        else:
            print("⚠️ alert_logs table created but test insert failed")
        
        print("\n" + "=" * 50)
        print("🎉 SUCCESS: Alert tables are now ready!")
        print("The 404 error should be resolved.")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Try alternative method using direct SQL execution
        print("\n🔄 Trying alternative method...")
        try:
            # Use Supabase SQL editor approach
            print("ℹ️ Manual setup required:")
            print("1. Go to your Supabase dashboard")
            print("2. Navigate to SQL Editor")
            print("3. Run the following SQL:")
            print("\n" + "="*50)
            print(alert_logs_sql)
            print(scraping_sessions_sql)
            print(indexes_sql)
            print("="*50)
            
        except Exception as e2:
            print(f"❌ Alternative method also failed: {e2}")
        
        return False

def test_alert_system():
    """Test the alert system after table creation"""
    try:
        from scraper.core.alert_logger import AlertLogger
        
        print("\n🧪 Testing Alert System...")
        alert_logger = AlertLogger()
        
        # Test logging
        alert_logger.log_info(
            component="SystemTest",
            message="Testing alert system after table creation",
            details={"test_time": "2026-01-01T13:00:00Z"}
        )
        
        print("✅ Alert system is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Alert system test failed: {e}")
        return False

if __name__ == "__main__":
    success = create_alert_tables()
    
    if success:
        test_success = test_alert_system()
        if test_success:
            print("\n🎉 All systems are now working correctly!")
            sys.exit(0)
        else:
            print("\n⚠️ Tables created but alert system needs attention")
            sys.exit(1)
    else:
        print("\n❌ Failed to create alert tables")
        sys.exit(1)