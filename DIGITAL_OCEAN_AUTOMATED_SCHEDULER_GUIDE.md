# Digital Ocean Automated News Scheduler - Complete Setup Guide

## 🎯 Overview

This guide sets up an automated news scheduler on Digital Ocean that:
- ✅ **Runs every 4 hours** (00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC)
- ✅ **Scrapes 100 articles** from BlockBeats per run
- ✅ **Filters by 21 security keywords** 
- ✅ **Enhanced duplicate detection** (database-aware)
- ✅ **AI content filtering** (optional, with DeepSeek API)
- ✅ **Automatic database updates** to Supabase
- ✅ **Dashboard auto-refresh** with new content

## 📋 Prerequisites

### 1. Digital Ocean Droplet
- **Minimum**: 1GB RAM, 1 vCPU, 25GB SSD
- **Recommended**: 2GB RAM, 1 vCPU, 50GB SSD
- **OS**: Ubuntu 20.04 or 22.04 LTS

### 2. Required Information
- ✅ Supabase URL and API Key
- ✅ DeepSeek API Key (optional, for AI filtering)
- ✅ SSH access to your Digital Ocean droplet

## 🚀 Installation Steps

### Step 1: Connect to Your Digital Ocean Droplet

```bash
ssh root@your_droplet_ip
```

### Step 2: Update System and Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Python and required packages
apt install -y python3 python3-pip git curl wget

# Install additional dependencies
pip3 install --upgrade pip
```

### Step 3: Clone Your Project

```bash
# Navigate to opt directory
cd /opt

# Clone your project (replace with your actual repository)
git clone https://github.com/yourusername/your-news-scraper.git news-scraper

# Or upload your project files
# scp -r /path/to/your/project root@your_droplet_ip:/opt/news-scraper
```

### Step 4: Set Up Environment

```bash
cd /opt/news-scraper

# Create environment file
cp .env.template .env

# Edit environment file with your credentials
nano .env
```

**Configure your .env file:**
```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# DeepSeek AI API (Optional - for AI filtering)
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Logging Level
LOG_LEVEL=INFO
```

### Step 5: Install Python Dependencies

```bash
# Install project dependencies
pip3 install -r requirements.txt

# Install additional packages if needed
pip3 install python-dotenv supabase requests beautifulsoup4 selenium
```

### Step 6: Test the Scheduler

```bash
# Run component tests
python3 test_automated_scheduler.py
```

**Expected output:**
```
🧪 Testing Automated News Scheduler
============================================================
📋 Step 1: Initializing scheduler...
✅ Scheduler initialized successfully
   - Database Manager: ✅
   - Alert Logger: ✅
   - AI Analyzer: ✅
   - Keywords: 21 security keywords

📋 Step 2: Running test scrape (10 articles)...
✅ Test scrape completed in 45.23 seconds

📊 Test Results:
   - Articles Found: 10
   - With Keywords: 3
   - After AI Filter: 2
   - Articles Stored: 1
   - Duplicates Removed: 1
   - Processing Time: 45.23s
   - Errors: None

🎉 All tests passed! Automated scheduler is ready for deployment.
```

### Step 7: Deploy the Automated Scheduler

```bash
# Make setup script executable
chmod +x setup_digital_ocean_scheduler.sh

# Run the setup script
sudo ./setup_digital_ocean_scheduler.sh
```

**The setup script will:**
- ✅ Create project directory `/opt/news-scraper`
- ✅ Set up log directory `/var/log/news-scraper`
- ✅ Create systemd service and timer
- ✅ Configure cron job backup
- ✅ Set up log rotation
- ✅ Create monitoring scripts

### Step 8: Verify Installation

```bash
# Check systemd timer status
systemctl status news-scheduler.timer

# Check next scheduled runs
systemctl list-timers news-scheduler.timer

# Run status check script
python3 /opt/news-scraper/check_scheduler_status.py
```

**Expected output:**
```
🔍 News Scheduler Status Check
========================================
Systemd Timer: ✅ Active
Recent Activity: ✅ Last run: 2026-01-01 12:00:15
Next Scheduled: ⏰ Wed 2026-01-01 16:00:00 UTC
========================================
✅ Scheduler is working properly
```

## 📊 Monitoring and Management

### View Logs

```bash
# Real-time logs
tail -f /var/log/news-scraper/scheduler.log

# Error logs
tail -f /var/log/news-scraper/scheduler-error.log

# Systemd logs
journalctl -u news-scheduler.service -f
```

### Manual Operations

```bash
# Run scheduler manually
sudo -u www-data python3 /opt/news-scraper/automated_news_scheduler.py

# Start/stop timer
systemctl start news-scheduler.timer
systemctl stop news-scheduler.timer

# Check status
systemctl status news-scheduler.timer
```

### Check Database Updates

```bash
# Connect to your Supabase dashboard
# Go to Table Editor > articles
# Verify new articles are being added every 4 hours
```

## 🔧 Configuration Options

### Modify Schedule

Edit the systemd timer:
```bash
sudo nano /etc/systemd/system/news-scheduler.timer
```

Change the `OnCalendar` line:
```ini
# Every 4 hours (current)
OnCalendar=*-*-* 00,04,08,12,16,20:00:00

