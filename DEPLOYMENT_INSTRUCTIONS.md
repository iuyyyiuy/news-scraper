# 🚀 Quick Deployment Instructions

## Choose Your Deployment Method

### 🌊 Digital Ocean (Recommended for Production)

**Quick Update (if already deployed):**
```bash
# 1. Update the IP in the script
nano deploy_multi_source_update.sh
# Change SERVER_IP to your actual IP

# 2. Make executable and run
chmod +x deploy_multi_source_update.sh
./deploy_multi_source_update.sh
```

**First Time Deployment:**
```bash
# 1. Follow the full guide
cat DEPLOYMENT_MULTI_SOURCE.md

# 2. Or use the automated script
chmod +x deploy.sh
./deploy.sh
```

**Access:** `http://YOUR_SERVER_IP`

---

### 🎨 Render.com (Recommended for Testing)

**One-Click Deploy:**

1. Push your code to GitHub:
```bash
git add .
git commit -m "Add multi-source scraper"
git push
```

2. Go to https://render.com
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Render will auto-detect `render.yaml` and configure everything
6. Click "Create Web Service"

**Or Manual Setup:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn scraper.web_api:app --host 0.0.0.0 --port $PORT`

**Access:** `https://your-app-name.onrender.com`

---

## ✅ Verify Deployment

After deployment, test these features:

1. **Multi-Source Selection**
   - [ ] See checkboxes for BlockBeats, Jinse, PANews
   - [ ] Can select/deselect sources

2. **Log Tabs**
   - [ ] See tabs: 全部, BlockBeats, Jinse, PANews
   - [ ] Can switch between tabs
   - [ ] Logs appear in correct tabs

3. **Scraping**
   - [ ] Start a scrape with all 3 sources
   - [ ] See real-time progress
   - [ ] See per-source logs

4. **Deduplication**
   - [ ] Toggle deduplication on/off
   - [ ] See deduplication statistics in logs

5. **Download**
   - [ ] Download CSV after completion
   - [ ] CSV contains articles from all sources
   - [ ] Source visible in URL column

---

## 🔧 Quick Troubleshooting

### Service won't start
```bash
# Digital Ocean
ssh root@YOUR_IP
sudo journalctl -u news-scraper -n 50

# Render
Check "Logs" tab in dashboard
```

### Missing files
```bash
# Verify files exist
ls -la scraper/core/jinse_scraper.py
ls -la scraper/core/panews_scraper.py
ls -la scraper/core/deduplicator.py
ls -la scraper/core/multi_source_scraper.py
```

### Test locally first
```bash
python test_web_interface_multi_source.py
# Open http://localhost:8000
```

---

## 📊 What's New in This Deployment

### New Files Added:
- `scraper/core/jinse_scraper.py` - Jinse (金色财经) scraper
- `scraper/core/panews_scraper.py` - PANews scraper
- `scraper/core/deduplicator.py` - Smart deduplication engine
- `scraper/core/multi_source_scraper.py` - Multi-source coordinator

### Updated Files:
- `scraper/web_api.py` - Multi-source API support
- `scraper/core/session.py` - Per-source logging
- `scraper/core/storage.py` - InMemoryDataStore
- `scraper/templates/index.html` - Log tabs UI

### New Features:
- ✅ 3 news sources (BlockBeats, Jinse, PANews)
- ✅ Per-source log tabs
- ✅ Smart deduplication (85% title, 80% body similarity)
- ✅ Parallel scraping
- ✅ Source selection UI
- ✅ Real-time per-source progress

---

## 💡 Tips

### For Digital Ocean:
- Use `deploy_multi_source_update.sh` for quick updates
- Backs up old files automatically
- Only uploads changed files (faster)

### For Render:
- Just `git push` to deploy updates
- Auto-deploys on every push
- Free tier sleeps after 15 min (upgrade to $7/month for 24/7)

### For Both:
- Test locally first: `python test_web_interface_multi_source.py`
- Check logs if issues occur
- Verify all new files are present

---

## 📞 Need Help?

1. **Check logs first**
   - Digital Ocean: `sudo journalctl -u news-scraper -f`
   - Render: Dashboard → Logs tab

2. **Test locally**
   - `python test_web_interface_multi_source.py`
   - Open http://localhost:8000

3. **Verify files**
   - Check all new files exist
   - Check file permissions

4. **Review guides**
   - `DEPLOYMENT_MULTI_SOURCE.md` - Full guide
   - `DIGITAL_OCEAN_DEPLOYMENT.md` - Digital Ocean specific
   - `RENDER_DEPLOYMENT.md` - Render specific

---

## 🎉 Success Checklist

After deployment, you should have:

- [ ] Web interface accessible at your URL
- [ ] 3 source checkboxes visible
- [ ] Deduplication toggle visible
- [ ] 4 log tabs (全部, BlockBeats, Jinse, PANews)
- [ ] Can scrape from multiple sources
- [ ] Can switch between log tabs
- [ ] Can download combined CSV
- [ ] Deduplication working (check logs)

---

**Ready to deploy? Choose your method above and follow the steps!** 🚀
