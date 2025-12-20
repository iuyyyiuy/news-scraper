#!/usr/bin/env python3
"""
Check the content quality of recently scraped articles.
"""

import os
from supabase import create_client, Client
from datetime import datetime, timedelta

def check_article_content():
    """Check the content of recently scraped articles."""
    
    # Initialize Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        print("💡 Copy .env.example to .env and fill in your credentials")
        return
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return
    
    supabase: Client = create_client(url, key)
    
    try:
        # Get the most recent articles
        response = supabase.table('articles').select('*').order('scraped_at', desc=True).limit(3).execute()
        
        if not response.data:
            print("❌ No articles found")
            return
        
        print("=== RECENT ARTICLE CONTENT ANALYSIS ===\n")
        
        for i, article in enumerate(response.data, 1):
            print(f"📰 Article {i}: {article['title']}")
            print(f"📅 Date: {article.get('publication_date', 'N/A')}")
            print(f"🌐 Source: {article.get('source_website', 'N/A')}")
            print(f"📝 Content length: {len(article.get('body_text', ''))} characters")
            
            # Show content preview
            content = article.get('body_text', '')
            if content:
                # Check if content is clean (no footer elements)
                footer_markers = ['AI 解读', '展开', '原文链接', '举报', 'farcaster评论']
                has_footer = any(marker in content for marker in footer_markers)
                
                print(f"🧹 Clean content: {'❌ Contains footer' if has_footer else '✅ Clean'}")
                print(f"📖 Content preview:")
                print(f"   {content[:200]}...")
                
                # Check for date in content
                if '2025-' in content or '月' in content:
                    print("📅 Contains date information: ✅")
                else:
                    print("📅 Contains date information: ❌")
                
                # Check for source information
                if '据' in content and '监测' in content:
                    print("📰 Contains source information: ✅")
                else:
                    print("📰 Contains source information: ❌")
            else:
                print("❌ No content found")
            
            print("-" * 80)
    
    except Exception as e:
        print(f"❌ Error checking articles: {e}")

if __name__ == "__main__":
    check_article_content()