#!/bin/bash
# Deploy multi-source scraper to BOTH Digital Ocean and Render
# Your setup: DO=143.198.219.220, Render=crypto-news-scraper.onrender.com

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Deploy to Both Platforms                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Deploy to Digital Ocean
echo -e "${YELLOW}📦 Step 1: Deploying to Digital Ocean...${NC}"
echo "  URL: http://143.198.219.220"
echo ""

if [ -f "./deploy_multi_source_update.sh" ]; then
    ./deploy_multi_source_update.sh
    DO_STATUS=$?
else
    echo -e "${YELLOW}⚠️  deploy_multi_source_update.sh not found, skipping Digital Ocean${NC}"
    DO_STATUS=1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 2: Deploy to Render
echo -e "${YELLOW}🎨 Step 2: Deploying to Render...${NC}"
echo "  URL: https://crypto-news-scraper.onrender.com"
echo ""

# Check if git repo
if [ -d ".git" ]; then
    echo "  - Adding files to git..."
    git add .
    
    echo "  - Committing changes..."
    git commit -m "Deploy multi-source scraper with deduplication" || echo "  (No changes to commit)"
    
    echo "  - Pushing to GitHub..."
    git push origin main || git push origin master
    
    RENDER_STATUS=$?
    
    if [ $RENDER_STATUS -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Pushed to GitHub successfully!${NC}"
        echo "  Render will auto-deploy in 2-3 minutes"
        echo "  Watch progress: https://dashboard.render.com"
    else
        echo ""
        echo -e "${YELLOW}⚠️  Git push failed. Check your git setup.${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Not a git repository. Initialize git first:${NC}"
    echo "  git init"
    echo "  git add ."
    echo "  git commit -m 'Initial commit'"
    echo "  git remote add origin YOUR_REPO_URL"
    echo "  git push -u origin main"
    RENDER_STATUS=1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Deployment Summary                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

if [ $DO_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ Digital Ocean: Deployed${NC}"
    echo "   http://143.198.219.220"
else
    echo -e "${YELLOW}⚠️  Digital Ocean: Check logs above${NC}"
fi

echo ""

if [ $RENDER_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ Render: Pushed to GitHub${NC}"
    echo "   https://crypto-news-scraper.onrender.com"
    echo "   (Auto-deploying in 2-3 minutes)"
else
    echo -e "${YELLOW}⚠️  Render: Check logs above${NC}"
fi

echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo ""
echo "1. Test Digital Ocean:"
echo "   open http://143.198.219.220"
echo ""
echo "2. Wait for Render (2-3 min), then test:"
echo "   open https://crypto-news-scraper.onrender.com"
echo ""
echo "3. Verify features:"
echo "   - 3 source checkboxes"
echo "   - 4 log tabs"
echo "   - Multi-source scraping"
echo "   - Deduplication"
echo ""
echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""
