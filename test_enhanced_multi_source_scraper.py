#!/usr/bin/env python3
"""
Test Enhanced Multi-Source Scraper with Database Duplicate Detection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta
from scraper.core.multi_source_scraper import MultiSourceScraper
from scraper.core.storage import InMemoryDataStore
from scraper.core import Config

def test_enhanced_multi_source_scraper():
    """Test the enhanced multi-source scraper with database duplicate detection"""
    
    print("🧪 Testing Enhanced Multi-Source Scraper")
    print("=" * 60)
    
    # Create config
    config = Config(
        target_url="https://www.theblockbeats.info/newsflash",
        max_articles=10,  # Small number for testing
        request_delay=1.0,
        timeout=30,
        max_retries=2
    )
    
    # Create in-memory data store
    data_store = InMemoryDataStore()
    
    # Date range: last 3 days
    end_date = date.today()
    start_date = end_date - timedelta(days=3)
    
    # Security keywords
    keywords = [
        "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
        "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
        "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
    ]
    
    # Progress callback
    def progress_callback(source: str, articles_found: int, articles_scraped: int):
        print(f"📊 {source.upper()}: 找到 {articles_found} 篇，抓取 {articles_scraped} 篇")
    
    # Log callback
    def log_callback(message: str, log_type: str = 'info', source: str = None, show_in_all: bool = True):
        if log_type == 'error':
            print(f"❌ {message}")
        elif log_type == 'success':
            print(f"✅ {message}")
        else:
            print(f"ℹ️  {message}")
    
    try:
        print(f"📅 日期范围: {start_date} 到 {end_date}")
        print(f"🔑 关键词: {len(keywords)} 个安全相关关键词")
        print(f"📰 来源: BlockBeats (仅测试)")
        print()
        
        # Create scraper with enhanced duplicate detection
        scraper = MultiSourceScraper(
            config=config,
            data_store=data_store,
            start_date=start_date,
            end_date=end_date,
            keywords_filter=keywords,
            sources=['blockbeats'],  # Only BlockBeats for testing
            enable_deduplication=True,  # Enable enhanced duplicate detection
            progress_callback=progress_callback,
            log_callback=log_callback
        )
        
        print("🚀 开始测试增强去重功能...")
        print()
        
        # Run scraper
        result = scraper.scrape(parallel=False)
        
        # Get articles
        articles = data_store.get_all_articles()
        
        print()
        print("📊 测试结果:")
        print(f"   - 总计检查文章: {result.total_articles_found}")
        print(f"   - 最终保存文章: {result.articles_scraped}")
        print(f"   - 失败文章: {result.articles_failed}")
        print(f"   - 处理耗时: {result.duration_seconds:.2f} 秒")
        
        if result.errors:
            print(f"   - 错误数量: {len(result.errors)}")
            for error in result.errors[:3]:  # Show first 3 errors
                print(f"     * {error}")
        
        print()
        print("📰 抓取到的文章:")
        for i, article in enumerate(articles[:5], 1):  # Show first 5 articles
            print(f"   [{i}] {article.title[:60]}...")
            print(f"       来源: {getattr(article, 'source_website', 'Unknown')}")
            print(f"       URL: {getattr(article, 'url', 'No URL')}")
            print()
        
        if len(articles) > 5:
            print(f"   ... 还有 {len(articles) - 5} 篇文章")
        
        print("✅ 增强多源抓取测试完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_multi_source_scraper()
    sys.exit(0 if success else 1)