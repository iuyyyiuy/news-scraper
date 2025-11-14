#!/bin/bash
# News Scraper Deployment Script for Digital Ocean
# Run this script on your Digital Ocean droplet

set -e  # Exit on error

echo "🚀 Starting News Scraper Deployment..."
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/home/scraper/news-scraper"
SERVICE_NAME="news-scraper"
NGINX_SITE="news-scraper"

# Step 1: Update system
echo -e "${YELLOW}📦 Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Step 2: Install dependencies
echo -e "${YELLOW}📦 Installing Python and dependencies...${NC}"
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx

# Step 3: Create user if doesn't exist
if ! id "scraper" &>/dev/null; then
    echo -e "${YELLOW}👤 Creating scraper user...${NC}"
    sudo adduser --disabled-password --gecos "" scraper
    sudo usermod -aG sudo scraper
fi

# Step 4: Create app directory
echo -e "${YELLOW}📁 Creating application directory...${NC}"
sudo mkdir -p $APP_DIR
sudo chown -R scraper:scraper $APP_DIR

# Step 5: Set up Python virtual environment
echo -e "${YELLOW}🐍 Setting up Python virtual environment...${NC}"
cd $APP_DIR
sudo -u scraper python3.11 -m venv venv
sudo -u scraper $APP_DIR/venv/bin/pip install --upgrade pip

# Step 6: Install Python packages
echo -e "${YELLOW}📚 Installing Python packages...${NC}"
sudo -u scraper $APP_DIR/venv/bin/pip install fastapi uvicorn requests beautifulsoup4 lxml python-dateutil

# Step 7: Create systemd service
echo -e "${YELLOW}⚙️  Creating systemd service...${NC}"
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=News Scraper Web Service
After=network.target

[Service]
Type=simple
User=scraper
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/uvicorn scraper.web_api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 8: Configure Nginx
echo -e "${YELLOW}🌐 Configuring Nginx...${NC}"
sudo tee /etc/nginx/sites-available/${NGINX_SITE} > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # For SSE (Server-Sent Events)
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        proxy_read_timeout 3600s;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/${NGINX_SITE} /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Step 9: Configure firewall
echo -e "${YELLOW}🔥 Configuring firewall...${NC}"
sudo ufw --force enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Step 10: Reload services
echo -e "${YELLOW}🔄 Reloading services...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl restart nginx

echo ""
echo -e "${GREEN}✅ Deployment setup complete!${NC}"
echo ""
echo "📝 Next steps:"
echo "1. Upload your code to: $APP_DIR"
echo "2. Start the service: sudo systemctl start ${SERVICE_NAME}"
echo "3. Check status: sudo systemctl status ${SERVICE_NAME}"
echo "4. View logs: sudo journalctl -u ${SERVICE_NAME} -f"
echo ""
echo "🌐 Your scraper will be available at: http://YOUR_SERVER_IP"
echo ""
