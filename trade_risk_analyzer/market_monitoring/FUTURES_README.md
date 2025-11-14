# Futures Market Monitoring Module

Complete implementation of futures market monitoring with real-time data collection, analysis, and manipulation detection.

## Components

### 1. MCP Client Extensions (`mcp_client.py`)
- **Futures Ticker**: Real-time price, volume, open interest
- **Futures K-lines**: OHLCV data with open interest at multiple intervals
- **Futures Order Books**: Bid/ask depth for liquidity analysis
- **Funding Rates**: Current and historical funding rate data
- **Premium Index**: Mark price vs index price tracking
- **Basis History**: Futures-spot price spread over time
- **Liquidation Events**: Real-time liquidation tracking
- **Position Tiers**: Margin requirements and leverage limits

### 2. Futures Feature Extractors (`futures_features.py`)
Extracts ML-ready features from futures market data:
- Funding rate statistics (mean, std, deviation, volatility, trend)
- Premium/basis spread metrics
- Liquidation frequency and volume
- Open interest changes and trends
- Position concentration risk indicators
- Funding rate farming detection

### 3. Futures Detector (`futures_detector.py`)
Detects manipulation patterns specific to futures markets:
- **Funding Rate Manipulation**: Abnormal spikes >3 std deviations
- **Liquidation Hunting**: Cascade events (5+ liquidations in 1 minute)
- **Basis Manipulation**: Abnormal futures-spot spread (>2%)
- **Position Concentration**: Excessive concentration in single tier (>30%)
- **Forced Liquidations**: Coordinated liquidation patterns

### 4. Futures Market Analyzer (`futures_analyzer.py`)
Integrates MCP client with detection algorithms:
- Real-time market analysis
- Health score calculation
- Alert generation and callbacks
- Pattern-specific analysis methods

### 5. Multi-Market Monitor (`multi_market_monitor.py`)
Enhanced with futures support:
- Discovers both spot and futures markets
- Priority-based scheduling
- Adaptive check intervals
- Concurrent monitoring with resource limits

### 6. Data Collector (`data_collector.py`)
Periodic data collection and storage:
- Funding rates (every 5 minutes)
- Liquidations (every 1 minute)
- Basis history (every 1 hour)
- Orderbook snapshots (every 30 seconds)
- Automatic data cleanup

### 7. Database Models (`models.py`)
New tables for futures data:
- `futures_funding_rates`: Historical funding rate data
- `futures_liquidations`: Liquidation event records
- `futures_basis_history`: Futures-spot spread history
- `market_snapshots`: Orderbook and K-line snapshots

## Usage Examples

### Basic Futures Market Analysis

```python
from trade_risk_analyzer.market_monitoring.mcp_client import MCPClient
from trade_risk_analyzer.market_monitoring.futures_analyzer import FuturesMarketAnalyzer

# Initialize
mcp_client = MCPClient()
await mcp_client.connect()

analyzer = FuturesMarketAnalyzer(mcp_client)

# Analyze a market
alerts = await analyzer.analyze_futures_market("BTCUSDT")

for alert in alerts:
    print(f"Alert: {alert.pattern_type}")
    print(f"Risk: {alert.risk_level}")
    print(f"Score: {alert.anomaly_score}")
    print(f"Explanation: {alert.explanation}")
```

### Multi-Market Monitoring

```python
from trade_risk_analyzer.market_monitoring.multi_market_monitor import MultiMarketMonitor

# Initialize monitor
monitor = MultiMarketMonitor(
    min_volume_24h=10000,
    max_concurrent=5
)

# Start monitoring all futures markets
await monitor.start_monitoring_all(
    quote_currency="USDT",
    market_type="futures"  # or "spot" or "both"
)
```

### Data Collection

```python
from trade_risk_analyzer.market_monitoring.data_collector import FuturesDataCollector

# Initialize collector
collector = FuturesDataCollector(
    mcp_client=mcp_client,
    funding_rate_interval=300,  # 5 minutes
    liquidation_check_interval=60  # 1 minute
)

# Start collecting data
markets = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
await collector.start_collection(markets)
```

