# 🚀 Deploy Now - Your Setup

## Your URLs

- **Digital Ocean**: http://143.198.219.220
- **Render**: https://crypto-news-scraper.onrender.com

---

## ⚡ One Command Deploy (Both Platforms)

```bash
./deploy_both.sh
```

This will:
1. Deploy to Digital Ocean (143.198.219.220)
2. Push to GitHub and trigger Render auto-deploy
3. Show you the status of both

**Time: ~5 minutes total**

---

## 📦 Deploy to Digital Ocean Only

```bash
./deploy_multi_source_update.sh
```

**Time: ~2-3 minutes**

---

## 🎨 Deploy to Render Only

```bash
git add .
git commit -m "Multi-source update"
git push
```

**Time: ~3-5 minutes (auto-deploy)**

---

## ✅ After Deployment

### Test Digital Ocean
```bash
open http://143.198.219.220
```

### Test Render
```bash
open https://crypto-news-scraper.onrender.com
```

### Verify Features
- [ ] See 3 source checkboxes
- [ ] See 4 log tabs (全部, BlockBeats, Jinse, PANews)
- [ ] Can scrape from multiple sources
- [ ] Logs appear in correct tabs
- [ ] Deduplication works
- [ ] Can download CSV

---

## 🔧 Quick Troubleshooting

### Digital Ocean not working?
```bash
ssh root@143.198.219.220 "sudo journalctl -u news-scraper -f"
```

### Render not working?
Check: https://dashboard.render.com → crypto-news-scraper → Logs

---

## 📞 Need Help?

Read: `DEPLOY_YOUR_SETUP.md` (detailed guide for your setup)

---

**Ready? Run `./deploy_both.sh` now! 🎯**
