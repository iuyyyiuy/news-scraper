# Streaming Analysis Module

## Overview

The streaming analysis module provides real-time trade processing capabilities with sliding window analysis, Redis caching, and near real-time alert generation.

## Components

### 1. StreamingProcessor

Main class for real-time trade analysis.

**Features:**
- Real-time trade processing
- Sliding window analysis
- Configurable alert thresholds
- Alert callbacks for immediate notifications
- Automatic periodic analysis
- Statistics tracking

**Usage:**
```python
from trade_risk_analyzer.detection.engine import DetectionEngine, DetectionConfig
from trade_risk_analyzer.detection.streaming_processor import (
    StreamingProcessor,
    StreamingConfig
)

# Create detection engine
engine = DetectionEngine(config=DetectionConfig())

# Create streaming processor
config = StreamingConfig(
    window_size_minutes=5,
    slide_interval_seconds=30,
    enable_redis=False
)
processor = StreamingProcessor(detection_engine=engine, config=config)

# Process individual trades
alerts = processor.process_trade(trade)

# Process batch of trades
result = processor.process_trades_batch(trades)

# Add alert callback
def on_alert(alert):
    print(f"Alert: {alert.pattern_type.value}")

processor.add_alert_callback(on_alert)
```

### 2. SlidingWindow

Maintains a time-based sliding window of recent trades.

**Features:**
- Configurable window size (minutes)
- Maximum size limit
- Thread-safe operations
- Automatic old trade removal
- DataFrame conversion

**Usage:**
```python
from trade_risk_analyzer.detection.streaming_processor import SlidingWindow

window = SlidingWindow(window_size_minutes=5, max_size=10000)

# Add trades
window.add_trade(trade)
window.add_trades_batch(trades)

# Get window trades
current_trades = window.get_window_trades()
df = window.get_trades_dataframe()
```

### 3. RedisCache

Optional Redis integration for caching recent trades and alerts.

**Features:**
- Trade caching with TTL
- Alert caching
- Recent trade retrieval
- Configurable key prefix

**Usage:**
```python
from trade_risk_analyzer.detection.streaming_processor import (
    RedisCache,
    StreamingConfig
)

config = StreamingConfig(
    enable_redis=True,
    redis_host='localhost',
    redis_port=6379
)
cache = RedisCache(config)

# Cache trade
cache.cache_trade(trade)

# Get recent trades
recent = cache.get_recent_trades(user_id='user_123', limit=100)
```

### 4. StreamingConfig

Configuration for streaming processor.

**Parameters:**
- `window_size_minutes`: Size of sliding window (default: 5)
- `slide_interval_seconds`: Interval between analyses (default: 30)
- `max_window_size`: Maximum trades in window (default: 10000)
- `batch_size`: Batch size for processing (default: 100)
- `min_trades_for_analysis`: Minimum trades to trigger analysis (default: 10)
- `alert_threshold_score`: Minimum score for alerts (default: 50.0)
- `enable_immediate_alerts`: Enable real-time alerts (default: True)
- `enable_redis`: Enable Redis caching (default: False)
- `enable_auto_processing`: Enable automatic periodic analysis (default: False)
- `auto_process_interval_seconds`: Auto-process interval (default: 30)

## Configuration

Add to `config.yaml`:

```yaml
streaming:
  window_size_minutes: 5
  slide_interval_seconds: 30
  max_window_size: 10000
  batch_size: 100
  min_trades_for_analysis: 10
  alert_threshold_score: 50.0
  enable_immediate_alerts: true
  enable_redis: false
  enable_auto_processing: false
  auto_process_interval_seconds: 30

redis:
  host: localhost
  port: 6379
  db: 0
  ttl: 3600
```

## Examples

See `example_streaming_analysis.py` for complete examples:

1. **Basic Streaming Analysis**: Process trades one by one with real-time alerts
2. **Batch Streaming Analysis**: Process trades in batches
3. **Sliding Window Behavior**: Understand how the sliding window works

## Performance

- Processes trades in near real-time (< 100ms per window analysis)
- Supports thousands of trades per minute
- Memory-efficient with configurable window size
- Thread-safe for concurrent access

## Requirements

- Python 3.9+
- pandas
- numpy
- redis (optional, for Redis caching)

## Testing

Run tests:
```bash
python test_streaming_processor.py
```

Run examples:
```bash
python example_streaming_analysis.py
```

## Architecture

```
StreamingProcessor
├── SlidingWindow (maintains recent trades)
├── RedisCache (optional caching)
├── DetectionEngine (analysis)
└── AlertManager (alert handling)
```

## Use Cases

1. **Real-time Monitoring**: Monitor live trading activity for suspicious patterns
2. **High-Frequency Trading Detection**: Detect rapid trading patterns as they occur
3. **Immediate Alerts**: Generate alerts within seconds of suspicious activity
4. **Streaming Data Pipelines**: Integrate with Kafka, RabbitMQ, or other streaming platforms
5. **API Integration**: Provide real-time analysis via REST/WebSocket APIs

## Future Enhancements

- WebSocket support for real-time alert streaming
- Kafka integration for distributed streaming
- Advanced windowing strategies (tumbling, hopping)
- Multi-symbol analysis
- Distributed processing with multiple workers
