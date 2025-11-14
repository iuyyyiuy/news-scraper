"""
Simple Database Query Tool

Run pre-defined queries or custom SQL against the trade database.
"""

import sqlite3
import pandas as pd
from datetime import datetime


def connect_db(db_path='trade_data.db'):
    """Connect to database"""
    return sqlite3.connect(db_path)


def query_1_all_users(conn):
    """Get all users with summary statistics"""
    print("\n" + "=" * 80)
    print("ALL USERS SUMMARY")
    print("=" * 80)
    
    query = '''
        SELECT 
            user_id,
            total_trades,
            first_seen,
            last_seen,
            ROUND((julianday(last_seen) - julianday(first_seen)), 2) as days,
            ROUND(total_trades / (julianday(last_seen) - julianday(first_seen) + 0.01), 2) as trades_per_day
        FROM users
        ORDER BY trades_per_day DESC
    '''
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    return df


def query_2_anomalous_users(conn):
    """Get users flagged as anomalies"""
    print("\n" + "=" * 80)
    print("ANOMALOUS USERS")
    print("=" * 80)
    
    query = '''
        SELECT 
            ar.user_id,
            ar.anomaly_score,
            ar.risk_level,
            ar.trades_per_day,
            ar.win_ratio,
            ar.analysis_date,
            u.total_trades
        FROM analysis_results ar
        JOIN users u ON ar.user_id = u.user_id
        WHERE ar.is_anomaly = 1
        ORDER BY ar.anomaly_score DESC
    '''
    
    df = pd.read_sql_query(query, conn)
    if df.empty:
        print("No analysis results found. Run analyze_from_database.py first.")
    else:
        print(df.to_string(index=False))
    return df


def query_3_user_trades(conn, user_id):
    """Get all trades for a specific user"""
    print("\n" + "=" * 80)
    print(f"TRADES FOR {user_id}")
    print("=" * 80)
    
    query = '''
        SELECT 
            timestamp,
            symbol,
            trade_type,
            price,
            volume,
            order_id
        FROM trades
        WHERE user_id = ?
        ORDER BY timestamp
    '''
    
    df = pd.read_sql_query(query, conn, params=[user_id])
    print(f"\nTotal trades: {len(df)}")
    print(df.head(20).to_string(index=False))
    if len(df) > 20:
        print(f"\n... and {len(df) - 20} more trades")
    return df


def query_4_coordinated_trading(conn):
    """Find potential coordinated trading"""
    print("\n" + "=" * 80)
    print("POTENTIAL COORDINATED TRADING")
    print("=" * 80)
    
    query = '''
        SELECT 
            timestamp,
            symbol,
            COUNT(DISTINCT user_id) as user_count,
            GROUP_CONCAT(DISTINCT user_id) as users,
            COUNT(*) as trade_count
        FROM trades
        GROUP BY timestamp, symbol
        HAVING user_count > 1
        ORDER BY user_count DESC, trade_count DESC
        LIMIT 20
    '''
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    return df


def query_5_trading_by_hour(conn, user_id=None):
    """Get trading activity by hour of day"""
    print("\n" + "=" * 80)
    if user_id:
        print(f"TRADING ACTIVITY BY HOUR - {user_id}")
    else:
        print("TRADING ACTIVITY BY HOUR - ALL USERS")
    print("=" * 80)
    
    if user_id:
        query = '''
            SELECT 
                strftime('%H', timestamp) as hour,
                COUNT(*) as trade_count
            FROM trades
            WHERE user_id = ?
            GROUP BY hour
            ORDER BY hour
        '''
        df = pd.read_sql_query(query, conn, params=[user_id])
    else:
        query = '''
            SELECT 
                user_id,
                strftime('%H', timestamp) as hour,
                COUNT(*) as trade_count
            FROM trades
            GROUP BY user_id, hour
            ORDER BY user_id, hour
        '''
        df = pd.read_sql_query(query, conn)
    
    print(df.to_string(index=False))
    return df


