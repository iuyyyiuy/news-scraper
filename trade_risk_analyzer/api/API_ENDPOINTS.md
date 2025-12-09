# Trade Risk Analyzer API - Complete Endpoint Documentation

## Base URL
```
http://localhost:8000
```

## API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Endpoints Overview

### 1. Health & Status
- `GET /api/v1/health` - Check API health status

### 2. Trade Data Management
- `POST /api/v1/trades/upload` - Upload trade data (CSV, JSON, Excel)
- `GET /api/v1/trades/upload/{job_id}` - Get upload job status

### 3. Alerts
- `GET /api/v1/alerts` - List alerts with filtering and pagination
- `GET /api/v1/alerts/{alert_id}` - Get specific alert details
- `GET /api/v1/alerts/stats/summary` - Get alert statistics

### 4. Market Data (Spot & Futures)
- `GET /api/v1/markets/spot/{market}/ticker` - Get spot market ticker
- `GET /api/v1/markets/spot/{market}/kline` - Get spot K-line data
- `GET /api/v1/markets/spot/{market}/orderbook` - Get spot order book
- `GET /api/v1/markets/spot/{market}/trades` - Get recent spot trades
- `GET /api/v1/markets/spot/{market}/analysis` - Analyze spot market for risks

### 5. Market Monitoring
- `POST /api/v1/monitoring/start` - Start market monitoring
- `POST /api/v1/monitoring/stop` - Stop market monitoring
- `GET /api/v1/monitoring/status` - Get monitoring status
- `GET /api/v1/monitoring/stats` - Get monitoring statistics

### 6. Analysis
- `POST /api/v1/analysis/run` - Trigger batch analysis
- `GET /api/v1/analysis/{job_id}` - Get analysis results

### 7. Configuration
- `GET /api/v1/config` - Get current configuration
- `PUT /api/v1/config` - Update configuration
- `POST /api/v1/config/reset` - Reset to default configuration

### 8. Feedback & Model Management
- `POST /api/v1/feedback` - Submit feedback on alerts
- `GET /api/v1/feedback/stats` - Get feedback statistics
- `POST /api/v1/feedback/models/retrain` - Trigger model retraining
- `GET /api/v1/feedback/models/retrain/{job_id}` - Get retraining status
- `GET /api/v1/feedback/models/versions` - List model versions
- `GET /api/v1/feedback/models/performance` - Get model performance metrics

---

## Detailed Endpoint Documentation

### Trade Data Upload

#### Upload Trade Data
```http
POST /api/v1/trades/upload
Content-Type: multipart/form-data

file: <trade_data.csv|json|xlsx>
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "queued",
  "message": "File upload queued for processing"
}
```

#### Check Upload Status
```http
GET /api/v1/trades/upload/{job_id}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "message": "Successfully imported 1000 records",
  "total_records": 1000,
  "valid_records": 1000,
  "invalid_records": 0,
  "errors": [],
  "created_at": "2025-11-12T10:00:00",
  "completed_at": "2025-11-12T10:01:00"
}
```

---

### Alerts

#### List Alerts
```http
GET /api/v1/alerts?page=1&page_size=50&risk_level=HIGH&sort_by=timestamp&sort_order=desc
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 50, max: 1000)
- `start_date` (string): Filter from date (ISO format)
- `end_date` (string): Filter to date (ISO format)
- `risk_level` (string): Filter by risk level (HIGH, MEDIUM, LOW)
- `user_id` (string): Filter by user ID
- `alert_type` (string): Filter by alert type
- `sort_by` (string): Sort field (timestamp, risk_level)
- `sort_order` (string): Sort order (asc, desc)

**Response:**
```json
{
  "page": 1,
  "page_size": 50,
  "total": 150,
  "total_pages": 3,
  "alerts": [
    {
      "id": 1,
      "user_id": "user123",
      "alert_type": "WASH_TRADING",
      "risk_level": "HIGH",
      "description": "Potential wash trading detected",
      "anomaly_score": 0.95,
      "timestamp": "2025-11-12T10:00:00",
      "metadata": {}
    }
  ]
}
```

#### Get Alert Statistics
```http
GET /api/v1/alerts/stats/summary?start_date=2025-11-01&end_date=2025-11-12
```

**Response:**
```json
{
  "total_alerts": 150,
  "by_risk_level": {
    "HIGH": 30,
    "MEDIUM": 70,
    "LOW": 50
  },
  "by_alert_type": {
    "WASH_TRADING": 40,
    "PUMP_AND_DUMP": 30,
    "HFT_MANIPULATION": 80
  },
  "date_range": {
    "start": "2025-11-01",
    "end": "2025-11-12"
  }
}
```

---

### Market Analysis

#### Analyze Spot Market
```http
GET /api/v1/markets/spot/ZEROLENDUSDT/analysis
```

**Response:**
```json
{
  "market": "ZEROLENDUSDT",
  "ticker": {
    "last_price": 0.00012345,
    "volume_24h": 2500000,
    "change_24h": 5.23,
    "high_24h": 0.00013000,
    "low_24h": 0.00011000,
    "volatility": 8.5
  },
  "volume_analysis": {
    "volume_spikes": 7,
    "avg_volume": 100000
  },
  "trade_analysis": {
    "buy_volume": 1300000,
    "sell_volume": 1200000,
    "buy_percentage": 52.0,
    "sell_percentage": 48.0
  },
  "orderbook_analysis": {
    "spread_percentage": 0.5,
    "imbalance": 0.1,
    "available": true
  },
  "alerts": [
    {
      "type": "VOLUME_SPIKE",
      "severity": "MEDIUM",
      "message": "7 volume spikes detected"
    }
  ],
  "health_score": 65,
  "health_status": "CAUTION"
}
```

---

### Batch Analysis

#### Run Batch Analysis
```http
POST /api/v1/analysis/run
Content-Type: application/json

