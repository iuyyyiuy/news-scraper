# 🚀 Deploy Multi-Source Update - Your Setup

## Your Current Setup

✅ **Digital Ocean**: http://143.198.219.220
✅ **Render**: https://crypto-news-scraper.onrender.com

Both are already configured and running!

---

## 📦 Deploy to Digital Ocean

### Quick Update (Recommended)

```bash
# Run the deployment script
./deploy_multi_source_update.sh
```

**What it does:**
1. ✅ Verifies all new files exist
2. ✅ Creates update package
3. ✅ Uploads to 143.198.219.220
4. ✅ Backs up old files
5. ✅ Installs new files
6. ✅ Restarts service
7. ✅ Verifies service is running

**Time:** ~2-3 minutes

### Manual Steps (if script fails)

```bash
# 1. Create package
tar -czf multi-source-update.tar.gz \
  scraper/core/jinse_scraper.py \
  scraper/core/panews_scraper.py \
  scraper/core/deduplicator.py \
  scraper/core/multi_source_scraper.py \
  scraper/web_api.py \
  scraper/core/session.py \
  scraper/core/storage.py \
  scraper/templates/index.html

# 2. Upload
scp multi-source-update.tar.gz root@143.198.219.220:~

# 3. SSH and extract
ssh root@143.198.219.220

# On server:
cd /home/scraper/news-scraper
tar -xzf ~/multi-source-update.tar.gz
sudo systemctl restart news-scraper
sudo systemctl status news-scraper

# 4. Check logs
sudo journalctl -u news-scraper -f
```

### Verify Digital Ocean

Open: http://143.198.219.220

Check for:
- [ ] 3 source checkboxes (BlockBeats, Jinse, PANews)
- [ ] Deduplication toggle
- [ ] 4 log tabs (全部, BlockBeats, Jinse, PANews)

---

## 🎨 Deploy to Render

### Auto-Deploy (Recommended)

```bash
# 1. Commit and push
git add .
git commit -m "Add multi-source scraper with deduplication"
git push origin main

# 2. Render auto-deploys (wait 2-3 minutes)
# Watch progress at: https://dashboard.render.com
```

**Time:** ~3-5 minutes (automatic)

### Manual Deploy (if auto-deploy disabled)

1. Go to https://dashboard.render.com
2. Find your service: **crypto-news-scraper**
3. Click "Manual Deploy" → "Deploy latest commit"
4. Wait for deployment to complete

### Verify Render

Open: https://crypto-news-scraper.onrender.com

Check for:
- [ ] 3 source checkboxes (BlockBeats, Jinse, PANews)
- [ ] Deduplication toggle
- [ ] 4 log tabs (全部, BlockBeats, Jinse, PANews)

---

## 🧪 Test Multi-Source Features

### Test on Digital Ocean

```bash
# Open in browser
open http://143.198.219.220
```

### Test on Render

```bash
# Open in browser
open https://crypto-news-scraper.onrender.com
```

### Test Checklist

1. **Select all 3 sources**
   - ✓ BlockBeats
   - ✓ Jinse
   - ✓ PANews

2. **Configure search**
   - Time range: 3 days
   - Keywords: `BTC, Bitcoin, 比特币`
   - Article limit: 20 per source
   - ✓ Enable deduplication

3. **Start scraping**
   - Click "开始爬取"
   - Watch logs appear

4. **Switch log tabs**
   - Click "全部" - see all logs
   - Click "BlockBeats" - see BlockBeats only
   - Click "Jinse" - see Jinse only
   - Click "PANews" - see PANews only

5. **Check results**
   - See completion message
   - See per-source statistics
   - See deduplication stats
   - Download CSV
   - Verify articles from all sources

---

## 📊 Expected Results

### Log Output

