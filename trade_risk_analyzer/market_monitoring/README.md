# Market Monitoring Module

## Overview

The market monitoring module provides real-time surveillance of cryptocurrency markets to detect manipulation patterns **before** they fully materialize. Unlike traditional trade-based analysis that examines historical data, this module continuously monitors live market data including K-line (candlestick) patterns, order book depth, and market microstructure.

**Key Advantage**: Proactive detection of manipulation attempts in real-time, enabling immediate intervention.

## Integration with CoinEx MCP Server

This module integrates with the [CoinEx MCP Server](https://pypi.org/project/coinex-mcp-server/) to access real-time market data **without requiring API credentials**. All data is public market data.

### Installation

```bash
# Install uv (Python package manager)
pip install uv

# Install CoinEx MCP server
uvx coinex-mcp-server
```

No API keys or credentials needed!

## Components

### 1. MCPClient

Connects to CoinEx MCP server for real-time market data.

**Available Data:**
- Market tickers (price, volume, 24h change)
- K-line/candlestick data (multiple intervals)
- Order book depth (up to 50 levels)
- Recent trades
- Market information

**Usage:**
```python
from trade_risk_analyzer.market_monitoring import MCPClient

# Async usage
async with MCPClient() as client:
    # Get ticker
    ticker = await client.get_ticker("BTCUSDT")
    
    # Get K-line data
    klines = await client.get_kline("BTCUSDT", interval="1min", limit=100)
    
    # Get order book
    orderbook = await client.get_orderbook("BTCUSDT", depth=20)
    
    # Get recent trades
    trades = await client.get_recent_trades("BTCUSDT", limit=100)

# Simple synchronous usage
from trade_risk_analyzer.market_monitoring.mcp_client import SimpleMCPClient

client = SimpleMCPClient()
ticker = client.get_ticker("BTCUSDT")
```

### 2. KLineMonitor

Monitors K-line (candlestick) data for price manipulation patterns.

**Detects:**
- **Pump and Dump**: Rapid price increase followed by crash
- **Abnormal Volatility**: Unusual price swings
- **Price Spikes**: Sudden large price movements
- **Volume Spikes**: Unusual trading volume
- **Coordinated Movements**: Suspicious directional patterns

**Usage:**
```python
from trade_risk_analyzer.market_monitoring import KLineMonitor

monitor = KLineMonitor(
    pump_threshold=10.0,  # 10% price increase
    dump_threshold=-10.0,  # 10% price decrease
    volatility_threshold=5.0,  # 5 std devs
    volume_spike_threshold=3.0  # 3x average volume
)

# Analyze K-line data
anomalies = monitor.analyze_klines(klines, "BTCUSDT")

for anomaly in anomalies:
    print(f"Detected: {anomaly.anomaly_type.value}")
    print(f"Severity: {anomaly.severity}/100")
    print(f"Risk: {anomaly.risk_level.value}")

# Get market health score
health = monitor.get_market_health_score(klines, "BTCUSDT")
print(f"Health Score: {health['health_score']}/100")
print(f"Status: {health['status']}")  # healthy, moderate, concerning, high_risk
```

### 3. OrderBookMonitor

Monitors order book depth for manipulation patterns.

**Detects:**
- **Spoofing**: Large fake orders to manipulate perception
- **Layering**: Multiple orders at different levels
- **Order Book Imbalance**: Extreme buy/sell pressure
- **Spread Manipulation**: Artificially wide spreads
- **Thin Liquidity**: Markets vulnerable to manipulation
- **Wash Trading Indicators**: Symmetric order patterns

**Usage:**
```python
from trade_risk_analyzer.market_monitoring import OrderBookMonitor

monitor = OrderBookMonitor(
    spoofing_threshold=5.0,  # 5x volume ratio
    imbalance_threshold=0.7,  # 70% imbalance
    spread_threshold=1.0,  # 1% spread
    thin_liquidity_threshold=1000.0  # Min $1000 liquidity
)

# Analyze order book
anomalies = monitor.analyze_orderbook(orderbook, "BTCUSDT")

for anomaly in anomalies:
    print(f"Detected: {anomaly.anomaly_type.value}")
    print(f"Description: {anomaly.description}")

# Get liquidity metrics
snapshot = monitor._parse_orderbook(orderbook, "BTCUSDT")
metrics = monitor.get_liquidity_metrics(snapshot)
print(f"Total Liquidity: ${metrics['total_liquidity']}")
print(f"Spread: {metrics['spread_pct']}%")
print(f"Imbalance: {metrics['imbalance_ratio']}")
```

### 4. MarketAnalyzer

Coordinates all monitoring and generates comprehensive alerts.

**Features:**
- Continuous market monitoring
- Multi-market surveillance
- Integrated K-line and order book analysis
- Risk indicator calculation
- Alert generation and callbacks
- Recommended actions

**Usage:**
```python
from trade_risk_analyzer.market_monitoring import MarketAnalyzer

# Create analyzer
analyzer = MarketAnalyzer()

# Add alert callback
def on_alert(alert):
    print(f"ALERT: {alert.title}")
    print(f"Market: {alert.market}")
    print(f"Severity: {alert.severity}/100")
    print(f"Action: {alert.recommended_action}")

analyzer.add_alert_callback(on_alert)

# Analyze single market
alerts = await analyzer.analyze_market("BTCUSDT")

# Start continuous monitoring
await analyzer.start_monitoring(
    markets=["BTCUSDT", "ETHUSDT", "BNBUSDT"],
    interval_seconds=60  # Check every minute
)
```

## Detection Patterns

### Price Manipulation (K-line Analysis)

#### 1. Pump and Dump
**Pattern**: Rapid price increase (>10%) followed by rapid decrease
**Risk**: HIGH
**Action**: Investigate immediately, potential coordinated manipulation

#### 2. Abnormal Volatility
**Pattern**: Price volatility >5 standard deviations above normal
**Risk**: MEDIUM-HIGH
**Action**: Monitor closely, may indicate manipulation or major news

#### 3. Volume Spike
**Pattern**: Trading volume >3x average
**Risk**: MEDIUM
**Action**: Verify if legitimate interest or manipulation

#### 4. Coordinated Movement
**Pattern**: 10+ consecutive candles in same direction with >15% total change
**Risk**: MEDIUM-HIGH
**Action**: Check for coordinated trading activity

### Order Book Manipulation

#### 1. Spoofing
**Pattern**: Single order >5x average size at best bid/ask
**Risk**: HIGH
**Action**: Monitor for order cancellation, potential fake liquidity

#### 2. Layering
**Pattern**: Multiple uniform-sized orders across price levels
**Risk**: HIGH
**Action**: Watch for rapid cancellations, classic manipulation tactic

#### 3. Order Book Imbalance
**Pattern**: >70% of liquidity on one side
**Risk**: MEDIUM
**Action**: Expect price movement toward imbalanced side

#### 4. Spread Manipulation
**Pattern**: Bid-ask spread >1% of mid price
**Risk**: MEDIUM
**Action**: Market may be illiquid or manipulated

#### 5. Thin Liquidity
**Pattern**: Total order book value <$1000
**Risk**: HIGH
**Action**: Market vulnerable to manipulation, increase monitoring

#### 6. Wash Trading Indicator
**Pattern**: >80% symmetry between bid and ask volumes
**Risk**: MEDIUM-HIGH
**Action**: Potential wash trading setup, monitor for matching trades

## Alert Types

### 1. PRICE_MANIPULATION
Generated when K-line analysis detects manipulation patterns.

**Triggers:**
- Pump and dump
- Abnormal volatility
- Price spikes
- Coordinated movements

### 2. ORDER_BOOK_MANIPULATION
Generated when order book shows manipulation patterns.

**Triggers:**
- Spoofing
- Layering
- Wash trading indicators

### 3. VOLUME_ANOMALY
Generated when unusual volume detected.

**Triggers:**
- Volume spikes
- Sudden volume changes

### 4. LIQUIDITY_RISK
Generated when market has insufficient liquidity.

**Triggers:**
- Thin liquidity
- Wide spreads

### 5. MARKET_HEALTH
Generated when overall market health is concerning.

**Triggers:**
- Low health score
- Multiple risk indicators

## Risk Indicators

Each market is continuously evaluated on:

- **Health Score** (0-100): Overall market health
- **Manipulation Risk** (0-100): Likelihood of manipulation
- **Liquidity Score** (0-100): Market liquidity level
- **Volatility Score** (0-100): Price stability
- **Overall Risk Level**: HIGH, MEDIUM, or LOW

## Continuous Monitoring

### Setup

```python
import asyncio
from trade_risk_analyzer.market_monitoring import MarketAnalyzer

async def monitor_markets():
    analyzer = MarketAnalyzer()
    
    # Add alert handler
    def handle_alert(alert):
        # Send to dashboard, database, email, etc.
        print(f"ALERT: {alert.title}")
        # Save to database
        # Send notification
        # Update dashboard
    
    analyzer.add_alert_callback(handle_alert)
    
    # Monitor multiple markets
    await analyzer.start_monitoring(
        markets=["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"],
        interval_seconds=60
    )

# Run monitoring
asyncio.run(monitor_markets())
```

### Integration with Detection Engine

```python
from trade_risk_analyzer.detection import DetectionEngine
from trade_risk_analyzer.market_monitoring import MarketAnalyzer

# Create both engines
detection_engine = DetectionEngine()
market_analyzer = MarketAnalyzer()

# When market alert is generated
def on_market_alert(alert):
    if alert.risk_level == RiskLevel.HIGH:
        # Trigger deeper analysis with detection engine
        # Get recent trades for this market
        trades = get_recent_trades(alert.market)
        
        # Run full detection
        result = detection_engine.detect(trades)
        
        # Generate comprehensive report
        if result.alerts:
            send_urgent_notification(alert, result)
```

## Configuration

Add to `config.yaml`:

```yaml
market_monitoring:
  # K-line monitoring
  kline:
    pump_threshold: 10.0  # % price increase
    dump_threshold: -10.0  # % price decrease
    volatility_threshold: 5.0  # std devs
    volume_spike_threshold: 3.0  # multiplier
    window_size: 20  # candles
  
  # Order book monitoring
  orderbook:
    spoofing_threshold: 5.0  # volume ratio
    imbalance_threshold: 0.7  # ratio
    spread_threshold: 1.0  # %
    thin_liquidity_threshold: 1000.0  # USD
    layering_levels: 5  # levels to check
  
  # Monitoring settings
  monitoring:
    interval_seconds: 60
    markets:
      - BTCUSDT
      - ETHUSDT
      - BNBUSDT
    
  # MCP settings
  mcp:
    server_command: "uvx"
    server_args: ["coinex-mcp-server"]
    timeout: 30
```

## Examples

See `example_market_monitoring.py` for comprehensive examples:

1. Basic market monitoring
2. Continuous monitoring
3. K-line analysis
4. Order book analysis
5. Simple synchronous client
6. Multi-market monitoring

Run examples:
```bash
python example_market_monitoring.py
```

## Use Cases

### 1. Exchange Surveillance
Monitor all trading pairs for manipulation in real-time.

### 2. Pre-Trade Analysis
Check market health before executing large orders.

### 3. Risk Management
Identify high-risk markets to avoid or increase margins.

### 4. Compliance Monitoring
Detect and report suspicious market activity.

### 5. Trading Strategy
Avoid markets with active manipulation.

### 6. Market Making
Identify spoofing and adjust quotes accordingly.

## Best Practices

### 1. Monitoring Frequency
- High-value markets: Every 30-60 seconds
- Medium-value markets: Every 2-5 minutes
- Low-value markets: Every 10-15 minutes

### 2. Alert Handling
- HIGH risk: Immediate investigation
- MEDIUM risk: Review within 5 minutes
- LOW risk: Log for analysis

### 3. False Positive Management
- Track alert accuracy
- Adjust thresholds based on market
- Use feedback system to improve

### 4. Resource Management
- Monitor 10-20 markets per instance
- Use async for efficiency
- Cache recent data

### 5. Integration
- Combine with trade-based detection
- Cross-reference with news/events
- Correlate across markets

## Advantages Over Trade-Based Analysis

| Aspect | Market Monitoring | Trade-Based Analysis |
|--------|------------------|---------------------|
| **Timing** | Real-time, proactive | Historical, reactive |
| **Detection** | Before manipulation completes | After manipulation occurred |
| **Data** | Order book, K-line, microstructure | Completed trades only |
| **Response** | Immediate intervention possible | Post-mortem analysis |
| **Coverage** | All market participants | Only executed trades |
| **Spoofing** | Detects fake orders | Cannot detect (orders cancelled) |
| **Prevention** | Can prevent manipulation | Can only document |

## Limitations

1. **Public Data Only**: Cannot see private orders or intentions
2. **False Positives**: Legitimate activity may trigger alerts
3. **Market Dependent**: Thresholds may need adjustment per market
4. **Latency**: Depends on MCP server and network speed
5. **No Historical Context**: Focuses on current state

## Future Enhancements

- Machine learning for pattern recognition
- Cross-market correlation analysis
- Predictive manipulation detection
- Integration with more exchanges
- Real-time dashboard
- Automated response actions
- Historical pattern database
- Alert clustering and deduplication

## Troubleshooting

### MCP Server Not Found
```bash
# Install uv and coinex-mcp-server
pip install uv
uvx coinex-mcp-server
```

### Connection Timeout
- Check internet connection
- Increase timeout in config
- Verify MCP server is running

### No Alerts Generated
- Markets may be healthy (good!)
- Adjust thresholds if too strict
- Verify data is being retrieved

### Too Many Alerts
- Thresholds may be too sensitive
- Adjust based on market characteristics
- Implement alert deduplication

## Support

For issues or questions:
1. Check example scripts
2. Review configuration
3. Check MCP server status
4. Review logs for errors
