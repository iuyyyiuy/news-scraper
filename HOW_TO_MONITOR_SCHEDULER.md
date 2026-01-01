# How to Monitor Your Automated News Scheduler 📊

**Droplet IP**: 143.198.219.220  
**Schedule**: Every 4 hours (00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC)

## 🔍 Quick Status Check Commands

### 1. Overall System Status
```bash
ssh root@143.198.219.220
cd /opt/news-scraper
python3 check_scheduler_status.py
```

**Expected Output (Working):**
```
🔍 News Scheduler Status Check
========================================
Systemd Timer: ✅ Active
Recent Activity: ✅ Last run: 2026-01-01 12:00:15
Next Scheduled: ⏰ Wed 2026-01-01 16:00:00 UTC
========================================
✅ Scheduler is working properly
```

### 2. Check Systemd Timer Status
```bash
systemctl status news-scheduler.timer
```

**Expected Output (Working):**
```
● news-scheduler.timer - Run News Scheduler every 4 hours
   Loaded: loaded (/etc/systemd/system/news-scheduler.timer; enabled; vendor preset: enabled)
   Active: active (waiting) since Wed 2026-01-01 08:00:00 UTC; 4h ago
   Trigger: Wed 2026-01-01 16:00:00 UTC; 3h 45min left
```

### 3. View Next Scheduled Runs
```bash
systemctl list-timers news-scheduler.timer
```

**Expected Output:**
```
NEXT                        LEFT     LAST                        PASSED UNIT                   ACTIVATES
Wed 2026-01-01 16:00:00 UTC 3h left Wed 2026-01-01 12:00:00 UTC 1h ago news-scheduler.timer   news-scheduler.service
```

## 📋 Log Monitoring

### 4. Real-Time Log Monitoring
```bash
# Watch logs in real-time
tail -f /var/log/news-scraper/scheduler.log

# Or using journalctl
journalctl -u news-scheduler.service -f
```

### 5. Check Recent Log Entries
```bash
# Last 20 lines
tail -20 /var/log/news-scraper/scheduler.log

# Last 50 lines with timestamps
tail -50 /var/log/news-scraper/scheduler.log | grep -E "(Starting|completed|ERROR|✅|❌)"
```

**Expected Log Pattern (Working):**
```
2026-01-01 12:00:15 - INFO - 🚀 Starting scheduled scrape at 2026-01-01 12:00:15
2026-01-01 12:00:15 - INFO - 📊 Target: 100 articles with 21 security keywords
2026-01-01 12:00:45 - INFO - 📊 Scraping completed: Total articles checked: 100
2026-01-01 12:01:15 - INFO - 🤖 AI analysis completed: 8 articles after filtering
2026-01-01 12:01:30 - INFO - 💾 Storing 8 articles in database...
2026-01-01 12:01:45 - INFO - ✅ Scheduled scrape completed successfully: 3 articles stored
```

## 💾 Database Verification

### 6. Check Database for New Articles
```bash
# Test database connection
cd /opt/news-scraper
python3 -c "
from scraper.core.database_manager import DatabaseManager
import datetime
db = DatabaseManager()
result = db.supabase.table('articles').select('*').gte('scraped_at', '2026-01-01T00:00:00').execute()
print(f'✅ Articles added today: {len(result.data)}')
for article in result.data[-3:]:  # Show last 3
    print(f'   - {article[\"title\"][:60]}...')
"
```

### 7. Check Supabase Dashboard
1. Go to https://supabase.com/dashboard
2. Open your project
3. Go to **Table Editor** → **articles**
4. Sort by **scraped_at** (descending)
5. Look for recent entries every 4 hours

## 🎯 Success Indicators

### ✅ Your Scheduler is Working When You See:

1. **Timer Active**: `systemctl status news-scheduler.timer` shows "active (waiting)"
2. **Regular Schedule**: Next run shows in 4-hour intervals
3. **Recent Logs**: New log entries every 4 hours
4. **Database Updates**: New articles in Supabase every 4 hours
5. **No Errors**: Log files don't show critical errors

### ❌ Signs Something is Wrong:

