#!/usr/bin/env python3
"""
AI-Powered Database Cleanup Tool
Uses AI to find duplicates and irrelevant articles, then removes them
"""

import sys
import os
sys.path.append('.')

from scraper.core.database_manager import DatabaseManager
from scraper.core.ai_content_analyzer import AIContentAnalyzer
from datetime import datetime
import json

class AIDatabaseCleanup:
    """AI-powered database cleanup for removing duplicates and irrelevant articles"""
    
    # The 21 security keywords we're filtering for
    SECURITY_KEYWORDS = [
        "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
        "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
        "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
    ]
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        
        # Try to initialize AI analyzer
        try:
            self.ai_analyzer = AIContentAnalyzer()
            self.use_ai = True
            print("✅ AI Content Analyzer initialized")
        except Exception as e:
            print(f"⚠️ AI analyzer not available: {e}")
            print("   Using fallback keyword-based analysis")
            self.ai_analyzer = None
            self.use_ai = False
        
        self.stats = {
            'total_articles': 0,
            'duplicates_found': 0,
            'duplicates_removed': 0,
            'irrelevant_found': 0,
            'irrelevant_removed': 0,
            'errors': 0
        }
    
    def get_all_articles(self):
        """Get all articles from database"""
        try:
            # Get all articles ordered by date (oldest first)
            response = self.db_manager.supabase.table('articles').select('*').order('scraped_at', desc=False).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"❌ Error getting articles: {e}")
            return []
    
    def find_duplicates_ai(self, articles):
        """Find duplicate articles using AI analysis"""
        print("\n🔍 Analyzing articles for duplicates using AI...")
        
        duplicates = []
        processed_articles = []
        
        for i, article in enumerate(articles):
            print(f"   Processing article {i+1}/{len(articles)}: {article['title'][:50]}...")
            
            if not self.use_ai:
                # Fallback: simple hash-based duplicate detection
                article_hash = self._calculate_content_hash(article['body_text'])
                
                for j, processed in enumerate(processed_articles):
                    processed_hash = self._calculate_content_hash(processed['body_text'])
                    if article_hash == processed_hash:
                        duplicates.append({
                            'duplicate': article,
                            'original': processed,
                            'similarity_score': 100.0,
                            'reason': 'Identical content hash'
                        })
                        break
                else:
                    processed_articles.append(article)
            else:
                # AI-based duplicate detection
                try:
                    duplicate_check = self.ai_analyzer.detect_duplicate_content(
                        {'title': article['title'], 'content': article['body_text']},
                        [{'title': p['title'], 'content': p['body_text']} for p in processed_articles]
                    )
                    
                    if duplicate_check['is_duplicate']:
                        # Find which article it's duplicate of
                        most_similar_index = duplicate_check.get('most_similar_index', 0)
                        if most_similar_index is not None and most_similar_index < len(processed_articles):
                            original = processed_articles[most_similar_index]
                        else:
                            original = processed_articles[0] if processed_articles else None
                        
                        if original:
                            duplicates.append({
                                'duplicate': article,
                                'original': original,
                                'similarity_score': duplicate_check['similarity_score'],
                                'reason': duplicate_check.get('explanation', 'AI detected similarity')
                            })
                        else:
                            processed_articles.append(article)
                    else:
                        processed_articles.append(article)
                        
                except Exception as e:
                    print(f"   ⚠️ AI analysis failed for article {i+1}: {e}")
                    self.stats['errors'] += 1
                    processed_articles.append(article)
        
        return duplicates
    
    def find_irrelevant_articles_ai(self, articles):
        """Find articles that aren't actually relevant to security keywords using AI"""
        print("\n🎯 Analyzing articles for relevance using AI...")
        
        irrelevant = []
        
        for i, article in enumerate(articles):
            print(f"   Analyzing relevance {i+1}/{len(articles)}: {article['title'][:50]}...")
            
            # Find which keywords this article matched
            matched_keywords = article.get('matched_keywords', [])
            if isinstance(matched_keywords, str):
                try:
                    matched_keywords = json.loads(matched_keywords)
                except:
                    matched_keywords = [matched_keywords] if matched_keywords else []
            
            if not matched_keywords:
                continue
            
            try:
                if self.use_ai:
                    # AI-based relevance analysis
                    relevance = self.ai_analyzer.analyze_content_relevance(
                        article['title'],
                        article['body_text'],
                        matched_keywords
                    )
                    
                    # Consider irrelevant if AI scores it below 40 or explicitly says not relevant
                    if not relevance.get('is_relevant', True) or relevance.get('relevance_score', 100) < 40:
                        irrelevant.append({
                            'article': article,
                            'matched_keywords': matched_keywords,
                            'relevance_score': relevance.get('relevance_score', 0),
                            'reason': relevance.get('explanation', 'AI determined not relevant'),
                            'ai_analysis': True
                        })
                else:
                    # Fallback: keyword frequency analysis
                    text = (article['title'] + ' ' + article['body_text']).lower()
                    keyword_count = sum(text.count(kw.lower()) for kw in matched_keywords)
                    
                    # Consider irrelevant if very few keyword matches
                    if keyword_count <= 1:
                        irrelevant.append({
                            'article': article,
                            'matched_keywords': matched_keywords,
                            'relevance_score': keyword_count * 20,
                            'reason': f'Only {keyword_count} keyword occurrences found',
                            'ai_analysis': False
                        })
                        
            except Exception as e:
                print(f"   ⚠️ Relevance analysis failed for article {i+1}: {e}")
                self.stats['errors'] += 1
        
        return irrelevant
    
    def delete_article(self, article_id, reason):
        """Delete an article from the database"""
        try:
            response = self.db_manager.supabase.table('articles').delete().eq('id', article_id).execute()
            if response.data:
                print(f"   ✅ Deleted: {reason}")
                return True
            else:
                print(f"   ❌ Failed to delete: {reason}")
                return False
        except Exception as e:
            print(f"   ❌ Error deleting article: {e}")
            return False
    
    def _calculate_content_hash(self, content):
        """Calculate hash for duplicate detection"""
        import hashlib
        normalized = ''.join(content.lower().split())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def run_cleanup(self, dry_run=True):
        """Run the complete cleanup process"""
        print("🧹 AI-Powered Database Cleanup")
        print("="*50)
        print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will delete articles)'}")
        print(f"AI Analysis: {'ENABLED' if self.use_ai else 'FALLBACK MODE'}")
        print()
        
        # Get all articles
        articles = self.get_all_articles()
        self.stats['total_articles'] = len(articles)
        
        if not articles:
            print("❌ No articles found in database")
            return
        
        print(f"📊 Found {len(articles)} articles to analyze")
        
        # Step 1: Find duplicates
        duplicates = self.find_duplicates_ai(articles)
        self.stats['duplicates_found'] = len(duplicates)
        
        print(f"\n📋 Duplicate Analysis Results:")
        print(f"   Found {len(duplicates)} duplicate articles")
        
        if duplicates:
            print("\n🔍 Duplicate Articles Found:")
            for i, dup in enumerate(duplicates, 1):
                print(f"\n   {i}. DUPLICATE:")
                print(f"      Title: {dup['duplicate']['title'][:80]}...")
                print(f"      Date: {dup['duplicate']['date']}")
                print(f"      Similarity: {dup['similarity_score']:.1f}%")
                print(f"      Reason: {dup['reason']}")
                print(f"   ORIGINAL:")
                print(f"      Title: {dup['original']['title'][:80]}...")
                print(f"      Date: {dup['original']['date']}")
                
                if not dry_run:
                    # Delete the newer article (duplicate)
                    if self.delete_article(dup['duplicate']['id'], f"Duplicate of {dup['original']['id']}"):
                        self.stats['duplicates_removed'] += 1
        
        # Step 2: Find irrelevant articles
        # Remove duplicates from analysis to avoid analyzing deleted articles
        remaining_articles = [a for a in articles if not any(d['duplicate']['id'] == a['id'] for d in duplicates)]
        
        irrelevant = self.find_irrelevant_articles_ai(remaining_articles)
        self.stats['irrelevant_found'] = len(irrelevant)
        
        print(f"\n📋 Relevance Analysis Results:")
        print(f"   Found {len(irrelevant)} irrelevant articles")
        
        if irrelevant:
            print("\n🎯 Irrelevant Articles Found:")
            for i, irr in enumerate(irrelevant, 1):
                article = irr['article']
                print(f"\n   {i}. IRRELEVANT:")
                print(f"      Title: {article['title'][:80]}...")
                print(f"      Keywords: {irr['matched_keywords']}")
                print(f"      Relevance Score: {irr['relevance_score']}/100")
                print(f"      Reason: {irr['reason']}")
                
                if not dry_run:
                    if self.delete_article(article['id'], f"Irrelevant (score: {irr['relevance_score']})"):
                        self.stats['irrelevant_removed'] += 1
        
        # Print summary
        print(f"\n📊 Cleanup Summary:")
        print(f"   Total articles analyzed: {self.stats['total_articles']}")
        print(f"   Duplicates found: {self.stats['duplicates_found']}")
        print(f"   Duplicates removed: {self.stats['duplicates_removed']}")
        print(f"   Irrelevant found: {self.stats['irrelevant_found']}")
        print(f"   Irrelevant removed: {self.stats['irrelevant_removed']}")
        print(f"   Errors encountered: {self.stats['errors']}")
        
        total_removed = self.stats['duplicates_removed'] + self.stats['irrelevant_removed']
        remaining = self.stats['total_articles'] - total_removed
        
        print(f"\n🎯 Final Result:")
        print(f"   Articles remaining: {remaining}")
        print(f"   Articles removed: {total_removed}")
        print(f"   Database quality improved: {(total_removed/max(self.stats['total_articles'], 1)*100):.1f}%")
        
        if dry_run:
            print(f"\n⚠️  This was a DRY RUN - no articles were actually deleted")
            print(f"   Run with dry_run=False to perform actual cleanup")

def main():
    """Main function"""
    cleanup = AIDatabaseCleanup()
    
    print("Choose cleanup mode:")
    print("1. Dry run (analyze only, no deletions)")
    print("2. Live run (will actually delete articles)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "2":
        confirm = input("⚠️  Are you sure you want to delete articles? Type 'YES' to confirm: ").strip()
        if confirm == "YES":
            cleanup.run_cleanup(dry_run=False)
        else:
            print("❌ Cleanup cancelled")
    else:
        cleanup.run_cleanup(dry_run=True)

if __name__ == "__main__":
    main()