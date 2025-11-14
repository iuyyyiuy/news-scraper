# New Database Structure Guide

## ✅ Database Created Successfully!

Your new database `trading_data.db` has been created with a professional structure.

## Database Structure

### 📊 Overview

```
trading_data.db
│
├── users (Central user registry)
│   ├── user_id (PRIMARY KEY)
│   ├── created_at
│   ├── updated_at
│   └── notes
│
├── FUTURES TRADES
│   ├── futures_trades_orders (Order history)
│   │   ├── order_id (PRIMARY KEY)
│   │   ├── user_id (FOREIGN KEY → users)
│   │   ├── symbol, price, quantity
│   │   └── ... 20+ columns
│   │
│   └── futures_trades_history (Trade executions)
│       ├── trade_id (PRIMARY KEY)
│       ├── user_id (FOREIGN KEY → users)
│       ├── order_id (FOREIGN KEY → futures_trades_orders)
│       ├── symbol, price, quantity
│       └── ... 15+ columns
│
└── SPOT TRADES
    ├── spot_trades_orders (Order history)
    │   ├── order_id (PRIMARY KEY)
    │   ├── user_id (FOREIGN KEY → users)
    │   ├── symbol, price, quantity
    │   └── ... 15+ columns
    │
    └── spot_trades_history (Trade executions)
        ├── trade_id (PRIMARY KEY)
        ├── user_id (FOREIGN KEY → users)
        ├── order_id (FOREIGN KEY → spot_trades_orders)
        ├── symbol, price, quantity
        └── ... 12+ columns
```

## Table Details

### 1. users
Central registry of all users.

**Columns:**
- `user_id` (TEXT, PRIMARY KEY) - Unique user identifier
- `created_at` (TIMESTAMP) - When user was added
- `updated_at` (TIMESTAMP) - Last update time
- `notes` (TEXT) - Flexible field for any notes

**Future-proof:** You can add more columns anytime:
```sql
ALTER TABLE users ADD COLUMN email TEXT;
ALTER TABLE users ADD COLUMN account_type TEXT;
ALTER TABLE users ADD COLUMN risk_level TEXT;
```

### 2. futures_trades_orders
All futures orders (limit, market, stop, etc.)

**Key Columns:**
- `order_id` - Unique order identifier
- `user_id` - Who placed the order
- `symbol` - Trading pair (BTCUSDT, ETHUSDT, etc.)
- `order_type` - LIMIT, MARKET, STOP, etc.
- `side` - BUY or SELL
- `price` - Order price
- `quantity` - Order quantity
- `filled_quantity` - How much was filled
- `status` - NEW, FILLED, CANCELED, etc.
- `order_time` - When order was placed
- `position_side` - LONG or SHORT
- `reduce_only` - If order only reduces position
- And more...

### 3. futures_trades_history
Individual trade executions for futures.

**Key Columns:**
- `trade_id` - Unique trade identifier
- `user_id` - Who made the trade
- `order_id` - Which order this trade belongs to
- `symbol` - Trading pair
- `side` - BUY or SELL
- `price` - Execution price
- `quantity` - Trade quantity
- `commission` - Fee paid
- `commission_asset` - Fee currency
- `trade_time` - When trade executed
- `realized_pnl` - Profit/loss realized
- `is_buyer` - 1 if buyer, 0 if seller
- `is_maker` - 1 if maker, 0 if taker

### 4. spot_trades_orders
All spot orders.

