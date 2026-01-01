# 市场分析系统 - Market Analysis System

## 概述 (Overview)

市场分析系统是一个实时监控加密货币永续合约市场的智能风控工具，专门用于检测市场操纵行为，包括拉盘砸盘、订单欺骗、对敲交易等异常模式。

The Market Analysis System is an intelligent risk management tool for real-time monitoring of cryptocurrency perpetual futures markets, specifically designed to detect market manipulation behaviors including pump & dump, spoofing, wash trading, and other anomalous patterns.

## 核心功能 (Core Features)

### 1. 实时市场监控 (Real-time Market Monitoring)
- **多市场同时监控**: 支持同时监控多个永续合约市场
- **可配置扫描间隔**: 5秒到1分钟的灵活扫描频率
- **三级敏感度设置**: 低、中、高敏感度检测阈值

### 2. 市场操纵检测 (Market Manipulation Detection)

#### A. 拉盘砸盘检测 (Pump & Dump Detection)
- **检测指标**: 价格快速变化 + 成交量异常放大
- **阈值设置**: 
  - 高敏感度: 5%价格变化 + 3倍成交量
  - 中敏感度: 10%价格变化 + 5倍成交量
  - 低敏感度: 20%价格变化 + 10倍成交量

#### B. 订单欺骗检测 (Order Spoofing Detection)
- **检测方法**: 识别远离市价的大额订单
- **判断标准**: 
  - 订单量 > 100万 (可配置)
  - 距离市价 > 2%
  - 持续时间短暂

#### C. 对敲交易检测 (Wash Trading Detection)
- **检测逻辑**: 高成交量但价格波动极小
- **判断条件**:
  - 价格波动 < 2%
  - 成交量 > 50万 (可配置)
  - 持续时间 > 20分钟

#### D. 订单簿失衡检测 (Order Book Imbalance Detection)
- **计算方法**: 买卖盘前5档订单量比较
- **警报阈值**:
  - 高敏感度: 3:1 失衡比例
  - 中敏感度: 5:1 失衡比例
  - 低敏感度: 10:1 失衡比例

### 3. AI增强分析 (AI-Enhanced Analysis)
- **模式识别**: 使用机器学习识别复杂操纵模式
- **自适应阈值**: 根据市场历史数据动态调整检测阈值
- **强化学习**: 基于用户反馈持续改进检测准确性

## 技术架构 (Technical Architecture)

### 后端组件 (Backend Components)
```
scraper/api/market_analysis_routes.py     # API路由和业务逻辑
trade_risk_analyzer/                      # 核心分析引擎
├── market_monitoring/                    # 市场监控模块
│   ├── futures_analyzer.py             # 永续合约分析器
│   ├── mcp_client.py                    # MCP客户端
│   └── multi_market_monitor.py          # 多市场监控器
└── detection/                           # 检测算法模块
```

### 前端组件 (Frontend Components)
```
scraper/templates/market_analysis.html    # 主界面HTML
scraper/static/js/market_analysis.js     # 前端JavaScript逻辑
```

### 数据源 (Data Sources)
- **CoinEx MCP Server**: 通过MCP协议获取实时市场数据
- **支持的数据类型**:
  - 实时价格和成交量
  - 订单簿深度数据
  - K线/蜡烛图数据
  - 资金费率 (计划中)
  - 持仓数据 (计划中)

## 使用指南 (Usage Guide)

### 1. 启动系统 (Starting the System)

```bash
# 启动Web服务器
python run_web_server.py

# 或使用FastAPI直接启动
uvicorn scraper.web_api:app --host 0.0.0.0 --port 8000
```

### 2. 访问界面 (Accessing the Interface)

打开浏览器访问: `http://localhost:8000/market-analysis`

### 3. 配置监控 (Configuring Monitoring)

#### 监控设置 (Monitoring Settings)
- **监控市场**: 选择要监控的永续合约市场
- **扫描间隔**: 设置数据获取频率 (5秒-1分钟)
- **敏感度**: 选择检测敏感度级别

#### 开始监控 (Start Monitoring)
1. 选择监控参数
2. 点击"开始监控"按钮
3. 系统开始实时扫描市场数据
4. 异常情况将实时显示在警报区域

### 4. 警报管理 (Alert Management)

