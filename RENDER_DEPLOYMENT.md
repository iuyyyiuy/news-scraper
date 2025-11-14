# 🚀 Deploy to Render.com (Free with Custom Domain)

Get your scraper online at `yourapp.onrender.com` in 5 minutes!

## Why Render?

- ✅ **Free subdomain** (like Streamlit)
- ✅ **Automatic SSL** (HTTPS)
- ✅ **No server management**
- ✅ **Auto-deploy from GitHub**
- ✅ **Free tier**: 750 hours/month

## Step 1: Prepare Your Code

Your code is already ready! Just need to push to GitHub.

## Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub (recommended)
3. Click "New +" → "Web Service"

## Step 3: Connect Repository

1. Connect your GitHub account
2. Select your repository
3. Or use "Deploy from Git URL"

## Step 4: Configure Service

**Settings:**
- **Name**: `crypto-news-scraper` (this becomes your URL)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn scraper.web_api:app --host 0.0.0.0 --port $PORT`
- **Instance Type**: `Free`

## Step 5: Deploy

Click "Create Web Service" and wait 2-3 minutes.

Your app will be live at:
```
https://crypto-news-scraper.onrender.com
```

## Alternative: Quick Deploy Button

Add this to your GitHub README:

```markdown
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
```

## Custom Domain (Optional)

If you buy a domain later:
1. Go to Render Dashboard → Your Service → Settings
2. Add Custom Domain
3. Point your domain's CNAME to Render

## Comparison: Digital Ocean vs Render

| Feature | Digital Ocean | Render |
|---------|--------------|--------|
| **Cost** | $6/month | Free (750hrs) |
| **Domain** | IP or buy domain | Free subdomain |
| **SSL** | Manual setup | Automatic |
| **Deployment** | Manual upload | Git push |
| **Maintenance** | You manage | Managed |
| **Best for** | Full control | Quick & easy |

## Other Free Alternatives

### Railway.app
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```
URL: `yourapp.up.railway.app`

### Fly.io
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```
URL: `yourapp.fly.dev`

## Recommendation

**For your use case:**
- **Quick demo/testing**: Use Render (free subdomain)
- **Production/business**: Keep Digital Ocean (more control)
- **Both**: Deploy to both! Use Render for testing, Digital Ocean for production

## Next Steps

1. Push your code to GitHub
2. Sign up for Render
3. Connect and deploy
4. Get your free `yourapp.onrender.com` URL!

Want me to help you set this up?
