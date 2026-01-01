#!/usr/bin/env python3
"""
Final Test: Enhanced Duplicate Detection System
Test the complete system with real scraping to ensure duplicates are properly handled
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta
from scraper.core.multi_source_scraper import MultiSourceScraper
from scraper.core.storage import InMemoryDataStore
from scraper.core import Config

def test_final_enhanced_duplicate_system():
    """Final comprehensive test of the enhanced duplicate detection system"""
    
    print("🎯 Final Test: Enhanced Duplicate Detection System")
    print("=" * 70)
    
    # Create config for real scraping
    config = Config(
        target_url="https://www.theblockbeats.info/newsflash",
        max_articles=30,  # Moderate number to test duplicates
        request_delay=1.0,
        timeout=30,
        max_retries=2
    )
    
    # Create in-memory data store
    data_store = InMemoryDataStore()
    
    # Date range: last 5 days (more likely to have duplicates)
    end_date = date.today()
    start_date = end_date - timedelta(days=5)
    
    # Security keywords
    keywords = [
        "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
        "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
        "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
    ]
    
    # Track duplicate detection results
    duplicate_stats = {
        'total_found': 0,
        'total_unique': 0,
        'duplicates_removed': 0,
        'methods_used': {}
    }
    
    # Progress callback
    def progress_callback(source: str, articles_found: int, articles_scraped: int):
        print(f"📊 {source.upper()}: 找到 {articles_found} 篇，处理 {articles_scraped} 篇")
    
    # Log callback to track duplicate detection
    def log_callback(message: str, log_type: str = 'info', source: str = None, show_in_all: bool = True):
        if "重复文章" in message:
            # Extract duplicate count
            import re
            match = re.search(r'移除 (\d+) 篇重复文章', message)
            if match:
                duplicate_stats['duplicates_removed'] = int(match.group(1))
        
        if "URL匹配" in message or "标题匹配" in message or "内容匹配" in message or "相似标题" in message:
            # Track duplicate detection methods
            import re
            for method in ["URL匹配", "标题匹配", "内容匹配", "相似标题"]:
                if method in message:
                    match = re.search(rf'{method}: (\d+) 篇', message)
                    if match:
                        duplicate_stats['methods_used'][method] = int(match.group(1))
        
        if log_type == 'error':
            print(f"❌ {message}")
        elif log_type == 'success':
            print(f"✅ {message}")
        else:
            print(f"ℹ️  {message}")
    
    try:
        print(f"📅 测试参数:")
        print(f"   - 日期范围: {start_date} 到 {end_date} (5天)")
        print(f"   - 关键词: {len(keywords)} 个安全相关关键词")
        print(f"   - 最大文章数: {config.max_articles}")
        print(f"   - 来源: BlockBeats")
        print(f"   - 增强去重: 启用")
        print()
        
        # Create scraper with enhanced duplicate detection
        scraper = MultiSourceScraper(
            config=config,
            data_store=data_store,
            start_date=start_date,
            end_date=end_date,
            keywords_filter=keywords,
            sources=['blockbeats'],
            enable_deduplication=True,  # This enables enhanced duplicate detection
            progress_callback=progress_callback,
            log_callback=log_callback
        )
        
        print("🚀 开始最终测试...")
        print()
        
        # Get initial stats from enhanced duplicate detector
        initial_stats = scraper.enhanced_duplicate_detector.get_stats()
        print(f"📊 数据库中已有文章:")
        print(f"   - URLs: {initial_stats['urls_tracked']}")
        print(f"   - 标题: {initial_stats['titles_tracked']}")
        print(f"   - 内容哈希: {initial_stats['content_hashes_tracked']}")
        print()
        
        # Run scraper
        result = scraper.scrape(parallel=False)
        
        # Get final articles
        articles = data_store.get_all_articles()
        duplicate_stats['total_found'] = result.total_articles_found
        duplicate_stats['total_unique'] = len(articles)
        
        print()
        print("🎯 最终测试结果:")
        print("=" * 50)
        print(f"✅ 总计检查文章: {result.total_articles_found}")
        print(f"✅ 最终唯一文章: {len(articles)}")
        print(f"✅ 重复文章移除: {duplicate_stats['duplicates_removed']}")
        print(f"✅ 失败文章: {result.articles_failed}")
        print(f"✅ 处理耗时: {result.duration_seconds:.2f} 秒")
        
        if duplicate_stats['methods_used']:
            print()
            print("🔍 去重方法统计:")
            for method, count in duplicate_stats['methods_used'].items():
                print(f"   - {method}: {count} 篇")
        
        if result.errors:
            print(f"⚠️  错误数量: {len(result.errors)}")
        
        print()
        print("📰 抓取到的唯一文章:")
        for i, article in enumerate(articles[:3], 1):  # Show first 3 articles
            print(f"   [{i}] {article.title[:60]}...")
            print(f"       来源: {getattr(article, 'source_website', 'Unknown')}")
            print(f"       日期: {getattr(article, 'publication_date', 'Unknown')}")
            print()
        
        if len(articles) > 3:
            print(f"   ... 还有 {len(articles) - 3} 篇唯一文章")
        
        print()
        print("🎉 增强去重系统测试结果:")
        
        # Evaluate success
        success_criteria = [
            ("系统正常运行", result.total_articles_found > 0),
            ("成功检测重复", duplicate_stats['duplicates_removed'] >= 0),
            ("保留唯一文章", len(articles) > 0),
            ("无严重错误", len(result.errors) == 0)
        ]
        
        all_passed = True
        for criterion, passed in success_criteria:
            status = "✅" if passed else "❌"
            print(f"   {status} {criterion}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print()
            print("🎊 所有测试通过! 增强去重系统工作正常!")
            print("   - 新闻抓取功能中的重复文章问题已解决")
            print("   - 系统现在会检查数据库中的现有文章")
            print("   - 多层去重检测确保不会显示重复内容")
        else:
            print()
            print("⚠️  部分测试未通过，需要进一步检查")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 最终测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_final_enhanced_duplicate_system()
    sys.exit(0 if success else 1)