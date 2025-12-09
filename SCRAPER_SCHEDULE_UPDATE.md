# Scraper Schedule Updated

## Changes Made

### 1. Schedule Time Changed
- **Old**: 8:00 AM UTC+8
- **New**: 11:30 AM UTC+8

### 2. Timezone Fix
Fixed `scraped_at` timestamp to use UTC properly:
- Changed from `datetime.now().isoformat()` (local time)
- To `datetime.now(timezone.utc).isoformat()` (UTC time)
- Frontend JavaScript adds 8 hours to display Hong Kong time

### 3. How It Works Now

**Backend (Supabase)**:
- Stores all timestamps in UTC
- `scraped_at` field uses UTC time

**Frontend (Dashboard)**:
- Reads UTC time from API
- Adds 8 hours (8 * 60 * 60 * 1000 ms)
- Displays as Hong Kong Time (UTC+8)

**Scheduler**:
- Uses `pytz.timezone('Asia/Shanghai')` for scheduling
- Runs at 11:30 AM Hong Kong Time every day
- Monthly cleanup runs on 1st at 00:00 Hong Kong Time

## Testing

### Test Scraper Now:
```bash
python3 test_scraper_now.py
```

### Check Schedule:
```bash
python3 scraper/core/scheduler.py
```

### View Dashboard:
```
http://localhost:8080/dashboard
```

The "最后更新" time will show the last time the scraper ran in Hong Kong Time (UTC+8).

## Next Scheduled Run
The scraper will run at **11:30 AM** today (2025-12-09) if the scheduler is running.

To start the scheduler in production, you need to run it as a background service.
