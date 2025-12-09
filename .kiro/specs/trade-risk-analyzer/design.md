# Trade Risk Analyzer - Design Document

## Overview

The Trade Risk Analyzer is a Python-based machine learning system that detects abnormal trading behaviors indicative of market manipulation, fraud, or suspicious activities. The system uses a combination of feature engineering, multiple ML algorithms, and rule-based detection to identify patterns such as wash trading, pump-and-dump schemes, high-frequency manipulation, and other anomalies.

The system is designed to be deployed on Digital Ocean as a scalable web service, with both batch processing capabilities for historical analysis and real-time streaming analysis for live monitoring.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Trade Risk Analyzer                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────┐      ┌───────────────┐                   │
│  │ Data Ingestion│─────▶│ Data Storage  │                   │
│  │   Module      │      │   (SQLite/    │                   │
│  └───────────────┘      │  PostgreSQL)  │                   │
│         │               └──────┬────────┘                   │
│         │                      │                            │
│         ▼                      ▼                            │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │Market Monitor│      │  Detection   │                     │
│  │  (MCP Client)│─────▶│    Engine    │                     │
│  │ - Spot       │      │              │                     │
│  │ - Futures    │      └──────┬───────┘                     │
│  └──────────────┘             │                             │
│         │                     │                             │ 
│         ▼                     ▼                             │
│  ┌──────────────┐      ┌───────────────┐                    │
│  │   Feature    │      │  ML Models    │                    │
│  │  Engineering │─────▶│  - Isolation  │                    │
│  │   Module     │      │    Forest     │                    │
│  └──────────────┘      │  - Autoencoder│                    │
│                        │  - Random     │                    │
│                        │    Forest     │                    │
│                        └──────┬────────┘                    │
│                               │                             │
│                               ▼                             │
│                        ┌──────────────┐                     │
│                        │   Reporting  │                     │
│                        │    Module    │                     │
│                        └──────────────┘                     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Web API (Flask/FastAPI)                    │   │
│  │  - REST endpoints for data upload                    │   │
│  │  - Analysis triggers                                 │   │
│  │  - Report retrieval                                  │   │
│  │  - Market monitoring                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```


### Technology Stack

**Core Framework:**
- Python 3.9+
- FastAPI for REST API (async support for better performance)
- Uvicorn as ASGI server

**Machine Learning:**
- scikit-learn (Isolation Forest, Random Forest)
- TensorFlow/Keras (Autoencoder for anomaly detection)
- pandas for data manipulation
- numpy for numerical operations

**Data Storage:**
- SQLite for development/testing
- PostgreSQL for production (Digital Ocean managed database)
- Redis for caching and real-time data streaming

**Deployment:**
- Docker containers
- Digital Ocean Droplet or App Platform
- Nginx as reverse proxy
- Gunicorn/Uvicorn workers

**Monitoring & Logging:**
- Python logging module
- Prometheus for metrics
- Grafana for visualization

## Components and Interfaces

### 1. Data Ingestion Module

**Purpose:** Import and validate trade data from various sources

**Classes:**
```python
class TradeDataImporter:
    """Handles importing trade data from CSV, JSON, and Excel formats"""
    
    def import_csv(file_path: str) -> pd.DataFrame
    def import_json(file_path: str) -> pd.DataFrame
    def import_excel(file_path: str) -> pd.DataFrame
    def validate_data(df: pd.DataFrame) -> ValidationResult
    def store_trades(df: pd.DataFrame) -> bool

class ValidationResult:
    """Contains validation results and error details"""
    
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[str]
    valid_records: int
    invalid_records: int
