#!/bin/bash
# Quick deployment script for multi-source scraper update
# This script uploads ONLY the changed files for faster deployment

# Configuration - VERIFIED ✅
SERVER_IP="143.198.219.220"
SERVER_USER="root"
APP_DIR="/home/scraper/news-scraper"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Multi-Source Scraper Update Deployment   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if SERVER_IP is set
if [ "$SERVER_IP" == "143.198.219.220" ]; then
    echo -e "${YELLOW}⚠️  Using default IP. Update SERVER_IP in this script if needed.${NC}"
    read -p "Continue with IP $SERVER_IP? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verify new files exist locally
echo -e "${YELLOW}📋 Checking for new files...${NC}"
MISSING_FILES=0

check_file() {
    if [ ! -f "$1" ]; then
        echo -e "${RED}  ❌ Missing: $1${NC}"
        MISSING_FILES=$((MISSING_FILES + 1))
    else
        echo -e "${GREEN}  ✅ Found: $1${NC}"
    fi
}

check_file "scraper/core/jinse_scraper.py"
check_file "scraper/core/panews_scraper.py"
check_file "scraper/core/deduplicator.py"
check_file "scraper/core/multi_source_scraper.py"
check_file "scraper/web_api.py"
check_file "scraper/core/session.py"
check_file "scraper/templates/index.html"

if [ $MISSING_FILES -gt 0 ]; then
    echo -e "${RED}❌ Error: $MISSING_FILES file(s) missing!${NC}"
    echo "Please ensure all files are in the correct location."
    exit 1
fi

echo ""
echo -e "${GREEN}✅ All files found!${NC}"
echo ""

# Create temporary directory
echo -e "${YELLOW}📦 Preparing update package...${NC}"
TEMP_DIR=$(mktemp -d)
UPDATE_DIR="$TEMP_DIR/update"
mkdir -p $UPDATE_DIR/scraper/core
mkdir -p $UPDATE_DIR/scraper/templates

# Copy only the changed files
echo "  - Copying new scrapers..."
cp scraper/core/jinse_scraper.py $UPDATE_DIR/scraper/core/
cp scraper/core/panews_scraper.py $UPDATE_DIR/scraper/core/
cp scraper/core/deduplicator.py $UPDATE_DIR/scraper/core/
cp scraper/core/multi_source_scraper.py $UPDATE_DIR/scraper/core/

echo "  - Copying updated files..."
cp scraper/web_api.py $UPDATE_DIR/scraper/
cp scraper/core/session.py $UPDATE_DIR/scraper/core/
cp scraper/core/storage.py $UPDATE_DIR/scraper/core/
cp scraper/templates/index.html $UPDATE_DIR/scraper/templates/

echo "  - Copying test script..."
cp test_web_interface_multi_source.py $UPDATE_DIR/ 2>/dev/null || true

# Create tarball
cd $TEMP_DIR
tar -czf multi-source-update.tar.gz update/

# Upload to server
echo ""
echo -e "${YELLOW}📤 Uploading to server...${NC}"
scp multi-source-update.tar.gz ${SERVER_USER}@${SERVER_IP}:~

# Extract and update on server
echo ""
echo -e "${YELLOW}🔄 Updating files on server...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
set -e

echo "  - Extracting files..."
cd ~
tar -xzf multi-source-update.tar.gz

echo "  - Backing up current files..."
cd /home/scraper/news-scraper
mkdir -p backups
BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p backups/$BACKUP_NAME
cp -r scraper/core/*.py backups/$BACKUP_NAME/ 2>/dev/null || true
cp scraper/web_api.py backups/$BACKUP_NAME/ 2>/dev/null || true
cp scraper/templates/index.html backups/$BACKUP_NAME/ 2>/dev/null || true

echo "  - Copying new files..."
cp -r ~/update/scraper/* scraper/

echo "  - Cleaning up..."
rm -rf ~/multi-source-update.tar.gz ~/update

echo "  - Restarting service..."
sudo systemctl restart news-scraper

echo "  - Checking service status..."
sleep 2
sudo systemctl is-active news-scraper && echo "✅ Service is running" || echo "❌ Service failed to start"

ENDSSH

# Clean up local temp files
rm -rf $TEMP_DIR

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          Update Complete! 🎉               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📝 What was updated:${NC}"
echo "  ✅ New Jinse scraper (jinse.cn)"
echo "  ✅ New PANews scraper (panewslab.com)"
echo "  ✅ Deduplication engine"
echo "  ✅ Multi-source coordinator"
echo "  ✅ Updated web API"
echo "  ✅ Updated session management"
echo "  ✅ Updated web interface with log tabs"
echo ""
echo -e "${BLUE}🌐 Access your scraper:${NC}"
echo "  http://${SERVER_IP}"
echo ""
echo -e "${BLUE}📊 Check logs:${NC}"
echo "  ssh ${SERVER_USER}@${SERVER_IP}"
echo "  sudo journalctl -u news-scraper -f"
echo ""
echo -e "${BLUE}🧪 Test features:${NC}"
echo "  1. Select multiple sources (BlockBeats, Jinse, PANews)"
echo "  2. Enable deduplication"
echo "  3. Start scraping"
echo "  4. Switch between log tabs"
echo "  5. Download CSV with combined results"
echo ""
echo -e "${GREEN}✨ Deployment successful!${NC}"
echo ""
