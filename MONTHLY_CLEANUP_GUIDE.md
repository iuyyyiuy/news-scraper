# Monthly News Database Cleanup System

## 📋 Overview

The Monthly Cleanup System automatically maintains the news database by keeping only articles from the current month. Articles from previous months are automatically deleted on the 1st of each month at 00:05 AM.

## 🎯 Purpose

- **Storage Management**: Prevents database from growing indefinitely
- **Performance**: Keeps database queries fast by limiting data size
- **Data Freshness**: Ensures dashboard shows only recent, relevant news
- **Automated Maintenance**: No manual intervention required

## 📅 Cleanup Schedule

- **When**: 1st of every month at 00:05 AM
- **Retention**: Current month's articles only
- **Deletion**: All articles from previous months
- **Automation**: Fully automated, no manual intervention needed

### Example Timeline

```
December 2025:
├── Dec 1-31: Articles accumulated throughout December
├── Jan 1, 2026 00:05: Cleanup runs
├── Result: Only January 2026 articles remain
└── All December 2025 articles deleted
```

## 🔧 System Components

### 1. Monthly Cleanup Scheduler (`monthly_cleanup_scheduler.py`)
- **Purpose**: Main scheduler that runs the cleanup process
- **Schedule**: Checks daily at 00:05, executes only on 1st of month
- **Logging**: Comprehensive logging to file and console
- **Safety**: Includes dry-run mode for testing

### 2. Database Manager (`scraper/core/database_manager.py`)
- **Method**: `delete_old_articles(before_date)`
- **Function**: Executes the actual deletion from Supabase
- **Safety**: Returns count of deleted articles for verification

### 3. Test Script (`test_monthly_cleanup.py`)
- **Purpose**: Test and preview cleanup functionality
- **Features**: Shows what would be deleted before execution
- **Safety**: Dry-run by default, requires explicit flag for execution

## 🚀 Usage

### Production Deployment
```bash
# Start the scheduler (runs continuously)
python monthly_cleanup_scheduler.py
```

### Testing and Maintenance
```bash
# Preview what would be deleted (safe)
python monthly_cleanup_scheduler.py --dry-run

# Run cleanup immediately (for testing)
python monthly_cleanup_scheduler.py --test

# Detailed testing with preview
python test_monthly_cleanup.py

# Execute actual cleanup (use with caution)
python test_monthly_cleanup.py --execute
```

### Help and Documentation
```bash
# Show usage help
python monthly_cleanup_scheduler.py --help
```

## 📊 Current Status

### Database State (as of December 20, 2025)
- **Total Articles**: 67
- **Date Range**: December 2025 only
- **Next Cleanup**: January 1, 2026 at 00:05
- **Articles to Delete**: 0 (all current month)

### Cleanup Preview
```
📅 Current date: 2025-12-20
🗑️  Cleanup cutoff: 2025-12-01 00:00:00
💾 Will keep: Articles from 2025-12-01 onwards
🗑️  Will delete: Articles before 2025-12-01
📋 Articles that would be deleted: 0
💾 Articles that would be kept: 67
```

## 🛡️ Safety Features

### 1. Dry-Run Mode
- Preview deletions without executing
- Shows exact count and sample articles
- Safe for testing and verification

### 2. Comprehensive Logging
- All operations logged with timestamps
- Separate log file: `monthly_cleanup.log`
- Console output for real-time monitoring

### 3. Error Handling
- Graceful handling of database connection issues
- Detailed error messages and stack traces
- Continues operation even if individual operations fail

### 4. Verification
- Reports before/after article counts
- Confirms deletion counts match expectations
- Logs retention policy compliance

## 📈 Monitoring

### Log File Location
```
monthly_cleanup.log
```

### Log Format
```
2025-12-20 18:29:36,812 - INFO - 🗑️  Monthly Cleanup - 2025-12-20 18:29:36
2025-12-20 18:29:36,813 - INFO - Cutoff date: 2025-12-01
2025-12-20 18:29:37,106 - INFO - Total articles before cleanup: 67
2025-12-20 18:29:37,304 - INFO - Articles to be deleted: 0
```