```

**Input Format:**
```json
{
  "user_id": "string",
  "timestamp": "ISO8601 datetime",
  "symbol": "string",
  "price": "float",
  "volume": "float",
  "trade_type": "BUY|SELL",
  "order_id": "string"
}
```

**Required Fields:**
- user_id: Unique identifier for the trader
- timestamp: Trade execution time
- symbol: Trading pair (e.g., BTC/USDT)
- price: Execution price
- volume: Trade volume
- trade_type: BUY or SELL

### 1.1 Market Monitoring Module (Real-Time via MCP)

**Purpose:** Monitor live market data from CoinEx exchange for both Spot and Futures markets

**Classes:**
```python
class MCPClient:
    """Client for CoinEx MCP server - handles both Spot and Futures markets"""
    
    # Spot Market Methods
    async def get_ticker(market: str) -> Dict[str, Any]
    async def get_kline(market: str, interval: str, limit: int) -> List[Dict]
    async def get_orderbook(market: str, depth: int) -> Dict[str, Any]
    async def get_recent_trades(market: str, limit: int) -> List[Dict]
    async def get_all_tickers() -> List[Dict[str, Any]]
    
    # Futures Market Methods
    async def get_futures_ticker(market: str) -> Dict[str, Any]
    async def get_futures_kline(market: str, interval: str, limit: int) -> List[Dict]
    async def get_futures_orderbook(market: str, depth: int) -> Dict[str, Any]
    async def get_futures_funding_rate(market: str) -> Dict[str, Any]
    async def get_futures_funding_rate_history(market: str, limit: int) -> List[Dict]
    async def get_futures_premium_index(market: str) -> Dict[str, Any]
    async def get_futures_basis_history(market: str, interval: str, limit: int) -> List[Dict]
    async def get_futures_liquidations(market: str, limit: int) -> List[Dict]
    async def get_futures_position_tiers(market: str) -> List[Dict]
    async def get_futures_market_info(market: Optional[str]) -> Dict[str, Any]
    async def get_all_futures_tickers() -> List[Dict[str, Any]]

class MultiMarketMonitor:
    """Monitors multiple markets efficiently with priority scheduling"""
    
    async def discover_markets(quote_currency: str, min_volume: float) -> List[str]
    async def discover_futures_markets(quote_currency: str, min_volume: float) -> List[str]
    async def start_monitoring_all(quote_currency: str, market_type: str) -> None
    async def start_monitoring_markets(markets: List[str], market_type: str) -> None
    def add_alert_callback(callback: Callable) -> None
    def get_statistics() -> Dict[str, Any]
    def get_high_risk_markets() -> List[str]

class MarketAnalyzer:
    """Analyzes market data for manipulation patterns"""
    
    async def analyze_market(market: str, market_type: str) -> List[MarketAlert]
    async def analyze_orderbook(orderbook: Dict) -> List[OrderbookAlert]
    async def analyze_kline(klines: List[Dict]) -> List[PriceAlert]
    async def analyze_funding_rate(funding_data: Dict) -> List[FundingAlert]
    async def analyze_liquidations(liquidations: List[Dict]) -> List[LiquidationAlert]
    async def detect_spoofing(orderbook_history: List[Dict]) -> Optional[Alert]
    async def detect_layering(orderbook_history: List[Dict]) -> Optional[Alert]
    async def detect_pump_dump(klines: List[Dict], volume_data: Dict) -> Optional[Alert]

class FuturesAnalyzer:
    """Specialized analyzer for futures market patterns"""
    
    async def analyze_funding_rate_manipulation(history: List[Dict]) -> List[Alert]
    async def analyze_basis_arbitrage(basis_history: List[Dict]) -> List[Alert]
    async def analyze_liquidation_cascades(liquidations: List[Dict]) -> List[Alert]
    async def analyze_position_concentration(position_tiers: List[Dict]) -> List[Alert]
    async def detect_funding_rate_farming(funding_history: List[Dict]) -> Optional[Alert]
    async def detect_forced_liquidations(liquidations: List[Dict], orderbook: Dict) -> Optional[Alert]
