#!/usr/bin/env python3
"""
Start ONLY the news scraper web API without any trading/ML components
This prevents SQLite database lock issues
"""
import uvicorn
import os
import sys

def main():
    print("🚀 Starting News Scraper ONLY (No Trading/ML Components)")
    print("=" * 60)
    print()
    print("📊 Dashboard: http://localhost:8000/dashboard")
    print("🔧 Manual Update API: http://localhost:8000/api/manual-update")
    print("📋 Health Check: http://localhost:8000/api/health")
    print("📰 Articles API: http://localhost:8000/api/database/articles")
    print()
    print("✨ Features Available:")
    print("   - 手动更新 (Manual Update) button in dashboard")
    print("   - Sequential scraping (BlockBeats → Jinse)")
    print("   - AI-powered content filtering")
    print("   - Supabase database storage")
    print("   - CSV export functionality")
    print()
    print("🚫 DISABLED Components (to prevent SQLite locks):")
    print("   - AI Trading System")
    print("   - ML Analysis")
    print("   - Trading Strategy Analysis")
    print("   - Enhanced Market Collection")
    print()
    print("🔒 Database: Supabase ONLY (no local SQLite)")
    print("=" * 60)
    print()
    
    # Ensure we're using the right environment
    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_KEY'):
        print("⚠️  WARNING: Supabase environment variables not set!")
        print("   Please check your .env file")
        print()
    
    try:
        # Start the server with only news scraper functionality
        uvicorn.run(
            "scraper.web_api:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload to prevent multiple processes
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 News scraper stopped")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()