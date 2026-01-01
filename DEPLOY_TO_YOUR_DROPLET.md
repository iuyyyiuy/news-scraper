# Deploy to Your Digital Ocean Droplet 🚀

**Droplet IP**: 143.198.219.220  
**Repository**: https://github.com/iuyyyiuy/news-scraper.git

## 🎯 Quick Deployment (Recommended)

### Option 1: Automated Deployment Script

```bash
# Make the deployment script executable
chmod +x deploy_to_droplet_143.198.219.220.sh

# Run automated deployment
./deploy_to_droplet_143.198.219.220.sh
```

### Option 2: Manual Step-by-Step

```bash
# 1. Connect to your droplet
ssh root@143.198.219.220

# 2. Update system and install dependencies
apt update && apt upgrade -y
apt install -y git python3 python3-pip curl wget build-essential python3-dev
pip3 install --upgrade pip

# 3. Clone your repository
cd /opt
git clone https://github.com/iuyyyiuy/news-scraper.git news-scraper
cd news-scraper

# 4. Install Python dependencies
pip3 install -r requirements.txt
pip3 install python-dotenv supabase requests beautifulsoup4 lxml

# 5. Make scripts executable
chmod +x *.sh

# 6. Create environment file
cp .env.template .env
nano .env  # Add your credentials (see below)
```

## 🔧 Environment Configuration

Edit your `.env` file with your actual credentials:

```bash
nano /opt/news-scraper/.env
```

**Add your credentials:**
```bash
# Supabase Configuration (REQUIRED)
SUPABASE_URL=https://vckulcbgaqyujucbbeno.supabase.co
SUPABASE_KEY=your_actual_supabase_key_here

# DeepSeek AI API (Optional - for AI filtering)
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Logging Configuration
LOG_LEVEL=INFO
```

## 🚀 Deploy the Automated Scheduler

```bash
# Run the setup script
sudo ./setup_digital_ocean_scheduler.sh
```

## 🧪 Test the Installation

```bash
# Test the automated scheduler
python3 test_automated_scheduler.py

# Check scheduler status
python3 check_scheduler_status.py

# Check systemd timer
systemctl status news-scheduler.timer

# View logs
tail -f /var/log/news-scraper/scheduler.log
```

## 📊 Verify Everything is Working

### Check Timer Status
```bash
systemctl list-timers news-scheduler.timer
```

**Expected output:**
```
NEXT                        LEFT     LAST PASSED UNIT                   ACTIVATES
Wed 2026-01-01 20:00:00 UTC 3h left  n/a  n/a    news-scheduler.timer   news-scheduler.service
```

### Check Recent Logs
```bash
tail -20 /var/log/news-scraper/scheduler.log
```

**Expected log pattern:**
```
2026-01-01 16:00:15 - INFO - 🚀 Starting scheduled scrape at 2026-01-01 16:00:15
2026-01-01 16:01:30 - INFO - 📊 Scraping completed: Total articles checked: 100
2026-01-01 16:02:00 - INFO - ✅ Scheduled scrape completed successfully: 5 articles stored
```

### Check Database Updates
1. Go to your Supabase dashboard
2. Open Table Editor → articles
3. Verify new articles are being added every 4 hours

## 🎯 Success Indicators

Your automated scheduler is working when you see:

- ✅ **Timer Active**: `systemctl status news-scheduler.timer` shows "active"
- ✅ **Regular Logs**: New entries every 4 hours in scheduler logs
- ✅ **Database Updates**: New articles in Supabase every 4 hours
- ✅ **No Duplicates**: Enhanced duplicate detection prevents duplicates
- ✅ **Dashboard Updates**: News dashboard shows fresh content

## 🔄 Schedule Information

- **Frequency**: Every 4 hours
- **Times**: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC
- **Articles per run**: 100 articles checked
- **Expected new articles**: 5-30 per day
- **Sources**: BlockBeats (Jinse disabled)
- **Keywords**: 21 security-related keywords

## 🛠️ Management Commands

```bash
# Start/stop the timer
systemctl start news-scheduler.timer
systemctl stop news-scheduler.timer

# Check status
systemctl status news-scheduler.timer
python3 /opt/news-scraper/check_scheduler_status.py

# View logs
tail -f /var/log/news-scraper/scheduler.log
journalctl -u news-scheduler.service -f

# Run manually (for testing)
sudo -u www-data python3 /opt/news-scraper/automated_news_scheduler.py

# Update from GitHub
cd /opt/news-scraper
git pull origin main
systemctl restart news-scheduler.timer
```

## 🚨 Troubleshooting

### Timer Not Running
```bash
systemctl enable news-scheduler.timer
systemctl start news-scheduler.timer
```

### Database Connection Issues
```bash
# Test database connection
cd /opt/news-scraper
python3 -c "from scraper.core.database_manager import DatabaseManager; db = DatabaseManager(); print('✅ Connected')"
```

### No Articles Being Stored
```bash
# Check recent logs for errors
tail -50 /var/log/news-scraper/scheduler.log

# Run manual test
sudo -u www-data python3 /opt/news-scraper/automated_news_scheduler.py
```

## 🎊 Final Result

Once deployed, your system will:

1. **Automatically scrape 100 articles every 4 hours**
2. **Filter for security-related content using 21 keywords**
3. **Remove duplicates using enhanced database-aware detection**
4. **Store relevant articles in your Supabase database**
5. **Update your news dashboard automatically**
6. **Provide comprehensive logging and monitoring**

Your automated news scheduler is now running on Digital Ocean! 🚀

---

**Droplet**: 143.198.219.220  
**Status**: Ready for deployment  
**Next**: Run the deployment commands above