```
🚀 开始多源爬取...
📰 来源: BLOCKBEATS, JINSE, PANEWS
🔄 去重: 启用

[BLOCKBEATS] 🔍 正在查找最新文章ID...
[BLOCKBEATS] ✅ 找到最新文章ID: 320000
[JINSE] 🔍 正在查找金色财经最新文章ID...
[JINSE] ✅ 找到最新文章ID: 7000000
[PANEWS] 🔍 正在查找PANews最新文章ID...
[PANEWS] ✅ 找到最新文章ID: 800000

[BLOCKBEATS] [1] ✅ 已保存: Bitcoin价格突破...
[JINSE] [1] ✅ 已保存: 比特币行情分析...
[PANEWS] [1] ✅ 已保存: BTC市场动态...

📊 各来源统计:
  BLOCKBEATS: 检查 20 篇, 抓取 5 篇
  JINSE: 检查 20 篇, 抓取 7 篇
  PANEWS: 检查 20 篇, 抓取 4 篇

🔍 去重统计: 移除 2 篇重复文章
✅ 爬取完成！最终保存 14 篇唯一文章
```

---

## 🔧 Troubleshooting

### Digital Ocean Issues

**Service won't start:**
```bash
ssh root@143.198.219.220
sudo journalctl -u news-scraper -n 100
```

**Reinstall dependencies:**
```bash
ssh root@143.198.219.220
cd /home/scraper/news-scraper
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
sudo systemctl restart news-scraper
```

**Check if files uploaded:**
```bash
ssh root@143.198.219.220
ls -la /home/scraper/news-scraper/scraper/core/jinse_scraper.py
ls -la /home/scraper/news-scraper/scraper/core/panews_scraper.py
ls -la /home/scraper/news-scraper/scraper/core/deduplicator.py
```

### Render Issues

**Check deployment logs:**
1. Go to https://dashboard.render.com
2. Click on **crypto-news-scraper**
3. Click "Logs" tab
4. Look for errors

**Manual redeploy:**
1. Go to dashboard
2. Click "Manual Deploy"
3. Select "Clear build cache & deploy"

**Check build logs:**
- Look for import errors
- Check if all files are in repo
- Verify requirements.txt is correct

---

## ✅ Deployment Checklist

### Pre-Deployment
- [x] All new files exist locally
- [x] Tested locally with `python test_web_interface_multi_source.py`
- [x] Digital Ocean IP confirmed: 143.198.219.220
- [x] Render URL confirmed: crypto-news-scraper.onrender.com

### Digital Ocean Deployment
- [ ] Run `./deploy_multi_source_update.sh`
- [ ] Wait for completion (~2-3 min)
- [ ] Check logs: `ssh root@143.198.219.220 "sudo journalctl -u news-scraper -f"`
- [ ] Test in browser: http://143.198.219.220
- [ ] Verify all features work

### Render Deployment
- [ ] Commit changes: `git add . && git commit -m "Multi-source update"`
- [ ] Push to GitHub: `git push origin main`
- [ ] Wait for auto-deploy (~3-5 min)
- [ ] Check dashboard: https://dashboard.render.com
- [ ] Test in browser: https://crypto-news-scraper.onrender.com
- [ ] Verify all features work

### Post-Deployment
- [ ] Test multi-source scraping on both platforms
- [ ] Test log tab switching
- [ ] Test deduplication
- [ ] Test CSV download
- [ ] Share updated URLs with team

---

## 🎯 Quick Commands

### Deploy to Digital Ocean
```bash
./deploy_multi_source_update.sh
```

### Deploy to Render
```bash
git add .
git commit -m "Multi-source update"
git push
```

### Check Digital Ocean Status
```bash
ssh root@143.198.219.220 "sudo systemctl status news-scraper"
```

### View Digital Ocean Logs
```bash
ssh root@143.198.219.220 "sudo journalctl -u news-scraper -f"
```

### Restart Digital Ocean Service
```bash
ssh root@143.198.219.220 "sudo systemctl restart news-scraper"
```

---

## 📞 Support

**If you encounter issues:**

1. **Check this file first** - most common issues covered
2. **Check logs** - errors usually show there
3. **Test locally** - `python test_web_interface_multi_source.py`
4. **Verify files** - make sure all new files exist

**Your URLs:**
- Digital Ocean: http://143.198.219.220
- Render: https://crypto-news-scraper.onrender.com

---

## 🎉 Ready to Deploy!

**Choose your deployment:**

**Quick (both platforms):**
```bash
# Deploy to Digital Ocean
./deploy_multi_source_update.sh

# Deploy to Render
git add . && git commit -m "Multi-source update" && git push
```

**Time:** ~5-8 minutes total

---

**Deployment guide for your specific setup** 🚀
