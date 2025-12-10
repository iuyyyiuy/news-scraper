#!/usr/bin/env python3
"""
Test script for AI Content Analyzer with DeepSeek API.
"""

import os
from scraper.core.ai_content_analyzer import AIContentAnalyzer

def test_ai_analyzer():
    """Test the AI content analyzer with sample articles."""
    
    print("=== TESTING AI CONTENT ANALYZER ===")
    
    # Check if API key is available
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY environment variable not set")
        print("Please set your DeepSeek API key:")
        print("export DEEPSEEK_API_KEY='your-api-key-here'")
        return
    
    try:
        # Initialize analyzer
        analyzer = AIContentAnalyzer()
        print("✅ AI Content Analyzer initialized")
        
        # Test case 1: Article that should be relevant to "合规" (compliance)
        print("\n📰 Test 1: Compliance-related article")
        title1 = "USDT获阿布扎比监管认定为「法币参考代币」"
        content1 = "BlockBeats 消息，12 月 10 日，据官方消息，阿布扎比全球市场金融服务监管局（FSRA）已将 USDT 认定为「法币参考代币」（Fiat-Referenced Token），这是该监管机构首次对稳定币进行此类分类。此举标志着 USDT 在阿布扎比获得了正式的监管认可，为其在该地区的合规运营奠定了基础。"
        keywords1 = ["合规", "监管"]
        
        relevance1 = analyzer.analyze_content_relevance(title1, content1, keywords1)
        print(f"   Relevance Score: {relevance1['relevance_score']}/100")
        print(f"   Is Relevant: {relevance1['is_relevant']}")
        print(f"   Explanation: {relevance1['explanation']}")
        
        # Test case 2: Article that should NOT be relevant to "合规" (compliance)
        print("\n📰 Test 2: Non-compliance article (Bitcoin price)")
        title2 = "Coinbase比特币溢价指数已连续8日处于正溢价，暂报0.0121%"
        content2 = "BlockBeats 消息，12 月 10 日，据 Coinglass 数据，Coinbase 比特币溢价指数已连续 8 日处于正溢价，暂报 0.0121%。该指数用于衡量 Coinbase 上的比特币价格相对于全球市场平均价格的差异。"
        keywords2 = ["合规"]
        
        relevance2 = analyzer.analyze_content_relevance(title2, content2, keywords2)
        print(f"   Relevance Score: {relevance2['relevance_score']}/100")
        print(f"   Is Relevant: {relevance2['is_relevant']}")
        print(f"   Explanation: {relevance2['explanation']}")
        
        # Test case 3: Duplicate detection
        print("\n🔍 Test 3: Duplicate detection")
        new_article = {
            'title': title1,
            'content': content1
        }
        
        existing_articles = [
            {
                'title': "USDT在阿布扎比获得监管认可",
                'content': "阿布扎比金融监管局将USDT认定为法币参考代币，这是首次对稳定币进行此类分类，标志着USDT获得正式监管认可。"
            }
        ]
        
        duplicate_check = analyzer.detect_duplicate_content(new_article, existing_articles)
        print(f"   Is Duplicate: {duplicate_check['is_duplicate']}")
        print(f"   Similarity Score: {duplicate_check['similarity_score']}/100")
        print(f"   Explanation: {duplicate_check.get('explanation', 'No explanation available')}")
        
        print("\n✅ AI Content Analyzer test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing AI analyzer: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_analyzer()