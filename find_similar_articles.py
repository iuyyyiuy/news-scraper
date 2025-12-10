#!/usr/bin/env python3
"""
Advanced Duplicate Detection Tool
Finds similar articles using multiple similarity methods
"""

import sys
import os
sys.path.append('.')

from scraper.core.database_manager import DatabaseManager
import hashlib
import re
from difflib import SequenceMatcher
from datetime import datetime
import json

class SimilarArticleFinder:
    """Advanced tool to find similar/duplicate articles using multiple methods"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.similar_groups = []
        
    def get_all_articles(self):
        """Get all articles from database"""
        try:
            response = self.db_manager.supabase.table('articles').select('*').order('scraped_at', desc=False).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"❌ Error getting articles: {e}")
            return []
    
    def normalize_text(self, text):
        """Normalize text for comparison"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common prefixes/suffixes
        text = re.sub(r'^(BlockBeats\s*消息[，,]\s*\d+\s*月\s*\d+\s*日[，,]\s*)', '', text)
        text = re.sub(r'^(据.*?消息[，,]\s*)', '', text)
        
        # Remove URLs
        text = re.sub(r'https?://[^\s]+', '', text)
        
        # Remove special characters but keep Chinese
        text = re.sub(r'[^\u4e00-\u9fff\w\s]', '', text)
        
        return text.lower().strip()
    
    def calculate_similarity(self, text1, text2):
        """Calculate similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        
        # Normalize texts
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)
        
        if not norm1 or not norm2:
            return 0.0
        
        # Use SequenceMatcher for similarity
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        return similarity * 100
    
    def find_title_similarities(self, articles, threshold=70):
        """Find articles with similar titles"""
        print(f"\n🔍 Finding articles with similar titles (threshold: {threshold}%)...")
        
        similar_groups = []
        processed = set()
        
        for i, article1 in enumerate(articles):
            if article1['id'] in processed:
                continue
                
            similar_group = [article1]
            processed.add(article1['id'])
            
            for j, article2 in enumerate(articles[i+1:], i+1):
                if article2['id'] in processed:
                    continue
                
                similarity = self.calculate_similarity(article1['title'], article2['title'])
                
                if similarity >= threshold:
                    similar_group.append(article2)
                    processed.add(article2['id'])
                    print(f"   📝 Similar titles ({similarity:.1f}%):")
                    print(f"      1: {article1['title'][:80]}...")
                    print(f"      2: {article2['title'][:80]}...")
            
            if len(similar_group) > 1:
                similar_groups.append({
                    'type': 'title_similarity',
                    'articles': similar_group,
                    'similarity': similarity
                })
        
        return similar_groups
    
    def find_content_similarities(self, articles, threshold=80):
        """Find articles with similar content"""
        print(f"\n🔍 Finding articles with similar content (threshold: {threshold}%)...")
        
        similar_groups = []
        processed = set()
        
        for i, article1 in enumerate(articles):
            if article1['id'] in processed:
                continue
                
            similar_group = [article1]
            processed.add(article1['id'])
            
            for j, article2 in enumerate(articles[i+1:], i+1):
                if article2['id'] in processed:
                    continue
                
                similarity = self.calculate_similarity(article1['body_text'], article2['body_text'])
                
                if similarity >= threshold:
                    similar_group.append(article2)
                    processed.add(article2['id'])
                    print(f"   📄 Similar content ({similarity:.1f}%):")
                    print(f"      1: {article1['title'][:60]}...")
                    print(f"      2: {article2['title'][:60]}...")
            
            if len(similar_group) > 1:
                similar_groups.append({
                    'type': 'content_similarity',
                    'articles': similar_group,
                    'similarity': similarity
                })
        
        return similar_groups
    
    def find_exact_duplicates(self, articles):
        """Find exact duplicates using content hashing"""
        print(f"\n🔍 Finding exact duplicates...")
        
        hash_groups = {}
        
        for article in articles:
            # Create hash of normalized content
            normalized = self.normalize_text(article['body_text'])
            content_hash = hashlib.md5(normalized.encode()).hexdigest()
            
            if content_hash not in hash_groups:
                hash_groups[content_hash] = []
            hash_groups[content_hash].append(article)
        
        # Find groups with multiple articles
        duplicate_groups = []
        for content_hash, group in hash_groups.items():
            if len(group) > 1:
                print(f"   🔄 Found {len(group)} exact duplicates:")
                for article in group:
                    print(f"      - {article['title'][:60]}... ({article['date']})")
                
                duplicate_groups.append({
                    'type': 'exact_duplicate',
                    'articles': group,
                    'similarity': 100.0
                })
        
        return duplicate_groups
    
    def find_keyword_pattern_duplicates(self, articles):
        """Find articles that are likely about the same event"""
        print(f"\n🔍 Finding articles about the same events...")
        
        # Group by similar key phrases
        event_groups = {}
        
        for article in articles:
            # Extract key phrases that might indicate the same event
            title = article['title']
            
            # Look for specific patterns
            patterns = [
                r'何一.*微信.*被盗',  # He Yi WeChat hack
                r'Mubarakah.*获利',   # Mubarakah profit
                r'CZ.*何一.*微信',    # CZ He Yi WeChat
                r'Bunni.*攻击.*ETH',  # Bunni attack
                r'CLARITY.*法案',     # CLARITY Act
                r'Coinbase.*溢价.*指数', # Coinbase premium index
            ]
            
            for pattern in patterns:
                if re.search(pattern, title):
                    if pattern not in event_groups:
                        event_groups[pattern] = []
                    event_groups[pattern].append(article)
                    break
        
        # Find groups with multiple articles
        event_duplicate_groups = []
        for pattern, group in event_groups.items():
            if len(group) > 1:
                print(f"   🎯 Found {len(group)} articles about same event:")
                for article in group:
                    print(f"      - {article['title'][:70]}... ({article['date']})")
                
                event_duplicate_groups.append({
                    'type': 'same_event',
                    'articles': group,
                    'pattern': pattern,
                    'similarity': 90.0
                })
        
        return event_duplicate_groups
    
    def analyze_all_similarities(self):
        """Run comprehensive similarity analysis"""
        print("🔍 Advanced Duplicate Detection Analysis")
        print("="*60)
        
        articles = self.get_all_articles()
        if not articles:
            print("❌ No articles found")
            return []
        
        print(f"📊 Analyzing {len(articles)} articles for similarities...")
        
        all_similar_groups = []
        
        # 1. Find exact duplicates
        exact_dupes = self.find_exact_duplicates(articles)
        all_similar_groups.extend(exact_dupes)
        
        # 2. Find title similarities
        title_sims = self.find_title_similarities(articles, threshold=70)
        all_similar_groups.extend(title_sims)
        
        # 3. Find content similarities
        content_sims = self.find_content_similarities(articles, threshold=80)
        all_similar_groups.extend(content_sims)
        
        # 4. Find same event articles
        event_dupes = self.find_keyword_pattern_duplicates(articles)
        all_similar_groups.extend(event_dupes)
        
        return all_similar_groups
    
    def delete_article(self, article_id, reason):
        """Delete an article from database"""
        try:
            response = self.db_manager.supabase.table('articles').delete().eq('id', article_id).execute()
            if response.data:
                print(f"   ✅ Deleted: {reason}")
                return True
            else:
                print(f"   ❌ Failed to delete: {reason}")
                return False
        except Exception as e:
            print(f"   ❌ Error deleting: {e}")
            return False
    
    def remove_duplicates(self, similar_groups, dry_run=True):
        """Remove duplicate articles, keeping the oldest one"""
        print(f"\n🧹 Removing Duplicates (Mode: {'DRY RUN' if dry_run else 'LIVE'})")
        print("="*50)
        
        total_removed = 0
        
        for i, group in enumerate(similar_groups, 1):
            articles = group['articles']
            if len(articles) <= 1:
                continue
            
            print(f"\n{i}. {group['type'].upper()} - {len(articles)} articles:")
            
            # Sort by scraped_at to keep the oldest
            articles.sort(key=lambda x: x['scraped_at'])
            
            keep_article = articles[0]  # Keep the oldest
            remove_articles = articles[1:]  # Remove the newer ones
            
            print(f"   ✅ KEEPING (oldest): {keep_article['title'][:60]}... ({keep_article['date']})")
            
            for article in remove_articles:
                print(f"   ❌ REMOVING (newer): {article['title'][:60]}... ({article['date']})")
                
                if not dry_run:
                    if self.delete_article(article['id'], f"Duplicate of {keep_article['id']}"):
                        total_removed += 1
                else:
                    total_removed += 1  # Count for dry run
        
        print(f"\n📊 Summary:")
        print(f"   Similar groups found: {len(similar_groups)}")
        print(f"   Articles to remove: {total_removed}")
        
        if dry_run:
            print(f"   ⚠️  This was a DRY RUN - no articles were deleted")
        else:
            print(f"   ✅ Articles successfully removed: {total_removed}")
        
        return total_removed

def main():
    """Main function"""
    finder = SimilarArticleFinder()
    
    # Run analysis
    similar_groups = finder.analyze_all_similarities()
    
    if not similar_groups:
        print("\n✅ No similar articles found!")
        return
    
    print(f"\n📋 Found {len(similar_groups)} groups of similar articles")
    
    # Ask user what to do
    print("\nChoose action:")
    print("1. Show details only (no deletions)")
    print("2. Dry run (show what would be deleted)")
    print("3. Remove duplicates (actual deletion)")
    
    choice = input("\nEnter choice (1, 2, or 3): ").strip()
    
    if choice == "1":
        print("\n📋 Similar Articles Analysis Complete")
    elif choice == "2":
        finder.remove_duplicates(similar_groups, dry_run=True)
    elif choice == "3":
        confirm = input("⚠️  Are you sure you want to delete duplicate articles? Type 'YES': ").strip()
        if confirm == "YES":
            finder.remove_duplicates(similar_groups, dry_run=False)
        else:
            print("❌ Deletion cancelled")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()