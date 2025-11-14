# Feedback and Continuous Learning Module

## Overview

The feedback module enables continuous improvement of the Trade Risk Analyzer through user feedback collection and automated model retraining. It implements a complete feedback loop where compliance officers can review alerts, provide feedback, and the system automatically incorporates this feedback to improve detection accuracy.

## Components

### 1. FeedbackCollector

Collects and manages user feedback on alerts.

**Features:**
- Submit feedback on alerts (true/false positives)
- Validate and sanitize feedback input
- Track feedback status (pending, reviewed, incorporated)
- Generate feedback statistics
- Retrieve labeled data for training

**Usage:**
```python
from trade_risk_analyzer.feedback.collector import (
    FeedbackCollector, FeedbackType, FeedbackStatus
)
from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage

# Initialize with database
storage = DatabaseStorage(database_url="postgresql://...")
collector = FeedbackCollector(storage=storage)

# Submit feedback
feedback = collector.submit_feedback(
    alert_id="alert_12345",
    reviewer_user_id="compliance_officer_1",
    is_true_positive=True,
    feedback_type=FeedbackType.TRUE_POSITIVE,
    reviewer_notes="Confirmed wash trading pattern",
    confidence_score=0.95
)

# Get feedback statistics
stats = collector.get_feedback_statistics()
print(f"Precision: {stats['precision']:.2%}")

# Get labeled data for training
labeled_data = collector.get_labeled_data_for_training(
    min_confidence=0.7,
    status=FeedbackStatus.REVIEWED
)
```

### 2. RetrainingPipeline

Handles model retraining with feedback data, versioning, and performance tracking.

**Features:**
- Retrain models with feedback data
- Incremental learning support
- Model versioning and rollback
- Performance tracking over time
- Automatic feature extraction

**Usage:**
```python
from trade_risk_analyzer.feedback.retraining import RetrainingPipeline

# Initialize pipeline
pipeline = RetrainingPipeline(
    storage=storage,
    model_dir="models",
    version_dir="model_versions"
)

# Retrain Random Forest
version = pipeline.retrain_random_forest(
    min_feedback_samples=50,
    min_confidence=0.7,
    incremental=True
)

print(f"New version: {version.version}")
print(f"Accuracy: {version.performance_metrics.accuracy:.3f}")

# Activate new version
pipeline.activate_model_version(version.version)

# Or rollback if needed
pipeline.rollback_to_version("random_forest_v20251111_100000")
```

## Feedback Types

### 1. TRUE_POSITIVE
Alert correctly identified suspicious activity.

```python
feedback = collector.submit_feedback(
    alert_id="alert_123",
    reviewer_user_id="officer_1",
    is_true_positive=True,
    feedback_type=FeedbackType.TRUE_POSITIVE,
    confidence_score=0.95
)
```

### 2. FALSE_POSITIVE
Alert incorrectly flagged normal activity.

```python
feedback = collector.submit_feedback(
    alert_id="alert_124",
    reviewer_user_id="officer_1",
    is_true_positive=False,
    feedback_type=FeedbackType.FALSE_POSITIVE,
    reviewer_notes="Normal market making activity",
    confidence_score=0.90
)
```

### 3. SEVERITY_ADJUSTMENT
Alert is correct but severity should be adjusted.

```python
feedback = collector.submit_feedback(
    alert_id="alert_125",
    reviewer_user_id="officer_1",
    is_true_positive=True,
    feedback_type=FeedbackType.SEVERITY_ADJUSTMENT,
    suggested_risk_level=RiskLevel.MEDIUM,
    confidence_score=0.85
)
```

### 4. PATTERN_CORRECTION
Alert is correct but pattern type should be corrected.

```python
feedback = collector.submit_feedback(
    alert_id="alert_126",
    reviewer_user_id="officer_1",
    is_true_positive=True,
    feedback_type=FeedbackType.PATTERN_CORRECTION,
    suggested_pattern_type=PatternType.PUMP_AND_DUMP,
    confidence_score=0.80
)
```

## Feedback Status

Feedback progresses through these statuses:

1. **PENDING**: Newly submitted, awaiting review
2. **REVIEWED**: Reviewed and validated by supervisor
3. **INCORPORATED**: Used in model retraining
4. **REJECTED**: Rejected (e.g., low confidence, conflicting)

## Model Versioning

### Version Format
```
{model_type}_v{YYYYMMDD}_{HHMMSS}
```

Example: `random_forest_v20251112_143000`

### Version Metadata
Each version includes:
- Version ID
- Creation timestamp
- Model type
- Performance metrics
- Parent version (for incremental training)
- Active status
- Notes

### Version Management

**List versions:**
```python
versions = pipeline.get_model_versions(
    model_type="random_forest",
    limit=10
)

for version in versions:
    print(f"{version.version}: F1={version.performance_metrics.f1_score:.3f}")
```

**Activate version:**
```python
pipeline.activate_model_version("random_forest_v20251112_143000")
```

**Rollback:**
```python
pipeline.rollback_to_version("random_forest_v20251111_100000")
```

## Performance Tracking

Track model performance over time:

```python
history = pipeline.get_performance_history(
    model_type="random_forest",
    limit=10
)

for metrics in history:
    print(f"{metrics.version}:")
    print(f"  Accuracy: {metrics.accuracy:.3f}")
    print(f"  Precision: {metrics.precision:.3f}")
    print(f"  Recall: {metrics.recall:.3f}")
    print(f"  F1 Score: {metrics.f1_score:.3f}")
```

