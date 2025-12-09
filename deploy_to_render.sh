#!/bin/bash
# Deploy to Render - Simple Script

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        Deploy to Render                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Add files
echo -e "${YELLOW}📦 Step 1: Adding files to git...${NC}"
git add .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Files added${NC}"
else
    echo -e "${YELLOW}⚠️  No new files to add${NC}"
fi

echo ""

# Step 2: Commit
echo -e "${YELLOW}💾 Step 2: Committing changes...${NC}"
git commit -m "Add multi-source scraper with deduplication and per-source log tabs"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Changes committed${NC}"
else
    echo -e "${YELLOW}⚠️  No changes to commit (already up to date)${NC}"
fi

echo ""

# Step 3: Push to GitHub
echo -e "${YELLOW}🚀 Step 3: Pushing to GitHub...${NC}"

# Try main branch first
git push origin main 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Pushed to main branch${NC}"
else
    # Try master branch
    echo "Trying master branch..."
    git push origin master 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Pushed to master branch${NC}"
    else
        echo -e "${YELLOW}⚠️  Push failed. Check your git setup.${NC}"
        echo ""
        echo "Possible issues:"
        echo "1. Not connected to GitHub - run: git remote -v"
        echo "2. Need to authenticate - check GitHub credentials"
        echo "3. Branch name different - check: git branch"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Deployment Complete! 🎉           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Pushed to GitHub successfully!${NC}"
echo ""
echo -e "${YELLOW}⏳ Render will auto-deploy in 2-3 minutes${NC}"
echo ""
echo "📊 Check deployment status:"
echo "   https://dashboard.render.com"
echo ""
echo "🌐 Your site will be updated at:"
echo "   https://crypto-news-scraper.onrender.com"
echo ""
echo "✨ New features deployed:"
echo "   - 3 news sources (BlockBeats, Jinse, PANews)"
echo "   - Per-source log tabs"
echo "   - Smart deduplication"
echo "   - Parallel scraping"
echo ""
