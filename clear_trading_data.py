#!/usr/bin/env python3
"""
Clear Trading Data
Removes all existing trading data to start fresh with only your uploaded CSV
"""

import sqlite3
import os
import requests

def clear_all_trading_data():
    """Clear all trading data from the database"""
    
    print("🗑️  Clearing All Trading Data")
    print("=" * 40)
    
    # Database path
    db_path = "trading_analysis.db"
    
    if not os.path.exists(db_path):
        print("❌ Trading database not found")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current data
        print("\n1. Checking current data...")
        cursor.execute("SELECT COUNT(*) FROM trading_records")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM trading_records")
        unique_users = cursor.fetchone()[0]
        
        print(f"   📊 Current records: {total_records}")
        print(f"   👥 Unique users: {unique_users}")
        
        if total_records == 0:
            print("✅ Database is already empty")
            conn.close()
            return True
        
        # Show current users
        cursor.execute("SELECT user_id, COUNT(*) as trade_count FROM trading_records GROUP BY user_id")
        users = cursor.fetchall()
        
        print("\n   Current users in database:")
        for user_id, count in users:
            print(f"      - {user_id}: {count} trades")
        
        # Clear all data
        print("\n2. Clearing all trading data...")
        
        # Clear trading records
        cursor.execute("DELETE FROM trading_records")
        deleted_records = cursor.rowcount
        
        # Clear news correlations
        cursor.execute("DELETE FROM news_correlations")
        deleted_correlations = cursor.rowcount
        
        # Clear strategy analysis
        cursor.execute("DELETE FROM strategy_analysis")
        deleted_analyses = cursor.rowcount
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print(f"✅ Cleared {deleted_records} trading records")
        print(f"✅ Cleared {deleted_correlations} news correlations")
        print(f"✅ Cleared {deleted_analyses} strategy analyses")
        
        return True
        
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        return False

def clear_via_api():
    """Clear data via API endpoint"""
    
    print("\n3. Clearing data via API...")
    
    try:
        response = requests.delete("http://localhost:8000/api/trading-strategy/clear-data")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ API clear successful")
                return True
            else:
                print(f"❌ API clear failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error calling API: {e}")
        return False

def verify_clean_state():
    """Verify that the database is now clean"""
    
    print("\n4. Verifying clean state...")
    
    try:
        response = requests.get("http://localhost:8000/api/trading-strategy/data-summary")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                summary = result.get('summary', {})
                total_trades = summary.get('total_trades', 0)
                unique_traders = summary.get('unique_traders', 0)
                
                print(f"   📊 Total trades: {total_trades}")
                print(f"   👥 Unique traders: {unique_traders}")
                
                if total_trades == 0:
                    print("✅ Database is now clean and ready for fresh upload")
                    return True
                else:
                    print("⚠️  Some data still remains")
                    return False
            else:
                print("❌ Could not verify clean state")
                return False
        else:
            print(f"❌ Verification request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying state: {e}")
        return False

def main():
    """Main function to clear all trading data"""
    
    print("🧹 Trading Data Cleanup Tool")
    print("This will remove ALL existing trading data from the system")
    print("=" * 60)
    
    # Method 1: Direct database clearing
    success1 = clear_all_trading_data()
    
    # Method 2: API clearing (if server is running)
    success2 = clear_via_api()
    
    # Verify clean state
    if success1 or success2:
        verify_clean_state()
    
    print("\n" + "=" * 60)
    
    if success1 or success2:
        print("🎉 Trading Data Cleared Successfully!")
        print("\n📋 What was cleared:")
        print("   ✅ All trading records")
        print("   ✅ All news correlations") 
        print("   ✅ All strategy analyses")
        print("\n🚀 Next Steps:")
        print("   1. Upload your CSV file again")
        print("   2. Only your data will be in the system")
        print("   3. Run analysis to see results for just your trader")
    else:
        print("❌ Failed to clear trading data")
        print("\n🔧 Manual Steps:")
        print("   1. Stop the server")
        print("   2. Delete the 'trading_analysis.db' file")
        print("   3. Restart the server")
        print("   4. Upload your CSV again")

if __name__ == "__main__":
    main()