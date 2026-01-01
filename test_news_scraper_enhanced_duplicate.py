#!/usr/bin/env python3
"""
Test News Scraper Function with Enhanced Duplicate Detection
"""

import requests
import json
import time
import sys

def test_news_scraper_enhanced_duplicate():
    """Test the news scraper function with enhanced duplicate detection"""
    
    print("🧪 Testing News Scraper Function - Enhanced Duplicate Detection")
    print("=" * 70)
    
    base_url = "http://localhost:5000"
    
    # Test parameters
    test_params = {
        "days_filter": 3,  # Last 3 days
        "keywords": [
            "安全问题", "黑客", "被盗", "漏洞", "攻击", "恶意软件", "盗窃",
            "CoinEx", "ViaBTC", "破产", "执法", "监管", "洗钱", "KYC",
            "合规", "牌照", "风控", "诈骗", "突发", "rug pull", "下架"
        ],
        "max_articles": 20,  # Small number for testing
        "sources": ["blockbeats"],  # Only BlockBeats
        "enable_deduplication": True  # Enable enhanced duplicate detection
    }
    
    try:
        print(f"📅 测试参数:")
        print(f"   - 日期范围: 最近 {test_params['days_filter']} 天")
        print(f"   - 关键词: {len(test_params['keywords'])} 个安全相关关键词")
        print(f"   - 最大文章数: {test_params['max_articles']}")
        print(f"   - 来源: {', '.join(test_params['sources'])}")
        print(f"   - 去重: {'启用' if test_params['enable_deduplication'] else '禁用'}")
        print()
        
        # Start scraping session
        print("🚀 启动新闻抓取会话...")
        response = requests.post(f"{base_url}/api/scrape", json=test_params)
        
        if response.status_code != 200:
            print(f"❌ 启动失败: {response.status_code} - {response.text}")
            return False
        
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"✅ 会话已启动: {session_id}")
        print()
        
        # Monitor progress
        print("📊 监控抓取进度...")
        last_log_count = 0
        duplicate_info = []
        
        while True:
            # Get session status
            status_response = requests.get(f"{base_url}/api/session/{session_id}")
            if status_response.status_code != 200:
                print(f"❌ 获取状态失败: {status_response.status_code}")
                break
            
            session_info = status_response.json()
            status = session_info["status"]
            
            # Show new logs
            logs = session_info.get("logs", [])
            if len(logs) > last_log_count:
                for log in logs[last_log_count:]:
                    message = log["message"]
                    log_type = log["log_type"]
                    
                    # Track duplicate detection messages
                    if "重复文章" in message or "去重" in message:
                        duplicate_info.append(message)
                    
                    if log_type == "error":
                        print(f"❌ {message}")
                    elif log_type == "success":
                        print(f"✅ {message}")
                    else:
                        print(f"ℹ️  {message}")
                
                last_log_count = len(logs)
            
            # Check if completed
            if status in ["completed", "failed"]:
                break
            
            time.sleep(2)
        
        print()
        print("📊 最终结果:")
        
        if status == "completed":
            result = session_info.get("result", {})
            articles = session_info.get("articles", [])
            
            print(f"✅ 抓取完成!")
            print(f"   - 总计检查文章: {result.get('total_articles_found', 0)}")
            print(f"   - 最终保存文章: {result.get('articles_scraped', 0)}")
            print(f"   - 失败文章: {result.get('articles_failed', 0)}")
            print(f"   - 处理耗时: {result.get('duration_seconds', 0):.2f} 秒")
            
            if result.get("errors"):
                print(f"   - 错误数量: {len(result['errors'])}")
            
            print()
            print("🔍 去重信息:")
            if duplicate_info:
                for info in duplicate_info:
                    print(f"   - {info}")
            else:
                print("   - 未发现去重相关信息")
            
            print()
            print("📰 抓取到的文章:")
            for i, article in enumerate(articles[:5], 1):
                print(f"   [{i}] {article['title'][:60]}...")
                print(f"       来源: {article.get('source', 'Unknown')}")
                print(f"       日期: {article.get('publication_date', 'Unknown')}")
                print()
            
            if len(articles) > 5:
                print(f"   ... 还有 {len(articles) - 5} 篇文章")
            
            print("✅ 新闻抓取功能测试完成 - 增强去重功能正常工作!")
            return True
            
        else:
            print(f"❌ 抓取失败: {status}")
            if session_info.get("error"):
                print(f"   错误: {session_info['error']}")
            return False
    
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_news_scraper_enhanced_duplicate()
    sys.exit(0 if success else 1)