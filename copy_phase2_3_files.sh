#!/bin/bash

echo "📦 Copying Phase 2 & 3 files to ai_code project..."
echo ""

SOURCE_DIR="/Users/kabellatsang/PycharmProjects/pythonProject3"
DEST_DIR="/Users/kabellatsang/PycharmProjects/ai_code"

# Create directories if they don't exist
mkdir -p "$DEST_DIR/scraper/api"
mkdir -p "$DEST_DIR/scraper/static/js"
mkdir -p "$DEST_DIR/scraper/templates"

# Create __init__.py for api module
touch "$DEST_DIR/scraper/api/__init__.py"

# Copy API routes
echo "📄 Copying database_routes.py..."
cp "$SOURCE_DIR/scraper/api/database_routes.py" "$DEST_DIR/scraper/api/"

# Copy dashboard template
echo "📄 Copying dashboard.html..."
cp "$SOURCE_DIR/scraper/templates/dashboard.html" "$DEST_DIR/scraper/templates/"

# Copy dashboard JavaScript
echo "📄 Copying dashboard.js..."
cp "$SOURCE_DIR/scraper/static/js/dashboard.js" "$DEST_DIR/scraper/static/js/"

# Copy integration guide
echo "📄 Copying integration guide..."
cp "$SOURCE_DIR/PHASE_2_3_INTEGRATION_GUIDE.md" "$DEST_DIR/"

echo ""
echo "✅ All Phase 2 & 3 files copied successfully!"
echo ""
echo "📍 Files copied to: $DEST_DIR"
echo ""
echo "Next steps:"
echo "1. Follow PHASE_2_3_INTEGRATION_GUIDE.md"
echo "2. Update web_api.py with the integration code"
echo "3. Update index.html with sidebar navigation"
echo "4. Test the dashboard"
echo ""