1. **Timer Inactive**: Status shows "inactive" or "failed"
2. **No Recent Logs**: No log entries in the last 5+ hours
3. **No Database Updates**: No new articles in Supabase
4. **Error Messages**: Logs show repeated errors

## 🔧 Troubleshooting Commands

### If Timer is Not Active:
```bash
# Enable and start the timer
systemctl enable news-scheduler.timer
systemctl start news-scheduler.timer

# Check status again
systemctl status news-scheduler.timer
```

### If No Recent Activity:
```bash
# Check for errors in logs
grep -i error /var/log/news-scraper/scheduler.log | tail -10

# Run manual test
sudo -u www-data python3 /opt/news-scraper/automated_news_scheduler.py
```

### If Database Connection Issues:
```bash
# Test database connection
cd /opt/news-scraper
python3 -c "from scraper.core.database_manager import DatabaseManager; db = DatabaseManager(); print('✅ Database connected')"

# Check environment file
cat .env | grep SUPABASE
```

## 📱 Dashboard Monitoring

### 8. Check Your News Dashboard
1. Open your news dashboard in browser
2. Look for **recent articles** (should update every 4 hours)
3. Check **article timestamps** (should be fresh)
4. Verify **no duplicates** (enhanced detection working)

## ⏰ Schedule Reference

**UTC Times** (Your scheduler runs at):
- 00:00 UTC (Midnight)
- 04:00 UTC (4 AM)
- 08:00 UTC (8 AM)
- 12:00 UTC (Noon)
- 16:00 UTC (4 PM)
- 20:00 UTC (8 PM)

**Convert to Your Local Time:**
- If you're in EST (UTC-5): subtract 5 hours
- If you're in PST (UTC-8): subtract 8 hours
- If you're in CST (UTC-6): subtract 6 hours

## 📊 Performance Metrics

### Expected Performance Per Run:
- **Duration**: 60-120 seconds
- **Articles Checked**: 100
- **Articles with Keywords**: 5-15
- **After Duplicate Removal**: 1-8
- **Final Stored**: 1-5

### Daily Expectations:
- **Total Runs**: 6 per day
- **Articles Checked**: ~600 per day
- **New Articles Added**: 5-30 per day
- **Database Growth**: Steady, relevant content

## 🚨 Alert Conditions

### Immediate Attention Needed If:
1. **No activity for 8+ hours** (missed 2 scheduled runs)
2. **Repeated database connection errors**
3. **Timer shows "failed" status**
4. **No new articles for 24+ hours**

### Normal Variations:
- Some runs may find 0 new articles (normal)
- Processing time varies (30-180 seconds)
- Occasional network timeouts (auto-retry)

## 📞 Quick Health Check Script

Create a simple health check:
```bash
# Create health check script
cat > /opt/news-scraper/health_check.sh << 'EOF'
#!/bin/bash
echo "🔍 Quick Health Check - $(date)"
echo "=================================="

# Check timer status
if systemctl is-active --quiet news-scheduler.timer; then
    echo "✅ Timer: Active"
else
    echo "❌ Timer: Inactive"
fi

# Check recent logs
if tail -100 /var/log/news-scraper/scheduler.log | grep -q "$(date -d '6 hours ago' '+%Y-%m-%d')"; then
    echo "✅ Recent Activity: Found"
else
    echo "❌ Recent Activity: None"
fi

# Check next run
echo "⏰ Next Run: $(systemctl list-timers news-scheduler.timer --no-pager | grep news-scheduler | awk '{print $1, $2}')"

echo "=================================="
EOF

chmod +x /opt/news-scraper/health_check.sh

# Run health check
/opt/news-scraper/health_check.sh
```

## 🎯 Summary Commands

**Quick status check:**
```bash
ssh root@143.198.219.220 "cd /opt/news-scraper && python3 check_scheduler_status.py"
```

**View recent activity:**
```bash
ssh root@143.198.219.220 "tail -20 /var/log/news-scraper/scheduler.log"
```

**Check next run:**
```bash
ssh root@143.198.219.220 "systemctl list-timers news-scheduler.timer"
```

Your automated scheduler is working correctly when you see regular log entries every 4 hours, new articles in your database, and an active systemd timer! 🚀