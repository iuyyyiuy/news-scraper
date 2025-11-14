#!/bin/bash
# Upload News Scraper to Digital Ocean
# Run this script on your LOCAL machine

# Configuration - UPDATE THESE!
SERVER_IP="143.198.219.220"
SERVER_USER="root"
APP_DIR="/home/scraper/news-scraper"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "📤 Uploading News Scraper to Digital Ocean..."
echo "=============================================="

# Check if SERVER_IP is set
if [ "$SERVER_IP" == "YOUR_SERVER_IP_HERE" ]; then
    echo -e "${RED}❌ Error: Please update SERVER_IP in this script!${NC}"
    echo "Edit upload_to_server.sh and set your server IP address"
    exit 1
fi

# Create temporary directory for upload
echo -e "${YELLOW}📦 Preparing files for upload...${NC}"
TEMP_DIR=$(mktemp -d)
mkdir -p $TEMP_DIR/scraper

# Copy necessary files
cp -r scraper/ $TEMP_DIR/
cp requirements.txt $TEMP_DIR/
cp run_web_server.py $TEMP_DIR/ 2>/dev/null || true

# Create tarball
cd $TEMP_DIR
tar -czf news-scraper.tar.gz scraper/ requirements.txt run_web_server.py 2>/dev/null || tar -czf news-scraper.tar.gz scraper/ requirements.txt

# Upload to server
echo -e "${YELLOW}📤 Uploading to server...${NC}"
scp news-scraper.tar.gz ${SERVER_USER}@${SERVER_IP}:~

# Extract on server
echo -e "${YELLOW}📂 Extracting files on server...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /home/scraper/news-scraper
tar -xzf ~/news-scraper.tar.gz
rm ~/news-scraper.tar.gz
echo "✅ Files extracted successfully"
ENDSSH

# Clean up
rm -rf $TEMP_DIR

echo ""
echo -e "${GREEN}✅ Upload complete!${NC}"
echo ""
echo "📝 Next steps:"
echo "1. SSH to server: ssh ${SERVER_USER}@${SERVER_IP}"
echo "2. Start service: sudo systemctl start news-scraper"
echo "3. Check status: sudo systemctl status news-scraper"
echo "4. View in browser: http://${SERVER_IP}"
echo ""