# Every 2 hours
OnCalendar=*-*-* 00,02,04,06,08,10,12,14,16,18,20,22:00:00

# Every 6 hours
OnCalendar=*-*-* 00,06,12,18:00:00
```

Then reload:
```bash
systemctl daemon-reload
systemctl restart news-scheduler.timer
```

### Modify Article Count

Edit the scheduler script:
```bash
sudo nano /opt/news-scraper/automated_news_scheduler.py
```

Change the default in the `main()` function:
```python
# Current: 100 articles
results = scheduler.run_scheduled_scrape(max_articles=100)

# Change to 200 articles
results = scheduler.run_scheduled_scrape(max_articles=200)
```

### Add/Remove Keywords

Edit the scheduler script:
```bash
sudo nano /opt/news-scraper/automated_news_scheduler.py
```

Modify the `KEYWORDS` list:
```python
KEYWORDS = [
    "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
    "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
    "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架",
    # Add your custom keywords here
    "新关键词1", "新关键词2"
]
```

## 📈 Expected Performance

### Typical Run Statistics
- **Duration**: 60-120 seconds per run
- **Articles Checked**: 100 per run
- **Articles with Keywords**: 5-15 per run
- **After Duplicate Removal**: 1-8 per run
- **Final Stored**: 1-5 per run

### Daily Statistics
- **Runs per Day**: 6 (every 4 hours)
- **Total Articles Checked**: ~600 per day
- **New Articles Added**: 5-30 per day
- **Database Growth**: ~150-900 articles per month

## 🔍 Troubleshooting

### Common Issues

#### 1. Timer Not Running
```bash
# Check timer status
systemctl status news-scheduler.timer

# If inactive, start it
systemctl start news-scheduler.timer
systemctl enable news-scheduler.timer
```

#### 2. Database Connection Errors
```bash
# Check environment variables
cat /opt/news-scraper/.env

# Test database connection
cd /opt/news-scraper
python3 -c "from scraper.core.database_manager import DatabaseManager; db = DatabaseManager(); print('✅ Database connected')"
```

#### 3. No Articles Being Stored
```bash
# Check recent logs
tail -50 /var/log/news-scraper/scheduler.log

# Run manual test
sudo -u www-data python3 /opt/news-scraper/automated_news_scheduler.py
```

#### 4. AI Analysis Errors
```bash
# Check DeepSeek API key
grep DEEPSEEK_API_KEY /opt/news-scraper/.env

# Test AI analyzer
cd /opt/news-scraper
python3 -c "from scraper.core.ai_content_analyzer import AIContentAnalyzer; ai = AIContentAnalyzer(); print('✅ AI analyzer working')"
```

### Log Analysis

**Successful run log pattern:**
```
2026-01-01 12:00:15 - INFO - 🚀 Starting scheduled scrape at 2026-01-01 12:00:15
2026-01-01 12:00:45 - INFO - 📊 Scraping completed: Total articles checked: 100
2026-01-01 12:01:15 - INFO - 🤖 AI analysis completed: 8 articles after filtering
2026-01-01 12:01:30 - INFO - 💾 Storing 8 articles in database...
2026-01-01 12:01:45 - INFO - ✅ Scheduled scrape completed successfully: 3 articles stored
```

## 🎯 Dashboard Integration

The automated scheduler automatically updates your news dashboard:

1. **Real-Time Updates**: New articles appear in dashboard within minutes
2. **Automatic Refresh**: Dashboard shows latest articles without manual refresh
3. **Duplicate-Free**: Enhanced duplicate detection ensures clean results
4. **Keyword Filtering**: Only security-related articles are added

### Verify Dashboard Updates

1. Open your news dashboard: `https://your-domain.com/dashboard`
2. Note the current article count and latest article date
3. Wait for next scheduled run (check with `systemctl list-timers`)
4. Refresh dashboard after scheduled run
5. Verify new articles have been added

## 🎊 Success Indicators

Your automated scheduler is working correctly when you see:

- ✅ **Systemd timer active**: `systemctl status news-scheduler.timer` shows "active"
- ✅ **Regular log entries**: New entries every 4 hours in `/var/log/news-scraper/scheduler.log`
- ✅ **Database updates**: New articles in Supabase `articles` table every 4 hours
- ✅ **Dashboard refresh**: News dashboard shows new articles automatically
- ✅ **No duplicate articles**: Enhanced duplicate detection prevents duplicates
- ✅ **Relevant content**: Only security-related articles are added

## 📞 Support

If you encounter issues:

1. **Check logs**: `/var/log/news-scraper/scheduler.log`
2. **Run manual test**: `python3 /opt/news-scraper/test_automated_scheduler.py`
3. **Verify configuration**: Check `.env` file and systemd timer
4. **Monitor status**: Use `check_scheduler_status.py` script

---

**🎉 Congratulations!** Your automated news scheduler is now running on Digital Ocean, scraping 100 articles every 4 hours, filtering duplicates and irrelevant content, and automatically updating your news dashboard with fresh, relevant security news!