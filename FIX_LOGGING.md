# Logging Fixes for Multi-Source Scraper

## Issues to Fix:

1. **"全部" (All) tab**: Should only show successfully matched news
2. **Per-source tabs**: Should show all logs (including filtered)
3. **Jinse scraper**: Verify it's working correctly

## Changes Needed:

### 1. Update `scraper/core/session.py`

Add a `show_in_all` parameter to the `add_log` method to control which logs appear in the "All" tab.

### 2. Update scrapers to mark logs appropriately

- Success logs: `show_in_all=True`
- Filtered/skipped logs: `show_in_all=False`
- Info/progress logs: `show_in_all=True` (for important info only)

### 3. Update `scraper/templates/index.html`

Filter logs in the "All" tab to only show logs marked with `show_in_all=True`.

## Implementation:

See the updated files in the next commits.
