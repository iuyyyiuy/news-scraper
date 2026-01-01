#!/usr/bin/env python3
"""
Phase 3 Integration Test - Complete system test with enhanced parser and reporting.
Tests the integration of all Phase 3 enhancements together.
"""

import sys
import os
import time
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.core.parser import HTMLParser
from scraper.core.session_reporter import SessionReporter

def test_phase3_integration():
    """Test complete Phase 3 integration with enhanced parser and session reporting."""
    
    print("🚀 Phase 3 Integration Test")
    print("=" * 60)
    
    # Initialize enhanced parser with debug mode
    parser = HTMLParser(debug_mode=True)
    
    # Initialize session reporter
    reporter = SessionReporter("phase3_integration_test")
    
    print(f"📊 Started session: {reporter.session_id}")
    print(f"🔧 Parser debug mode: {parser.debug_mode}")
    
    # Test articles with various structures and challenges
    test_articles = [
        {
            "name": "Standard BlockBeats Article",
            "html": """
            <html>
            <head>
                <title>BlockBeats - 市场分析</title>
                <meta property="og:title" content="加密货币市场深度分析">
                <meta property="article:published_time" content="2024-12-20T16:00:00Z">
                <meta name="author" content="市场分析师">
            </head>
            <body>
                <article>
                    <h1 class="article-title">加密货币市场深度分析</h1>
                    <div class="article-meta">
                        <span class="author">市场分析师</span>
                        <time datetime="2024-12-20T16:00:00Z">2024-12-20 16:00</time>
                    </div>
                    <div class="article-content">
                        <p>BlockBeats 消息，本周加密货币市场表现强劲，主要数字资产价格普遍上涨。比特币重新站稳关键支撑位，以太坊也显示出积极的技术信号。</p>
                        <p>分析师指出，机构投资者的持续流入和监管环境的逐步明朗是推动市场上涨的主要因素。预计短期内市场将继续保持乐观态势。</p>
                    </div>
                </article>
            </body>
            </html>
            """,
            "url": "https://theblockbeats.info/news/analysis-123",
            "source": "BlockBeats"
        },
        {
            "name": "Jinse Flash News",
            "html": """
            <html>
            <head>
                <title>金色财经 - 快讯</title>
            </head>
            <body>
                <div class="flash-top">
                    <h3>🚨 重要快讯</h3>
                    <p>BlockBeats 消息，某大型交易所宣布将新增多个DeFi代币的交易支持，此举预计将进一步推动DeFi生态的发展。</p>
                    <span class="time">16:30</span>
                </div>
            </body>
            </html>
            """,
            "url": "https://jinse.com/flash/456",
            "source": "Jinse"
        },
        {
            "name": "Challenging Structure",
            "html": """
            <html>
            <head>
                <title>Crypto News</title>
                <meta property="og:description" content="BlockBeats 消息，NFT市场出现新的发展趋势，艺术类NFT交易量显著增长。">
            </head>
            <body>
                <div class="content-wrapper">
                    <div class="news-item">
                        <h2>NFT市场新趋势</h2>
                        <div class="content-text">
                            BlockBeats 消息，NFT市场出现新的发展趋势，艺术类NFT交易量显著增长。收藏家和投资者对高质量数字艺术品的需求持续上升。
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """,
            "url": "https://cryptonews.com/nft-trends",
            "source": "CryptoNews"
        },
        {
            "name": "Broken Structure (Expected to Fail)",
            "html": """
            <html>
            <body>
                <div>
                    <span>Some text</span>
                    <div>Random content without clear structure</div>
                </div>
            </body>
            </html>
            """,
            "url": "https://broken.com/test",
            "source": "BrokenSite"
        }
    ]
    
    print(f"\n🔄 Processing {len(test_articles)} test articles...")
    
    successful_articles = []
    
    for i, test_article in enumerate(test_articles, 1):
        print(f"\n📄 Article {i}: {test_article['name']}")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            # Parse the article
            article = parser.parse_article(
                test_article['html'],
                test_article['url'],
                test_article['source']
            )
            
            processing_time = time.time() - start_time
            
            # Record successful attempt
            reporter.record_attempt(
                url=test_article['url'],
                source=test_article['source'],
                success=True,
                title=article.title,
                content_length=len(article.body_text),
                processing_time=processing_time
            )
            
            successful_articles.append(article)
            
            print(f"✅ SUCCESS ({processing_time:.3f}s)")
            print(f"   Title: {article.title}")
            print(f"   Author: {article.author or 'N/A'}")
            print(f"   Date: {article.publication_date or 'N/A'}")
            print(f"   Content: {len(article.body_text)} chars")
            print(f"   Preview: {article.body_text[:80]}...")
            
            # Simulate storage
            reporter.record_storage(test_article['source'], 1)
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            # Record failed attempt
            reporter.record_attempt(
                url=test_article['url'],
                source=test_article['source'],
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
            
            print(f"❌ FAILED ({processing_time:.3f}s): {e}")
    
    # Wait a moment to show session duration
    time.sleep(1)
    
    # Finalize session and generate report
    print(f"\n📊 Finalizing session...")
    final_report = reporter.finalize_session()
    
    # Print detailed session report
    reporter.print_summary()
    
    # Test enhanced features
    print(f"\n🔍 Testing Enhanced Features:")
    
    # Check debug files
    debug_dir = Path("debug_html")
    if debug_dir.exists():
        debug_files = list(debug_dir.glob("*.html"))
        print(f"✅ Debug HTML capture: {len(debug_files)} files saved")
    else:
        print(f"❌ Debug HTML capture: No files found")
    
    # Check session reports
    reports_dir = Path("session_reports")
    if reports_dir.exists():
        report_files = list(reports_dir.glob(f"{reporter.session_id}_report.json"))
        print(f"✅ Session reporting: {len(report_files)} report files created")
    else:
        print(f"❌ Session reporting: No report files found")
    
    # Performance analysis
    print(f"\n⚡ Performance Analysis:")
    if final_report.summary:
        avg_time = final_report.summary.get('avg_processing_time_seconds', 0)
        success_rate = final_report.summary.get('success_rate_percent', 0)
        print(f"   Average processing time: {avg_time:.3f}s")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Articles processed: {final_report.summary.get('successful_extractions', 0)}")
        print(f"   Articles stored: {final_report.summary.get('articles_stored', 0)}")
    
    # Final assessment
    print(f"\n🎯 Phase 3 Integration Assessment:")
    
    success_count = len(successful_articles)
    total_count = len(test_articles)
    success_rate = (success_count / total_count) * 100
    
    features_working = []
    
    # Check each Phase 3 feature
    if debug_dir.exists() and list(debug_dir.glob("*.html")):
        features_working.append("✅ HTML Debug Capture")
    else:
        features_working.append("❌ HTML Debug Capture")
    
    if reports_dir.exists() and list(reports_dir.glob("*_report.json")):
        features_working.append("✅ Session Reporting")
    else:
        features_working.append("❌ Session Reporting")
    
    if success_rate >= 75:  # Expecting 3/4 to succeed (excluding broken test)
        features_working.append("✅ Parser Resilience")
    else:
        features_working.append("❌ Parser Resilience")
    
    print(f"\n📋 Feature Status:")
    for feature in features_working:
        print(f"   {feature}")
    
    all_features_working = all("✅" in feature for feature in features_working)
    
    if all_features_working and success_rate >= 75:
        print(f"\n🎉 PHASE 3 INTEGRATION: SUCCESS!")
        print(f"   All enhanced features are working correctly")
        print(f"   Parser success rate: {success_rate:.1f}%")
        print(f"   System is ready for production use")
    else:
        print(f"\n⚠️  PHASE 3 INTEGRATION: NEEDS ATTENTION")
        print(f"   Some features may need additional work")
        print(f"   Parser success rate: {success_rate:.1f}%")
    
    print(f"\n✅ Phase 3 Integration Test Complete!")
    return all_features_working and success_rate >= 75

if __name__ == "__main__":
    test_phase3_integration()