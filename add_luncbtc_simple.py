"""
Simple script to add LUNCBTC extraction attack data
This version has minimal dependencies
"""

import sys
import os

# Check if files exist
victim_file = "Extraction_Attack_case1/1445939.xlsx"
attacker_file = "Extraction_Attack_case1/4866868.xlsx"

print("=" * 70)
print("ADD LUNCBTC EXTRACTION ATTACK DATA")
print("=" * 70)
print("\nChecking files...")

if not os.path.exists(victim_file):
    print(f"✗ Victim file not found: {victim_file}")
    sys.exit(1)
else:
    print(f"✓ Found victim file: {victim_file}")

if not os.path.exists(attacker_file):
    print(f"✗ Attacker file not found: {attacker_file}")
    sys.exit(1)
else:
    print(f"✓ Found attacker file: {attacker_file}")

print("\nAttempting to import required modules...")

try:
    from add_labeled_training_data import LabeledDataManager
    print("✓ Modules imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nPlease install required dependencies:")
    print("  pip install sqlalchemy pandas numpy scikit-learn openpyxl")
    sys.exit(1)

print("\n" + "-" * 70)
print("ADDING DATA")
print("-" * 70)

# Initialize manager
manager = LabeledDataManager("sqlite:///trade_risk_analyzer.db")

# Add victim
print("\n1. Adding victim data (User 1445939)...")
victim_success = manager.add_labeled_user(
    file_path=victim_file,
    user_id="1445939",
    label='victim',
    attack_type='extraction_attack',
    notes="Victim of extraction attack on LUNCBTC in spot market"
)

if not victim_success:
    print("✗ Failed to add victim data")
    sys.exit(1)

print("✓ Victim data added successfully")

# Add attacker
print("\n2. Adding attacker data (User 4866868)...")
attacker_success = manager.add_labeled_user(
    file_path=attacker_file,
    user_id="4866868",
    label='attacker',
    attack_type='extraction_attack',
    notes="Attacker in extraction attack on LUNCBTC, coordinated trades to extract value"
)

if not attacker_success:
    print("✗ Failed to add attacker data")
    sys.exit(1)

print("✓ Attacker data added successfully")

# List labeled users
print("\n" + "-" * 70)
print("LABELED USERS")
print("-" * 70)
manager.list_labeled_users()

# Ask about training
print("\n" + "=" * 70)
print("DATA ADDED SUCCESSFULLY")
print("=" * 70)

train_input = input("\nTrain models with this data now? (y/n): ").strip().lower()

if train_input == 'y':
    print("\nTraining models...")
    print("This may take a few minutes...\n")
    
    try:
        results = manager.train_with_labeled_data(output_dir="models_labeled")
        
        if results:
            print("\n" + "=" * 70)
            print("✓ MODEL TRAINING COMPLETE")
            print("=" * 70)
            print("\nModels saved to: models_labeled/")
            print("\nThe models can now detect extraction attacks similar to")
            print("the LUNCBTC case (victim: 1445939, attacker: 4866868)")
        else:
            print("\n✗ Model training failed")
    except Exception as e:
        print(f"\n✗ Training error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\nYou can train the models later by running:")
    print("  python add_labeled_training_data.py train")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
