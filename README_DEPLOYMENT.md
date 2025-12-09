# 🚀 Dual Deployment Setup

Your news scraper is deployed on **both** platforms:

## 🌐 Public Access (Render)
**URL**: https://crypto-news-scraper.onrender.com
- Free subdomain
- Automatic HTTPS
- Auto-deploy from GitHub
- **Use this for sharing with others**

## 🔧 Development/Testing (Digital Ocean)
**URL**: http://143.198.219.220
- Full server control
- Direct access
- Manual deployment
- **Use this for testing**

## Quick Deploy to Render

### Step 1: Push to GitHub

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - News Scraper"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/news-scraper.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Render

1. Go to https://render.com
2. Sign up with GitHub
3. Click **New +** → **Web Service**
4. Connect your repository
5. Configure:
   - **Name**: `crypto-news-scraper`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn scraper.web_api:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free

6. Click **Create Web Service**

### Step 3: Wait 2-3 Minutes

Your app will be live at:
```
https://crypto-news-scraper.onrender.com
```

## Update Code

### Update Render (Automatic)
```bash
git add .
git commit -m "Update scraper"
git push
# Render auto-deploys!
```

### Update Digital Ocean (Manual)
```bash
tar -czf /tmp/scraper-upload.tar.gz scraper/ requirements.txt
scp /tmp/scraper-upload.tar.gz root@143.198.219.220:/tmp/
ssh root@143.198.219.220 "cd /home/scraper/news-scraper && tar -xzf /tmp/scraper-upload.tar.gz && chown -R scraper:scraper /home/scraper/news-scraper && systemctl restart news-scraper"
```

## When to Use Each

### Use Render When:
- ✅ Sharing with others
- ✅ Public demo
- ✅ Production use
- ✅ Need nice URL

### Use Digital Ocean When:
- ✅ Testing new features
- ✅ Debugging
- ✅ Running other services
- ✅ Need full control

## Cost Comparison

| Platform | Cost | URL |
|----------|------|-----|
| Render | FREE | yourapp.onrender.com |
| Digital Ocean | $6/month | 143.198.219.220 |

## Later: Delete Digital Ocean?

Once Render is working well, you can:
1. Delete Digital Ocean droplet
2. Save $6/month
3. Use only Render

Or keep both for redundancy!