```

**Futures Market Data Structures:**

**Funding Rate:**
```json
{
  "market": "BTCUSDT",
  "funding_rate": "0.0001",
  "funding_time": "ISO8601 datetime",
  "next_funding_time": "ISO8601 datetime",
  "predicted_rate": "0.00012"
}
```

**Premium Index:**
```json
{
  "market": "BTCUSDT",
  "mark_price": "50000.00",
  "index_price": "49995.00",
  "premium": "5.00",
  "premium_rate": "0.0001",
  "timestamp": "ISO8601 datetime"
}
```

**Basis History:**
```json
{
  "timestamp": "ISO8601 datetime",
  "futures_price": "50000.00",
  "spot_price": "49995.00",
  "basis": "5.00",
  "basis_rate": "0.0001"
}
```

**Liquidation Data:**
```json
{
  "liquidation_id": "string",
  "market": "BTCUSDT",
  "side": "LONG|SHORT",
  "price": "50000.00",
  "volume": "1.5",
  "timestamp": "ISO8601 datetime",
  "type": "ADL|FORCED"
}
```

**Position Tiers (Margin Tiers):**
```json
{
  "market": "BTCUSDT",
  "tiers": [
    {
      "tier": 1,
      "max_position": "100",
      "maintenance_margin_rate": "0.005",
      "initial_margin_rate": "0.01",
      "max_leverage": "100"
    }
  ]
}
```

**Futures K-line:**
```json
{
  "timestamp": "ISO8601 datetime",
  "open": "50000.00",
  "high": "50500.00",
  "low": "49800.00",
  "close": "50200.00",
  "volume": "1500.5",
  "turnover": "75000000.00",
  "open_interest": "25000.00"
}
```

**Futures Order Book:**
```json
{
  "market": "BTCUSDT",
  "timestamp": "ISO8601 datetime",
  "bids": [
    ["50000.00", "10.5"],
    ["49999.00", "5.2"]
  ],
  "asks": [
    ["50001.00", "8.3"],
    ["50002.00", "12.1"]
  ],
  "last_price": "50000.50"
}
```

### 2. Feature Engineering Module

**Purpose:** Extract meaningful features from raw trade data for ML model input

**Classes:**
```python
class FeatureExtractor:
    """Extracts features from trade data"""
    
    def calculate_frequency_metrics(trades: pd.DataFrame, 
                                   windows: List[str]) -> pd.DataFrame
    def calculate_volume_statistics(trades: pd.DataFrame) -> pd.DataFrame
    def calculate_temporal_patterns(trades: pd.DataFrame) -> pd.DataFrame
    def calculate_price_impact(trades: pd.DataFrame, 
                              market_data: pd.DataFrame) -> pd.DataFrame
    def calculate_velocity_metrics(trades: pd.DataFrame) -> pd.DataFrame
    def build_feature_vector(trades: pd.DataFrame) -> np.ndarray
```

**Feature Categories:**

1. **Frequency Features:**
   - Trades per hour/day/week
   - Order-to-trade ratio
   - Cancellation rate
   - Quote stuffing indicator

2. **Volume Features:**
   - Mean/median/std volume
   - Volume percentile ranking
   - Volume spike detection
   - Volume consistency score

3. **Temporal Features:**
   - Hour-of-day distribution
   - Day-of-week patterns
   - Trading session concentration
   - Time between trades

4. **Price Impact Features:**
   - Price deviation from market average
   - Slippage metrics
   - Price reversal patterns
   - Spread analysis

5. **Behavioral Features:**
   - Account age
   - Trading pair diversity
   - Position holding time
   - Win/loss ratio

6. **Futures-Specific Features:**
   - Funding rate deviation from historical average
   - Funding rate volatility
   - Premium/basis spread anomalies
   - Liquidation frequency and volume
   - Position concentration by tier
   - Open interest changes
   - Mark price vs index price deviation
   - Leverage usage patterns
   - Funding rate farming indicators
   - Cascade liquidation risk score

### 3. Detection Engine

**Purpose:** Apply ML models and rule-based detection to identify anomalies

**Classes:**
```python
class DetectionEngine:
    """Orchestrates anomaly detection using multiple methods"""
    
    def __init__(self, config: DetectionConfig)
    def detect_anomalies(features: np.ndarray) -> DetectionResult
    def apply_rule_based_detection(trades: pd.DataFrame) -> List[RuleViolation]
    def calculate_anomaly_score(results: List[ModelResult]) -> float
    def assign_risk_flag(score: float) -> RiskLevel

class RuleBasedDetector:
    """Implements specific pattern detection rules"""
    
    def detect_wash_trading(trades: pd.DataFrame) -> List[Alert]
    def detect_pump_and_dump(trades: pd.DataFrame) -> List[Alert]
    def detect_layering(trades: pd.DataFrame) -> List[Alert]
    def detect_spoofing(trades: pd.DataFrame) -> List[Alert]
    def detect_hft_manipulation(trades: pd.DataFrame) -> List[Alert]
    
    # Futures-specific detection
    def detect_funding_rate_manipulation(funding_history: List[Dict]) -> List[Alert]
    def detect_liquidation_hunting(liquidations: List[Dict], orderbook: Dict) -> List[Alert]
    def detect_basis_manipulation(basis_history: List[Dict]) -> List[Alert]
    def detect_position_manipulation(position_tiers: List[Dict]) -> List[Alert]
