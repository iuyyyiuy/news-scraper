#!/bin/bash
# Quick upload script for scraper files

SERVER="root@143.198.219.220"
DEST="/home/scraper/news-scraper"

echo "📤 Uploading scraper files..."

# Upload scraper directory with all contents
scp -r scraper/ ${SERVER}:${DEST}/

# Upload requirements.txt
scp requirements.txt ${SERVER}:${DEST}/

echo "✅ Upload complete!"
echo ""
echo "Now SSH to server and run:"
echo "  ssh ${SERVER}"
echo "  cd ${DEST}"
echo "  chown -R scraper:scraper ${DEST}"
echo "  source venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  systemctl start news-scraper"
