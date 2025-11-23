# 🚀 Deploy Now - Quick Commands

## Digital Ocean (Quick Update)

```bash
# 1. Set your server IP
nano deploy_multi_source_update.sh
# Change: SERVER_IP="YOUR_IP_HERE"

# 2. Deploy
./deploy_multi_source_update.sh

# 3. Access
# Open: http://YOUR_IP
```

**Time: 2-3 minutes**

---

## Render.com (One-Click)

```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy multi-source scraper"
git push

# 2. Go to https://render.com
# 3. New + → Web Service → Connect repo
# 4. Click "Create Web Service"

# 5. Access
# Open: https://your-app.onrender.com
```

**Time: 5 minutes**

---

## Test First

```bash
python test_web_interface_multi_source.py
# Open: http://localhost:8000
```

---

## Verify After Deploy

- [ ] See 3 source checkboxes
- [ ] See 4 log tabs
- [ ] Can scrape from multiple sources
- [ ] Logs appear in correct tabs
- [ ] Can download CSV

---

## Need Help?

Read: `DEPLOYMENT_INSTRUCTIONS.md`

---

**Ready? Run the commands above! 🎯**