```

**Detection Workflow:**
1. Extract features from trade data (including futures-specific features)
2. Apply unsupervised models (Isolation Forest, Autoencoder)
3. Apply supervised model if labeled data available (Random Forest)
4. Run rule-based detectors for specific patterns
5. Run futures-specific detectors (funding rate, liquidations, basis)
6. Aggregate scores using weighted ensemble
7. Assign risk flags based on thresholds

**Futures Market Detection Patterns:**

1. **Funding Rate Manipulation:**
   - Detect abnormal funding rate spikes (>3 std deviations)
   - Identify coordinated position building before funding time
   - Flag funding rate farming patterns

2. **Liquidation Hunting:**
   - Detect price movements targeting liquidation levels
   - Identify large orders placed near liquidation prices
   - Flag cascade liquidation events

3. **Basis Manipulation:**
   - Detect abnormal futures-spot price divergence
   - Identify arbitrage opportunities exploitation
   - Flag coordinated basis trading

4. **Position Concentration:**
   - Detect excessive position concentration in single tier
   - Identify whale manipulation patterns
   - Flag systemic risk from large positions

### 4. ML Models Module

**Purpose:** Train and deploy machine learning models for anomaly detection

**Model 1: Isolation Forest (Unsupervised)**
- Best for: General anomaly detection without labeled data
- Use case: Initial deployment, discovering unknown patterns
- Parameters: n_estimators=100, contamination=0.1, max_features=1.0

**Model 2: Autoencoder (Unsupervised)**
- Best for: Complex pattern recognition, high-dimensional data
- Architecture:
  ```
  Input Layer (n_features)
  ↓
  Dense(64, activation='relu')
  ↓
  Dense(32, activation='relu') ← Bottleneck
  ↓
  Dense(64, activation='relu')
  ↓
  Output Layer (n_features)
  ```
- Anomaly detection: High reconstruction error indicates anomaly

**Model 3: Random Forest Classifier (Supervised)**
- Best for: When labeled training data is available
- Use case: Fine-tuning detection after collecting feedback
- Parameters: n_estimators=200, max_depth=20, class_weight='balanced'

**Classes:**
```python
class ModelTrainer:
    """Handles model training and evaluation"""
    
    def train_isolation_forest(X_train: np.ndarray) -> IsolationForest
    def train_autoencoder(X_train: np.ndarray, 
                         epochs: int = 50) -> tf.keras.Model
    def train_random_forest(X_train: np.ndarray, 
                           y_train: np.ndarray) -> RandomForestClassifier
    def evaluate_model(model, X_test: np.ndarray, 
                      y_test: np.ndarray) -> ModelMetrics
    def save_model(model, path: str) -> bool
    def load_model(path: str) -> Model

class ModelEnsemble:
    """Combines predictions from multiple models"""
    
    def __init__(self, models: List[Model], weights: List[float])
    def predict(features: np.ndarray) -> np.ndarray
    def predict_proba(features: np.ndarray) -> np.ndarray
```

### 5. Reporting Module

**Purpose:** Generate risk assessment reports and visualizations

**Classes:**
```python
class ReportGenerator:
    """Generates analysis reports in various formats"""
    
    def generate_daily_summary(date: datetime) -> Report
    def generate_user_risk_profile(user_id: str) -> Report
    def generate_pattern_analysis(pattern_type: str) -> Report
    def export_to_pdf(report: Report, output_path: str) -> bool
    def export_to_csv(report: Report, output_path: str) -> bool
    def export_to_json(report: Report) -> dict

class Alert:
    """Represents a risk alert"""
    
    alert_id: str
    timestamp: datetime
    user_id: str
    trade_ids: List[str]
    anomaly_score: float
    risk_level: RiskLevel
    pattern_type: str
    explanation: str
    recommended_action: str
```

**Report Structure:**
```json
{
  "report_id": "string",
  "generated_at": "ISO8601 datetime",
  "period": {
    "start": "ISO8601 datetime",
    "end": "ISO8601 datetime"
  },
  "summary": {
    "total_trades_analyzed": "int",
    "total_users": "int",
    "high_risk_alerts": "int",
    "medium_risk_alerts": "int",
    "low_risk_alerts": "int"
  },
  "alerts": [
    {
      "alert_id": "string",
      "user_id": "string",
      "anomaly_score": "float",
      "risk_level": "HIGH|MEDIUM|LOW",
      "pattern_type": "string",
      "explanation": "string",
      "trade_details": []
    }
  ],
  "model_performance": {
    "precision": "float",
    "recall": "float",
    "f1_score": "float"
  }
}
```

### 6. Web API Module

**Purpose:** Provide REST API for system interaction

**Endpoints:**

```python
# Data Upload
POST /api/v1/trades/upload
Content-Type: multipart/form-data
Body: file (CSV/JSON/Excel)
Response: {"job_id": "string", "status": "processing"}

