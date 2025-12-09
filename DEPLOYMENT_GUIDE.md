# Deployment Guide - News Database Feature

## Option 1: Deploy to Render (Recommended - Easiest)

### Step 1: Prepare Your Repository

1. Make sure all changes are committed to Git:
```bash
cd /Users/kabellatsang/PycharmProjects/ai_code
git add .
git commit -m "Add news database feature"
git push origin main
```

2. Update `requirements.txt` to include all dependencies:
```bash
# Add these lines to requirements.txt
supabase==1.0.3
APScheduler==3.10.4
pytz==2024.1
python-dotenv==1.0.0
uvicorn==0.38.0
fastapi
```

### Step 2: Create Render Web Service

1. Go to https://render.com and sign in
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `crypto-news-scraper`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn scraper.web_api:app --host 0.0.0.0 --port $PORT`

### Step 3: Add Environment Variables

In Render dashboard, go to "Environment" and add:

```
SUPABASE_URL=https://vckulcbgaqyujucbbeno.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZja3VsY2JnYXF5dWp1Y2JiZW5vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3Mjc1NDcsImV4cCI6MjA4MDMwMzU0N30.k713c5eTsM-fEFAxp8ST5IIh_AhJZtHVBrb4-oViHZU
```

### Step 4: Deploy

1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Your app will be available at: `https://crypto-news-scraper.onrender.com`

### Step 5: Verify

Visit:
- Dashboard: `https://crypto-news-scraper.onrender.com/dashboard`
- Scraper: `https://crypto-news-scraper.onrender.com/`
- API Docs: `https://crypto-news-scraper.onrender.com/docs`

---

## Option 2: Deploy to DigitalOcean App Platform

### Step 1: Prepare Your Repository

Same as Render - commit and push all changes.

### Step 2: Create App

1. Go to https://cloud.digitalocean.com
2. Click "Create" → "Apps"
3. Connect your GitHub repository
4. Select the repository and branch

### Step 3: Configure App

1. **App Info**:
   - Name: `crypto-news-scraper`
   - Region: Choose closest to you

2. **Resources**:
   - Type: Web Service
   - Source Directory: `/`
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `uvicorn scraper.web_api:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables**:
   ```
   SUPABASE_URL=https://vckulcbgaqyujucbbeno.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZja3VsY2JnYXF5dWp1Y2JiZW5vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3Mjc1NDcsImV4cCI6MjA4MDMwMzU0N30.k713c5eTsM-fEFAxp8ST5IIh_AhJZtHVBrb4-oViHZU
   ```

4. **Plan**: Select Basic ($5/month) or Pro ($12/month)

### Step 4: Deploy

1. Click "Create Resources"
2. Wait for deployment
3. Your app will be available at: `https://crypto-news-scraper-xxxxx.ondigitalocean.app`

---

## Option 3: Deploy to DigitalOcean Droplet (VPS)

### Step 1: Create Droplet

1. Go to DigitalOcean → Create → Droplets
2. Choose:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($6/month - 1GB RAM)
   - **Region**: Closest to you
   - **Authentication**: SSH Key (recommended)

### Step 2: Connect to Droplet

```bash
ssh root@your_droplet_ip
```

### Step 3: Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Python and pip
apt install python3 python3-pip python3-venv git -y

# Install nginx (for reverse proxy)
apt install nginx -y

# Install supervisor (for process management)
apt install supervisor -y
```

### Step 4: Clone and Setup Project

```bash
# Create app directory
mkdir -p /var/www/crypto-news
cd /var/www/crypto-news

# Clone your repository
git clone https://github.com/yourusername/ai_code.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Configure Environment

```bash
# Create .env file
cat > .env << EOF
SUPABASE_URL=https://vckulcbgaqyujucbbeno.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZja3VsY2JnYXF5dWp1Y2JiZW5vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3Mjc1NDcsImV4cCI6MjA4MDMwMzU0N30.k713c5eTsM-fEFAxp8ST5IIh_AhJZtHVBrb4-oViHZU
EOF
```