### Feature Extraction

```python
from trade_risk_analyzer.feature_engineering.futures_features import FuturesFeatureExtractor

extractor = FuturesFeatureExtractor()

# Extract all features
features = extractor.extract_all_futures_features(
    funding_history=funding_data,
    premium_data=premium_data,
    basis_history=basis_data,
    liquidations=liquidations,
    klines=klines,
    position_tiers=position_tiers,
    current_oi=current_open_interest
)

print(f"Funding rate deviation: {features['funding_rate_deviation_std']}")
print(f"Liquidation cascade detected: {features['liquidation_cascade_detected']}")
print(f"Basis anomaly: {features['basis_anomaly']}")
```

## Detection Thresholds

Default thresholds (configurable):
- **Funding Rate**: 3.0 std deviations
- **Basis Anomaly**: 2% deviation
- **Liquidation Cascade**: 5 liquidations in 1 minute
- **Position Concentration**: 30% in single tier
- **Premium Deviation**: 1% mark-index deviation

## Database Migration

Run the migration to add futures tables:

```bash
python trade_risk_analyzer/data_ingestion/migrations/add_futures_tables.py
```

Or with custom database URL:

```bash
python trade_risk_analyzer/data_ingestion/migrations/add_futures_tables.py postgresql://user:pass@localhost/db
```

## Configuration

Add to `config.yaml`:

```yaml
market_monitoring:
  enabled: true
  spot_markets: true
  futures_markets: true
  min_volume_24h: 10000
  max_concurrent_checks: 5
  
  futures_data_collection:
    funding_rate_interval: 300  # 5 minutes
    liquidation_check_interval: 60  # 1 minute
    basis_history_interval: 3600  # 1 hour
    orderbook_snapshot_interval: 30  # 30 seconds

detection:
  thresholds:
    funding_rate_std_deviation: 3.0
    basis_anomaly_threshold: 0.02
    liquidation_cascade_threshold: 5
    position_concentration_threshold: 0.3
    premium_deviation_threshold: 0.01
```

## Alert Types

### Funding Rate Manipulation
- **Pattern**: Abnormal funding rate spikes
- **Risk Level**: HIGH (score >85) or MEDIUM
- **Trigger**: >3 std deviations from mean

### Funding Rate Farming
- **Pattern**: Sustained high funding rates
- **Risk Level**: MEDIUM
- **Trigger**: 70% of recent periods above threshold

### Liquidation Cascade
- **Pattern**: Multiple liquidations in short time
- **Risk Level**: HIGH
- **Trigger**: 5+ liquidations within 1 minute

### Basis Manipulation
- **Pattern**: Abnormal futures-spot spread
- **Risk Level**: HIGH (>3%) or MEDIUM
- **Trigger**: Basis rate >2%

### Position Concentration
- **Pattern**: Excessive position in single tier
- **Risk Level**: MEDIUM
- **Trigger**: >30% concentration

### Forced Liquidations
- **Pattern**: Coordinated same-side liquidations
- **Risk Level**: MEDIUM
- **Trigger**: >80% same side

## Integration with ML Models

Futures features integrate seamlessly with existing ML models:

```python
from trade_risk_analyzer.feature_engineering.extractor import FeatureExtractor
from trade_risk_analyzer.feature_engineering.futures_features import FuturesFeatureExtractor

# Extract both spot and futures features
spot_extractor = FeatureExtractor()
futures_extractor = FuturesFeatureExtractor()

spot_features = spot_extractor.build_feature_vector(trades)
futures_features = futures_extractor.extract_all_futures_features(...)

# Combine for ML model input
combined_features = {**spot_features, **futures_features}
```

## Performance

- Supports monitoring 100+ futures markets concurrently
- Priority-based scheduling optimizes resource usage
- Adaptive check intervals based on market activity
- Database indexing for fast queries
- Redis caching for real-time data (optional)

## Next Steps

1. Run database migration
2. Configure monitoring parameters
3. Start multi-market monitor
4. Set up alert callbacks
5. Integrate with detection engine
6. Train ML models with futures features