# Trigger Analysis
POST /api/v1/analysis/run
Body: {
  "start_date": "ISO8601",
  "end_date": "ISO8601",
  "user_ids": ["string"] (optional)
}
Response: {"job_id": "string", "status": "queued"}

# Get Analysis Results
GET /api/v1/analysis/{job_id}
Response: {
  "job_id": "string",
  "status": "completed|processing|failed",
  "results": Report
}

# Get Alerts
GET /api/v1/alerts?start_date=...&end_date=...&risk_level=...
Response: {
  "alerts": [Alert],
  "total": "int",
  "page": "int"
}

# Submit Feedback
POST /api/v1/feedback
Body: {
  "alert_id": "string",
  "is_true_positive": "boolean",
  "notes": "string"
}
Response: {"status": "success"}

# Get Configuration
GET /api/v1/config
Response: DetectionConfig

# Update Configuration
PUT /api/v1/config
Body: DetectionConfig
Response: {"status": "success"}

# Model Retraining
POST /api/v1/models/retrain
Body: {
  "model_type": "isolation_forest|autoencoder|random_forest",
  "use_feedback": "boolean"
}
Response: {"job_id": "string", "status": "training"}

# Market Monitoring Endpoints

# Start Market Monitoring
POST /api/v1/monitoring/start
Body: {
  "market_type": "spot|futures|both",
  "markets": ["BTCUSDT", "ETHUSDT"] (optional),
  "quote_currency": "USDT",
  "min_volume": 10000
}
Response: {"status": "monitoring", "markets_count": "int"}

# Stop Market Monitoring
POST /api/v1/monitoring/stop
Response: {"status": "stopped"}

# Get Monitoring Statistics
GET /api/v1/monitoring/stats
Response: {
  "total_markets": "int",
  "active_markets": "int",
  "total_checks": "int",
  "total_alerts": "int",
  "high_risk_markets": ["string"],
  "uptime_seconds": "float"
}

# Get Market Data (Spot)
GET /api/v1/markets/spot/{market}/ticker
GET /api/v1/markets/spot/{market}/kline?interval=1min&limit=100
GET /api/v1/markets/spot/{market}/orderbook?depth=20
GET /api/v1/markets/spot/{market}/trades?limit=100

# Get Market Data (Futures)
GET /api/v1/markets/futures/{market}/ticker
GET /api/v1/markets/futures/{market}/kline?interval=1min&limit=100
GET /api/v1/markets/futures/{market}/orderbook?depth=20
GET /api/v1/markets/futures/{market}/funding-rate
GET /api/v1/markets/futures/{market}/funding-history?limit=100
GET /api/v1/markets/futures/{market}/premium-index
GET /api/v1/markets/futures/{market}/basis-history?interval=1hour&limit=100
GET /api/v1/markets/futures/{market}/liquidations?limit=100
GET /api/v1/markets/futures/{market}/position-tiers

