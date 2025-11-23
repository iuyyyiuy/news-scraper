# SQL Database Guide for Trade Risk Analyzer

## Overview

This guide will help you set up and use a SQL database to store and analyze trade data instead of reading from Excel files each time.

## Quick Start

### Step 1: Set Up the Database

Run this command to create the database and load all your Excel data:

```bash
python setup_database.py
```

This will:
- Create a SQLite database file called `trade_data.db`
- Create tables for users, trades, and analysis results
- Load all Excel files from your directories
- Verify the data was loaded correctly

### Step 2: Run Analysis from Database

```bash
python analyze_from_database.py
```

This will:
- Load trade data from the database (much faster!)
- Perform the same analysis as before
- Save results back to the database
- Export CSV files for review

## Database Schema

### Tables

#### 1. `users` table
Stores user information:
- `user_id` (TEXT, PRIMARY KEY): Unique user identifier
- `first_seen` (TIMESTAMP): First trade timestamp
- `last_seen` (TIMESTAMP): Last trade timestamp
- `total_trades` (INTEGER): Total number of trades
- `data_source` (TEXT): Original Excel file path
- `notes` (TEXT): Optional notes

#### 2. `trades` table
Stores all trade records:
- `trade_id` (TEXT, PRIMARY KEY): Unique trade identifier
- `user_id` (TEXT): User who made the trade
- `timestamp` (TIMESTAMP): When the trade occurred
- `symbol` (TEXT): Trading pair (e.g., BTCUSDT)
- `price` (REAL): Trade price
- `volume` (REAL): Trade volume
- `trade_type` (TEXT): BUY or SELL
- `order_id` (TEXT): Order identifier

#### 3. `analysis_results` table
Stores analysis results:
- `id` (INTEGER, PRIMARY KEY): Auto-increment ID
- `user_id` (TEXT): User analyzed
- `analysis_date` (TIMESTAMP): When analysis was run
- `anomaly_score` (REAL): ML anomaly score
- `is_anomaly` (BOOLEAN): 1 if anomaly, 0 if normal
- `trades_per_day` (REAL): Trading frequency
- `win_ratio` (REAL): Win/loss ratio
- `risk_level` (TEXT): CRITICAL, HIGH, MEDIUM, or LOW
- `notes` (TEXT): Optional notes

## Useful SQL Queries

### Basic Queries

#### Get all users
```sql
SELECT * FROM users ORDER BY total_trades DESC;
```

#### Get trades for a specific user
```sql
SELECT * FROM trades 
WHERE user_id = 'user_8363457' 
ORDER BY timestamp;
```

#### Get latest analysis results
```sql
SELECT * FROM analysis_results 
ORDER BY analysis_date DESC, anomaly_score DESC;
```

### Advanced Queries

#### Find high-frequency traders
```sql
SELECT 
    user_id,
    total_trades,
    ROUND((julianday(last_seen) - julianday(first_seen)), 2) as days,
    ROUND(total_trades / (julianday(last_seen) - julianday(first_seen) + 0.01), 2) as trades_per_day
FROM users
WHERE trades_per_day > 100
ORDER BY trades_per_day DESC;
```

#### Get trading activity by hour
```sql
SELECT 
    user_id,
    strftime('%H', timestamp) as hour,
    COUNT(*) as trade_count
FROM trades
GROUP BY user_id, hour
ORDER BY user_id, hour;
```

#### Find users with suspicious patterns
```sql
SELECT 
    u.user_id,
    u.total_trades,
    ar.anomaly_score,
    ar.risk_level,
    ar.trades_per_day,
    ar.win_ratio
FROM users u
JOIN analysis_results ar ON u.user_id = ar.user_id
WHERE ar.is_anomaly = 1
ORDER BY ar.anomaly_score DESC;
```

#### Get symbol distribution per user
```sql
SELECT 
    user_id,
    symbol,
    COUNT(*) as trade_count,
    ROUND(AVG(price), 2) as avg_price,
    ROUND(SUM(volume), 2) as total_volume
FROM trades
GROUP BY user_id, symbol
ORDER BY user_id, trade_count DESC;
```

#### Find coordinated trading (same timestamps)
```sql
SELECT 
    t1.timestamp,
    t1.symbol,
    COUNT(DISTINCT t1.user_id) as user_count,
    GROUP_CONCAT(DISTINCT t1.user_id) as users
FROM trades t1
GROUP BY t1.timestamp, t1.symbol
HAVING user_count > 1
ORDER BY user_count DESC, t1.timestamp;
```

## Python Database Access

### Using Python to Query the Database

```python
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('trade_data.db')

# Query using pandas
df = pd.read_sql_query("SELECT * FROM users", conn)
print(df)

# Query using cursor
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM trades")
count = cursor.fetchone()[0]
print(f"Total trades: {count}")

# Close connection
conn.close()
```

### Example: Get Specific User's Trades

```python
import sqlite3
import pandas as pd

def get_user_trades(user_id):
    conn = sqlite3.connect('trade_data.db')
    
    query = """
        SELECT * FROM trades 
        WHERE user_id = ? 
        ORDER BY timestamp
    """
    
    df = pd.read_sql_query(query, conn, params=[user_id])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    conn.close()
    return df

# Usage
trades = get_user_trades('user_8363457')
print(f"Found {len(trades)} trades")
```

### Example: Add Notes to Users

```python
import sqlite3

def add_user_note(user_id, note):
    conn = sqlite3.connect('trade_data.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE users SET notes = ? WHERE user_id = ?",
        (note, user_id)
    )
    
    conn.commit()
    conn.close()

# Usage
add_user_note('user_8363457', 'Suspected wash trading - high volume, low profit')
```

## Benefits of Using Database

1. **Performance**: Much faster than reading Excel files every time
2. **Persistence**: Analysis results are saved and can be tracked over time
3. **Querying**: Use SQL to ask complex questions about the data
4. **Scalability**: Can handle millions of trades efficiently
5. **Integration**: Easy to connect to other tools and dashboards
6. **History**: Track how user behavior changes over time

## Database Tools

### SQLite Browser (GUI)
Download: https://sqlitebrowser.org/

This free tool lets you:
- Browse tables visually
- Run SQL queries with a GUI
- Export data to various formats
- Edit data manually if needed

### Command Line Access

```bash
# Open database in SQLite CLI
sqlite3 trade_data.db

# Run queries
sqlite> SELECT COUNT(*) FROM users;
sqlite> .tables
sqlite> .schema trades
sqlite> .quit
```

## Maintenance

### Backup Database
```bash
cp trade_data.db trade_data_backup_$(date +%Y%m%d).db
```

### Clear Analysis Results
```sql
DELETE FROM analysis_results;
```

### Re-import Data
```bash
# Delete old database
rm trade_data.db

# Run setup again
python setup_database.py
```

## Next Steps

1. Run `setup_database.py` to create your database
2. Run `analyze_from_database.py` to perform analysis
3. Use SQL queries to explore the data
4. Build custom reports or dashboards
5. Integrate with other systems

## Troubleshooting

### Database locked error
- Close any programs that have the database open
- Make sure only one script accesses the database at a time

### Missing data
- Check that Excel files are in the correct directories
- Verify file names start with "UID "
- Run setup_database.py again

### Slow queries
- The database has indexes on common fields
- For very large datasets, consider PostgreSQL or MySQL
