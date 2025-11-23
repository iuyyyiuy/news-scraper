# Quick Start: Multi-Source News Scraping

## 快速开始：多源新闻抓取

### 1. 最简单的使用方式

```bash
# 运行测试脚本
python test_multi_source_scraper.py
```

这将从所有三个来源（BlockBeats、金色财经、PANews）抓取最近3天的BTC相关新闻。

### 2. 自定义抓取

```python
from datetime import date, timedelta
from scraper.core.config import Config
from scraper.core.storage import CSVDataStore
from scraper.core.multi_source_scraper import MultiSourceScraper

# 配置
end_date = date.today()
start_date = end_date - timedelta(days=7)  # 最近7天
keywords = ["以太坊", "ETH", "Ethereum"]    # 搜索以太坊相关

config = Config(
    max_articles=100,      # 每个来源检查100篇
    request_delay=1.0,     # 请求间隔1秒
    output_path="eth_news.csv"
)

data_store = CSVDataStore("eth_news.csv")

scraper = MultiSourceScraper(
    config=config,
    data_store=data_store,
    start_date=start_date,
    end_date=end_date,
    keywords_filter=keywords,
    sources=['blockbeats', 'jinse', 'panews'],  # 所有来源
    enable_deduplication=True                    # 启用去重
)

result = scraper.scrape(parallel=True)
print(f"✅ 抓取完成: {result.articles_scraped} 篇唯一文章")
```

### 3. 只抓取特定来源

```python
# 只抓取金色财经
scraper = MultiSourceScraper(
    # ... 其他参数 ...
    sources=['jinse'],  # 只选择金色财经
)

# 或者只抓取BlockBeats和PANews
scraper = MultiSourceScraper(
    # ... 其他参数 ...
    sources=['blockbeats', 'panews'],
)
```

### 4. 禁用去重

```python
scraper = MultiSourceScraper(
    # ... 其他参数 ...
    enable_deduplication=False  # 保留所有文章，包括重复的
)
```

### 5. 调整去重灵敏度

```python
from scraper.core.deduplicator import DeduplicationEngine

# 创建更严格的去重引擎
deduplicator = DeduplicationEngine(
    title_threshold=0.95,      # 标题必须95%相似
    body_threshold=0.90,       # 正文必须90%相似
    combined_threshold=0.85    # 综合评分85%
)

# 手动去重
unique_articles = deduplicator.deduplicate(all_articles)
```

### 6. 查看详细统计

```python
result = scraper.scrape(parallel=True)

# 总体统计
print(f"检查: {result.total_articles_found}")
print(f"抓取: {result.articles_scraped}")
print(f"耗时: {result.duration_seconds:.2f}秒")

# 各来源统计
for source, src_result in scraper.get_source_results().items():
    print(f"{source}: {src_result.articles_scraped} 篇")

# 去重统计
if scraper.deduplicator:
    stats = scraper.deduplicator.get_statistics()
    print(f"移除重复: {stats['duplicates_found']} 篇")
```

## 常用配置

### 快速抓取（适合测试）
```python
config = Config(
    max_articles=20,       # 少量文章
    request_delay=0.5,     # 快速请求
)
```

### 深度抓取（适合生产）
```python
config = Config(
    max_articles=200,      # 大量文章
    request_delay=2.0,     # 礼貌请求
)
```

### 无关键词过滤（抓取所有）
```python
scraper = MultiSourceScraper(
    # ... 其他参数 ...
    keywords_filter=[],    # 空列表 = 不过滤
)
```

## 输出文件

生成的CSV文件包含：
- 发布日期
- 标题
- 正文内容
- 链接
- 匹配关键词

可以用Excel、Google Sheets等工具打开。

## 故障排除

### 问题：抓取速度太慢
**解决**：
- 减少 `max_articles`
- 减少 `request_delay`（但不要太小）
- 确保使用 `parallel=True`

### 问题：某个来源没有结果
**解决**：
- 检查日期范围是否合理
- 检查关键词是否太严格
- 查看日志中的错误信息

### 问题：太多重复文章
**解决**：
- 确保 `enable_deduplication=True`
- 降低去重阈值（更激进的去重）

### 问题：误删了不重复的文章
**解决**：
- 提高去重阈值（更保守的去重）
- 或者禁用去重，手动处理

## 更多信息

详细文档请参考：
- `MULTI_SOURCE_SCRAPING_GUIDE.md` - 完整使用指南
- `IMPLEMENTATION_SUMMARY_MULTI_SOURCE.md` - 技术实现细节
