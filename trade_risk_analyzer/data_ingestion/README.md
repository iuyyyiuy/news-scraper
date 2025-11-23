# Data Ingestion Module

The data ingestion module handles importing, validating, and storing trade data from various sources.

## Components

### 1. TradeDataImporter (`importer.py`)

Handles importing trade data from multiple file formats:

- **CSV Import**: Reads CSV files with automatic column detection
- **JSON Import**: Parses JSON files (supports both array and nested object formats)
- **Excel Import**: Reads Excel files (.xlsx, .xls) with sheet selection
- **Auto-detection**: Automatically detects file format based on extension

**Features:**
- Automatic timestamp normalization to ISO8601 format
- Handles multiple date/time format patterns
- Proper type conversion for numeric and string fields
- Generates trade_id if not present
- Column name normalization (lowercase, strip whitespace)

**Usage:**
```python
from trade_risk_analyzer.data_ingestion import TradeDataImporter

importer = TradeDataImporter()

# Import CSV
df = importer.import_csv('trades.csv')

# Import JSON
df = importer.import_json('trades.json')

# Import Excel
df = importer.import_excel('trades.xlsx', sheet_name=0)

# Auto-detect format
df = importer.import_data('trades.csv')
```

### 2. TradeDataValidator (`validator.py`)

Validates imported trade data with detailed error reporting:

**Validation Rules:**
- Required fields: user_id, timestamp, symbol, price, volume, trade_type
- Data type validation for all fields
- Value range validation (price > 0, volume > 0)
- Trade type must be 'BUY' or 'SELL'
- Timestamp must be valid datetime

**Features:**
- Strict mode: Any error invalidates entire dataset
- Non-strict mode: Allows partial imports (skip invalid records)
- Detailed error reporting with row numbers and field names
- Warning system for potential issues
- Extract valid records from mixed dataset

**Usage:**
```python
from trade_risk_analyzer.data_ingestion import TradeDataValidator

validator = TradeDataValidator()

# Validate data (non-strict mode)
result = validator.validate(df, strict=False)

print(f"Valid: {result.valid_records}")
print(f"Invalid: {result.invalid_records}")
print(f"Errors: {len(result.errors)}")

# Get only valid records
valid_df = validator.get_valid_records(df, result)
```

### 3. DatabaseStorage (`storage.py`)

Manages database operations with connection pooling and batch optimization:

**Features:**
- SQLAlchemy-based ORM
- Connection pooling for performance
- Batch insert optimization for large datasets
- Context manager for session management
- CRUD operations for trades and alerts
- Flexible filtering and querying
- Support for both SQLite and PostgreSQL

**Usage:**
```python
from trade_risk_analyzer.data_ingestion import DatabaseStorage

# Initialize storage
storage = DatabaseStorage("sqlite:///trade_risk_analyzer.db")
storage.connect()

# Save trades from DataFrame
storage.save_trades_from_dataframe(df)

# Retrieve trades
trades = storage.get_trades({'user_id': 'user_001'})

# Get as DataFrame
df = storage.get_trades_as_dataframe({
    'start_date': datetime(2024, 1, 1),
    'end_date': datetime(2024, 1, 31)
})

# Get count
count = storage.get_trade_count({'symbol': 'BTC/USDT'})

storage.disconnect()
```

### 4. Database Models (`models.py`)

SQLAlchemy ORM models for database tables:

- **TradeModel**: Stores trade data
- **AlertModel**: Stores risk alerts
- **FeedbackModel**: Stores user feedback on alerts
- **ModelVersionModel**: Tracks ML model versions

**Schema Features:**
- Proper indexing for common queries
- Composite indices for performance
- Foreign key relationships
- JSON fields for flexible data storage
- Automatic timestamp tracking

## Data Flow

```
File (CSV/JSON/Excel)
    ↓
TradeDataImporter
    ↓
DataFrame (normalized)
    ↓
TradeDataValidator
    ↓
Valid DataFrame
    ↓
DatabaseStorage
    ↓
Database (SQLite/PostgreSQL)
```

## Requirements

The module requires the following dependencies:
- pandas >= 2.0.0
- numpy >= 1.24.0
- sqlalchemy >= 2.0.0
- openpyxl (for Excel support)
- pyyaml >= 6.0

## Testing

Run the test suite to verify functionality:

```bash
python test_data_ingestion.py
```

The test suite covers:
- CSV import with various formats
- JSON import with nested structures
- Data validation with invalid records
- Database operations (save, retrieve, filter)
- Batch insert performance

## Error Handling

The module provides comprehensive error handling:

- **FileNotFoundError**: When input file doesn't exist
- **ValueError**: When file format is invalid or unsupported
- **ValidationError**: Detailed field-level validation errors
- **DatabaseError**: Connection and query errors with automatic rollback

All errors are logged with structured logging for debugging.

## Performance Considerations

- **Batch Inserts**: Uses SQLAlchemy's `bulk_insert_mappings` for optimal performance
- **Connection Pooling**: Reuses database connections to reduce overhead
- **Lazy Loading**: Only loads data when needed
- **Index Optimization**: Proper indexing on frequently queried columns

## Future Enhancements

Potential improvements for future versions:
- Streaming import for very large files
- Parallel processing for multiple files
- Data deduplication
- Incremental updates
- Data versioning
- Audit logging