# Get All Markets
GET /api/v1/markets/spot/all
GET /api/v1/markets/futures/all
```

## Data Models

### Database Schema

**trades table:**
```sql
CREATE TABLE trades (
    trade_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,
    trade_type VARCHAR(10) NOT NULL,
    order_id VARCHAR(255),
    market_type VARCHAR(10) DEFAULT 'spot',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_timestamp (user_id, timestamp),
    INDEX idx_symbol_timestamp (symbol, timestamp),
    INDEX idx_market_type (market_type)
);
```

**futures_funding_rates table:**
```sql
CREATE TABLE futures_funding_rates (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    market VARCHAR(50) NOT NULL,
    funding_rate DECIMAL(10, 8) NOT NULL,
    funding_time TIMESTAMP NOT NULL,
    next_funding_time TIMESTAMP,
    predicted_rate DECIMAL(10, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_market_time (market, funding_time)
);
```

**futures_liquidations table:**
```sql
CREATE TABLE futures_liquidations (
    liquidation_id VARCHAR(255) PRIMARY KEY,
    market VARCHAR(50) NOT NULL,
    side VARCHAR(10) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    liquidation_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_market_timestamp (market, timestamp),
    INDEX idx_timestamp (timestamp)
);
```

**futures_basis_history table:**
```sql
CREATE TABLE futures_basis_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    market VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    futures_price DECIMAL(20, 8) NOT NULL,
    spot_price DECIMAL(20, 8) NOT NULL,
    basis DECIMAL(20, 8) NOT NULL,
    basis_rate DECIMAL(10, 8) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_market_timestamp (market, timestamp)
);
```

**market_snapshots table:**
```sql
CREATE TABLE market_snapshots (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    market VARCHAR(50) NOT NULL,
    market_type VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    volume_24h DECIMAL(20, 8),
    orderbook_data JSON,
    kline_data JSON,
    open_interest DECIMAL(20, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_market_timestamp (market, timestamp),
    INDEX idx_market_type (market_type)
);
```

**alerts table:**
```sql
CREATE TABLE alerts (
    alert_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    anomaly_score DECIMAL(5, 2) NOT NULL,
    risk_level VARCHAR(10) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL,
    explanation TEXT,
    trade_ids JSON,
    is_reviewed BOOLEAN DEFAULT FALSE,
    is_true_positive BOOLEAN,
    reviewer_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_risk_level (risk_level),
    INDEX idx_timestamp (timestamp)
);
```

**feedback table:**
```sql
CREATE TABLE feedback (
    feedback_id VARCHAR(255) PRIMARY KEY,
    alert_id VARCHAR(255) NOT NULL,
    is_true_positive BOOLEAN NOT NULL,
    notes TEXT,
    submitted_by VARCHAR(255),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alert_id) REFERENCES alerts(alert_id)
);
```

**model_versions table:**
```sql
CREATE TABLE model_versions (
    version_id VARCHAR(255) PRIMARY KEY,
    model_type VARCHAR(50) NOT NULL,
    trained_at TIMESTAMP NOT NULL,
    training_samples INT,
    performance_metrics JSON,
    model_path VARCHAR(500),
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Error Handling

### Error Categories

1. **Data Validation Errors:**
   - Missing required fields
   - Invalid data types
   - Out-of-range values
   - Duplicate records

2. **Processing Errors:**
   - Feature extraction failures
   - Model prediction errors
   - Database connection issues
   - Insufficient data for analysis

3. **API Errors:**
   - Invalid request format
   - Authentication failures
   - Rate limiting
   - Resource not found

### Error Response Format

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {},
    "timestamp": "ISO8601"
  }
}
```

### Error Handling Strategy

- **Graceful Degradation:** If one model fails, continue with others
- **Retry Logic:** Automatic retry for transient failures (3 attempts with exponential backoff)
- **Logging:** Comprehensive error logging with stack traces
- **Alerting:** Critical errors trigger notifications to administrators
- **Fallback:** Use rule-based detection if ML models unavailable

## Testing Strategy

### Unit Tests

**Coverage Areas:**
- Data validation logic
- Feature extraction functions
- Model prediction methods
- Report generation
- API endpoint handlers

**Framework:** pytest with pytest-cov for coverage reporting

**Example Test:**
```python
def test_wash_trading_detection():
    # Arrange
    trades = create_wash_trading_pattern()
    detector = RuleBasedDetector()
    
    # Act
    alerts = detector.detect_wash_trading(trades)
    
    # Assert
    assert len(alerts) > 0
    assert alerts[0].pattern_type == "WASH_TRADING"
    assert alerts[0].anomaly_score > 80
```

### Integration Tests

**Coverage Areas:**
- End-to-end data flow (upload → analysis → report)
- Database operations
- API request/response cycles
- Model training and prediction pipeline

### Performance Tests

**Metrics:**
- Processing throughput (trades per minute)
- API response times
- Memory usage under load
- Database query performance

**Tools:** locust for load testing, pytest-benchmark for benchmarking

### Model Validation

**Approach:**
- Cross-validation (5-fold) during training
- Hold-out test set (15% of data)
- Metrics: Precision, Recall, F1-Score, AUC-ROC
- Confusion matrix analysis
- False positive rate monitoring

**Acceptance Criteria:**
- Precision > 0.75 (minimize false positives)
- Recall > 0.70 (catch most anomalies)
- F1-Score > 0.72
- False positive rate < 10%

## Deployment Architecture (Digital Ocean)

### Infrastructure Components

**1. Application Server:**
- Digital Ocean Droplet (4GB RAM, 2 vCPUs minimum)
- Ubuntu 22.04 LTS
- Docker + Docker Compose
- Nginx reverse proxy

**2. Database:**
- Digital Ocean Managed PostgreSQL
- 2GB RAM, 1 vCPU minimum
- Automated backups enabled
- Connection pooling via PgBouncer

**3. Cache Layer:**
- Digital Ocean Managed Redis
- 1GB RAM minimum
- Used for session management and real-time data

**4. Storage:**
- Digital Ocean Spaces (S3-compatible)
- Store trained models, reports, and uploaded files
- CDN enabled for report delivery

### Deployment Process

**1. Containerization:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**2. Docker Compose Configuration:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - redis
    restart: always

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: always
```

