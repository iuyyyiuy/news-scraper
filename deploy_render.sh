#!/bin/bash

echo "🚀 Render Deployment Script"
echo "=========================="

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check environment variables
echo "🔑 Checking environment variables..."
if [ -z "$SUPABASE_URL" ]; then
    echo "❌ SUPABASE_URL not set"
    exit 1
fi

if [ -z "$SUPABASE_KEY" ]; then
    echo "❌ SUPABASE_KEY not set"
    exit 1
fi

if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ DEEPSEEK_API_KEY not set"
    exit 1
fi

echo "✅ All environment variables set"

# Test database connection
echo "🔍 Testing database connection..."
python3 -c "
import os
from supabase import create_client
try:
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
    response = supabase.table('articles').select('id').limit(1).execute()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

echo "🎉 Deployment checks passed"