#### 警报级别 (Alert Levels)
- **🔴 高风险 (High)**: 严重市场操纵行为
- **🟡 中风险 (Medium)**: 可疑交易模式
- **🔵 低风险 (Low)**: 轻微异常情况

#### 警报信息 (Alert Information)
每个警报包含:
- **市场**: 触发警报的交易对
- **标题**: 检测到的异常类型
- **描述**: 详细的异常情况说明
- **指标**: 相关的数值指标
- **AI分析**: 智能分析和建议

### 5. 数据导出 (Data Export)

支持将警报数据导出为CSV格式，包含:
- 时间戳
- 市场信息
- 异常类型
- 详细指标
- AI分析结果

## API接口文档 (API Documentation)

### 获取可用市场 (Get Available Markets)
```http
GET /api/market-analysis/markets
```

### 开始监控 (Start Monitoring)
```http
POST /api/market-analysis/start
Content-Type: application/json

{
  "markets": ["BTC", "ETH", "SOL"],
  "interval": 10,
  "sensitivity": "medium"
}
```

### 获取警报 (Get Alerts)
```http
GET /api/market-analysis/alerts
```

### 停止监控 (Stop Monitoring)
```http
POST /api/market-analysis/stop
```

### 清除警报 (Clear Alerts)
```http
POST /api/market-analysis/clear-alerts
```

### 导出警报 (Export Alerts)
```http
GET /api/market-analysis/export-alerts
```

## 测试指南 (Testing Guide)

### 运行测试脚本 (Run Test Script)
```bash
python test_market_analysis_system.py
```

### 测试内容 (Test Coverage)
- Web服务器连接性
- 市场数据获取
- 监控启动/停止
- 警报生成和管理
- 数据导出功能

## 配置说明 (Configuration)

### 敏感度阈值 (Sensitivity Thresholds)

#### 高敏感度 (High Sensitivity)
```python
{
    "price_change": 5.0,        # 5% 价格变化
    "orderbook_imbalance": 3.0, # 3:1 订单簿失衡
    "spread_threshold": 0.5,    # 0.5% 价差阈值
    "volume_spike": 3.0         # 3倍成交量激增
}
```

#### 中敏感度 (Medium Sensitivity)
```python
{
    "price_change": 10.0,       # 10% 价格变化
    "orderbook_imbalance": 5.0, # 5:1 订单簿失衡
    "spread_threshold": 1.0,    # 1% 价差阈值
    "volume_spike": 5.0         # 5倍成交量激增
}
```

#### 低敏感度 (Low Sensitivity)
```python
{
    "price_change": 20.0,       # 20% 价格变化
    "orderbook_imbalance": 10.0,# 10:1 订单簿失衡
    "spread_threshold": 2.0,    # 2% 价差阈值
    "volume_spike": 10.0        # 10倍成交量激增
}
```

## 故障排除 (Troubleshooting)

### 常见问题 (Common Issues)

#### 1. MCP连接失败
```bash
# 检查MCP配置
python check_mcp_setup.py

# 测试CoinEx MCP
python test_coinex_mcp.py
```

#### 2. 监控无法启动
- 检查端口占用情况
- 确认MCP服务器运行状态
- 查看日志文件错误信息

#### 3. 数据获取异常
- 验证网络连接
- 检查API限制
- 确认市场符号正确性

### 日志查看 (Log Viewing)
```bash
# 查看应用日志
tail -f logs/market_analysis.log

# 查看错误日志
grep ERROR logs/market_analysis.log
```

## 未来规划 (Future Plans)

### 短期目标 (Short-term Goals)
- [ ] 添加更多检测算法
- [ ] 优化检测准确性
- [ ] 增加历史数据分析
- [ ] 支持更多交易所

### 长期目标 (Long-term Goals)
- [ ] 机器学习模型训练
- [ ] 预测性分析功能
- [ ] 自动交易保护
- [ ] 多语言支持

## 贡献指南 (Contributing)

欢迎提交问题报告、功能请求和代码贡献。请遵循以下步骤:

1. Fork项目仓库
2. 创建功能分支
3. 提交代码更改
4. 创建Pull Request

## 许可证 (License)

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式 (Contact)

如有问题或建议，请通过以下方式联系:
- 创建GitHub Issue
- 发送邮件至项目维护者
- 加入项目讨论群组