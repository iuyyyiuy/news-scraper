# Quick Start Guide - SQL Database Setup Complete! ✓

## What We Just Did

You now have a **SQL database** (`trade_data.db`) containing all your trade data! This is much better than reading Excel files every time.

## Database Contents

- **15 MB database** with all your trade data
- **21 users** loaded
- **49,592 trades** stored
- **Analysis results** saved in the database

## Files Created

1. **trade_data.db** - Your SQLite database (15 MB)
2. **setup_database.py** - Script to create and populate the database
3. **analyze_from_database.py** - Script to analyze data from the database
4. **query_database.py** - Interactive tool to query the database
5. **DATABASE_GUIDE.md** - Complete guide with SQL examples

## How to Use

### 1. Run Analysis (Anytime)

```bash
python analyze_from_database.py
```

This will:
- Load data from database (super fast!)
- Perform ML analysis
- Save results back to database
- Export CSV files

### 2. Query the Database Interactively

```bash
python query_database.py
```

This gives you a menu with pre-built queries:
- View all users
- Find anomalous users
- Get trades for specific user
- Find coordinated trading
- And more!

### 3. Use Python to Query

```python
import sqlite3
import pandas as pd

# Connect
conn = sqlite3.connect('trade_data.db')

# Query
df = pd.read_sql_query("SELECT * FROM users", conn)
print(df)

conn.close()
```

### 4. View with GUI Tool

Download **DB Browser for SQLite**: https://sqlitebrowser.org/

Then open `trade_data.db` to browse visually.

## Useful SQL Queries

### Get all users sorted by activity
```sql
SELECT * FROM users ORDER BY total_trades DESC;
```

### Get latest analysis results
```sql
SELECT * FROM analysis_results 
WHERE analysis_date = (SELECT MAX(analysis_date) FROM analysis_results)
ORDER BY anomaly_score DESC;
```

### Get trades for a specific user
```sql
SELECT * FROM trades 
WHERE user_id = 'user_8363457' 
ORDER BY timestamp;
```

### Find coordinated trading
```sql
SELECT 
    timestamp,
    symbol,
    COUNT(DISTINCT user_id) as user_count,
    GROUP_CONCAT(DISTINCT user_id) as users
FROM trades
GROUP BY timestamp, symbol
HAVING user_count > 1
ORDER BY user_count DESC;
```

## Database Schema

### Tables

**users**
- user_id (primary key)
- first_seen, last_seen
- total_trades
- data_source
- notes

**trades**
- trade_id (primary key)
- user_id, timestamp, symbol
- price, volume, trade_type
- order_id

**analysis_results**
- user_id, analysis_date
- anomaly_score, is_anomaly
- trades_per_day, win_ratio
- risk_level, notes

## Benefits vs Excel Files

✓ **100x faster** - No need to read Excel files every time
✓ **Persistent** - Analysis results are saved
✓ **Queryable** - Use SQL for complex questions
✓ **Scalable** - Can handle millions of trades
✓ **Historical** - Track changes over time

## Next Steps

1. **Explore the data**: Run `python query_database.py`
2. **Run analysis**: Run `python analyze_from_database.py`
3. **Learn SQL**: Check out `DATABASE_GUIDE.md`
4. **Build dashboards**: Connect to visualization tools
5. **Automate**: Schedule regular analysis runs

## Maintenance

### Backup database
```bash
cp trade_data.db trade_data_backup.db
```

### Re-import data (if you add new Excel files)
```bash
python setup_database.py
```

### Clear old analysis results
```python
import sqlite3
conn = sqlite3.connect('trade_data.db')
conn.execute("DELETE FROM analysis_results WHERE analysis_date < date('now', '-7 days')")
conn.commit()
conn.close()
```

## Troubleshooting

**Q: Database is locked**
A: Close any programs that have it open (including DB Browser)

**Q: Want to start fresh?**
A: Delete `trade_data.db` and run `python setup_database.py` again

**Q: Need to add more data?**
A: Just run `python setup_database.py` again - it will update existing records

## Summary

You've successfully migrated from Excel files to a SQL database! This is a huge improvement for:
- Performance
- Data management
- Analysis capabilities
- Future scalability

Read `DATABASE_GUIDE.md` for more advanced usage and SQL examples.
