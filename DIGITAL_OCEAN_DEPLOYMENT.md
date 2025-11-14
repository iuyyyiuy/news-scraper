# 🚀 Digital Ocean Deployment Guide

This guide will help you deploy the News Scraper to Digital Ocean.

## Prerequisites

- Digital Ocean account
- SSH key set up
- Basic knowledge of Linux commands

## Step 1: Create a Droplet

1. **Log in to Digital Ocean**
2. **Create a new Droplet:**
   - Choose **Ubuntu 22.04 LTS**
   - Select a plan: **Basic $6/month** (1GB RAM, 1 CPU) is sufficient
   - Choose a datacenter region close to you
   - Add your SSH key
   - Choose a hostname: `news-scraper`
   - Click **Create Droplet**

3. **Note your Droplet's IP address** (e.g., `123.456.789.0`)

## Step 2: Connect to Your Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

## Step 3: Set Up the Server

### Update the system
```bash
apt update && apt upgrade -y
```

### Install Python and dependencies
```bash
apt install -y python3.11 python3.11-venv python3-pip git nginx
```

### Create a non-root user (recommended)
```bash
adduser scraper
usermod -aG sudo scraper
su - scraper
```

## Step 4: Upload Your Code

### Option A: Using Git (Recommended)

If your code is in a Git repository:

```bash
cd ~
git clone YOUR_REPOSITORY_URL
cd YOUR_REPOSITORY_NAME
```

### Option B: Using SCP (from your local machine)

```bash
# On your local machine
cd /Users/kabellatsang/Desktop/trade_risk_analyzer
tar -czf scraper.tar.gz scraper/ run_web_server.py requirements.txt
scp scraper.tar.gz scraper@YOUR_DROPLET_IP:~

# On the server
tar -xzf scraper.tar.gz
```

## Step 5: Set Up Python Environment

```bash
cd ~/scraper  # or your project directory

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install fastapi uvicorn requests beautifulsoup4 lxml python-dateutil
```

## Step 6: Test the Application

```bash
# Test run
uvicorn scraper.web_api:app --host 0.0.0.0 --port 8000

# Open another terminal and test
curl http://localhost:8000/health
```

If you see `{"status":"healthy",...}`, it's working!

Press `Ctrl+C` to stop the test server.

## Step 7: Set Up Systemd Service (Auto-start)

Create a service file:

```bash
sudo nano /etc/systemd/system/news-scraper.service
```

Add this content:

```ini
[Unit]
Description=News Scraper Web Service
After=network.target

[Service]
Type=simple
User=scraper
WorkingDirectory=/home/scraper/YOUR_PROJECT_DIR
Environment="PATH=/home/scraper/YOUR_PROJECT_DIR/venv/bin"
ExecStart=/home/scraper/YOUR_PROJECT_DIR/venv/bin/uvicorn scraper.web_api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Replace `YOUR_PROJECT_DIR` with your actual directory name!**

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable news-scraper
sudo systemctl start news-scraper
sudo systemctl status news-scraper
```

## Step 8: Set Up Nginx (Reverse Proxy)

Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/news-scraper
```

Add this content:

```nginx
server {
    listen 80;
    server_name YOUR_DROPLET_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # For SSE (Server-Sent Events)
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/news-scraper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 9: Configure Firewall

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS (for future SSL)
sudo ufw enable
```

## Step 10: Access Your Scraper

Open your browser and go to:
```
http://YOUR_DROPLET_IP
```

You should see the news scraper interface! 🎉

## Step 11: Add Basic Authentication (Optional but Recommended)

Install apache2-utils:
```bash
sudo apt install apache2-utils
```

Create password file:
```bash
sudo htpasswd -c /etc/nginx/.htpasswd admin
# Enter password when prompted
```

Update Nginx config:
```bash
sudo nano /etc/nginx/sites-available/news-scraper
```

Add inside the `location /` block:
```nginx
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
```

Restart Nginx:
```bash
sudo systemctl restart nginx
```

## Step 12: Set Up SSL (Optional but Recommended)

Install Certbot:
```bash
sudo apt install certbot python3-certbot-nginx
```

Get SSL certificate (requires a domain name):
```bash
sudo certbot --nginx -d your-domain.com
```

## Maintenance Commands

### View logs
```bash
# Application logs
sudo journalctl -u news-scraper -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart services
```bash
sudo systemctl restart news-scraper
sudo systemctl restart nginx
```

### Update code
```bash
cd ~/YOUR_PROJECT_DIR
git pull  # if using git
sudo systemctl restart news-scraper
```

### Check status
```bash
sudo systemctl status news-scraper
sudo systemctl status nginx
```

## Troubleshooting

### Service won't start
```bash
sudo journalctl -u news-scraper -n 50
```

### Port already in use
```bash
sudo lsof -i :8000
sudo kill <PID>
```

### Permission issues
```bash
sudo chown -R scraper:scraper /home/scraper/YOUR_PROJECT_DIR
```

## Security Best Practices

1. ✅ Use a non-root user
2. ✅ Enable firewall (ufw)
3. ✅ Add basic authentication
4. ✅ Use SSL/HTTPS (with domain)
5. ✅ Keep system updated: `sudo apt update && sudo apt upgrade`
6. ✅ Monitor logs regularly
7. ✅ Use strong passwords
8. ✅ Disable root SSH login (optional)

## Cost Estimate

- **Basic Droplet**: $6/month (1GB RAM)
- **Domain** (optional): $12/year
- **Total**: ~$6-7/month

## Backup Strategy

### Backup scraped data
```bash
# Create backup
tar -czf backup-$(date +%Y%m%d).tar.gz ~/YOUR_PROJECT_DIR/*.csv

# Download to local machine
scp scraper@YOUR_DROPLET_IP:~/backup-*.tar.gz ~/Downloads/
```

### Automated backups
Add to crontab:
```bash
crontab -e
```

Add line:
```
0 2 * * * tar -czf ~/backup-$(date +\%Y\%m\%d).tar.gz ~/YOUR_PROJECT_DIR/*.csv
```

## Next Steps

1. ✅ Deploy to Digital Ocean
2. ✅ Test the scraper
3. ✅ Share the URL with your team
4. ✅ Set up monitoring (optional)
5. ✅ Configure automated backups

## Support

If you encounter issues:
1. Check the logs: `sudo journalctl -u news-scraper -f`
2. Verify the service is running: `sudo systemctl status news-scraper`
3. Test locally: `curl http://localhost:8000/health`
4. Check Nginx: `sudo nginx -t`

---

**Created by Kabella** 🚀
