"""
Test script for individual news scrapers (Jinse and PANews).
"""
from datetime import date, timedelta
from scraper.core.config import Config
from scraper.core.storage import CSVDataStore
from scraper.core.jinse_scraper import JinseScraper
from scraper.core.panews_scraper import PANewsScraper


def test_jinse_scraper():
    """Test Jinse scraper."""
    print("\n" + "=" * 60)
    print("测试金色财经抓取器")
    print("=" * 60)
    
    # Set up date range (last 2 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=2)
    
    # Keywords to filter
    keywords = ["BTC", "Bitcoin", "比特币"]
    
    # Create config
    config = Config(
        target_url="https://www.jinse.cn/lives",
        max_articles=20,  # Check 20 articles
        request_delay=1.0,
        output_format="csv",
        output_path="jinse_test.csv"
    )
    
    # Create data store
    data_store = CSVDataStore("jinse_test.csv")
    
    # Create scraper
    scraper = JinseScraper(
        config=config,
        data_store=data_store,
        start_date=start_date,
        end_date=end_date,
        keywords_filter=keywords
    )
    
    print(f"日期范围: {start_date} 到 {end_date}")
    print(f"关键词: {keywords}")
    print(f"最多检查: {config.max_articles} 篇")
    print()
    
    # Run scraping
    result = scraper.scrape()
    
    print()
    print("结果:")
    print(f"  检查: {result.total_articles_found} 篇")
    print(f"  抓取: {result.articles_scraped} 篇")
    print(f"  失败: {result.articles_failed} 篇")
    print(f"  耗时: {result.duration_seconds:.2f} 秒")
    print("=" * 60)


def test_panews_scraper():
    """Test PANews scraper."""
    print("\n" + "=" * 60)
    print("测试PANews抓取器")
    print("=" * 60)
    
    # Set up date range (last 2 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=2)
    
    # Keywords to filter
    keywords = ["BTC", "Bitcoin", "比特币"]
    
    # Create config
    config = Config(
        target_url="https://www.panewslab.com/zh/index.html",
        max_articles=20,  # Check 20 articles
        request_delay=1.0,
        output_format="csv",
        output_path="panews_test.csv"
    )
    
    # Create data store
    data_store = CSVDataStore("panews_test.csv")
    
    # Create scraper
    scraper = PANewsScraper(
        config=config,
        data_store=data_store,
        start_date=start_date,
        end_date=end_date,
        keywords_filter=keywords
    )
    
    print(f"日期范围: {start_date} 到 {end_date}")
    print(f"关键词: {keywords}")
    print(f"最多检查: {config.max_articles} 篇")
    print()
    
    # Run scraping
    result = scraper.scrape()
    
    print()
    print("结果:")
    print(f"  检查: {result.total_articles_found} 篇")
    print(f"  抓取: {result.articles_scraped} 篇")
    print(f"  失败: {result.articles_failed} 篇")
    print(f"  耗时: {result.duration_seconds:.2f} 秒")
    print("=" * 60)


if __name__ == "__main__":
    print("开始测试各个抓取器...")
    
    # Test Jinse
    try:
        test_jinse_scraper()
    except Exception as e:
        print(f"❌ 金色财经测试失败: {e}")
    
    # Test PANews
    try:
        test_panews_scraper()
    except Exception as e:
        print(f"❌ PANews测试失败: {e}")
    
    print("\n测试完成!")
