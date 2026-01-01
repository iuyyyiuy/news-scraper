#!/usr/bin/env python3
"""
Comprehensive test for parser resilience with various HTML structures.
Tests the parser's ability to handle different website layouts and structures.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.core.parser import HTMLParser

def test_parser_resilience():
    """Test parser resilience with 5 different HTML structures."""
    
    print("🧪 Testing Parser Resilience")
    print("=" * 60)
    
    # Initialize parser with debug mode
    parser = HTMLParser(debug_mode=True)
    
    test_cases = []
    
    # Test Case 1: Standard news website structure
    test_cases.append({
        "name": "Standard News Website",
        "html": """
        <html>
        <head>
            <title>Breaking News: Market Update</title>
            <meta property="og:title" content="Market Update: Crypto Surge">
            <meta property="article:published_time" content="2024-12-20T15:30:00Z">
            <meta name="author" content="Financial Reporter">
        </head>
        <body>
            <article>
                <header>
                    <h1 class="article-title">Market Update: Crypto Surge</h1>
                    <div class="meta">
                        <span class="author">Financial Reporter</span>
                        <time datetime="2024-12-20T15:30:00Z">Dec 20, 2024</time>
                    </div>
                </header>
                <div class="article-content">
                    <p>BlockBeats 消息，加密货币市场今日出现大幅上涨。比特币价格突破重要阻力位，带动整个市场情绪转暖。</p>
                    <p>分析师认为，这次上涨主要受到机构投资者增持和监管环境改善的推动。</p>
                </div>
            </article>
        </body>
        </html>
        """,
        "url": "https://news.com/crypto-surge",
        "expected_success": True
    })
    
    # Test Case 2: Blog-style layout
    test_cases.append({
        "name": "Blog-style Layout",
        "html": """
        <html>
        <head>
            <title>DeFi Analysis | Crypto Blog</title>
            <meta name="description" content="BlockBeats 消息，DeFi协议锁仓量创新高，显示市场对去中心化金融的信心持续增强。">
        </head>
        <body>
            <div class="container">
                <div class="post">
                    <h2 class="post-title">DeFi协议锁仓量创新高</h2>
                    <div class="post-meta">
                        <span>作者：DeFi分析师</span>
                        <span>2024-12-20</span>
                    </div>
                    <div class="post-content">
                        <p>BlockBeats 消息，DeFi协议锁仓量创新高，显示市场对去中心化金融的信心持续增强。</p>
                        <p>主要协议如Uniswap、Aave等都出现了显著增长。</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """,
        "url": "https://blog.com/defi-analysis",
        "expected_success": True
    })
    
    # Test Case 3: Flash news format (minimal structure)
    test_cases.append({
        "name": "Flash News Format",
        "html": """
        <html>
        <head>
            <title>Flash: 重要消息</title>
        </head>
        <body>
            <div class="flash-container">
                <div class="flash-item">
                    <h3>🚨 重要消息</h3>
                    <p>BlockBeats 消息，某知名交易所宣布支持新的加密货币交易对，预计将提升市场流动性。</p>
                    <span class="time">18:30</span>
                </div>
            </div>
        </body>
        </html>
        """,
        "url": "https://flash.com/news-1",
        "expected_success": True
    })
    
    # Test Case 4: Social media style (challenging structure)
    test_cases.append({
        "name": "Social Media Style",
        "html": """
        <html>
        <head>
            <title>Crypto Discussion</title>
            <meta property="og:description" content="BlockBeats 消息，社区讨论显示投资者对即将到来的升级充满期待。">
        </head>
        <body>
            <div class="feed">
                <div class="post-card">
                    <div class="user-info">
                        <span class="username">@crypto_analyst</span>
                        <span class="timestamp">2小时前</span>
                    </div>
                    <div class="post-text">
                        BlockBeats 消息，社区讨论显示投资者对即将到来的升级充满期待。技术分析表明价格可能突破关键阻力位。
                    </div>
                    <div class="engagement">
                        <span>👍 125</span>
                        <span>💬 45</span>
                        <span>🔄 78</span>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """,
        "url": "https://social.com/post-123",
        "expected_success": True
    })
    
    # Test Case 5: Minimal/broken structure (stress test)
    test_cases.append({
        "name": "Minimal Structure (Stress Test)",
        "html": """
        <html>
        <body>
            <div>
                <span>新闻标题</span>
                <div>
                    BlockBeats 消息，这是一个结构很简单的页面，测试解析器的容错能力。
                    内容可能分布在不同的标签中。
                </div>
                <small>来源：测试网站</small>
            </div>
        </body>
        </html>
        """,
        "url": "https://minimal.com/test",
        "expected_success": False  # This one might fail, which is acceptable
    })
    
    # Run all test cases
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📄 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            article = parser.parse_article(
                test_case['html'], 
                test_case['url'], 
                "test.com"
            )
            
            success = True
            print(f"✅ SUCCESS")
            print(f"   Title: {article.title}")
            print(f"   Author: {article.author or 'N/A'}")
            print(f"   Date: {article.publication_date or 'N/A'}")
            print(f"   Body length: {len(article.body_text)} chars")
            print(f"   Body preview: {article.body_text[:100]}...")
            
        except Exception as e:
            success = False
            print(f"❌ FAILED: {e}")
        
        results.append({
            "name": test_case['name'],
            "success": success,
            "expected": test_case['expected_success']
        })
    
    # Calculate success rate
    print(f"\n📊 Results Summary")
    print("=" * 60)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    expected_successes = sum(1 for r in results if r['expected'])
    
    success_rate = (successful_tests / total_tests) * 100
    expected_rate = (expected_successes / total_tests) * 100
    
    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Expected success rate: {expected_rate:.1f}%")
    
    # Detailed results
    print(f"\n📋 Detailed Results:")
    for result in results:
        status = "✅" if result['success'] else "❌"
        expected = "(expected)" if result['expected'] else "(stress test)"
        print(f"  {status} {result['name']} {expected}")
    
    # Check debug files
    debug_dir = Path("debug_html")
    if debug_dir.exists():
        debug_files = list(debug_dir.glob("*.html"))
        failed_tests = [r for r in results if not r['success']]
        print(f"\n🔍 Debug files created: {len(debug_files)}")
        print(f"   Failed tests: {len(failed_tests)}")
    
    # Final assessment
    print(f"\n🎯 Assessment:")
    if success_rate >= 80:
        print(f"✅ EXCELLENT: {success_rate:.1f}% success rate meets the >80% target!")
    elif success_rate >= 60:
        print(f"⚠️  GOOD: {success_rate:.1f}% success rate is acceptable but could be improved")
    else:
        print(f"❌ NEEDS IMPROVEMENT: {success_rate:.1f}% success rate is below expectations")
    
    print(f"\n✅ Parser Resilience Test Complete!")
    return success_rate >= 80

if __name__ == "__main__":
    test_parser_resilience()