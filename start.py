#!/usr/bin/env python3
"""
Production startup script for CoinEx Dashboard
Optimized for Render deployment
"""

import os
import sys
from complete_dashboard import app

if __name__ == '__main__':
    # Get port from environment (Render sets this automatically)
    port = int(os.environ.get('PORT', 8080))
    
    # Production settings
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("🚀 Starting CoinEx Professional Trading Dashboard")
    print(f"🌐 Port: {port}")
    print(f"🔧 Debug: {debug_mode}")
    print("📊 Features: Complete monitoring + Real-time data + Professional metrics")
    
    try:
        # Start the application
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug_mode,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)