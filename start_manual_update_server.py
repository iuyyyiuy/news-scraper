#!/usr/bin/env python3
"""
Start the dashboard server with 手动更新 functionality
"""
import uvicorn
from scraper.web_api import app

def main():
    print("🚀 Starting Dashboard with 手动更新 Function")
    print("=" * 60)
    print()
    print("📊 Dashboard: http://localhost:8000/dashboard")
    print("🔧 API: http://localhost:8000/api/manual-update")
    print("📋 Health: http://localhost:8000/api/health")
    print()
    print("✨ Features Available:")
    print("   - 手动更新 button in dashboard")
    print("   - Sequential scraping (BlockBeats → Jinse)")
    print("   - AI-powered filtering")
    print("   - Real-time database updates")
    print("   - Progress notifications")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    # Start the server
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    main()