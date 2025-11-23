# Example: Adding Extraction Attack Data

This example shows how to add your extraction attack data (victim and attacker) to the training dataset.

## Scenario

You have identified an extraction attack in the spot market with:
- **Victim**: User ID `1445939` (file: `1445939.xlsx`)
- **Attacker**: User ID `4866868` (file: `4866868.xlsx`)
- **Symbol**: `LUNCBTC`

## Method 1: Interactive Script (Recommended)

Run the interactive script:

```bash
python add_extraction_attack_data.py
```

You'll be prompted for:

```
Database URL (press Enter for default): [Press Enter]

VICTIM DATA
-----------
Path to victim's Excel file: 1445939.xlsx
Victim's User ID: 1445939
Notes about victim (optional): Victim of extraction attack on LUNCBTC, lost significant value

ATTACKER DATA
-------------
Path to attacker's Excel file: 4866868.xlsx
Attacker's User ID: 4866868
Notes about attacker (optional): Attacker in extraction attack on LUNCBTC, coordinated trades

Would you like to train the models with this new data? (y/n): y
Output directory for models (press Enter for 'models_labeled'): [Press Enter]
```

## Method 2: Command Line

### Step 1: Add Victim

```bash
python add_labeled_training_data.py add \
  --file "1445939.xlsx" \
  --user-id "1445939" \
  --label victim \
  --attack-type extraction_attack \
  --notes "Victim of extraction attack on LUNCBTC in spot market, lost significant value"
```

### Step 2: Add Attacker

```bash
python add_labeled_training_data.py add \
  --file "4866868.xlsx" \
  --user-id "4866868" \
  --label attacker \
  --attack-type extraction_attack \
  --notes "Attacker in extraction attack on LUNCBTC, coordinated trades to extract value"
```

### Step 3: Verify Data Was Added

```bash
python add_labeled_training_data.py list
```

Expected output:
```
======================================================================
LABELED USERS
======================================================================

1. User ID: 1445939
   Label: victim
   Attack Type: extraction_attack
   Trades: 1234
   Date Range: 2024-09-01 to 2024-09-30
   Added: 2025-11-12T11:30:00
   Notes: Victim of extraction attack on LUNCBTC in spot market, lost significant value

2. User ID: 4866868
   Label: attacker
   Attack Type: extraction_attack
   Trades: 987
   Date Range: 2024-09-01 to 2024-09-30
   Added: 2025-11-12T11:31:00
   Notes: Attacker in extraction attack on LUNCBTC, coordinated trades to extract value

======================================================================
Total: 2 labeled users
======================================================================
```

### Step 4: Train Models

```bash
python add_labeled_training_data.py train --output-dir models_labeled
```

Expected output:
```
Training models with labeled data...
Found 2 labeled users
  1445939: 1 feature vectors (label: victim)
  4866868: 1 feature vectors (label: attacker)
Total labeled samples: 2
  Anomalous: 2
  Normal: 0

Training data shape: X=(2, 45), y=(2,)

Training Isolation Forest model...
Training Autoencoder model...
Training Random Forest model...

======================================================================
MODEL EVALUATION RESULTS
======================================================================

ISOLATION_FOREST:
  Anomaly ratio: 1.0000
  Mean anomaly score: 0.8234

AUTOENCODER:
  Anomaly ratio: 1.0000
  Mean anomaly score: 0.7891

RANDOM_FOREST:
  Accuracy:  1.0000
  Precision: 1.0000
  Recall:    1.0000
  F1-Score:  1.0000
  AUC-ROC:   1.0000

✓ Models saved to models_labeled
```

## Method 3: Python Script

Create a custom script:

```python
from add_labeled_training_data import LabeledDataManager

# Initialize manager
manager = LabeledDataManager("sqlite:///trade_risk_analyzer.db")

# Add victim
manager.add_labeled_user(
    file_path="1445939.xlsx",
    user_id="1445939",
    label="victim",
    attack_type="extraction_attack",
    notes="Victim of extraction attack on LUNCBTC in spot market"
)

# Add attacker
manager.add_labeled_user(
    file_path="4866868.xlsx",
    user_id="4866868",
    label="attacker",
    attack_type="extraction_attack",
    notes="Attacker in extraction attack on LUNCBTC"
)

# Train models
results = manager.train_with_labeled_data(output_dir="models_labeled")

print("Training complete!")
print(f"Models saved to: models_labeled")
```

## Using the Trained Models

After training, update your analysis scripts to use the new models:

```python
from trade_risk_analyzer.models.trainer import ModelTrainer

# Load the trained models
trainer = ModelTrainer()
models = trainer.load_models('models_labeled')

# Use for detection
random_forest = models['random_forest']
predictions = random_forest.predict(features)
anomaly_scores = random_forest.predict_anomaly_score(features)

# High scores indicate likely manipulation
for i, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
    if score > 0.7:
        print(f"User {i}: High risk (score: {score:.2f})")
```

## Adding More Examples

As you identify more cases, keep adding them:

```bash
# Add another victim (if you have more cases)
python add_labeled_training_data.py add \
  --file "path/to/another_victim.xlsx" \
  --user-id "another_user_id" \
  --label victim \
  --attack-type extraction_attack

# Add a normal user for comparison
python add_labeled_training_data.py add \
  --file "path/to/normal_user.xlsx" \
  --user-id "normal_user_id" \
  --label normal \
  --notes "Normal trading behavior, no manipulation detected"

# Retrain with all data
python add_labeled_training_data.py train
```

## Tips

1. **Start Small**: Begin with 2-3 clear cases (like your extraction attack)
2. **Add Gradually**: As you identify more cases, add them and retrain
3. **Include Normal Users**: Add some normal users to help the model distinguish
4. **Document Well**: Use the notes field to record important details
5. **Test Results**: After training, test the models on new data to verify improvement

## Next Steps

1. Add your extraction attack data using one of the methods above
2. Train the models
3. Test the models on other users to see if they detect similar patterns
4. Continue adding more labeled examples as you identify them
5. Retrain periodically to improve accuracy
