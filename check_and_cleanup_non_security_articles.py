#!/usr/bin/env python3
"""
Check and cleanup articles that don't match the security keywords.
This script will:
1. Check current articles in database
2. Identify articles that don't match the 21 security keywords
3. Optionally remove non-matching articles
"""

import logging
from datetime import datetime, timedelta
from scraper.core.database_manager import DatabaseManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityArticleChecker:
    """Check and cleanup articles that don't match security keywords"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        
        # Original 21 security keywords
        self.security_keywords = [
            "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
            "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
            "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
        ]
    
    def check_recent_articles(self, days_back=1):
        """Check recent articles for security keyword matches"""
        print("=" * 60)
        print("CHECKING RECENT ARTICLES FOR SECURITY KEYWORD MATCHES")
        print("=" * 60)
        
        try:
            # Get recent articles from database
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Query recent articles (using scraped_at column)
            response = self.db_manager.supabase.table('articles').select('*').gte('scraped_at', cutoff_date.isoformat()).execute()
            
            if not response.data:
                print("No recent articles found in database")
                return []
            
            articles = response.data
            print(f"Found {len(articles)} recent articles (last {days_back} day(s))")
            
            matching_articles = []
            non_matching_articles = []
            
            for article in articles:
                title = article.get('title', '')
                body_text = article.get('body_text', '')
                full_text = f"{title} {body_text}".lower()
                
                # Check for security keyword matches
                matched_keywords = [kw for kw in self.security_keywords if kw.lower() in full_text]
                
                if matched_keywords:
                    matching_articles.append({
                        'article': article,
                        'matched_keywords': matched_keywords
                    })
                else:
                    non_matching_articles.append(article)
            
            print(f"\n--- ANALYSIS RESULTS ---")
            print(f"Articles matching security keywords: {len(matching_articles)}")
            print(f"Articles NOT matching security keywords: {len(non_matching_articles)}")
            
            if matching_articles:
                print(f"\n--- MATCHING ARTICLES ---")
                for i, match in enumerate(matching_articles[:5]):  # Show first 5
                    article = match['article']
                    keywords = match['matched_keywords']
                    print(f"{i+1}. {article.get('title', '')[:60]}...")
                    print(f"   Keywords: {', '.join(keywords)}")
                    print(f"   Source: {article.get('source', '')}")
                    print(f"   Date: {article.get('publication_date', '')}")
            
            if non_matching_articles:
                print(f"\n--- NON-MATCHING ARTICLES (SHOULD BE REMOVED) ---")
                for i, article in enumerate(non_matching_articles[:10]):  # Show first 10
                    print(f"{i+1}. {article.get('title', '')[:60]}...")
                    print(f"   Source: {article.get('source', '')}")
                    print(f"   Date: {article.get('publication_date', '')}")
                    print(f"   ID: {article.get('id', '')}")
                
                if len(non_matching_articles) > 10:
                    print(f"   ... and {len(non_matching_articles) - 10} more")
            
            return non_matching_articles
            
        except Exception as e:
            print(f"❌ Error checking articles: {e}")
            return []
    
    def remove_non_matching_articles(self, articles_to_remove):
        """Remove articles that don't match security keywords"""
        if not articles_to_remove:
            print("No articles to remove")
            return
        
        print(f"\n--- REMOVING {len(articles_to_remove)} NON-MATCHING ARTICLES ---")
        
        removed_count = 0
        failed_count = 0
        
        for article in articles_to_remove:
            try:
                article_id = article.get('id')
                title = article.get('title', '')[:50]
                
                # Delete from database
                response = self.db_manager.supabase.table('articles').delete().eq('id', article_id).execute()
                
                if response.data:
                    removed_count += 1
                    print(f"✅ Removed: {title}...")
                else:
                    failed_count += 1
                    print(f"❌ Failed to remove: {title}...")
                    
            except Exception as e:
                failed_count += 1
                print(f"❌ Error removing article {article.get('id', '')}: {e}")
        
        print(f"\n--- CLEANUP SUMMARY ---")
        print(f"Successfully removed: {removed_count}")
        print(f"Failed to remove: {failed_count}")
        print(f"Total processed: {len(articles_to_remove)}")
    
    def run_check_and_cleanup(self, days_back=1, auto_remove=False):
        """Run complete check and cleanup process"""
        print("🔍 SECURITY ARTICLE CHECKER")
        print("=" * 60)
        print(f"Security keywords: {', '.join(self.security_keywords[:5])}...")
        print(f"Checking articles from last {days_back} day(s)")
        print("=" * 60)
        
        # Check articles
        non_matching_articles = self.check_recent_articles(days_back)
        
        if not non_matching_articles:
            print("\n✅ All recent articles match security keywords - no cleanup needed!")
            return
        
        # Ask user for confirmation unless auto_remove is True
        if not auto_remove:
            print(f"\n⚠️  Found {len(non_matching_articles)} articles that don't match security keywords")
            response = input("Do you want to remove these articles? (y/N): ").strip().lower()
            
            if response in ['y', 'yes']:
                self.remove_non_matching_articles(non_matching_articles)
            else:
                print("Cleanup cancelled - articles remain in database")
        else:
            self.remove_non_matching_articles(non_matching_articles)

def main():
    """Main function"""
    import sys
    
    checker = SecurityArticleChecker()
    
    # Check command line arguments
    auto_remove = '--auto-remove' in sys.argv
    days_back = 1
    
    if '--days' in sys.argv:
        try:
            days_index = sys.argv.index('--days')
            days_back = int(sys.argv[days_index + 1])
        except (IndexError, ValueError):
            print("Invalid --days argument, using default of 1 day")
    
    try:
        checker.run_check_and_cleanup(days_back=days_back, auto_remove=auto_remove)
    except KeyboardInterrupt:
        print("\n🛑 Cleanup interrupted by user")
    except Exception as e:
        print(f"\n❌ Cleanup failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Usage:")
    print("  python check_and_cleanup_non_security_articles.py                    # Check and ask for confirmation")
    print("  python check_and_cleanup_non_security_articles.py --auto-remove     # Automatically remove non-matching articles")
    print("  python check_and_cleanup_non_security_articles.py --days 3          # Check last 3 days")
    print()
    main()