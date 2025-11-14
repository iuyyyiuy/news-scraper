# Trade Risk Analyzer

ML-powered system for detecting abnormal trading behaviors.

## Project Structure

```
trade_risk_analyzer/
├── __init__.py
├── core/                      # Core infrastructure
│   ├── __init__.py
│   ├── config.py             # Configuration management
│   ├── logger.py             # Structured logging
│   └── base.py               # Base classes and interfaces
├── data_ingestion/           # Data import and validation
│   └── __init__.py
├── feature_engineering/      # Feature extraction
│   └── __init__.py
├── detection/                # Anomaly detection engine
│   └── __init__.py
├── models/                   # ML models
│   └── __init__.py
├── reporting/                # Report generation
│   └── __init__.py
└── api/                      # REST API
    └── __init__.py
```

## Configuration

Configuration is managed through YAML files with environment variable support.

### Configuration File

The system looks for `config.yaml` in the following locations:
1. Current directory
2. `config/config.yaml`
3. `trade_risk_analyzer/config.yaml`
4. `~/.trade_risk_analyzer/config.yaml`

### Environment Variables

Environment variables can be used in the configuration file using the `${VAR_NAME}` syntax:

```yaml
database:
  url: ${DATABASE_URL}
```

### Usage

```python
from trade_risk_analyzer.core.config import get_config

# Get configuration
config = get_config()

# Access configuration values
db_url = config.database.url
high_risk_threshold = config.detection.thresholds.high_risk_score
```

## Logging

The system uses structured logging with support for JSON and text formats.

### Usage

```python
from trade_risk_analyzer.core.logger import get_logger

# Get logger
logger = get_logger(__name__)

# Log messages
logger.info("Processing trades", user_id="12345", trade_count=100)
logger.error("Failed to process", error="Connection timeout")
```

### Log Formats

- **JSON**: Structured logs for machine parsing
- **Text**: Human-readable logs for development

## Base Classes

The system provides abstract base classes for extensibility:

- `BaseDataImporter`: For implementing custom data importers
- `BaseFeatureExtractor`: For implementing custom feature extractors
- `BaseModel`: For implementing custom ML models
- `BaseDetector`: For implementing custom pattern detectors
- `BaseReportGenerator`: For implementing custom report generators
- `BaseStorage`: For implementing custom storage backends

### Example

```python
from trade_risk_analyzer.core.base import BaseDetector, Alert, PatternType

class CustomDetector(BaseDetector):
    def detect(self, trades):
        # Implementation
        return []
    
    def get_pattern_type(self):
        return PatternType.GENERAL_ANOMALY
```

## Getting Started

1. Copy `.env.example` to `.env` and configure environment variables
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `config.yaml` as needed
4. Import the modules and start building!
