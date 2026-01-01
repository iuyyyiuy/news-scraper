#!/usr/bin/env python3
"""
Test AI Duplicate Detection
Test if the DeepSeek AI is properly detecting duplicate articles
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.core.ai_content_analyzer import AIContentAnalyzer
from scraper.core.database_manager import DatabaseManager

def test_ai_duplicate_detection():
    """Test AI duplicate detection functionality"""
    
    print("🧪 Testing AI Duplicate Detection")
    print("=" * 50)
    
    try:
        # Initialize AI analyzer
        print("1. Initializing AI Content Analyzer...")
        ai_analyzer = AIContentAnalyzer()
        print("✅ AI Content Analyzer initialized successfully")
        
        # Test duplicate detection with sample articles
        print("\n2. Testing duplicate detection...")
        
        # Sample articles - one is clearly a duplicate
        new_article = {
            'title': '老牌国产公链NDO两位创始人撕逼，财务不透明为核心原因',
            'content': '老牌国产公链NDO两位创始人撕逼，财务不透明为核心原因，项目方资金管理存在问题'
        }
        
        existing_articles = [
            {
                'title': '老牌国产公链NDO两位创始人撕逼，财务不透明为核心原因',
                'content': '老牌国产公链NDO两位创始人撕逼，财务不透明为核心原因，项目方资金管理存在问题'
            },
            {
                'title': 'Bitcoin价格突破新高',
                'content': 'Bitcoin今日价格突破历史新高，市场情绪乐观'
            }
        ]
        
        # Test duplicate detection
        result = ai_analyzer.detect_duplicate_content(new_article, existing_articles)
        
        print(f"📊 Duplicate Detection Result:")
        print(f"   Is Duplicate: {result['is_duplicate']}")
        print(f"   Similarity Score: {result['similarity_score']}")
        print(f"   Duplicate Type: {result.get('duplicate_type', 'None')}")
        print(f"   Reason: {result.get('reason', result.get('explanation', 'No reason provided'))}")
        
        if result['is_duplicate']:
            print("✅ AI correctly detected duplicate article")
        else:
            print("❌ AI failed to detect obvious duplicate")
        
        # Test with non-duplicate
        print("\n3. Testing with non-duplicate article...")
        
        non_duplicate = {
            'title': 'Ethereum升级完成，网络性能提升',
            'content': 'Ethereum网络完成重大升级，交易速度和安全性都有显著提升'
        }
        
        result2 = ai_analyzer.detect_duplicate_content(non_duplicate, existing_articles)
        
        print(f"📊 Non-Duplicate Detection Result:")
        print(f"   Is Duplicate: {result2['is_duplicate']}")
        print(f"   Similarity Score: {result2['similarity_score']}")
        
        if not result2['is_duplicate']:
            print("✅ AI correctly identified non-duplicate article")
        else:
            print("❌ AI incorrectly flagged non-duplicate as duplicate")
        
        # Test with database articles
        print("\n4. Testing with real database articles...")
        
        db_manager = DatabaseManager()
        
        # Get recent articles from database
        result_db = db_manager.supabase.table('articles').select(
            'title, body_text'
        ).order('scraped_at', desc=True).limit(5).execute()
        
        if result_db.data:
            db_articles = []
            for article in result_db.data:
                db_articles.append({
                    'title': article['title'],
                    'content': article.get('body_text', article['title'])
                })
            
            print(f"   Retrieved {len(db_articles)} articles from database")
            
            # Test with first article as "new" article
            if len(db_articles) > 1:
                test_article = db_articles[0]
                comparison_articles = db_articles[1:]
                
                result3 = ai_analyzer.detect_duplicate_content(test_article, comparison_articles)
                
                print(f"📊 Database Article Test:")
                print(f"   Test Article: {test_article['title'][:50]}...")
                print(f"   Is Duplicate: {result3['is_duplicate']}")
                print(f"   Similarity Score: {result3['similarity_score']}")
        
        print("\n" + "=" * 50)
        print("🎯 AI Duplicate Detection Test Complete")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI duplicate detection: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ai_duplicate_detection()