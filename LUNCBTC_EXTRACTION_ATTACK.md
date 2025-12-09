# LUNCBTC Extraction Attack - Training Data

## Case Details

**Attack Type**: Extraction Attack in Spot Market  
**Symbol**: LUNCBTC  
**Victim**: User ID `1445939` (file: `1445939.xlsx`)  
**Attacker**: User ID `4866868` (file: `4866868.xlsx`)

## Quick Start

The fastest way to add this data to the training set:

```bash
python add_luncbtc_extraction_attack.py
```

This script will:
1. Add the victim's trade data (1445939.xlsx) with label "victim"
2. Add the attacker's trade data (4866868.xlsx) with label "attacker"
3. Optionally train the models with this new labeled data

## Manual Method

If you prefer to add the data manually:

### Step 1: Add Victim

```bash
python add_labeled_training_data.py add \
  --file "1445939.xlsx" \
  --user-id "1445939" \
  --label victim \
  --attack-type extraction_attack \
  --notes "Victim of extraction attack on LUNCBTC in spot market"
```

### Step 2: Add Attacker

```bash
python add_labeled_training_data.py add \
  --file "4866868.xlsx" \
  --user-id "4866868" \
  --label attacker \
  --attack-type extraction_attack \
  --notes "Attacker in extraction attack on LUNCBTC, coordinated trades"
```

### Step 3: Verify

```bash
python add_labeled_training_data.py list
```

You should see both users listed with their labels.

### Step 4: Train Models

```bash
python add_labeled_training_data.py train --output-dir models_labeled
```

## What This Does

1. **Imports Trade Data**: Loads all trades from both Excel files
2. **Labels Data**: Marks victim and attacker as anomalous patterns
3. **Extracts Features**: Analyzes trading patterns, volumes, timing, etc.
4. **Trains Models**: Three ML models learn from this labeled example:
   - Isolation Forest (unsupervised anomaly detection)
   - Autoencoder (deep learning anomaly detection)
   - Random Forest (supervised classification)
5. **Saves Models**: Trained models are saved to `models_labeled/`

## Using the Trained Models

After training, the models can detect similar extraction attacks:

```python
from trade_risk_analyzer.models.trainer import ModelTrainer
from trade_risk_analyzer.feature_engineering import FeatureExtractor
from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage

# Load trained models
trainer = ModelTrainer()
models = trainer.load_models('models_labeled')

# Get trades for a new user
storage = DatabaseStorage("sqlite:///trade_risk_analyzer.db")
storage.connect()
trades_df = storage.get_trades_as_dataframe({'user_id': 'new_user_id'})

# Extract features
extractor = FeatureExtractor()
features_df = extractor.extract_features(trades_df)

# Get predictions
random_forest = models['random_forest']
predictions = random_forest.predict(features_df.drop('user_id', axis=1).values)
scores = random_forest.predict_anomaly_score(features_df.drop('user_id', axis=1).values)

# Check results
for i, (pred, score) in enumerate(zip(predictions, scores)):
    if score > 0.7:
        print(f"⚠️  High risk detected (score: {score:.2f})")
        print(f"   Similar to LUNCBTC extraction attack pattern")
```

## Analysis of the Attack Pattern

The models will learn to recognize:

1. **Volume Patterns**: Unusual volume spikes or coordinated volume
2. **Price Impact**: Trades that significantly move the price
3. **Timing Patterns**: Coordinated timing between victim and attacker
4. **Trade Frequency**: Abnormal trading frequency
5. **Order Characteristics**: Unusual order sizes or patterns
6. **Symbol-Specific**: Patterns specific to LUNCBTC or similar low-liquidity pairs

## Adding More Examples

As you identify more extraction attacks, add them:

```bash
# Add another case
python add_labeled_training_data.py add \
  --file "another_victim.xlsx" \
  --user-id "victim_id" \
  --label victim \
  --attack-type extraction_attack

python add_labeled_training_data.py add \
  --file "another_attacker.xlsx" \
  --user-id "attacker_id" \
  --label attacker \
  --attack-type extraction_attack

# Retrain with all data
python add_labeled_training_data.py train
```

## Expected Results

After training with this data, the models should be able to:

- ✓ Detect similar extraction attacks on LUNCBTC
- ✓ Identify coordinated trading patterns between users
- ✓ Flag unusual volume/price patterns characteristic of extraction
- ✓ Recognize victim and attacker behavioral patterns
- ✓ Generalize to similar attacks on other low-liquidity symbols

## Monitoring

To monitor for similar attacks:

1. Run detection on all users regularly
2. Focus on low-liquidity symbols (like LUNCBTC)
3. Look for coordinated patterns between multiple users
4. Check for sudden volume spikes followed by price movements
5. Investigate high-scoring users immediately

## Files Created

- `labeled_users.json` - Metadata about labeled users
- `models_labeled/` - Directory with trained models
  - `isolation_forest` - Isolation Forest model
  - `autoencoder_*` - Autoencoder model files
  - `random_forest` - Random Forest model
  - `evaluation_results.json` - Model performance metrics
  - `training_metadata.json` - Training configuration

## Next Steps

1. ✓ Add the LUNCBTC extraction attack data
2. ✓ Train models with this labeled data
3. Run detection on other users to find similar patterns
4. Add more labeled examples as you identify them
5. Retrain periodically to improve accuracy
6. Monitor LUNCBTC and similar symbols closely

## Support

For questions or issues:
- See `LABELED_DATA_GUIDE.md` for detailed documentation
- See `EXAMPLE_ADD_LABELED_DATA.md` for more examples
- Check logs in the console output for debugging