**Similar to futures_trades_orders but for spot market**
- No position_side, reduce_only (spot doesn't have positions)
- Has iceberg_quantity for iceberg orders
- Has self_trade_prevention_mode

### 5. spot_trades_history
Individual trade executions for spot.

**Similar to futures_trades_history but for spot market**
- No realized_pnl (spot doesn't have positions)
- Has is_best_match field

## Indexes Created

For fast queries, indexes are created on:
- All `user_id` columns
- All `symbol` columns
- All time columns (`order_time`, `trade_time`)
- All `order_id` foreign keys

## How to Use

### 1. Open in DB Browser

1. Open DB Browser for SQLite
2. File → Open Database
3. Select `trading_data.db`
4. Explore the tables!

### 2. Add Users

```python
import sqlite3

conn = sqlite3.connect('trading_data.db')
cursor = conn.cursor()

cursor.execute('''
    INSERT INTO users (user_id, notes)
    VALUES ('user_12345', 'High-frequency trader')
''')

conn.commit()
conn.close()
```

### 3. Import Futures Trades

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('trading_data.db')

# Read your data
df = pd.read_excel('futures_data.xlsx')

# Import each trade
for idx, row in df.iterrows():
    cursor.execute('''
        INSERT INTO futures_trades_history (
            trade_id, user_id, symbol, side, price, quantity, trade_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        f"trade_{idx}",
        row['user_id'],
        row['symbol'],
        row['side'],
        row['price'],
        row['quantity'],
        row['timestamp']
    ))

conn.commit()
conn.close()
```

### 4. Import Spot Trades

Same as futures, but use `spot_trades_history` table.

## Useful Queries

### Get all trades for a user (both futures and spot)

```sql
SELECT 'futures' as market, trade_id, symbol, side, price, quantity, trade_time
FROM futures_trades_history
WHERE user_id = 'user_12345'

UNION ALL

SELECT 'spot' as market, trade_id, symbol, side, price, quantity, trade_time
FROM spot_trades_history
WHERE user_id = 'user_12345'

ORDER BY trade_time DESC;
```

### Get trading volume by user and market

```sql
SELECT 
    user_id,
    'futures' as market,
    COUNT(*) as trade_count,
    SUM(quantity) as total_volume
FROM futures_trades_history
GROUP BY user_id

UNION ALL

SELECT 
    user_id,
    'spot' as market,
    COUNT(*) as trade_count,
    SUM(quantity) as total_volume
FROM spot_trades_history
GROUP BY user_id;
```

### Find users trading both futures and spot

```sql
SELECT DISTINCT f.user_id
FROM futures_trades_history f
INNER JOIN spot_trades_history s ON f.user_id = s.user_id;
```

### Get all trades for a symbol across both markets

```sql
SELECT 'futures' as market, * FROM futures_trades_history WHERE symbol = 'BTCUSDT'
UNION ALL
SELECT 'spot' as market, * FROM spot_trades_history WHERE symbol = 'BTCUSDT'
ORDER BY trade_time;
```

### Trading activity by hour

```sql
SELECT 
    strftime('%H', trade_time) as hour,
    COUNT(*) as trade_count
FROM futures_trades_history
GROUP BY hour
ORDER BY hour;
```

## Adding More Columns (Future-Proof)

You can easily add columns to any table:

```sql
-- Add to users table
ALTER TABLE users ADD COLUMN email TEXT;
ALTER TABLE users ADD COLUMN account_type TEXT;
ALTER TABLE users ADD COLUMN parent_account TEXT;
ALTER TABLE users ADD COLUMN risk_category TEXT;
ALTER TABLE users ADD COLUMN registration_date TIMESTAMP;

-- Add to trades tables
ALTER TABLE futures_trades_history ADD COLUMN strategy_id TEXT;
ALTER TABLE spot_trades_history ADD COLUMN api_key_id TEXT;
```

## Migration from Old Database

If you want to migrate data from `trade_data.db` to `trading_data.db`:

```python
import sqlite3

# Connect to both databases
old_conn = sqlite3.connect('trade_data.db')
new_conn = sqlite3.connect('trading_data.db')

# Read from old
old_cursor = old_conn.cursor()
old_cursor.execute("SELECT DISTINCT user_id FROM trades")
users = old_cursor.fetchall()

# Write to new
new_cursor = new_conn.cursor()
for user in users:
    new_cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", user)

new_conn.commit()

# Migrate trades (you'll need to decide if they're futures or spot)
old_cursor.execute("SELECT * FROM trades")
trades = old_cursor.fetchall()

for trade in trades:
    # Map to new structure and insert
    # ... your logic here
    pass

old_conn.close()
new_conn.close()
```

## Best Practices

1. **Always insert users first** before adding their trades
2. **Use transactions** for bulk imports (faster)
3. **Use prepared statements** to prevent SQL injection
4. **Backup regularly** - just copy the .db file
5. **Add indexes** if you add new query patterns
6. **Use foreign keys** to maintain data integrity

## Next Steps

1. ✅ Database structure created
2. 📝 Decide how to import your existing data
3. 🔄 Write import scripts for your Excel files
4. 📊 Start querying and analyzing
5. 🚀 Build dashboards or reports

## Files Created

- `trading_data.db` - Your new database
- `create_new_schema.py` - Script to recreate schema
- `import_trades_template.py` - Template for importing data
- `NEW_DATABASE_GUIDE.md` - This guide

## Support

The structure is flexible and can grow with your needs. You can:
- Add more columns anytime
- Add more tables (e.g., for alerts, investigations)
- Add more indexes for performance
- Migrate to PostgreSQL later if needed (same structure works!)

Your database is ready to use! 🎉
