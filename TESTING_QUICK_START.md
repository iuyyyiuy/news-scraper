# Testing Quick Start 🚀

## Start Testing in 3 Steps

### 1️⃣ Start the Server
```bash
./START_WEB_SERVER.sh
```

### 2️⃣ Open Browser
Go to: **http://localhost:8000**

### 3️⃣ Run Quick Test
- Date: **2 days**
- Keywords: **BTC, Bitcoin, 比特币, ETH, 以太坊**
- Sources: **✓ All 3**
- Articles: **10**

Click **Start Scraping** and wait ~1 minute

---

## What to Check ✅

### "全部" Tab (Should be CLEAN)
```
✅ Shows: Matched articles only
❌ Hides: Filtered articles, skipped articles
```

### Source Tabs (Should be COMPLETE)
```
✅ Shows: Everything (matched + filtered + skipped)
```

### Jinse Articles
```
✅ Titles: Specific (e.g., "Cardano周五因旧代码...")
❌ NOT: "金色财经_区块链资讯_数字货币行情分析"
✅ Dates: 2025-11-23 (no time)
```

---

## Quick Tests

| Test | Articles | Time | Purpose |
|------|----------|------|---------|
| Quick | 10 | 1 min | Basic functionality |
| Medium | 25 | 2 min | Stability check |
| Full | 50 | 3-5 min | Production test |

---

## Troubleshooting

### Server won't start?
```bash
lsof -i :8000  # Check if port is in use
kill -9 <PID>  # Kill the process
```

### Wrong titles/dates?
```bash
# Restart server
Ctrl+C
./START_WEB_SERVER.sh
```

### Browser issues?
- Hard refresh: **Cmd+Shift+R** (Mac) or **Ctrl+Shift+R** (Windows)
- Check console: **F12** or **Cmd+Option+I**

---

## Success = All Green ✅

- ✅ "全部" tab clean (no filtered logs)
- ✅ Source tabs complete (all logs visible)
- ✅ Jinse titles correct
- ✅ Dates show as 2025-MM-DD
- ✅ Each source checks specified articles
- ✅ No errors in console

---

## Files Created for You

1. **START_WEB_SERVER.sh** - Start the server
2. **WEB_INTERFACE_TEST_GUIDE.md** - Detailed testing guide
3. **TESTING_QUICK_START.md** - This file
4. **FINAL_IMPLEMENTATION_SUMMARY.md** - What was done
5. **JINSE_PARSER_FIX.md** - Parser fix details

---

## Ready? Let's Go! 🎯

```bash
./START_WEB_SERVER.sh
```

Then open **http://localhost:8000** and start testing!

---

## Need Help?

Check these files:
- **WEB_INTERFACE_TEST_GUIDE.md** - Full testing instructions
- **IMPLEMENTATION_COMPLETE.md** - What was implemented
- **QUICK_REFERENCE.md** - Quick commands

Or review the test results from Jinse standalone test:
```bash
cd /Users/kabellatsang/PycharmProjects/ai_code
python test_jinse_only.py
```

---

**Everything is ready! Start the server and begin testing! 🚀**
