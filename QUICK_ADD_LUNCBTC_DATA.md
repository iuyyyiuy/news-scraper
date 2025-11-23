# Quick Guide: Add LUNCBTC Extraction Attack Data

## Your Case
- **Victim**: User `1445939` (file: `1445939.xlsx`)
- **Attacker**: User `4866868` (file: `4866868.xlsx`)
- **Symbol**: LUNCBTC

## Fastest Method

Run this single command:

```bash
python add_luncbtc_extraction_attack.py
```

Press `y` to confirm, then `y` again to train models.

Done! The models will now detect similar extraction attacks.

## Alternative: Step-by-Step

```bash
# 1. Add victim
python add_labeled_training_data.py add --file "1445939.xlsx" --user-id "1445939" --label victim --attack-type extraction_attack

# 2. Add attacker
python add_labeled_training_data.py add --file "4866868.xlsx" --user-id "4866868" --label attacker --attack-type extraction_attack

# 3. Train models
python add_labeled_training_data.py train
```

## What Happens

1. Trade data is imported from both Excel files
2. Victim labeled as "victim", attacker as "attacker"
3. Features extracted from trading patterns
4. ML models trained to recognize this attack pattern
5. Models saved to `models_labeled/` directory

## Using Trained Models

```python
from trade_risk_analyzer.models.trainer import ModelTrainer

# Load models
trainer = ModelTrainer()
models = trainer.load_models('models_labeled')

# Use for detection
rf = models['random_forest']
predictions = rf.predict(features)
```

## Files You Need

Make sure these files are in your current directory:
- `1445939.xlsx` (victim's trades)
- `4866868.xlsx` (attacker's trades)

## More Info

- Full guide: `LUNCBTC_EXTRACTION_ATTACK.md`
- General guide: `LABELED_DATA_GUIDE.md`
- Examples: `EXAMPLE_ADD_LABELED_DATA.md`