def query_6_symbol_distribution(conn):
    """Get symbol distribution per user"""
    print("\n" + "=" * 80)
    print("SYMBOL DISTRIBUTION PER USER")
    print("=" * 80)
    
    query = '''
        SELECT 
            user_id,
            symbol,
            COUNT(*) as trade_count,
            ROUND(AVG(price), 2) as avg_price,
            ROUND(SUM(volume), 2) as total_volume
        FROM trades
        GROUP BY user_id, symbol
        ORDER BY user_id, trade_count DESC
    '''
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    return df


def query_7_high_frequency_periods(conn, user_id):
    """Find high-frequency trading periods for a user"""
    print("\n" + "=" * 80)
    print(f"HIGH-FREQUENCY PERIODS - {user_id}")
    print("=" * 80)
    
    query = '''
        SELECT 
            DATE(timestamp) as date,
            strftime('%H', timestamp) as hour,
            COUNT(*) as trade_count
        FROM trades
        WHERE user_id = ?
        GROUP BY date, hour
        HAVING trade_count > 10
        ORDER BY trade_count DESC
        LIMIT 20
    '''
    
    df = pd.read_sql_query(query, conn, params=[user_id])
    print(df.to_string(index=False))
    return df


def query_8_latest_analysis(conn):
    """Get the latest analysis results"""
    print("\n" + "=" * 80)
    print("LATEST ANALYSIS RESULTS")
    print("=" * 80)
    
    query = '''
        SELECT 
            user_id,
            anomaly_score,
            CASE WHEN is_anomaly = 1 THEN 'ANOMALY' ELSE 'NORMAL' END as status,
            risk_level,
            ROUND(trades_per_day, 2) as trades_per_day,
            ROUND(win_ratio, 3) as win_ratio,
            analysis_date
        FROM analysis_results
        WHERE analysis_date = (SELECT MAX(analysis_date) FROM analysis_results)
        ORDER BY anomaly_score DESC
    '''
    
    df = pd.read_sql_query(query, conn)
    if df.empty:
        print("No analysis results found. Run analyze_from_database.py first.")
    else:
        print(df.to_string(index=False))
    return df


def custom_query(conn, sql):
    """Run a custom SQL query"""
    print("\n" + "=" * 80)
    print("CUSTOM QUERY RESULTS")
    print("=" * 80)
    print(f"Query: {sql}\n")
    
    try:
        df = pd.read_sql_query(sql, conn)
        print(df.to_string(index=False))
        return df
    except Exception as e:
        print(f"Error: {e}")
        return None


def interactive_menu():
    """Interactive query menu"""
    conn = connect_db()
    
    while True:
        print("\n" + "=" * 80)
        print("DATABASE QUERY TOOL")
        print("=" * 80)
        print("\nAvailable Queries:")
        print("  1. All users summary")
        print("  2. Anomalous users")
        print("  3. User trades (specify user_id)")
        print("  4. Coordinated trading patterns")
        print("  5. Trading by hour")
        print("  6. Symbol distribution")
        print("  7. High-frequency periods (specify user_id)")
        print("  8. Latest analysis results")
        print("  9. Custom SQL query")
        print("  0. Exit")
        
        choice = input("\nEnter choice (0-9): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            query_1_all_users(conn)
        elif choice == '2':
            query_2_anomalous_users(conn)
        elif choice == '3':
            user_id = input("Enter user_id (e.g., user_8363457): ").strip()
            query_3_user_trades(conn, user_id)
        elif choice == '4':
            query_4_coordinated_trading(conn)
        elif choice == '5':
            user_id = input("Enter user_id (or press Enter for all users): ").strip()
            query_5_trading_by_hour(conn, user_id if user_id else None)
        elif choice == '6':
            query_6_symbol_distribution(conn)
        elif choice == '7':
            user_id = input("Enter user_id (e.g., user_8363457): ").strip()
            query_7_high_frequency_periods(conn, user_id)
        elif choice == '8':
            query_8_latest_analysis(conn)
        elif choice == '9':
            sql = input("Enter SQL query: ").strip()
            custom_query(conn, sql)
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")
    
    conn.close()
    print("\nGoodbye!")


def main():
    """Main function"""
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "DATABASE QUERY TOOL".center(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    
    interactive_menu()


if __name__ == "__main__":
    main()
