"""
Web API - Now redirects to Dashboard
This file is kept for backward compatibility with Render deployment
"""
# Import the dashboard app
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from start_dashboard import app

# Export app for uvicorn
__all__ = ['app']
