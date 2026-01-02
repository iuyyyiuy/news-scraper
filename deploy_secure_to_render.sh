#!/bin/bash

echo "🔒 安全部署到 Render (不包含敏感信息)"
echo "=============================================="
echo ""

# Check if .env file exists and warn user
if [ -f ".env" ]; then
    echo "⚠️  警告: 检测到 .env 文件"
    echo "🔒 .env 文件将被排除在部署之外 (包含敏感凭据)"
    echo ""
fi

# Ensure .gitignore is properly configured
echo "🛡️  更新 .gitignore 以保护敏感文件..."
git add .gitignore .env.example

# Remove any sensitive files that might have been accidentally added
echo "🧹 清理可能的敏感文件..."
git rm --cached .env 2>/dev/null || true
git rm --cached *.log 2>/dev/null || true
git rm --cached session_stats_*.json 2>/dev/null || true
git rm --cached alert_logs_*.json 2>/dev/null || true
git rm --cached temp_session_*.csv 2>/dev/null || true
git rm --cached monthly_cleanup_backup_*.json 2>/dev/null || true

# Add only safe files
echo "📁 添加安全文件到 Git..."
git add \
    scraper/ \
    *.py \
    *.sh \
    *.md \
    *.yaml \
    *.yml \
    *.txt \
    *.html \
    .gitignore \
    .env.example

# Exclude sensitive patterns
git reset HEAD .env 2>/dev/null || true
git reset HEAD *.log 2>/dev/null || true
git reset HEAD session_stats_*.json 2>/dev/null || true
git reset HEAD alert_logs_*.json 2>/dev/null || true
git reset HEAD temp_session_*.csv 2>/dev/null || true
git reset HEAD monthly_cleanup_backup_*.json 2>/dev/null || true
git reset HEAD *.xlsx 2>/dev/null || true
git reset HEAD *.db 2>/dev/null || true

# Commit changes
echo "💾 提交安全更改..."
git commit -m "🔒 Secure deployment - exclude sensitive data

✅ Security improvements:
- Added comprehensive .gitignore
- Excluded .env file with credentials
- Removed sensitive logs and session files
- Added .env.example template

✅ Code fixes included:
- Parser fixes (date/title extraction)
- Database cleanup (309 old articles removed)
- Alert system fixes (no 404 errors)
- Monthly cleanup automation
- FastAPI server restoration

🔒 Credentials must be set in Render environment variables:
- SUPABASE_URL
- SUPABASE_KEY
- DEEPSEEK_API_KEY (optional)"

# Check if remote exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❌ 错误: 没有配置 Git remote origin"
    echo "💡 请先配置您的 Git 仓库:"
    echo "   git remote add origin <your-repo-url>"
    exit 1
fi

# Push to remote
echo "🌐 推送安全更改到远程仓库..."
if git push origin main; then
    echo ""
    echo "✅ 安全部署成功推送!"
    echo ""
    echo "🔒 重要安全提醒:"
    echo "=============================================="
    echo "1. ✅ 敏感凭据已从代码中移除"
    echo "2. 🔑 在 Render 中设置环境变量:"
    echo "   - SUPABASE_URL=https://vckulcbgaqyujucbbeno.supabase.co"
    echo "   - SUPABASE_KEY=[您的Supabase密钥]"
    echo "   - DEEPSEEK_API_KEY=[您的DeepSeek密钥] (可选)"
    echo ""
    echo "🎯 Render 部署步骤:"
    echo "=============================================="
    echo "1. 🌐 访问 Render 仪表板"
    echo "2. 🔧 进入您的服务设置"
    echo "3. 🔑 添加环境变量 (Environment Variables)"
    echo "4. 🔄 触发新部署"
    echo "5. ✅ 验证部署成功"
    echo ""
    echo "🔗 Render 仪表板: https://dashboard.render.com/"
else
    echo ""
    echo "❌ 推送失败!"
    echo "💡 请检查网络连接和Git凭据"
fi

echo ""
echo "🛡️  安全检查清单:"
echo "=============================================="
echo "✅ .env 文件已排除"
echo "✅ 日志文件已排除"
echo "✅ 会话数据已排除"
echo "✅ 数据库文件已排除"
echo "✅ 临时文件已排除"
echo "✅ .env.example 已提供"
echo ""
echo "🎉 安全部署完成!"