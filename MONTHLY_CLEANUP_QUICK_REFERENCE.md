# Monthly Cleanup System - Quick Reference

## 🎯 What It Does
Automatically deletes articles older than the current month on the 1st of each month at 00:05 AM.

## 📅 Schedule
- **When**: 1st of every month at 00:05 AM
- **Keeps**: Current month's articles only
- **Deletes**: All previous months' articles

## 🚀 Quick Commands

### Start Scheduler (Production)
```bash
python monthly_cleanup_scheduler.py
```

### Preview What Would Be Deleted (Safe)
```bash
python monthly_cleanup_scheduler.py --dry-run
```

### Test Cleanup Immediately
```bash
python monthly_cleanup_scheduler.py --test
```

### Detailed Testing
```bash
# Preview only (safe)
python test_monthly_cleanup.py

# Execute actual cleanup (use with caution)
python test_monthly_cleanup.py --execute
```

## 📊 Current Status

### Next Cleanup
- **Date**: January 1, 2026 at 00:05 AM
- **Days Until**: 11 days
- **Will Keep**: Articles from January 1, 2026 onwards
- **Will Delete**: All December 2025 articles

### Current Database
- **Total Articles**: 67
- **Date Range**: December 2025 only
- **Articles to Delete on Next Cleanup**: All 67 December articles

## 📝 Log File
```bash
# View logs
tail -f monthly_cleanup.log

# Check recent cleanup
tail -20 monthly_cleanup.log
```

## ⚠️ Important Notes

1. **Permanent Deletion**: Deleted articles cannot be recovered
2. **Test First**: Always use `--dry-run` before production deployment
3. **Monitor Logs**: Check logs after first cleanup
4. **Continuous Running**: Scheduler must run continuously in production

## 🔍 Verification

### Check Scheduler Status
```bash
# Check if running
ps aux | grep monthly_cleanup_scheduler

# View current database state
python test_monthly_cleanup.py
```

### After Cleanup
- Check log file for success message
- Verify article count in dashboard
- Confirm only current month's articles remain

## 🆘 Troubleshooting

### Scheduler Not Running
```bash
# Restart scheduler
python monthly_cleanup_scheduler.py
```

### Database Connection Issues
```bash
# Test connection
python test_monthly_cleanup.py
```

### Unexpected Results
```bash
# Run dry-run to preview
python monthly_cleanup_scheduler.py --dry-run

# Check logs
tail -f monthly_cleanup.log
```

## ✅ Quick Checklist

Before Production:
- [ ] Test with `--dry-run`
- [ ] Verify database connection
- [ ] Check log file creation
- [ ] Confirm expected deletion count
- [ ] Start scheduler
- [ ] Monitor first cleanup

---

**For detailed documentation, see `MONTHLY_CLEANUP_GUIDE.md`**