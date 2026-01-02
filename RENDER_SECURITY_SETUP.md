# 🔒 Render 安全环境变量设置指南

## ⚠️ 重要安全提醒

您的敏感凭据已从代码中移除，现在需要在 Render 中安全地设置环境变量。

## 🔑 需要设置的环境变量

### 1. Supabase 配置 (必需)
```
SUPABASE_URL=https://vckulcbgaqyujucbbeno.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZja3VsY2JnYXF5dWp1Y2JiZW5vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3Mjc1NDcsImV4cCI6MjA4MDMwMzU0N30.k713c5eTsM-fEFAxp8ST5IIh_AhJZtHVBrb4-oViHZU
```

### 2. DeepSeek API 配置 (可选 - 用于AI功能)
```
DEEPSEEK_API_KEY=sk-5192eebd30f446128039a5bae58556a3
```

## 📋 Render 设置步骤

### 步骤 1: 访问 Render 仪表板
1. 🌐 打开 https://dashboard.render.com/
2. 🔑 登录您的账户
3. 📱 找到您的新闻爬虫服务

### 步骤 2: 进入环境变量设置
1. 🔧 点击您的服务名称
2. ⚙️ 点击左侧菜单中的 "Environment"
3. 🔑 点击 "Add Environment Variable"

### 步骤 3: 添加环境变量
对每个变量重复以下步骤:

1. **添加 SUPABASE_URL**:
   - Key: `SUPABASE_URL`
   - Value: `https://vckulcbgaqyujucbbeno.supabase.co`
   - 🔒 点击 "Add"

2. **添加 SUPABASE_KEY**:
   - Key: `SUPABASE_KEY`
   - Value: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZja3VsY2JnYXF5dWp1Y2JiZW5vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3Mjc1NDcsImV4cCI6MjA4MDMwMzU0N30.k713c5eTsM-fEFAxp8ST5IIh_AhJZtHVBrb4-oViHZU`
   - 🔒 点击 "Add"

3. **添加 DEEPSEEK_API_KEY** (可选):
   - Key: `DEEPSEEK_API_KEY`
   - Value: `sk-5192eebd30f446128039a5bae58556a3`
   - 🔒 点击 "Add"

### 步骤 4: 触发部署
1. 🔄 环境变量设置完成后，Render 会自动重新部署
2. ⏱️ 等待部署完成 (2-5分钟)
3. ✅ 检查部署日志确认成功

## 🎯 验证部署

部署完成后，访问您的 Render URL 并验证:

### ✅ 检查清单:
- [ ] 🌐 网站可以正常访问
- [ ] 📊 仪表板显示12篇文章 (不是321篇)
- [ ] 🏷️ 每篇文章标题唯一 (无重复)
- [ ] 📅 日期显示正确 (2026/01/01)
- [ ] 🔄 手动更新按钮工作
- [ ] 📤 CSV导出功能正常
- [ ] ❌ 浏览器控制台无404错误

## 🛡️ 安全最佳实践

### ✅ 已实施的安全措施:
- 🔒 敏感凭据从代码中移除
- 📝 .env 文件已添加到 .gitignore
- 🧹 清理了所有敏感日志文件
- 📋 提供了 .env.example 模板

### 🔑 环境变量安全:
- ✅ 凭据仅存储在 Render 的安全环境中
- ✅ 不会出现在 Git 历史记录中
- ✅ 不会暴露在公共代码库中

## 🚨 如果遇到问题

### 常见问题解决:

1. **数据库连接失败**:
   - 检查 SUPABASE_URL 和 SUPABASE_KEY 是否正确设置
   - 确认没有多余的空格或换行符

2. **部署失败**:
   - 检查 Render 部署日志
   - 确认所有环境变量都已设置

3. **功能异常**:
   - 检查浏览器控制台是否有错误
   - 验证 API 端点是否响应

## 📞 支持

如果需要帮助:
1. 🔍 检查 Render 部署日志
2. 🌐 访问 /api/health 端点检查系统状态
3. 📊 查看仪表板 /dashboard 确认功能

---

**🎉 设置完成后，您的新闻系统将安全运行，包含所有最新修复!**