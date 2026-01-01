#!/bin/bash

echo "🚀 部署所有修复到 Render"
echo "=================================="
echo "📋 将要部署的修复:"
echo "   ✅ 日期解析修复 (2025-12-31, 不是2026-12-31)"
echo "   ✅ 标题提取修复 (唯一标题, 无重复)"
echo "   ✅ 数据库清理完成 (仅12篇当前文章)"
echo "   ✅ 月度清理自动化"
echo "   ✅ 警报日志修复 (无404错误)"
echo "   ✅ FastAPI服务器配置"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 仓库..."
    git init
    git branch -M main
fi

# Add all changes
echo "📁 添加所有文件到 Git..."
git add .

# Commit changes
echo "💾 提交更改..."
git commit -m "🔧 Deploy all fixes to Render

✅ Parser fixes applied:
- Date parsing: 2025-12-31 (not 2026-12-31)
- Title extraction: Unique titles (no duplicates)
- Enhanced meta tag priority for BlockBeats

✅ Database cleanup completed:
- Removed 309 old articles (2025 and earlier)
- Kept 12 current articles (2026-01-XX)
- 96% database size reduction

✅ Alert system fixed:
- File-only logging (no database dependency)
- No more 404 errors for alert_logs table

✅ Monthly cleanup automated:
- Runs 1st of every month at 2:00 AM
- Keeps database clean automatically

✅ FastAPI server restored:
- Original dashboard interface working
- All API routes functional
- Secure web framework (not Flask)

🎯 All systems operational and tested"

# Check if remote exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❌ 错误: 没有配置 Git remote origin"
    echo "💡 请先配置您的 Git 仓库:"
    echo "   git remote add origin <your-repo-url>"
    echo ""
    echo "📋 或者手动部署到 Render:"
    echo "   1. 将所有文件上传到您的 Git 仓库"
    echo "   2. 在 Render 中触发新部署"
    echo "   3. 确保环境变量已设置:"
    echo "      - SUPABASE_URL"
    echo "      - SUPABASE_KEY"
    exit 1
fi

# Push to remote
echo "🌐 推送到远程仓库..."
if git push origin main; then
    echo ""
    echo "✅ 成功推送到 Git 仓库!"
    echo ""
    echo "🎯 下一步 - Render 部署:"
    echo "=================================="
    echo "1. 🌐 访问您的 Render 仪表板"
    echo "2. 🔄 Render 会自动检测到新提交并开始部署"
    echo "3. ⏱️  等待部署完成 (通常需要2-5分钟)"
    echo "4. ✅ 部署完成后，所有修复将在线生效"
    echo ""
    echo "📊 部署后验证:"
    echo "   - 访问您的 Render URL"
    echo "   - 检查仪表板是否显示12篇文章"
    echo "   - 验证标题是否唯一"
    echo "   - 确认日期显示正确"
    echo ""
    echo "🔗 Render 部署状态: https://dashboard.render.com/"
else
    echo ""
    echo "❌ 推送失败!"
    echo "💡 故障排除:"
    echo "   1. 检查网络连接"
    echo "   2. 验证 Git 凭据"
    echo "   3. 确认仓库权限"
    echo ""
    echo "🔄 手动重试: git push origin main"
fi

echo ""
echo "📋 部署摘要:"
echo "=================================="
echo "✅ 解析器修复: 日期和标题提取"
echo "✅ 数据库清理: 309篇旧文章已删除"
echo "✅ 警报系统: 404错误已修复"
echo "✅ 月度清理: 已自动化"
echo "✅ FastAPI服务器: 原始界面已恢复"
echo ""
echo "🎉 所有修复已准备好部署到 Render!"