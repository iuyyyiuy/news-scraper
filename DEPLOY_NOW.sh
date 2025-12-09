#!/bin/bash

# Quick deployment script for multi-source scraper improvements
# This will deploy all changes to both Digital Ocean and Render

echo "============================================================"
echo "Deploying Multi-Source Scraper Improvements"
echo "============================================================"
echo ""
echo "Changes to deploy:"
echo "  ✅ Session manager - log filtering system"
echo "  ✅ Jinse scraper - fixed title & date extraction"
echo "  ✅ BlockBeats scraper - log visibility updates"
echo "  ✅ PANews scraper - log visibility updates"
echo "  ✅ Web interface - log filtering by show_in_all flag"
echo "  ✅ Web API - callback parameter updates"
echo ""
echo "============================================================"
echo ""

cd /Users/kabellatsang/PycharmProjects/ai_code

# Check git status
echo "📋 Checking git status..."
git status --short
echo ""

# Add all modified files (but not backup files)
echo "📦 Adding modified files to git..."
git add scraper/core/session.py
git add scraper/core/jinse_scraper.py
git add scraper/core/blockbeats_scraper.py
git add scraper/core/panews_scraper.py
git add scraper/core/multi_source_scraper.py
git add scraper/web_api.py
git add scraper/templates/index.html

echo "✅ Files staged for commit"
echo ""

# Show what will be committed
echo "📝 Files to be committed:"
git diff --cached --name-only
echo ""

# Commit changes
echo "💾 Committing changes..."
git commit -m "Improve multi-source scraper: fix Jinse parser, add log filtering

- Fix Jinse title extraction (use <span class='title'> instead of page title)
- Fix Jinse date extraction (from js-liveDetail__date element)
- Add show_in_all parameter to control log visibility
- Update session manager to support log filtering
- Update all scrapers to use show_in_all flag
- Update web interface to filter logs in 全部 tab
- Source tabs still show all logs for debugging

Test results:
- Jinse scraper: 13/20 articles scraped successfully
- Titles: Correct and specific
- Dates: 2025-MM-DD format
- Log filtering: Ready for testing"

COMMIT_STATUS=$?

if [ $COMMIT_STATUS -ne 0 ]; then
    echo ""
    echo "⚠️  Commit failed or no changes to commit"
    echo "Checking if there are already committed changes to push..."
    echo ""
fi

# Push to GitHub (which triggers Render deployment)
echo "🚀 Pushing to GitHub..."
git push origin main

PUSH_STATUS=$?

echo ""
echo "============================================================"

if [ $PUSH_STATUS -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "📍 Deployment Status:"
    echo ""
    echo "1. Render (Auto-deploy):"
    echo "   - Status: Deploying now..."
    echo "   - URL: https://crypto-news-scraper.onrender.com"
    echo "   - Time: 2-3 minutes"
    echo "   - Dashboard: https://dashboard.render.com"
    echo ""
    echo "2. Digital Ocean (Manual):"
    echo "   - Run: ./deploy_multi_source_update.sh"
    echo "   - URL: http://143.198.219.220"
    echo ""
    echo "============================================================"
    echo ""
    echo "🎯 Next Steps:"
    echo ""
    echo "1. Wait 2-3 minutes for Render to deploy"
    echo ""
    echo "2. Test Render deployment:"
    echo "   open https://crypto-news-scraper.onrender.com"
    echo ""
    echo "3. Verify improvements:"
    echo "   ✓ Jinse titles are correct (not generic)"
    echo "   ✓ Dates show as 2025-MM-DD"
    echo "   ✓ '全部' tab shows only matched articles"
    echo "   ✓ Source tabs show all logs"
    echo ""
    echo "4. (Optional) Deploy to Digital Ocean:"
    echo "   cd /Users/kabellatsang/PycharmProjects/ai_code"
    echo "   ./deploy_multi_source_update.sh"
    echo ""
    echo "============================================================"
    echo ""
    echo "✨ Deployment initiated successfully!"
    echo ""
else
    echo "❌ Push failed!"
    echo ""
    echo "Common issues:"
    echo "1. Not authenticated with GitHub"
    echo "2. No internet connection"
    echo "3. Remote repository issues"
    echo ""
    echo "Try:"
    echo "  git push origin main --verbose"
    echo ""
fi
