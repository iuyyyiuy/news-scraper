#!/usr/bin/env python3
# Monthly cleanup script - run this on the 1st of each month
import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def monthly_cleanup():
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    supabase = create_client(supabase_url, supabase_key)
    
    # Delete articles older than current month
    current_month = datetime.now().strftime('%Y-%m-01')
    
    delete_response = supabase.table('articles').delete().lt('date', current_month).execute()
    
    print(f"Monthly cleanup completed: {datetime.now()}")
    print(f"Deleted articles older than {current_month}")

if __name__ == "__main__":
    monthly_cleanup()
