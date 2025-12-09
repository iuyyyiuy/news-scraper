# 🚀 Multi-Source Scraper Deployment Guide

## Overview

This guide covers deploying the updated multi-source news scraper with:
- ✅ 3 news sources (BlockBeats, Jinse, PANews)
- ✅ Per-source log tabs
- ✅ Smart deduplication
- ✅ Real-time progress tracking

## Quick Deploy Options

### Option 1: Digital Ocean (Recommended for Production)
- **Cost**: $6/month
- **Control**: Full server access
- **Performance**: Dedicated resources
- **Setup time**: 15-20 minutes

### Option 2: Render.com (Recommended for Testing)
- **Cost**: Free (750 hours/month)
- **Control**: Managed platform
- **Performance**: Shared resources
- **Setup time**: 5 minutes

## 📦 Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] All new scraper files:
  - `scraper/core/jinse_scraper.py`
  - `scraper/core/panews_scraper.py`
  - `scraper/core/deduplicator.py`
  - `scraper/core/multi_source_scraper.py`
  - Updated `scraper/web_api.py`
  - Updated `scraper/core/session.py`
  - Updated `scraper/templates/index.html`

- [ ] Updated `requirements.txt` (should already be correct)

- [ ] Test locally first:
  ```bash
  python test_web_interface_multi_source.py
  # Open http://localhost:8000 and test
  ```

## 🌊 Deploy to Digital Ocean

### Step 1: Update Your Local Files

Make sure all new files are in your project directory.

### Step 2: Update Upload Script

Edit `upload_to_server.sh` and set your server IP:

```bash
SERVER_IP="143.198.219.220"  # Your actual IP
```

### Step 3: Upload Files

```bash
chmod +x upload_to_server.sh
./upload_to_server.sh
```

This will upload:
- All scraper files (including new multi-source scrapers)
- Updated web API
- Updated templates
- Requirements

### Step 4: SSH to Server and Restart

```bash
ssh root@YOUR_SERVER_IP

# Navigate to app directory
cd /home/scraper/news-scraper

# Activate virtual environment
source venv/bin/activate

# Install any new dependencies (if needed)
pip install -r requirements.txt

# Restart the service
sudo systemctl restart news-scraper

# Check status
sudo systemctl status news-scraper

# View logs
sudo journalctl -u news-scraper -f
```

### Step 5: Test the Deployment

Open your browser:
```
http://YOUR_SERVER_IP
```

You should see:
- ✅ Source selection checkboxes (BlockBeats, Jinse, PANews)
- ✅ Deduplication toggle
- ✅ Log tabs (全部, BlockBeats, Jinse, PANews)

### Step 6: Test Multi-Source Scraping

1. Select all three sources
2. Enter keywords: `BTC, Bitcoin`
3. Set time range: 3 days
4. Enable deduplication
5. Click "开始爬取"
6. Switch between log tabs to see per-source progress

## 🎨 Deploy to Render.com

### Step 1: Push to GitHub

If not already done:

```bash
# Initialize git (if needed)
git init
git add .
git commit -m "Add multi-source scraper with deduplication"

# Create GitHub repo and push
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### Step 2: Create Render Service

1. Go to https://render.com
2. Sign up/Login with GitHub
3. Click "New +" → "Web Service"
4. Connect your repository
5. Configure:
   - **Name**: `crypto-news-scraper`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn scraper.web_api:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

### Step 3: Deploy

Click "Create Web Service" and wait 2-3 minutes.

Your app will be live at:
```
https://crypto-news-scraper.onrender.com
```

### Step 4: Test

Open the URL and verify:
- ✅ Multi-source selection works
- ✅ Log tabs appear
- ✅ Scraping works
- ✅ CSV download works

## 🔧 Troubleshooting

### Issue: Service won't start

**Check logs:**
```bash
# Digital Ocean
sudo journalctl -u news-scraper -n 100

# Render
Check the "Logs" tab in Render dashboard
```

**Common causes:**
- Missing dependencies
- Import errors
- Port conflicts

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Test locally first
python test_web_interface_multi_source.py
```

### Issue: New scrapers not working

**Check if files uploaded:**
```bash
# Digital Ocean
ls -la /home/scraper/news-scraper/scraper/core/
# Should see: jinse_scraper.py, panews_scraper.py, deduplicator.py, multi_source_scraper.py
```

**If missing:**
```bash
# Re-upload
./upload_to_server.sh
```

### Issue: Log tabs not showing

**Check browser console:**
- Open Developer Tools (F12)
- Look for JavaScript errors
- Check Network tab for failed requests

**Solution:**
- Clear browser cache
- Hard refresh (Ctrl+Shift+R)
- Check if template updated correctly

### Issue: Deduplication not working

**Check logs for errors:**
```bash
# Look for deduplication messages
sudo journalctl -u news-scraper -f | grep "去重"
```

**Verify deduplicator imported:**
```bash
# On server
cd /home/scraper/news-scraper
source venv/bin/activate
python -c "from scraper.core.deduplicator import DeduplicationEngine; print('OK')"
```

### Issue: Sources not scraping

**Test individual scrapers:**
```bash
# On server
cd /home/scraper/news-scraper
source venv/bin/activate
python test_individual_scrapers.py
```

