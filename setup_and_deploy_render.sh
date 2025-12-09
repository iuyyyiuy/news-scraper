#!/bin/bash
# Setup Git and Deploy to Render

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Setup Git & Deploy to Render             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if git repo exists
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}📦 No git repository found. Setting up...${NC}"
    echo ""
    
    # Initialize git
    echo "1. Initializing git repository..."
    git init
    
    echo ""
    echo -e "${YELLOW}⚠️  You need to connect to GitHub!${NC}"
    echo ""
    echo "Please follow these steps:"
    echo ""
    echo "1. Create a new repository on GitHub:"
    echo "   - Go to: https://github.com/new"
    echo "   - Repository name: crypto-news-scraper (or any name)"
    echo "   - Make it Public or Private"
    echo "   - DON'T initialize with README"
    echo "   - Click 'Create repository'"
    echo ""
    echo "2. Copy the repository URL (it looks like):"
    echo "   https://github.com/YOUR_USERNAME/crypto-news-scraper.git"
    echo ""
    read -p "3. Paste your GitHub repository URL here: " REPO_URL
    
    if [ -z "$REPO_URL" ]; then
        echo -e "${RED}❌ No URL provided. Exiting.${NC}"
        exit 1
    fi
    
    echo ""
    echo "4. Adding remote repository..."
    git remote add origin "$REPO_URL"
    
    echo ""
    echo "5. Adding all files..."
    git add .
    
    echo ""
    echo "6. Creating initial commit..."
    git commit -m "Initial commit: Multi-source news scraper"
    
    echo ""
    echo "7. Setting default branch to main..."
    git branch -M main
    
    echo ""
    echo "8. Pushing to GitHub..."
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Successfully pushed to GitHub!${NC}"
    else
        echo ""
        echo -e "${RED}❌ Push failed. You may need to authenticate.${NC}"
        echo ""
        echo "If you see authentication errors:"
        echo "1. Generate a Personal Access Token:"
        echo "   https://github.com/settings/tokens"
        echo "2. Use the token as your password when prompted"
        echo ""
        echo "Or set up SSH keys:"
        echo "   https://docs.github.com/en/authentication/connecting-to-github-with-ssh"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Git repository found${NC}"
    echo ""
    
    # Check if remote exists
    if ! git remote -v | grep -q origin; then
        echo -e "${YELLOW}⚠️  No remote repository configured${NC}"
        echo ""
        read -p "Enter your GitHub repository URL: " REPO_URL
        git remote add origin "$REPO_URL"
    fi
    
    echo "Adding files..."
    git add .
    
    echo "Committing changes..."
    git commit -m "Add multi-source scraper with deduplication" || echo "No changes to commit"
    
    echo "Pushing to GitHub..."
    git push origin main 2>/dev/null || git push origin master
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Successfully pushed to GitHub!${NC}"
    else
        echo -e "${RED}❌ Push failed${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Setup Complete! 🎉                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo ""
echo "1. Go to Render: https://render.com"
echo "2. Click 'New +' → 'Web Service'"
echo "3. Connect your GitHub repository"
echo "4. Configure:"
echo "   - Name: crypto-news-scraper"
echo "   - Environment: Python 3"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: uvicorn scraper.web_api:app --host 0.0.0.0 --port \$PORT"
echo "5. Click 'Create Web Service'"
echo ""
echo "Your app will be live at:"
echo "https://crypto-news-scraper.onrender.com"
echo ""
