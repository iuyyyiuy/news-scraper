# 多源新闻抓取与去重指南

## 概述

新闻抓取系统现已支持从三个主要加密货币新闻源抓取内容：

1. **BlockBeats** (theblockbeats.info) - 区块律动
2. **Jinse** (jinse.cn) - 金色财经
3. **PANews** (panewslab.com) - PANews

系统还包含智能去重功能，可以自动识别和过滤重复的新闻文章。

## 新功能

### 1. 多源抓取

- 同时从多个新闻源抓取内容
- 支持并行抓取以提高效率
- 每个来源独立配置和统计
- 自动聚合所有来源的结果

### 2. 智能去重

去重引擎使用多个信号来检测重复文章：

- **标题相似度** (主要信号)
  - 阈值: 85%
  - 标题高度相似的文章被视为重复
  
- **正文相似度** (次要信号)
  - 阈值: 80%
  - 使用文章前500字符进行比较
  
- **综合评分**
  - 阈值: 75%
  - 标题权重60% + 正文权重40%

当检测到重复文章时，系统会保留最早发布的版本。

## 使用方法

### 方法1: 使用多源抓取器

```python
from datetime import date, timedelta
from scraper.core.config import Config
from scraper.core.storage import CSVDataStore
from scraper.core.multi_source_scraper import MultiSourceScraper

# 设置日期范围
end_date = date.today()
start_date = end_date - timedelta(days=3)

# 关键词过滤
keywords = ["BTC", "Bitcoin", "比特币"]

# 创建配置
config = Config(
    target_url="",
    max_articles=50,  # 每个来源检查50篇
    request_delay=1.0,
    output_format="csv",
    output_path="news.csv"
)

# 创建数据存储
data_store = CSVDataStore("news.csv")

# 创建多源抓取器
scraper = MultiSourceScraper(
    config=config,
    data_store=data_store,
    start_date=start_date,
    end_date=end_date,
    keywords_filter=keywords,
    sources=['blockbeats', 'jinse', 'panews'],  # 选择来源
    enable_deduplication=True  # 启用去重
)

# 执行抓取
result = scraper.scrape(parallel=True)

# 查看结果
print(f"总计抓取: {result.articles_scraped} 篇")
print(f"耗时: {result.duration_seconds:.2f} 秒")
```

### 方法2: 单独使用各个抓取器

#### 金色财经 (Jinse)

```python
from scraper.core.jinse_scraper import JinseScraper

scraper = JinseScraper(
    config=config,
    data_store=data_store,
    start_date=start_date,
    end_date=end_date,
    keywords_filter=keywords
)

result = scraper.scrape()
```

#### PANews

```python
from scraper.core.panews_scraper import PANewsScraper

scraper = PANewsScraper(
    config=config,
    data_store=data_store,
    start_date=start_date,
    end_date=end_date,
    keywords_filter=keywords
)

result = scraper.scrape()
```

### 方法3: 自定义去重参数

```python
from scraper.core.deduplicator import DeduplicationEngine

# 创建自定义去重引擎
deduplicator = DeduplicationEngine(
    title_threshold=0.90,      # 更严格的标题匹配
    body_threshold=0.85,       # 更严格的正文匹配
    combined_threshold=0.80    # 更严格的综合评分
)

# 手动去重文章列表
unique_articles = deduplicator.deduplicate(articles)

# 查看统计
stats = deduplicator.get_statistics()
print(f"发现重复: {stats['duplicates_found']} 篇")
```

## 测试脚本

### 测试所有功能

```bash
python test_multi_source_scraper.py
```

这将：
- 从所有三个来源抓取新闻
- 应用关键词过滤
- 执行去重处理
- 生成CSV文件
- 显示详细统计

### 测试单个抓取器

```bash
python test_individual_scrapers.py
```

这将分别测试金色财经和PANews抓取器。

## 输出格式

CSV文件包含以下列：

| 列名 | 说明 |
|------|------|
| 发布日期 | 文章发布日期 |
| 标题 | 文章标题 |
| 正文内容 | 文章正文 |
| 链接 | 文章URL |
| 匹配关键词 | 匹配的关键词列表 |

