# ZEROLEND Market Analysis Setup

## Prerequisites

To analyze the ZEROLEND spot market, you need to install the CoinEx MCP server dependencies.

### Install UV (Python Package Manager)

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using Homebrew
brew install uv

# Or using pip
pip install uv
```

After installation, restart your terminal or run:
```bash
source ~/.bashrc  # or ~/.zshrc
```

### Verify Installation

```bash
uvx --version
```

## Running the Analysis

Once `uvx` is installed, run:

```bash
python analyze_zerolend_market.py
```

## What the Analysis Does

The script will:

1. **Connect to CoinEx MCP Server** - Fetches real-time market data
2. **Retrieve Ticker Data** - Price, volume, 24h change
3. **Analyze K-line Data** - 100 recent 1-minute candles
4. **Examine Order Book** - Bid/ask spread and imbalance
5. **Review Recent Trades** - Buy/sell volume distribution
6. **Detect Manipulation Patterns**:
   - Pump and dump schemes
   - Spoofing/layering
   - Wash trading
   - Order book manipulation
7. **Calculate Health Score** - Overall market health (0-100)

## Expected Output

```
============================================================
ZEROLEND Spot Market Analysis
Market: ZEROLENDUSDT
Time: 2025-11-12 16:53:07
============================================================

✅ Connected to MCP server

1. Ticker Data:
   Last Price: $0.000123
   24h Volume: $45,678.90
   24h Change: +5.23%
   ...

2. K-line Data (Last 100 candles, 1min interval):
   Retrieved 100 candles
   ...

3. Order Book (Depth: 20):
   Best Bid: $0.000122
   Best Ask: $0.000124
   Spread: $0.000002 (1.639%)
   ...

4. Recent Trades (Last 100):
   Buy Volume: 12,345.67 (55.2%)
   Sell Volume: 10,012.34 (44.8%)
   ...

============================================================
MANIPULATION DETECTION ANALYSIS
============================================================

🚨 ALERTS DETECTED: 2 potential issues found

Alert #1:
  Pattern: PUMP_AND_DUMP
  Risk Level: HIGH
  Anomaly Score: 85.50/100
  Explanation: Sudden volume spike detected...
  ...

============================================================
MARKET HEALTH SUMMARY
============================================================

Overall Health Score: 65/100
Status: ⚠️  CAUTION

Issues Detected:
  • Wide spread (1.64%)
  • 2 manipulation alerts
```

## Alternative: Manual MCP Testing

If you want to test the MCP connection manually:

```bash
# Test if uvx works
uvx coinex-mcp-server --help

# Test a single MCP call
uvx coinex-mcp-server get_ticker ZEROLENDUSDT
```

## Troubleshooting

### Error: "No such file or directory: 'uvx'"
- Install `uv` using the instructions above
- Make sure `uvx` is in your PATH

### Error: "Failed to connect to MCP server"
- Check your internet connection
- Verify CoinEx API is accessible
- Try running `uvx coinex-mcp-server` manually

### Error: "No ticker data available"
- The market symbol might be incorrect
- Try: ZEROLENDUSDT, ZEROLEND/USDT, or check CoinEx for the exact symbol
- Use `get_all_tickers()` to list available markets

## Next Steps

After successful analysis:

1. Review the health score and alerts
2. If manipulation detected, investigate further
3. Set up continuous monitoring with `MultiMarketMonitor`
4. Store results in database for historical analysis
5. Train ML models with the collected data