**Check network connectivity:**
```bash
# Test if server can reach news sites
curl -I https://www.theblockbeats.info
curl -I https://www.jinse.cn
curl -I https://www.panewslab.com
```

## 📊 Performance Optimization

### For Digital Ocean

**Increase resources if needed:**
- Upgrade to $12/month droplet (2GB RAM) for better performance
- Handles more concurrent scraping sessions

**Optimize Nginx:**
```bash
sudo nano /etc/nginx/sites-available/news-scraper
```

Add inside `location /`:
```nginx
# Increase timeouts for long scraping sessions
proxy_connect_timeout 600s;
proxy_send_timeout 600s;
proxy_read_timeout 600s;
```

**Monitor resources:**
```bash
# Check memory usage
free -h

# Check CPU usage
top

# Check disk space
df -h
```

### For Render

**Upgrade to paid plan if needed:**
- Free tier: 750 hours/month, sleeps after 15 min inactivity
- Starter ($7/month): Always on, better performance

**Keep service awake:**
- Use a service like UptimeRobot to ping every 5 minutes
- Or upgrade to paid plan

## 🔒 Security Recommendations

### Add Basic Authentication

**Digital Ocean:**
```bash
# Install apache2-utils
sudo apt install apache2-utils

# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd admin

# Update Nginx config
sudo nano /etc/nginx/sites-available/news-scraper
```

Add inside `location /`:
```nginx
auth_basic "Restricted Access";
auth_basic_user_file /etc/nginx/.htpasswd;
```

```bash
sudo systemctl restart nginx
```

**Render:**
- Use environment variables for API keys
- Add authentication in the FastAPI app

### Rate Limiting

Add to Nginx config:
```nginx
limit_req_zone $binary_remote_addr zone=scraper:10m rate=10r/m;

location / {
    limit_req zone=scraper burst=5;
    # ... rest of config
}
```

## 📈 Monitoring

### Set Up Monitoring (Optional)

**Digital Ocean:**
```bash
# Install monitoring agent
curl -sSL https://repos.insights.digitalocean.com/install.sh | sudo bash
```

**Render:**
- Built-in monitoring in dashboard
- View metrics, logs, and events

### Health Check Endpoint

Already available at:
```
http://YOUR_URL/health
```

Returns:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-23T...",
  "active_sessions": 0
}
```

## 🔄 Update Workflow

### When You Make Changes

**Digital Ocean:**
```bash
# 1. Test locally
python test_web_interface_multi_source.py

# 2. Upload to server
./upload_to_server.sh

# 3. SSH and restart
ssh root@YOUR_SERVER_IP
cd /home/scraper/news-scraper
sudo systemctl restart news-scraper
```

**Render:**
```bash
# 1. Test locally
python test_web_interface_multi_source.py

# 2. Push to GitHub
git add .
git commit -m "Update feature"
git push

# 3. Render auto-deploys (wait 2-3 min)
```

## 📝 Deployment Checklist

### Pre-Deployment
- [ ] Test locally with all 3 sources
- [ ] Verify log tabs work
- [ ] Test deduplication
- [ ] Check CSV download
- [ ] Review requirements.txt

### Digital Ocean Deployment
- [ ] Update upload_to_server.sh with IP
- [ ] Run upload script
- [ ] SSH to server
- [ ] Restart service
- [ ] Check logs
- [ ] Test in browser
- [ ] Verify all features work

### Render Deployment
- [ ] Push to GitHub
- [ ] Create Render service
- [ ] Configure build/start commands
- [ ] Wait for deployment
- [ ] Test in browser
- [ ] Verify all features work

### Post-Deployment
- [ ] Test multi-source scraping
- [ ] Test log tab switching
- [ ] Test deduplication
- [ ] Test CSV download
- [ ] Share URL with team
- [ ] Document any issues

## 🎯 Quick Commands Reference

### Digital Ocean

```bash
# Upload files
./upload_to_server.sh

# SSH to server
ssh root@YOUR_SERVER_IP

# Restart service
sudo systemctl restart news-scraper

# View logs
sudo journalctl -u news-scraper -f

# Check status
sudo systemctl status news-scraper

# Test locally on server
cd /home/scraper/news-scraper
source venv/bin/activate
python test_web_interface_multi_source.py
```

### Render

```bash
# Push updates
git add .
git commit -m "Update"
git push

# View logs
# Go to Render dashboard → Your service → Logs

# Restart service
# Go to Render dashboard → Your service → Manual Deploy → Deploy latest commit
```

## 💰 Cost Comparison

| Feature | Digital Ocean | Render Free | Render Paid |
|---------|--------------|-------------|-------------|
| **Cost** | $6/month | Free | $7/month |
| **Uptime** | 24/7 | Sleeps after 15min | 24/7 |
| **Resources** | 1GB RAM, 1 CPU | Shared | 512MB RAM |
| **Domain** | IP or custom | .onrender.com | Custom |
| **SSL** | Manual | Auto | Auto |
| **Control** | Full | Limited | Limited |

## 🎉 Success!

Your multi-source news scraper is now deployed and accessible online!

**Next Steps:**
1. Share the URL with your team
2. Set up monitoring (optional)
3. Configure backups (optional)
4. Add custom domain (optional)
5. Set up SSL/HTTPS (optional)

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review logs for error messages
3. Test locally first
4. Verify all files uploaded correctly

---

**Deployment completed by Kabella** 🚀
