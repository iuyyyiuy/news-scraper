# Labeled Training Data Guide

This guide explains how to add labeled training data from real extraction attack events to improve the Trade Risk Analyzer's detection accuracy.

## Overview

When you identify real cases of manipulation (like extraction attacks), you can add them as labeled training data. This allows the system to learn from actual attack patterns and improve its detection capabilities.

## Quick Start - Interactive Method

The easiest way to add your extraction attack data is using the interactive script:

```bash
python add_extraction_attack_data.py
```

This will guide you through:
1. Adding the victim's trade data
2. Adding the attacker's trade data
3. Optionally training the models with the new data

## Command Line Method

### 1. Add Victim Data

```bash
python add_labeled_training_data.py add \
  --file "path/to/victim_trades.xlsx" \
  --user-id "victim_user_id" \
  --label victim \
  --attack-type extraction_attack \
  --notes "Victim of extraction attack in spot market"
```

### 2. Add Attacker Data

```bash
python add_labeled_training_data.py add \
  --file "path/to/attacker_trades.xlsx" \
  --user-id "attacker_user_id" \
  --label attacker \
  --attack-type extraction_attack \
  --notes "Attacker in extraction attack in spot market"
```

### 3. List All Labeled Users

```bash
python add_labeled_training_data.py list
```

### 4. Train Models with Labeled Data

```bash
python add_labeled_training_data.py train --output-dir models_labeled
```

## Label Types

- **`attacker`**: User who performed the manipulation
- **`victim`**: User who was targeted/affected by the manipulation
- **`normal`**: User with normal trading behavior (for comparison)

Both `attacker` and `victim` are treated as anomalous (label=1) for training purposes.

## Attack Types

You can specify different attack types:
- `extraction_attack` - Price extraction/manipulation
- `wash_trading` - Self-trading patterns
- `pump_and_dump` - Coordinated price manipulation
- `layering` - Order book manipulation
- `spoofing` - Fake order placement

## How It Works

1. **Data Import**: Trade data is imported from Excel files
2. **Validation**: Data is validated for completeness and correctness
3. **Storage**: Trades are stored in the database
4. **Labeling**: User is labeled with attack type and role
5. **Feature Extraction**: Features are extracted from trade patterns
6. **Training**: Models learn from labeled examples

## Training Process

When you train with labeled data:

1. **Feature Extraction**: System extracts behavioral features from all labeled users
2. **Data Splitting**: Data is split into train (70%), validation (15%), and test (15%)
3. **Model Training**: Three models are trained:
   - Isolation Forest (unsupervised anomaly detection)
   - Autoencoder (deep learning anomaly detection)
   - Random Forest (supervised classification)
4. **Evaluation**: Models are evaluated on test data
5. **Model Saving**: Trained models are saved for future use

## Using Trained Models

After training, you can use the models for detection:

```python
from trade_risk_analyzer.models.trainer import ModelTrainer

# Load trained models
trainer = ModelTrainer()
models = trainer.load_models('models_labeled')

# Use for prediction
isolation_forest = models['isolation_forest']
predictions = isolation_forest.predict(new_features)
```

## Best Practices

1. **Add Multiple Examples**: The more labeled examples you add, the better the models will perform
2. **Include Normal Users**: Add some normal users for comparison
3. **Document Cases**: Use the notes field to document details about each case
4. **Retrain Regularly**: Retrain models as you add more labeled data
5. **Validate Results**: Test the trained models on new data to ensure they generalize well

## File Structure

```
labeled_users.json          # Metadata about all labeled users
models_labeled/             # Directory with trained models
  ├── isolation_forest      # Isolation Forest model
  ├── autoencoder_*         # Autoencoder model files
  ├── random_forest         # Random Forest model
  ├── evaluation_results.json
  └── training_metadata.json
```

## Example Workflow

```bash
# 1. Add extraction attack data
python add_extraction_attack_data.py

# 2. List all labeled users to verify
python add_labeled_training_data.py list

# 3. Train models
python add_labeled_training_data.py train

# 4. Use trained models in your analysis scripts
# (Update your scripts to load from 'models_labeled' instead of default models)
```

## Troubleshooting

### "No data imported from file"
- Check that the Excel file path is correct
- Ensure the file has the expected columns (timestamp, symbol, price, volume, trade_type)

### "Validation issues found"
- Review the validation errors
- Common issues: missing timestamps, invalid prices, incorrect trade types
- The system will still import valid records

### "No labeled data available for training"
- Ensure you've added at least one labeled user
- Check that `labeled_users.json` exists and contains entries

### "Model training failed"
- Ensure you have enough labeled examples (at least 10-20 users recommended)
- Check that features were extracted successfully
- Review error logs for specific issues

## Support

For questions or issues, refer to:
- Main README.md
- Database Guide (DATABASE_GUIDE.md)
- Feature Engineering documentation
