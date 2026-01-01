# Parser Title & Date Bug Fix - January 1, 2026

## Problems Identified

### 1. Title Extraction Bug
The parser was extracting the same title "永续合约前传：用魔法公式为流动性定价，透明度让其无法发扬光大..." for ALL articles, regardless of their actual content.

### 2. Date Parsing Bug  
The parser was incorrectly converting 2025 dates to 2026. For example:
- Article from "2025-12-31" was being parsed as "2026-12-31"
- This caused the scraper to skip valid articles thinking they were from the future

### Evidence
User's curl commands showed different titles for each article:
- Article 326513: "Bithumb将上线XAUT韩元交易对"
- Article 326512: "张铮文：短期争议终将过去，专注于Neo持续建设和长期发展"  
- Article 326511: "Lummis：《负责任金融创新法案》将允许大型银行提供数字资产托管、质押和支付服务"

But the scraper logs showed:
- Same wrong title for all articles
- Dates like "2026-12-31" when they should be "2025-12-31"

## Root Cause Analysis

### Title Bug
The issue was in the title extraction strategy priority in `scraper/core/parser.py`. The parser was:
1. **Using unreliable selectors first**: Generic `h3`, `h2`, `h1` selectors were matching content that wasn't the actual article title
2. **Meta tags as fallback**: The most reliable sources (`og:title` and `<title>` tag) were used as fallbacks instead of primary sources

### Date Bug
The issue was in date parsing for Chinese dates without years (like "12月31日"):
1. **Naive year assignment**: Used `datetime.now().year` (2026) for all dates without years
2. **No future date logic**: Didn't consider that dates far in the future are likely from the previous year

## Solutions Implemented

### 1. Fixed Title Extraction Priority
Changed the extraction strategy to prioritize the most reliable sources:

```python
# NEW PRIORITY ORDER:
# 1. og:title meta tag (most reliable for BlockBeats)
# 2. <title> tag (second most reliable) 
# 3. Configured selectors
# 4. Other meta tags
# 5. Generic HTML selectors (last resort)
```

### 2. Fixed Date Parsing with Smart Year Logic
Added intelligent year determination for dates without years:

```python
def _determine_smart_year(self, month: int, day: int) -> int:
    """
    Intelligently determine the year for dates without year information.
    
    Logic:
    - If the date is more than 30 days in the future, assume it's from last year
    - Otherwise, use current year
    """
```

### 3. Updated 2025/2026 References
Updated hardcoded 2025 dates to 2026 in:
- `backfill_dec_10_20.py` - Updated date range to 2026-01-01 to 2026-01-10
- `scraper/core/parser.py` - Updated example date comments

## Files Modified
- `scraper/core/parser.py` - Fixed title extraction priority & date parsing logic
- `backfill_dec_10_20.py` - Updated 2025 dates to 2026
- `test_parser_fix_simple.py` - Created title extraction test
- `test_date_parsing_fix.py` - Created date parsing test
- `deploy_parser_fix.sh` - Updated deployment script

## Testing
Created comprehensive tests:
- `test_parser_fix_simple.py` - Tests title extraction with real articles
- `test_date_parsing_fix.py` - Tests date parsing logic and smart year assignment

## Deployment
Use `deploy_parser_fix.sh` to:
1. Upload fixed parser to Digital Ocean server
2. Run title extraction tests
3. Run date parsing tests  
4. Restart scheduler if all tests pass

## Expected Results
After deployment:
- ✅ Each article should have its correct, unique title
- ✅ No more duplicate titles across different articles
- ✅ Dates like "12月31日" should be parsed as 2025-12-31, not 2026-12-31
- ✅ Articles won't be skipped due to incorrect future dates
- ✅ Scheduler should work correctly with proper article data
- ✅ Date parsing should work correctly in 2026

## Next Steps
1. Deploy the fix using `./deploy_parser_fix.sh`
2. Monitor scheduler logs to confirm:
   - Different titles are being extracted for each article
   - Dates are being parsed correctly (2025 dates stay as 2025)
3. Complete automated scheduler setup once parser is confirmed working