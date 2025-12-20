# 手动更新 (Manual Update) 使用指南

## 🚀 快速启动

### 1. 启动服务器
```bash
python start_manual_update_server.py
```

### 2. 打开浏览器
访问: http://localhost:8000/dashboard

### 3. 点击"手动更新"按钮
在仪表板中找到蓝色的"手动更新"按钮，点击即可开始

## ✨ 功能特点

### 📋 处理流程
1. **BlockBeats 抓取** - 检查最新新闻ID，向后抓取200篇文章
2. **Jinse 抓取** - 检查最新新闻ID，向后抓取200篇文章  
3. **AI智能过滤** - 过滤重复、相似、无关新闻
4. **实时数据库更新** - 直接保存到Supabase数据库

### 🎯 内容提取
- 标题 (title)
- 正文内容 (body_text)
- 发布日期 (publication_date)
- 来源 (source: BlockBeats/Jinse)
- 匹配关键词 (matched_keywords)
- 文章链接 (url)

### 🔍 关键词过滤
自动使用以下安全相关关键词过滤:
- 安全问题、黑客、被盗、漏洞、攻击
- CoinEx、ViaBTC、破产、执法、监管
- 洗钱、KYC、合规、牌照、风控
- 诈骗、突发、rug pull、下架

## 🌐 API 接口

### 启动手动更新
```bash
curl -X POST http://localhost:8000/api/manual-update \
  -H "Content-Type: application/json" \
  -d '{"max_articles": 200}'
```

### 检查状态
```bash
curl http://localhost:8000/api/manual-update/status
```

### 健康检查
```bash
curl http://localhost:8000/api/health
```

## 📊 实时监控

### 仪表板功能
- ✅ 实时进度通知
- ✅ 自动数据刷新
- ✅ 错误状态显示
- ✅ 完成状态提醒

### 日志查看
- 控制台显示详细处理日志
- 每个步骤都有时间戳
- 显示找到/保存/过滤的文章数量

## 🔧 故障排除

### 如果AI分析失败
- 系统会自动回退到关键词过滤
- 不会影响整体抓取流程

### 如果某个源失败
- 会继续处理下一个源
- 错误会被记录但不会中断流程

### 如果数据库连接失败
- 会显示连接错误
- 可以重试手动更新

## 📝 使用建议

1. **首次使用**: 建议先用少量文章测试 (max_articles: 10)
2. **正常使用**: 默认每源200篇文章，大约需要2-3分钟
3. **频率控制**: 建议间隔至少5分钟再次运行
4. **监控日志**: 注意观察控制台输出了解处理状态

## ✅ 准备就绪

手动更新功能已完全配置好，可以在localhost上使用！