# Trade Risk Analyzer REST API

FastAPI-based REST API for cryptocurrency market monitoring and risk analysis.

## Features

- ✅ **Secure**: Uses CoinEx HTTP service (no local installation required)
- ✅ **Real-time**: Live market data analysis
- ✅ **Comprehensive**: Spot and futures market support
- ✅ **Interactive**: Auto-generated API documentation
- ✅ **Fast**: Async/await for high performance

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-api.txt
```

### 2. Start the API Server

```bash
python run_api.py
```

The API will start on `http://localhost:8000`

### 3. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health & Status

- `GET /api/v1/health` - Health check
- `GET /api/v1/status` - System status

### Market Data (Spot)

- `GET /api/v1/markets/spot/{market}/ticker` - Get ticker data
- `GET /api/v1/markets/spot/{market}/kline` - Get K-line data
- `GET /api/v1/markets/spot/{market}/orderbook` - Get order book
- `GET /api/v1/markets/spot/{market}/trades` - Get recent trades
- `GET /api/v1/markets/spot/{market}/analysis` - **Comprehensive market analysis**

### Monitoring

- `POST /api/v1/monitoring/start` - Start monitoring
- `POST /api/v1/monitoring/stop` - Stop monitoring
- `GET /api/v1/monitoring/stats` - Get statistics

### Analysis

- `POST /api/v1/analysis/run` - Trigger analysis
- `GET /api/v1/analysis/{job_id}` - Get results

## Usage Examples

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Get ticker for ZEROLEND
curl http://localhost:8000/api/v1/markets/spot/ZEROLENDUSDT/ticker

# Analyze ZEROLEND market
curl http://localhost:8000/api/v1/markets/spot/ZEROLENDUSDT/analysis
```

### Using Python

```python
import requests

# Analyze a market
response = requests.get(
    "http://localhost:8000/api/v1/markets/spot/ZEROLENDUSDT/analysis"
)
data = response.json()

print(f"Health Score: {data['health_score']}/100")
print(f"Status: {data['health_status']}")
print(f"Alerts: {len(data['alerts'])}")
```

### Using JavaScript/Fetch

```javascript
// Analyze a market
fetch('http://localhost:8000/api/v1/markets/spot/ZEROLENDUSDT/analysis')
  .then(response => response.json())
  .then(data => {
    console.log(`Health Score: ${data.health_score}/100`);
    console.log(`Status: ${data.health_status}`);
    console.log(`Alerts: ${data.alerts.length}`);
  });
```

## Response Format

### Market Analysis Response

```json
{
  "market": "ZEROLENDUSDT",
  "ticker": {
    "last_price": 0.000065,
    "volume_24h": 0,
    "change_24h": 0,
    "high_24h": 0.00013,
    "low_24h": 0.0000084,
    "volatility": 1451.76
  },
  "volume_analysis": {
    "volume_spikes": 6,
    "avg_volume": 2414931.16
  },
  "trade_analysis": {
    "buy_volume": 6389517.17,
    "sell_volume": 8713882.25,
    "buy_percentage": 42.3,
    "sell_percentage": 57.7
  },
  "orderbook_analysis": {
    "spread_percentage": 0,
    "imbalance": 0,
    "available": false
  },
  "alerts": [
    {
      "type": "HIGH_VOLATILITY",
      "severity": "MEDIUM",
      "message": "High volatility: 1451.8%"
    }
  ],
  "health_score": 70,
  "health_status": "CAUTION"
}
```

## Configuration

### CORS

By default, CORS is configured to allow all origins. For production, update in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Port

Change the port in `run_api.py`:

```python
uvicorn.run(
    "trade_risk_analyzer.api.main:app",
    host="0.0.0.0",
    port=3000,  # Your custom port
    reload=True
)
```

## Production Deployment

### Using Gunicorn

```bash
gunicorn trade_risk_analyzer.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "trade_risk_analyzer.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t trade-risk-analyzer-api .
docker run -p 8000:8000 trade-risk-analyzer-api
```

## Security Considerations

1. **Rate Limiting**: Add rate limiting for production
2. **Authentication**: Implement JWT or API keys
3. **HTTPS**: Use SSL/TLS in production
4. **Input Validation**: All inputs are validated via Pydantic
5. **Error Handling**: Comprehensive error handling implemented

## Monitoring

The API includes built-in monitoring:

- Request logging
- Error tracking
- System metrics (CPU, memory, disk)

## Next Steps

1. Add authentication (JWT)
2. Implement WebSocket for real-time updates
3. Add database integration for historical data
4. Implement caching (Redis)
5. Add rate limiting
6. Set up monitoring (Prometheus/Grafana)

## Support

For issues or questions, refer to the main project documentation.
