#!/usr/bin/env python3
"""
Environment Variable Loader for Scraper
"""

import os
from dotenv import load_dotenv

# Force load environment variables
load_dotenv(override=True)

# Verify critical environment variables
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not DEEPSEEK_API_KEY:
    print("⚠️ WARNING: DEEPSEEK_API_KEY not found in environment")
    print("   AI content analysis will be disabled")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️ WARNING: Supabase configuration incomplete")
    print("   Database operations may fail")

# Export for other modules
__all__ = ['DEEPSEEK_API_KEY', 'SUPABASE_URL', 'SUPABASE_KEY']
