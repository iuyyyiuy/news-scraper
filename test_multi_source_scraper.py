"""
Test script for multi-source news scraper with deduplication.
"""
from datetime import date, timedelta
from scraper.core.config import Config
from scraper.core.storage import CSVDataStore
from scraper.core.multi_source_scraper import MultiSourceScraper


def test_multi_source_scraper():
    """Test scraping from multiple sources with deduplication."""
    
    # Set up date range (last 3 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=3)
    
    # Keywords to filter
    keywords = ["BTC", "Bitcoin", "比特币"]
    
    # Create config
    config = Config(
        target_url="",  # Not used for multi-source
        max_articles=50,  # Check 50 articles per source
        request_delay=1.0,  # 1 second delay between requests
        output_format="csv",
        output_path="multi_source_news.csv"
    )
    
    # Create data store
    data_store = CSVDataStore("multi_source_news.csv")
    
    # Create multi-source scraper
    # Test with all three sources
    scraper = MultiSourceScraper(
        config=config,
        data_store=data_store,
        start_date=start_date,
        end_date=end_date,
        keywords_filter=keywords,
        sources=['blockbeats', 'jinse', 'panews'],  # All sources
        enable_deduplication=True
    )
    
    print("=" * 60)
    print("多源新闻抓取测试")
    print("=" * 60)
    print(f"来源: BlockBeats, Jinse, PANews")
    print(f"日期范围: {start_date} 到 {end_date}")
    print(f"关键词: {keywords}")
    print(f"每个来源最多检查: {config.max_articles} 篇")
    print(f"去重: 启用")
    print("=" * 60)
    print()
    
    # Run scraping
    result = scraper.scrape(parallel=True)
    
    # Print results
    print()
    print("=" * 60)
    print("抓取完成!")
    print("=" * 60)
    print(f"总计检查: {result.total_articles_found} 篇")
    print(f"成功抓取: {result.articles_scraped} 篇")
    print(f"失败: {result.articles_failed} 篇")
    print(f"耗时: {result.duration_seconds:.2f} 秒")
    print(f"输出文件: {config.output_path}")
    print("=" * 60)
    
    # Print per-source statistics
    print()
    print("各来源统计:")
    print("-" * 60)
    source_results = scraper.get_source_results()
    for source, src_result in source_results.items():
        print(f"{source.upper()}:")
        print(f"  检查: {src_result.total_articles_found} 篇")
        print(f"  抓取: {src_result.articles_scraped} 篇")
        print(f"  失败: {src_result.articles_failed} 篇")
    print("=" * 60)
    
    # Print deduplication statistics
    if scraper.deduplicator:
        dedup_stats = scraper.deduplicator.get_statistics()
        print()
        print("去重统计:")
        print("-" * 60)
        print(f"发现重复: {dedup_stats['duplicates_found']} 篇")
        print(f"比较次数: {dedup_stats['comparisons_made']} 次")
        print(f"标题阈值: {dedup_stats['title_threshold']}")
        print(f"正文阈值: {dedup_stats['body_threshold']}")
        print(f"综合阈值: {dedup_stats['combined_threshold']}")
        print("=" * 60)


if __name__ == "__main__":
    test_multi_source_scraper()
