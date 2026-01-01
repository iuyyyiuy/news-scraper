#!/usr/bin/env python3
"""
Test script for enhanced parser functionality.
Tests the improved error handling, debugging capabilities, and fallback strategies.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.core.parser import HTMLParser
from scraper.core.models import Article

def test_enhanced_parser():
    """Test the enhanced parser with various HTML structures."""
    
    print("🧪 Testing Enhanced HTML Parser")
    print("=" * 50)
    
    # Test with debug mode enabled
    parser = HTMLParser(debug_mode=True)
    
    # Test Case 1: Standard article structure
    print("\n📄 Test Case 1: Standard Article Structure")
    html1 = """
    <html>
    <head>
        <title>Test Article - News Site</title>
        <meta property="og:title" content="Test Article Title">
        <meta property="og:description" content="This is a test article description">
        <meta property="article:published_time" content="2024-12-20T10:30:00Z">
        <meta name="author" content="Test Author">
    </head>
    <body>
        <article>
            <h1 class="article-title">Test Article Title</h1>
            <div class="article-meta">
                <span class="author">Test Author</span>
                <time datetime="2024-12-20T10:30:00Z">2024-12-20 10:30</time>
            </div>
            <div class="article-content">
                <p>BlockBeats 消息，这是一篇测试文章的内容。文章包含了足够的文本来测试解析器的功能。</p>
                <p>这是第二段内容，用来验证多段落的处理。</p>
            </div>
        </article>
    </body>
    </html>
    """
    
    try:
        article1 = parser.parse_article(html1, "https://test.com/article1", "test.com")
        print(f"✅ Title: {article1.title}")
        print(f"✅ Author: {article1.author}")
        print(f"✅ Date: {article1.publication_date}")
        print(f"✅ Body: {article1.body_text[:100]}...")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test Case 2: Missing primary selectors (fallback test)
    print("\n📄 Test Case 2: Missing Primary Selectors (Fallback Test)")
    html2 = """
    <html>
    <head>
        <title>Fallback Test Article</title>
        <meta property="og:title" content="Fallback Article Title">
        <meta name="description" content="BlockBeats 消息，这是通过meta标签提取的内容。测试fallback机制是否正常工作。">
    </head>
    <body>
        <div class="content">
            <h2>Fallback Article Title</h2>
            <p>BlockBeats 消息，这是通过fallback机制提取的内容。</p>
        </div>
    </body>
    </html>
    """
    
    try:
        article2 = parser.parse_article(html2, "https://test.com/article2", "test.com")
        print(f"✅ Title: {article2.title}")
        print(f"✅ Body: {article2.body_text[:100]}...")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test Case 3: Flash news structure
    print("\n📄 Test Case 3: Flash News Structure")
    html3 = """
    <html>
    <head>
        <title>Flash News</title>
    </head>
    <body>
        <div class="flash-top">
            <h3>Flash: 重要新闻快讯</h3>
            <p>BlockBeats 消息，这是一条快讯内容，通常比较简短。</p>
        </div>
    </body>
    </html>
    """
    
    try:
        article3 = parser.parse_article(html3, "https://test.com/flash1", "test.com")
        print(f"✅ Title: {article3.title}")
        print(f"✅ Body: {article3.body_text}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test Case 4: Malformed HTML (should trigger debug save)
    print("\n📄 Test Case 4: Malformed HTML (Debug Test)")
    html4 = """
    <html>
    <head>
        <title>Broken Article</title>
    </head>
    <body>
        <div>
            <!-- No clear title or content structure -->
            <span>Some random text</span>
        </div>
    </body>
    </html>
    """
    
    try:
        article4 = parser.parse_article(html4, "https://test.com/broken", "test.com")
        print(f"✅ Unexpectedly succeeded: {article4.title}")
    except Exception as e:
        print(f"✅ Expected failure (debug HTML should be saved): {e}")
    
    # Test Case 5: Chinese date formats
    print("\n📄 Test Case 5: Chinese Date Formats")
    html5 = """
    <html>
    <head>
        <title>Chinese Date Test</title>
    </head>
    <body>
        <article>
            <h1>中文日期测试</h1>
            <div class="date">2024年12月20日</div>
            <div class="content">
                <p>BlockBeats 消息，测试中文日期格式的解析。</p>
            </div>
        </article>
    </body>
    </html>
    """
    
    try:
        article5 = parser.parse_article(html5, "https://test.com/chinese-date", "test.com")
        print(f"✅ Title: {article5.title}")
        print(f"✅ Date: {article5.publication_date}")
        print(f"✅ Body: {article5.body_text}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Check if debug files were created
    print("\n🔍 Checking Debug Files")
    debug_dir = Path("debug_html")
    if debug_dir.exists():
        debug_files = list(debug_dir.glob("*.html"))
        print(f"✅ Debug directory exists with {len(debug_files)} files")
        for file in debug_files:
            print(f"   📁 {file.name}")
    else:
        print("❌ No debug directory found")
    
    print("\n✅ Enhanced Parser Test Complete!")

if __name__ == "__main__":
    test_enhanced_parser()