### Key Metrics to Monitor
- **Total articles before/after cleanup**
- **Number of articles deleted**
- **Cleanup execution time**
- **Any error messages or failures**

## 🔄 Integration with News System

### Dashboard Impact
- **Immediate**: Articles disappear from dashboard after cleanup
- **Performance**: Faster loading due to smaller dataset
- **User Experience**: Only current month's news visible

### Scraper Integration
- **No Impact**: Scraper continues to add new articles normally
- **Compatibility**: Works with all existing scraper functionality
- **Data Flow**: New articles → Database → Monthly cleanup (if old)

### CSV Export Integration
- **Behavior**: Export only includes current month's articles after cleanup
- **Filters**: Date filters automatically limited to available data
- **Performance**: Faster exports due to smaller dataset

## ⚙️ Configuration

### Cleanup Time
Current: **00:05 AM on 1st of each month**

To change the time, modify this line in `monthly_cleanup_scheduler.py`:
```python
schedule.every().day.at("00:05").do(lambda: cleanup_if_first_of_month())
```

### Retention Period
Current: **Current month only**

To change retention (e.g., keep 2 months), modify the cutoff calculation:
```python
# Keep current month only (current behavior)
first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

# Keep 2 months (example modification)
if today.month == 1:
    cutoff_month = 12
    cutoff_year = today.year - 1
else:
    cutoff_month = today.month - 1
    cutoff_year = today.year
first_day_of_month = datetime(cutoff_year, cutoff_month, 1)
```

## 🚨 Important Notes

### Data Loss Warning
- **Permanent**: Deleted articles cannot be recovered
- **Backup**: Consider backing up data before first deployment
- **Testing**: Always test with dry-run mode first

### Production Deployment
1. **Test First**: Run dry-run mode to verify behavior
2. **Monitor Logs**: Check log files after first cleanup
3. **Verify Results**: Confirm article counts match expectations
4. **Schedule**: Ensure scheduler runs continuously in production

### Maintenance
- **Log Rotation**: Consider rotating log files monthly
- **Monitoring**: Set up alerts for cleanup failures
- **Backup**: Regular database backups recommended

## 📞 Troubleshooting

### Common Issues

#### Scheduler Not Running
```bash
# Check if process is running
ps aux | grep monthly_cleanup_scheduler

# Restart scheduler
python monthly_cleanup_scheduler.py
```

#### Database Connection Issues
```bash
# Test database connection
python test_monthly_cleanup.py

# Check environment variables
echo $SUPABASE_URL
echo $SUPABASE_KEY
```

#### Unexpected Deletion Counts
```bash
# Run dry-run to preview
python monthly_cleanup_scheduler.py --dry-run

# Check log files for details
tail -f monthly_cleanup.log
```

### Error Recovery
1. **Check Logs**: Review `monthly_cleanup.log` for error details
2. **Test Connection**: Verify database connectivity
3. **Dry Run**: Use dry-run mode to verify expected behavior
4. **Manual Cleanup**: Use test script with `--execute` flag if needed

## ✅ Verification Checklist

Before deploying to production:

- [ ] Test dry-run mode works correctly
- [ ] Verify database connection
- [ ] Check log file creation and format
- [ ] Confirm scheduler starts without errors
- [ ] Test manual cleanup with test script
- [ ] Verify article counts match expectations
- [ ] Ensure dashboard shows correct data after cleanup
- [ ] Set up monitoring for log files
- [ ] Document any custom configuration changes

## 🎉 Benefits

### For Users
- **Faster Dashboard**: Smaller dataset means faster loading
- **Current News**: Only recent, relevant articles displayed
- **Better Performance**: Improved search and filtering speed

### For Administrators
- **Automated Maintenance**: No manual database cleanup needed
- **Predictable Storage**: Database size remains stable
- **Easy Monitoring**: Comprehensive logging and reporting
- **Safe Operation**: Multiple safety features prevent data loss

### For System
- **Optimal Performance**: Database queries remain fast
- **Storage Efficiency**: Prevents unlimited growth
- **Maintenance Free**: Fully automated operation
- **Reliable**: Robust error handling and recovery

---

**The Monthly Cleanup System ensures your news database remains fast, current, and efficiently managed with minimal maintenance overhead.**