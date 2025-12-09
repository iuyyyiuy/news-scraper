#!/bin/bash
cd /Users/kabellatsang/PycharmProjects/ai_code
git add scraper/core/database_manager.py
git commit -m "Fix Supabase header validation"
git push origin main
echo "✅ Fix pushed! Wait 5 minutes for Render to redeploy."
