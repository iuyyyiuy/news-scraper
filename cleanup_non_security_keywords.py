#!/usr/bin/env python3
"""
Cleanup Non-Security Keywords
Removes general crypto keywords that are not security-related and their associated articles.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database manager
sys.path.append('.')
from scraper.core.database_manager import DatabaseManager

def cleanup_non_security_keywords():
    """Remove non-security keywords and their associated articles"""
    
    # Keywords to remove (general crypto terms, not security-related)
    keywords_to_remove = [
        "币安",      # Binance (Chinese)
        "价格",      # Price
        "代币",      # Token
        "比特币",    # Bitcoin
        "以太坊",    # Ethereum
        "Binance"    # Binance (English)
    ]
    
    print("🧹 Cleaning up non-security keywords and articles")
    print("=" * 60)
    
    # Initialize database manager
    db_manager = DatabaseManager()
    if not db_manager.supabase:
        print("❌ Failed to connect to database")
        return False
    
    print(f"📋 Keywords to remove: {', '.join(keywords_to_remove)}")
    
    # Step 1: Check current articles with these keywords
    print("\n🔍 Step 1: Analyzing articles with non-security keywords...")
    
    total_articles_to_remove = 0
    articles_by_keyword = {}
    
    for keyword in keywords_to_remove:
        try:
            # Find articles that contain this keyword in the JSON array
            # Use PostgreSQL JSON operators to search in the array
            response = db_manager.supabase.table('articles').select('*').filter('matched_keywords', 'cs', f'["{keyword}"]').execute()
            
            if response.data:
                articles_by_keyword[keyword] = response.data
                count = len(response.data)
                total_articles_to_remove += count
                print(f"   📊 '{keyword}': {count} articles")
                
                # Show some example titles
                for i, article in enumerate(response.data[:3]):  # Show first 3
                    print(f"      - {article['title'][:60]}...")
                if count > 3:
                    print(f"      ... and {count - 3} more")
            else:
                print(f"   📊 '{keyword}': 0 articles")
                
        except Exception as e:
            print(f"   ❌ Error checking keyword '{keyword}': {e}")
            # Try alternative approach with contains operator
            try:
                response = db_manager.supabase.table('articles').select('*').contains('matched_keywords', [keyword]).execute()
                if response.data:
                    articles_by_keyword[keyword] = response.data
                    count = len(response.data)
                    total_articles_to_remove += count
                    print(f"   📊 '{keyword}' (alt method): {count} articles")
                else:
                    print(f"   📊 '{keyword}': 0 articles (alt method)")
            except Exception as e2:
                print(f"   ❌ Alternative method also failed for '{keyword}': {e2}")
    
    print(f"\n📈 Total articles to remove: {total_articles_to_remove}")
    
    if total_articles_to_remove == 0:
        print("✅ No articles found with non-security keywords. Nothing to clean up.")
        return True
    
    # Step 2: Confirm deletion
    print(f"\n⚠️  WARNING: This will permanently delete {total_articles_to_remove} articles!")
    print("These articles contain general crypto keywords that are not security-related.")
    
    confirm = input("\nDo you want to proceed? (yes/no): ").lower().strip()
    if confirm != 'yes':
        print("❌ Operation cancelled by user")
        return False
    
    # Step 3: Delete articles
    print("\n🗑️  Step 2: Deleting articles with non-security keywords...")
    
    deleted_count = 0
    errors = []
    
    for keyword, articles in articles_by_keyword.items():
        print(f"\n   🔄 Processing keyword '{keyword}' ({len(articles)} articles)...")
        
        for article in articles:
            try:
                # Delete the article
                response = db_manager.supabase.table('articles').delete().eq('id', article['id']).execute()
                
                if response.data:
                    deleted_count += 1
                    if deleted_count % 10 == 0:  # Progress indicator
                        print(f"      ✅ Deleted {deleted_count} articles...")
                else:
                    errors.append(f"Failed to delete article {article['id']}: {article['title'][:50]}")
                    
            except Exception as e:
                errors.append(f"Error deleting article {article['id']}: {e}")
    
    # Step 4: Report results
    print(f"\n📊 Cleanup Results:")
    print(f"   ✅ Successfully deleted: {deleted_count} articles")
    
    if errors:
        print(f"   ❌ Errors encountered: {len(errors)}")
        for error in errors[:5]:  # Show first 5 errors
            print(f"      - {error}")
        if len(errors) > 5:
            print(f"      ... and {len(errors) - 5} more errors")
    
    # Step 5: Verify cleanup
    print(f"\n🔍 Step 3: Verifying cleanup...")
    
    remaining_articles = 0
    for keyword in keywords_to_remove:
        try:
            response = db_manager.supabase.table('articles').select('id').contains('matched_keywords', [keyword]).execute()
            count = len(response.data) if response.data else 0
            remaining_articles += count
            if count > 0:
                print(f"   ⚠️  '{keyword}': {count} articles still remain")
            else:
                print(f"   ✅ '{keyword}': cleaned up successfully")
        except Exception as e:
            print(f"   ❌ Error verifying keyword '{keyword}': {e}")
    
    # Step 6: Get final statistics
    print(f"\n📈 Final Statistics:")
    try:
        response = db_manager.supabase.table('articles').select('id').execute()
        total_remaining = len(response.data) if response.data else 0
        print(f"   📊 Total articles remaining: {total_remaining}")
        
        # Get keyword distribution
        response = db_manager.supabase.rpc('get_keyword_counts').execute()
        if response.data:
            print(f"   📊 Active keywords: {len(response.data)}")
            print("   🔝 Top keywords:")
            for item in response.data[:5]:
                print(f"      - {item['keyword']}: {item['count']} articles")
    except Exception as e:
        print(f"   ❌ Error getting final statistics: {e}")
    
    if remaining_articles == 0:
        print(f"\n🎉 Cleanup completed successfully!")
        print(f"   ✅ Removed {deleted_count} articles with non-security keywords")
        print(f"   ✅ Database now contains only security-related articles")
    else:
        print(f"\n⚠️  Cleanup partially completed")
        print(f"   ✅ Removed {deleted_count} articles")
        print(f"   ⚠️  {remaining_articles} articles with non-security keywords still remain")
    
    return remaining_articles == 0

def main():
    """Main function"""
    print("🧹 Non-Security Keywords Cleanup Tool")
    print("This tool removes general crypto keywords and their articles")
    print("Keeping only security-related content in the database")
    print()
    
    success = cleanup_non_security_keywords()
    
    if success:
        print("\n✅ Cleanup completed successfully!")
        print("💡 Refresh your dashboard to see the updated article list")
    else:
        print("\n❌ Cleanup encountered issues")
        print("💡 Check the error messages above and try again if needed")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())