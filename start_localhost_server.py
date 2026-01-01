#!/usr/bin/env python3
"""
Start the news scraper web server on localhost for testing
"""
import uvicorn
import sys
import os

def main():
    """Start the localhost server"""
    print("🚀 Starting News Scraper on Localhost")
    print("=" * 50)
    
    try:
        # Import the web API
        from scraper.web_api import app
        
        print("🌐 Server starting on: http://localhost:8000")
        print("📱 Dashboard URL: http://localhost:8000/dashboard")
        print("🔧 API Documentation: http://localhost:8000/docs")
        print("📊 Manual Update API: http://localhost:8000/api/manual-update")
        print()
        print("💡 Features available:")
        print("   ✅ BlockBeats scraping")
        print("   ✅ ForesightNews scraping (with Selenium)")
        print("   ⚠️  Jinse temporarily disabled")
        print("   ✅ Manual update functionality")
        print("   ✅ CSV export")
        print("   ✅ Article filtering")
        print()
        print("🔍 To test ForesightNews:")
        print("   1. Go to http://localhost:8000/dashboard")
        print("   2. Click '手動更新' button")
        print("   3. Wait for processing (may take 2-3 minutes)")
        print("   4. Check for new ForesightNews articles")
        print()
        print("⚠️  Note: ForesightNews uses Selenium and may be slower")
        print("👋 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start the server
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            log_level="info",
            reload=False  # Disable reload for stability
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're in the correct directory and dependencies are installed")
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        print("💡 Check that port 8000 is available")

if __name__ == "__main__":
    main()