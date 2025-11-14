"""
Run Trade Risk Analyzer API

Starts the FastAPI server with uvicorn.
"""

import sys
import os

# Ensure we're using the virtual environment
if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    print("✅ Using virtual environment")
else:
    print("⚠️  Warning: Not running in virtual environment")
    print("   Run: source .venv/bin/activate")

try:
    import uvicorn
except ImportError:
    print("\n❌ Error: uvicorn not installed")
    print("   Run: pip install fastapi uvicorn psutil")
    sys.exit(1)


if __name__ == "__main__":
    print("="*60)
    print("Trade Risk Analyzer API")
    print("="*60)
    print()
    print("Starting server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Alternative Docs: http://localhost:8000/redoc")
    print()
    print("Press CTRL+C to stop")
    print("="*60)
    print()
    
    try:
        uvicorn.run(
            "trade_risk_analyzer.api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Auto-reload on code changes
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)