**3. CI/CD Pipeline:**
- GitHub Actions for automated testing
- Build Docker image on successful tests
- Push to Digital Ocean Container Registry
- Deploy to droplet via SSH
- Health check verification
- Rollback on failure

### Scaling Strategy

**Horizontal Scaling:**
- Add more API server instances behind load balancer
- Use Digital Ocean Load Balancer for distribution
- Stateless design enables easy scaling

**Vertical Scaling:**
- Upgrade droplet size for more CPU/RAM
- Upgrade database tier for better performance

**Optimization:**
- Implement caching for frequently accessed data
- Use background workers (Celery) for long-running tasks
- Batch processing for large datasets
- Database query optimization and indexing

## Configuration Management

**Configuration File (config.yaml):**
```yaml
detection:
  thresholds:
    high_risk_score: 80
    medium_risk_score: 50
    hft_trades_per_hour: 100
    wash_trading_time_window: 300  # seconds
    pump_dump_volume_spike: 3.0  # multiplier
    pump_dump_price_change: 0.5  # 50%
    
    # Futures-specific thresholds
    funding_rate_std_deviation: 3.0  # std deviations
    basis_anomaly_threshold: 0.02  # 2% deviation
    liquidation_cascade_threshold: 5  # liquidations in 1 minute
    position_concentration_threshold: 0.3  # 30% in single tier
    premium_deviation_threshold: 0.01  # 1% mark-index deviation
  
  model_weights:
    isolation_forest: 0.3
    autoencoder: 0.4
    random_forest: 0.3
  
  feature_windows:
    - "1H"
    - "24H"
    - "7D"

market_monitoring:
  enabled: true
  spot_markets: true
  futures_markets: true
  min_volume_24h: 10000  # USD
  max_concurrent_checks: 5
  base_check_interval: 60  # seconds
  high_priority_interval: 30  # seconds
  low_priority_interval: 300  # seconds
  
  futures_data_collection:
    funding_rate_interval: 300  # 5 minutes
    liquidation_check_interval: 60  # 1 minute
    basis_history_interval: 3600  # 1 hour
    orderbook_snapshot_interval: 30  # 30 seconds
    kline_intervals: ["1min", "5min", "15min", "1hour"]

database:
  url: ${DATABASE_URL}
  pool_size: 10
  max_overflow: 20

redis:
  url: ${REDIS_URL}
  ttl: 3600

api:
  rate_limit: 100  # requests per minute
  max_upload_size: 100  # MB
  cors_origins:
    - "https://yourdomain.com"

logging:
  level: INFO
  format: json
  output: /var/log/trade-risk-analyzer/app.log
```

## Futures Market Monitoring Architecture

### Real-Time Data Collection

**Data Sources via CoinEx MCP:**
1. **Futures Tickers** - Real-time price, volume, open interest
2. **Futures K-lines** - OHLCV data with open interest at multiple intervals
3. **Futures Order Books** - Bid/ask depth for liquidity analysis
4. **Funding Rates** - Current and historical funding rate data
5. **Premium Index** - Mark price vs index price tracking
6. **Basis History** - Futures-spot price spread over time
7. **Liquidation Events** - Real-time liquidation tracking
8. **Position Tiers** - Margin requirements and leverage limits

### Futures-Specific Detection Algorithms

**1. Funding Rate Manipulation Detection:**
```python
def detect_funding_rate_manipulation(funding_history: List[Dict]) -> Optional[Alert]:
    """
    Detects abnormal funding rate patterns:
    - Sudden spikes >3 std deviations
    - Sustained high rates (funding rate farming)
    - Coordinated rate manipulation
    """
    rates = [f['funding_rate'] for f in funding_history]
    mean_rate = np.mean(rates)
    std_rate = np.std(rates)
    
    for funding in funding_history[-10:]:
        if abs(funding['funding_rate'] - mean_rate) > 3 * std_rate:
            return Alert(
                pattern_type="FUNDING_RATE_MANIPULATION",
                anomaly_score=85,
                explanation="Abnormal funding rate spike detected"
            )
```