## 性能优化

### 并行抓取

```python
# 并行抓取（推荐）
result = scraper.scrape(parallel=True)

# 顺序抓取
result = scraper.scrape(parallel=False)
```

并行抓取可以显著减少总耗时，特别是在抓取多个来源时。

### 调整请求延迟

```python
config = Config(
    request_delay=0.5,  # 减少延迟以加快速度
    # 注意：太快可能被网站限制
)
```

### 限制检查数量

```python
config = Config(
    max_articles=30,  # 每个来源只检查30篇
)
```

## 去重算法详解

### 文本标准化

在比较之前，文本会被标准化：
1. 转换为小写
2. 移除标点符号
3. 移除多余空格
4. 去除首尾空格

### 相似度计算

使用 `SequenceMatcher` 计算两个文本之间的相似度：
- 返回0到1之间的分数
- 1表示完全相同
- 0表示完全不同

### 重复判定规则

文章被判定为重复，如果满足以下任一条件：

1. **标题高度相似**: `title_similarity >= 0.85`
2. **正文高度相似且标题相似**: `body_similarity >= 0.80 AND title_similarity >= 0.6`
3. **综合评分高**: `combined_score >= 0.75`

其中综合评分 = `title_similarity * 0.6 + body_similarity * 0.4`

### 保留策略

当检测到重复时：
- 保留发布日期最早的文章
- 如果没有发布日期，保留先抓取到的文章

## 日志和调试

### 启用详细日志

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,  # 显示所有日志
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 查看去重详情

去重过程会记录：
- 每对重复文章的相似度分数
- 保留和丢弃的文章信息
- 总体去重统计

## 常见问题

### Q: 为什么某些文章没有被抓取？

A: 可能的原因：
1. 文章不在指定的日期范围内
2. 文章不包含指定的关键词
3. 文章ID不存在（404错误）
4. 网站结构变化导致解析失败

### Q: 去重是否会误判？

A: 去重算法经过调优，但可能出现：
- **假阳性**: 不同文章被误判为重复（较少）
- **假阴性**: 重复文章未被检测到（较少）

可以通过调整阈值来平衡：
- 提高阈值 → 减少假阳性，增加假阴性
- 降低阈值 → 减少假阴性，增加假阳性

### Q: 如何处理网站结构变化？

A: 如果某个网站的HTML结构发生变化：
1. 检查 `scraper/core/parser.py` 中的选择器
2. 更新对应抓取器中的 `selectors` 配置
3. 测试并验证修改

### Q: 可以添加更多新闻源吗？

A: 可以！按照以下步骤：
1. 创建新的抓取器类（参考 `jinse_scraper.py`）
2. 在 `MultiSourceScraper.AVAILABLE_SOURCES` 中注册
3. 添加对应的CSS选择器
4. 测试新抓取器

## 最佳实践

1. **合理设置日期范围**: 不要设置太长的日期范围，建议1-7天
2. **使用关键词过滤**: 减少不相关文章的抓取
3. **启用去重**: 特别是在使用多个来源时
4. **监控错误日志**: 及时发现和处理问题
5. **尊重网站**: 设置合理的请求延迟，避免过度请求

## 技术架构

```
MultiSourceScraper
├── BlockBeatsScraper
│   ├── HTTPClient
│   ├── HTMLParser
│   └── InMemoryDataStore
├── JinseScraper
│   ├── HTTPClient
│   ├── HTMLParser
│   └── InMemoryDataStore
├── PANewsScraper
│   ├── HTTPClient
│   ├── HTMLParser
│   └── InMemoryDataStore
├── DeduplicationEngine
└── CSVDataStore (final output)
```

每个抓取器独立运行，结果汇总后进行去重，最终保存到CSV文件。

## 下一步

- [ ] 集成到Web界面
- [ ] 添加更多新闻源
- [ ] 使用更高级的相似度算法（如TF-IDF、BERT）
- [ ] 添加文章分类和标签
- [ ] 实现增量抓取（只抓取新文章）
