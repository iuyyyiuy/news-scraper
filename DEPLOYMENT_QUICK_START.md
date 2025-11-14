# 🚀 Quick Deployment Guide

Follow these steps to deploy your News Scraper to Digital Ocean in ~15 minutes.

## Prerequisites

- [ ] Digital Ocean account
- [ ] Credit card for billing
- [ ] SSH key (we'll create one if needed)

---

## Part 1: Create Digital Ocean Droplet (5 minutes)

### 1. Go to Digital Ocean
Visit: https://cloud.digitalocean.com/

### 2. Create SSH Key (if you don't have one)

On your Mac, run:
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
# Press Enter for all prompts (use defaults)

# Copy your public key
cat ~/.ssh/id_rsa.pub | pbcopy
```

### 3. Add SSH Key to Digital Ocean
1. In Digital Ocean, go to **Settings** → **Security** → **SSH Keys**
2. Click **Add SSH Key**
3. Paste your key (already in clipboard)
4. Name it: "My Mac"
5. Click **Add SSH Key**

### 4. Create Droplet
1. Click **Create** → **Droplets**
2. Choose:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic
   - **CPU**: Regular - $6/month (1GB RAM, 1 CPU)
   - **Datacenter**: Choose closest to you
   - **Authentication**: Select your SSH key
   - **Hostname**: `news-scraper`
3. Click **Create Droplet**
4. **Wait 1-2 minutes** for droplet to be created
5. **Copy the IP address** (e.g., 123.456.789.0)

---

## Part 2: Initial Server Setup (5 minutes)

### 1. Connect to your server

```bash
ssh root@YOUR_DROPLET_IP
# Type 'yes' when asked about fingerprint
```

### 2. Run the deployment script

```bash
# Download and run the setup script
curl -o deploy.sh https://raw.githubusercontent.com/YOUR_REPO/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

Or manually paste the deploy.sh content:

```bash
nano deploy.sh
# Paste the content from deploy.sh
# Press Ctrl+X, then Y, then Enter

chmod +x deploy.sh
./deploy.sh
```

This will:
- ✅ Update the system
- ✅ Install Python, Nginx
- ✅ Create a 'scraper' user
- ✅ Set up virtual environment
- ✅ Configure services
- ✅ Set up firewall

**Wait for it to complete (~3-5 minutes)**

---

## Part 3: Upload Your Code (3 minutes)

### Option A: Using the upload script (Recommended)

On your **local machine**:

```bash
cd /Users/kabellatsang/Desktop/trade_risk_analyzer

# Edit the upload script
nano upload_to_server.sh
# Change YOUR_SERVER_IP_HERE to your actual IP
# Press Ctrl+X, then Y, then Enter

# Make it executable
chmod +x upload_to_server.sh

# Run it
./upload_to_server.sh
```

### Option B: Manual upload

```bash
cd /Users/kabellatsang/Desktop/trade_risk_analyzer

# Create tarball
tar -czf news-scraper.tar.gz scraper/ requirements.txt

# Upload
scp news-scraper.tar.gz scraper@YOUR_DROPLET_IP:~

# SSH to server
ssh scraper@YOUR_DROPLET_IP

# Extract
cd /home/scraper/news-scraper
tar -xzf ~/news-scraper.tar.gz
```

---

## Part 4: Start the Service (2 minutes)

On the **server** (via SSH):

```bash
# Start the service
sudo systemctl start news-scraper

# Check if it's running
sudo systemctl status news-scraper

# You should see "active (running)" in green
```

If you see errors, check logs:
```bash
sudo journalctl -u news-scraper -n 50
```

---

## Part 5: Test It! (1 minute)

### Open in your browser:
```
http://YOUR_DROPLET_IP
```

You should see the News Scraper interface! 🎉

### Test the scraper:
1. Set days: 7
2. Keep default keywords
3. Set max articles: 100
4. Click "开始爬取"
5. Watch the logs in real-time!

---

## Part 6: Add Password Protection (Optional, 2 minutes)

On the **server**:

```bash
# Install password tool
sudo apt install apache2-utils

# Create password (username: admin)
sudo htpasswd -c /etc/nginx/.htpasswd admin
# Enter password when prompted

# Update Nginx config
sudo nano /etc/nginx/sites-available/news-scraper
```

Add these two lines inside the `location /` block:
```nginx
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
```

Save and restart:
```bash
sudo systemctl restart nginx
```

Now when you visit the site, you'll need to enter:
- Username: `admin`
- Password: (what you set)

---

## Useful Commands

### View logs (real-time)
```bash
sudo journalctl -u news-scraper -f
```

### Restart service
```bash
sudo systemctl restart news-scraper
```

### Stop service
```bash
sudo systemctl stop news-scraper
```

### Update code
```bash
# On local machine: run upload script again
./upload_to_server.sh

# On server: restart service
sudo systemctl restart news-scraper
```

### Check service status
```bash
sudo systemctl status news-scraper
sudo systemctl status nginx
```

---

## Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u news-scraper -n 100

# Check if port is in use
sudo lsof -i :8000

# Test manually
cd /home/scraper/news-scraper
source venv/bin/activate
uvicorn scraper.web_api:app --host 0.0.0.0 --port 8000
```

### Can't connect to server
```bash
# Check firewall
sudo ufw status

# Check Nginx
sudo nginx -t
sudo systemctl status nginx
```

### Permission errors
```bash
sudo chown -R scraper:scraper /home/scraper/news-scraper
```

---

## Cost

- **Droplet**: $6/month
- **Bandwidth**: 1TB included (more than enough)
- **Total**: ~$6/month

You can destroy the droplet anytime to stop charges.

---

## Next Steps

1. ✅ Share the URL with your team
2. ✅ Set up password protection
3. ✅ Bookmark the IP address
4. ✅ Set up automated backups (optional)
5. ✅ Get a domain name (optional, ~$12/year)

---

## Need Help?

Common issues and solutions:

**"Connection refused"**
- Check if service is running: `sudo systemctl status news-scraper`
- Check firewall: `sudo ufw status`

**"502 Bad Gateway"**
- Service is not running: `sudo systemctl start news-scraper`
- Check logs: `sudo journalctl -u news-scraper -f`

**"Can't SSH"**
- Check your SSH key is added to Digital Ocean
- Try: `ssh -v root@YOUR_IP` for verbose output

---

**You're all set! Enjoy your deployed News Scraper! 🎉**