**2. Liquidation Hunting Detection:**
```python
def detect_liquidation_hunting(liquidations: List[Dict], orderbook: Dict) -> Optional[Alert]:
    """
    Detects price manipulation to trigger liquidations:
    - Large orders near liquidation levels
    - Cascade liquidation events
    - Coordinated liquidation triggering
    """
    # Check for liquidation cascades (5+ in 1 minute)
    recent_liquidations = [l for l in liquidations if is_recent(l, 60)]
    
    if len(recent_liquidations) >= 5:
        total_volume = sum(l['volume'] for l in recent_liquidations)
        return Alert(
            pattern_type="LIQUIDATION_CASCADE",
            anomaly_score=90,
            explanation=f"Cascade liquidation: {len(recent_liquidations)} events, {total_volume} volume"
        )
```

**3. Basis Manipulation Detection:**
```python
def detect_basis_manipulation(basis_history: List[Dict]) -> Optional[Alert]:
    """
    Detects abnormal futures-spot price divergence:
    - Excessive basis spread (>2% deviation)
    - Coordinated arbitrage exploitation
    - Market inefficiency manipulation
    """
    for basis in basis_history[-20:]:
        if abs(basis['basis_rate']) > 0.02:  # 2% threshold
            return Alert(
                pattern_type="BASIS_MANIPULATION",
                anomaly_score=75,
                explanation=f"Abnormal basis spread: {basis['basis_rate']*100:.2f}%"
            )
```

**4. Position Concentration Risk:**
```python
def detect_position_concentration(position_tiers: List[Dict]) -> Optional[Alert]:
    """
    Detects excessive position concentration:
    - >30% of open interest in single tier
    - Whale manipulation risk
    - Systemic liquidation risk
    """
    # Analyze position distribution across tiers
    # Flag if concentration exceeds threshold
```

### Monitoring Workflow

```
┌─────────────────────────────────────────────────────────┐
│         Futures Market Monitoring Workflow              │
└─────────────────────────────────────────────────────────┘

1. Market Discovery
   ↓
   - Get all futures markets via MCP
   - Filter by volume and quote currency
   - Initialize monitoring priorities

2. Data Collection Loop (every 30-60 seconds)
   ↓
   - Fetch ticker data
   - Fetch K-line data (multiple intervals)
   - Fetch order book snapshots
   - Fetch funding rate (every 5 min)
   - Fetch liquidations (every 1 min)
   - Fetch basis history (every 1 hour)

3. Real-Time Analysis
   ↓
   - Analyze funding rate patterns
   - Detect liquidation cascades
   - Check basis anomalies
   - Analyze order book manipulation
   - Calculate risk scores

4. Alert Generation
   ↓
   - Generate alerts for detected patterns
   - Store in database
   - Trigger callbacks/notifications
   - Update market risk levels

5. Feature Extraction
   ↓
   - Extract futures-specific features
   - Combine with historical data
   - Feed to ML models for deeper analysis

6. Reporting
   ↓
   - Generate real-time dashboards
   - Create periodic reports
   - Track market health metrics
```

### Integration with Existing System

**Data Flow:**
```
CoinEx MCP Server
    ↓
MCPClient (Spot + Futures methods)
    ↓
MultiMarketMonitor (Priority scheduling)
    ↓
MarketAnalyzer + FuturesAnalyzer
    ↓
DetectionEngine (ML + Rule-based)
    ↓
AlertManager → Database → Reporting
```

**Feature Engineering Integration:**
- Futures features added to existing feature vectors
- Combined spot + futures analysis for cross-market manipulation
- Temporal features include funding rate cycles
- Volume features include open interest changes

**Storage Strategy:**
- Real-time data stored in Redis (TTL: 1 hour)
- Historical data persisted to PostgreSQL
- Aggregated metrics cached for performance
- Time-series data optimized with partitioning

## Security Considerations

1. **Authentication & Authorization:**
   - JWT-based authentication
   - Role-based access control (Admin, Analyst, Viewer)
   - API key management for programmatic access

2. **Data Protection:**
   - Encryption at rest (database encryption)
   - Encryption in transit (TLS/SSL)
   - PII anonymization in logs

3. **Input Validation:**
   - Strict schema validation for all inputs
   - SQL injection prevention (parameterized queries)
   - File upload validation (type, size, content)

4. **Rate Limiting:**
   - Per-user rate limits
   - IP-based throttling
   - DDoS protection via Digital Ocean firewall
   - MCP rate limiting to avoid exchange API limits

5. **Audit Logging:**
   - Log all data access and modifications
   - Track user actions
   - Maintain audit trail for compliance
