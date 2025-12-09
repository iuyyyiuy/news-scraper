#!/bin/bash

# Script to copy News Database files to ai_code project

echo "📦 Copying News Database files to ai_code project..."
echo ""

# Define source and destination
SOURCE_DIR="/Users/kabellatsang/PycharmProjects/pythonProject3"
DEST_DIR="/Users/kabellatsang/PycharmProjects/ai_code"

# Check if destination exists
if [ ! -d "$DEST_DIR" ]; then
    echo "❌ Error: ai_code directory not found at $DEST_DIR"
    exit 1
fi

# Create scraper/core directory if it doesn't exist
mkdir -p "$DEST_DIR/scraper/core"

# Copy core files
echo "📄 Copying database_manager.py..."
cp "$SOURCE_DIR/scraper/core/database_manager.py" "$DEST_DIR/scraper/core/"

echo "📄 Copying scheduled_scraper.py..."
cp "$SOURCE_DIR/scraper/core/scheduled_scraper.py" "$DEST_DIR/scraper/core/"

echo "📄 Copying scheduler.py..."
cp "$SOURCE_DIR/scraper/core/scheduler.py" "$DEST_DIR/scraper/core/"

# Copy environment file
echo "📄 Copying .env..."
cp "$SOURCE_DIR/.env" "$DEST_DIR/"

# Copy test file
echo "📄 Copying test_database_connection.py..."
cp "$SOURCE_DIR/test_database_connection.py" "$DEST_DIR/"

# Copy requirements
echo "📄 Copying requirements_news_database.txt..."
cp "$SOURCE_DIR/requirements_news_database.txt" "$DEST_DIR/"

echo ""
echo "✅ All files copied successfully!"
echo ""
echo "📍 Files copied to: $DEST_DIR"
echo ""
echo "Next steps:"
echo "1. cd $DEST_DIR"
echo "2. pip install -r requirements_news_database.txt"
echo "3. python test_database_connection.py"
echo ""
