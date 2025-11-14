# 🚀 Deploy to Render in 5 Minutes

## Prerequisites
- GitHub account
- Your code (already ready!)

## Step-by-Step Guide

### 1. Create GitHub Repository

Go to https://github.com/new and create a new repository:
- **Name**: `news-scraper` (or any name)
- **Visibility**: Public or Private (both work)
- **Don't** initialize with README (we have code already)

### 2. Push Your Code to GitHub

Open terminal in your project folder and run:

```bash
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - News Scraper"

# Add GitHub remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 3. Sign Up for Render

1. Go to https://render.com
2. Click **Get Started**
3. Sign up with **GitHub** (easiest)
4. Authorize Render to access your repositories

### 4. Create Web Service

1. Click **New +** button (top right)
2. Select **Web Service**
3. Click **Connect** next to your repository
4. If you don't see it, click **Configure account** and grant access

### 5. Configure Service

Fill in these settings:

**Basic Settings:**
- **Name**: `crypto-news-scraper` (this becomes your URL)
- **Region**: Singapore (closest to you)
- **Branch**: `main`
- **Root Directory**: (leave blank)
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  uvicorn scraper.web_api:app --host 0.0.0.0 --port $PORT
  ```

**Instance Type:**
- Select **Free** (750 hours/month)

### 6. Deploy!

1. Click **Create Web Service**
2. Wait 2-3 minutes while Render:
   - Installs dependencies
   - Starts your app
   - Generates SSL certificate

### 7. Access Your App

Once deployed, your app will be live at:
```
https://crypto-news-scraper.onrender.com
```

(Replace `crypto-news-scraper` with whatever name you chose)

## Troubleshooting

### Build Failed?

Check the logs in Render dashboard. Common issues:
- Missing dependencies in `requirements.txt`
- Python version mismatch

### App Not Starting?

Make sure start command is exactly:
```
uvicorn scraper.web_api:app --host 0.0.0.0 --port $PORT
```

Note: `$PORT` is important - Render provides this automatically

### Can't Find Repository?

1. Go to Render Dashboard
2. Click your profile → Account Settings
3. Go to **GitHub** section
4. Click **Configure** and grant access to your repository

## Update Your App

Whenever you make changes:

```bash
git add .
git commit -m "Update feature"
git push
```

Render will automatically redeploy! 🎉

## Free Tier Limits

Render free tier includes:
- ✅ 750 hours/month (enough for 24/7)
- ✅ Automatic HTTPS
- ✅ Custom domain support
- ⚠️ Spins down after 15 min of inactivity
- ⚠️ Takes ~30 seconds to wake up

**Note**: First request after inactivity will be slow. Subsequent requests are fast.

## Upgrade to Paid (Optional)

If you need 24/7 with no spin-down:
- **Starter Plan**: $7/month
- Always on, no cold starts
- More resources

## Next Steps

1. ✅ Deploy to Render (get nice URL)
2. ✅ Keep Digital Ocean running (for testing)
3. ✅ Share Render URL with others
4. ✅ Later: Decide if you want to keep both or just Render

## Need Help?

If you get stuck:
1. Check Render logs (Dashboard → Your Service → Logs)
2. Verify your `requirements.txt` is correct
3. Make sure `render.yaml` is in your repository
4. Ask me for help!

---

**Ready to deploy?** Follow the steps above and you'll have your scraper live in 5 minutes! 🚀