### Step 6: Configure Supervisor

```bash
cat > /etc/supervisor/conf.d/crypto-news.conf << EOF
[program:crypto-news]
directory=/var/www/crypto-news
command=/var/www/crypto-news/venv/bin/uvicorn scraper.web_api:app --host 0.0.0.0 --port 8000
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/crypto-news.err.log
stdout_logfile=/var/log/crypto-news.out.log
EOF

# Reload supervisor
supervisorctl reread
supervisorctl update
supervisorctl start crypto-news
```

### Step 7: Configure Nginx

```bash
cat > /etc/nginx/sites-available/crypto-news << EOF
server {
    listen 80;
    server_name your_domain.com;  # Replace with your domain or IP

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/crypto-news /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Step 8: Configure Firewall

```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### Step 9: Setup SSL (Optional but Recommended)

```bash
# Install certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot --nginx -d your_domain.com
```

---

## Comparison: Render vs DigitalOcean

### Render (Recommended for Beginners)
✅ **Pros**:
- Easiest setup (5 minutes)
- Automatic deployments from Git
- Free tier available
- Automatic SSL
- No server management

❌ **Cons**:
- Free tier sleeps after inactivity
- Limited customization
- $7/month for always-on

### DigitalOcean App Platform
✅ **Pros**:
- Easy setup (10 minutes)
- Automatic deployments
- Good performance
- Scalable

❌ **Cons**:
- Minimum $5/month
- Less flexible than VPS

### DigitalOcean Droplet (VPS)
✅ **Pros**:
- Full control
- Best performance
- Most cost-effective long-term
- Can run multiple apps

❌ **Cons**:
- Requires server management
- More complex setup
- Need to handle security updates

---

## Post-Deployment Checklist

After deployment, verify:

- [ ] Dashboard loads: `/dashboard`
- [ ] Scraper works: `/`
- [ ] API docs accessible: `/docs`
- [ ] Scheduler is running: Check `/api/database/scheduler/status`
- [ ] Database connection works: Check `/api/database/stats`
- [ ] Articles are being scraped (wait until 8 AM UTC+8)
- [ ] SSL certificate is active (https://)

---

## Monitoring

### Check Scheduler Status
```bash
curl https://your-app-url.com/api/database/scheduler/status
```

### Check Database Stats
```bash
curl https://your-app-url.com/api/database/stats
```

### Trigger Manual Scrape (for testing)
```bash
curl -X POST https://your-app-url.com/api/database/scheduler/trigger
```

---

## Troubleshooting

### Scheduler Not Running
- Check environment variables are set
- Check logs for errors
- Verify Supabase credentials

### Database Connection Failed
- Verify SUPABASE_URL and SUPABASE_KEY
- Check Supabase project is active
- Test connection locally first

### App Crashes on Startup
- Check logs in deployment platform
- Verify all dependencies in requirements.txt
- Check Python version compatibility

---

## Updating Your Deployment

### For Render/DigitalOcean App Platform:
```bash
git add .
git commit -m "Update feature"
git push origin main
# Auto-deploys!
```

### For DigitalOcean Droplet:
```bash
ssh root@your_droplet_ip
cd /var/www/crypto-news
git pull
source venv/bin/activate
pip install -r requirements.txt
supervisorctl restart crypto-news
```

---

## Cost Estimates

### Render
- Free tier: $0 (sleeps after 15 min inactivity)
- Starter: $7/month (always on)
- Standard: $25/month (more resources)

### DigitalOcean App Platform
- Basic: $5/month
- Professional: $12/month

### DigitalOcean Droplet
- Basic: $6/month (1GB RAM)
- Standard: $12/month (2GB RAM)
- Plus Supabase: Free tier (up to 500MB database)

**Recommended**: Start with Render free tier for testing, then upgrade to Render Starter ($7/month) or DigitalOcean Droplet ($6/month) for production.