{
  "start_date": "2025-11-01T00:00:00",
  "end_date": "2025-11-12T23:59:59",
  "user_ids": ["user123", "user456"]
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "queued",
  "message": "Analysis queued successfully"
}
```

#### Get Analysis Results
```http
GET /api/v1/analysis/{job_id}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "message": "Analysis completed: 45 alerts generated",
  "total_trades": 10000,
  "alerts_generated": 45,
  "risk_distribution": {
    "high": 10,
    "medium": 20,
    "low": 15
  },
  "created_at": "2025-11-12T10:00:00",
  "completed_at": "2025-11-12T10:05:00",
  "results": {
    "alerts": [...]
  }
}
```

---

### Configuration Management

#### Get Configuration
```http
GET /api/v1/config
```

**Response:**
```json
{
  "detection_thresholds": {
    "wash_trading": {
      "time_window_seconds": 300,
      "min_probability": 0.7
    },
    "pump_and_dump": {
      "volume_spike_multiplier": 3.0,
      "price_change_threshold": 0.2
    },
    "hft_manipulation": {
      "max_trades_per_minute": 100,
      "layering_threshold": 5
    }
  },
  "model_parameters": {
    "isolation_forest": {
      "n_estimators": 100,
      "contamination": 0.1
    }
  },
  "monitoring_settings": {
    "check_interval_seconds": 60,
    "max_concurrent_markets": 10
  }
}
```

#### Update Configuration
```http
PUT /api/v1/config
Content-Type: application/json

{
  "detection_thresholds": {
    "wash_trading": {
      "time_window_seconds": 600
    }
  }
}
```

---

### Feedback & Model Retraining

#### Submit Feedback
```http
POST /api/v1/feedback
Content-Type: application/json

{
  "alert_id": 123,
  "is_correct": true,
  "comments": "Confirmed wash trading pattern",
  "user_id": "analyst1"
}
```

**Response:**
```json
{
  "feedback_id": 456,
  "status": "success",
  "message": "Feedback submitted successfully"
}
```

#### Trigger Model Retraining
```http
POST /api/v1/feedback/models/retrain
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "queued",
  "message": "Model retraining queued successfully"
}
```

#### Get Model Performance
```http
GET /api/v1/feedback/models/performance
```

**Response:**
```json
{
  "model_version": "v1.2.0",
  "metrics": {
    "precision": 0.92,
    "recall": 0.88,
    "f1_score": 0.90,
    "auc_roc": 0.94
  },
  "last_updated": "2025-11-12T10:00:00"
}
```

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

---

## Rate Limiting

Currently no rate limiting is implemented. For production deployment, consider adding rate limiting middleware.

---

## Authentication

Task 10.8 (Authentication) is not yet implemented. All endpoints are currently public.

For production deployment, implement:
- JWT-based authentication
- API key management
- Role-based access control (Admin, Analyst, Viewer)

---

## Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Get alerts
curl "http://localhost:8000/api/v1/alerts?page=1&page_size=10"

# Analyze market
curl http://localhost:8000/api/v1/markets/spot/ZEROLENDUSDT/analysis

# Upload file
curl -X POST -F "file=@trades.csv" http://localhost:8000/api/v1/trades/upload
```

### Using Python

```python
import requests

# Analyze market
response = requests.get("http://localhost:8000/api/v1/markets/spot/ZEROLENDUSDT/analysis")
data = response.json()
print(f"Health Score: {data['health_score']}")

# Submit feedback
feedback = {
    "alert_id": 123,
    "is_correct": True,
    "comments": "Confirmed"
}
response = requests.post("http://localhost:8000/api/v1/feedback", json=feedback)
print(response.json())
```

---

## Next Steps

1. **Test all endpoints** using the Swagger UI at http://localhost:8000/docs
2. **Implement authentication** (Task 10.8) for production use
3. **Add rate limiting** to prevent abuse
4. **Set up monitoring** for API performance
5. **Deploy to production** using Docker and Digital Ocean

---

## Support

For issues or questions:
- Check the Swagger documentation: http://localhost:8000/docs
- Review the logs in the console
- Check the database for stored data