## Retraining Workflow

### 1. Collect Feedback
```python
# Compliance officers review alerts
for alert in alerts:
    feedback = collector.submit_feedback(
        alert_id=alert.alert_id,
        reviewer_user_id="officer_1",
        is_true_positive=True,  # or False
        confidence_score=0.9
    )
```

### 2. Accumulate Sufficient Data
```python
# Check if enough feedback collected
stats = collector.get_feedback_statistics()
if stats['total_feedback'] >= 50:
    print("Ready for retraining")
```

### 3. Retrain Model
```python
# Retrain with feedback data
version = pipeline.retrain_random_forest(
    min_feedback_samples=50,
    min_confidence=0.7,
    test_size=0.2,
    incremental=True
)
```

### 4. Evaluate Performance
```python
# Check if improvement
if version.performance_metrics.f1_score > 0.85:
    print("Model improved, activating...")
    pipeline.activate_model_version(version.version)
else:
    print("No improvement, keeping current version")
```

### 5. Monitor and Iterate
```python
# Continue collecting feedback
# Retrain periodically (e.g., weekly)
# Track performance trends
```

## Incremental Learning

The system supports incremental learning for Random Forest models:

```python
# First training
version1 = pipeline.retrain_random_forest(
    incremental=False  # Train from scratch
)

# Later retraining with new feedback
version2 = pipeline.retrain_random_forest(
    incremental=True  # Build on existing model
)
```

**Benefits:**
- Faster retraining
- Preserves learned patterns
- Adapts to new patterns
- Reduces computational cost

## Performance Metrics

Each model version tracks:

- **Accuracy**: Overall correctness
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1 Score**: Harmonic mean of precision and recall
- **AUC-ROC**: Area under ROC curve (if available)
- **Training Samples**: Number of samples used
- **Feedback Samples**: Number of feedback samples incorporated

## Best Practices

### 1. Feedback Quality
- Require minimum confidence scores (e.g., 0.7)
- Have supervisors review feedback
- Provide clear guidelines for reviewers
- Document reasoning in notes

### 2. Retraining Frequency
- Collect minimum 50-100 feedback samples
- Retrain weekly or monthly
- Monitor performance trends
- Don't retrain too frequently

### 3. Version Management
- Keep at least 5 previous versions
- Test new versions before activation
- Have rollback plan ready
- Document version changes

### 4. Performance Monitoring
- Track metrics over time
- Compare to baseline
- Monitor for degradation
- Alert on significant changes

## Database Schema

The feedback system requires these database tables:

### feedback table
```sql
CREATE TABLE feedback (
    feedback_id VARCHAR PRIMARY KEY,
    alert_id VARCHAR NOT NULL,
    user_id VARCHAR NOT NULL,
    feedback_type VARCHAR NOT NULL,
    is_true_positive BOOLEAN NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    reviewer_notes TEXT,
    suggested_risk_level VARCHAR,
    suggested_pattern_type VARCHAR,
    confidence_score FLOAT,
    status VARCHAR NOT NULL,
    incorporated_at TIMESTAMP
);
```

### model_versions table
```sql
CREATE TABLE model_versions (
    version VARCHAR PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    model_type VARCHAR NOT NULL,
    model_path VARCHAR NOT NULL,
    performance_metrics JSONB NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    parent_version VARCHAR,
    notes TEXT
);
```

## Configuration

Add to `config.yaml`:

```yaml
feedback:
  min_feedback_samples: 50
  min_confidence: 0.7
  retraining_frequency: "weekly"
  incremental_learning: true
  
  model_versioning:
    keep_versions: 10
    auto_activate: false
    rollback_threshold: 0.05  # F1 score drop
```

## Examples

See `example_feedback.py` for comprehensive examples:
1. Feedback submission
2. Feedback statistics
3. Model retraining
4. Version management
5. Performance tracking
6. Complete workflow

Run examples:
```bash
python example_feedback.py
```

## Testing

Run tests:
```bash
python test_feedback.py
```

Tests cover:
- Feedback collection
- Input validation
- Feedback types
- Statistics calculation
- Model versioning
- Complete workflow

## API Integration

Feedback can be integrated into REST APIs:

```python
from fastapi import FastAPI
from trade_risk_analyzer.feedback import FeedbackCollector

app = FastAPI()

@app.post("/feedback")
async def submit_feedback(
    alert_id: str,
    is_true_positive: bool,
    reviewer_notes: str = None,
    confidence_score: float = None
):
    collector = FeedbackCollector(storage=storage)
    feedback = collector.submit_feedback(
        alert_id=alert_id,
        reviewer_user_id=current_user.id,
        is_true_positive=is_true_positive,
        reviewer_notes=reviewer_notes,
        confidence_score=confidence_score
    )
    return feedback.to_dict()

@app.get("/feedback/statistics")
async def get_statistics():
    collector = FeedbackCollector(storage=storage)
    return collector.get_feedback_statistics()

@app.post("/models/retrain")
async def retrain_model(model_type: str = "random_forest"):
    pipeline = RetrainingPipeline(storage=storage)
    version = pipeline.retrain_random_forest()
    return version.to_dict() if version else {"error": "Insufficient data"}
```

## Future Enhancements

- Active learning (suggest alerts for review)
- Automated retraining schedules
- A/B testing of model versions
- Ensemble of multiple versions
- Transfer learning support
- Explainable AI for feedback
- Feedback quality scoring
- Reviewer performance tracking
