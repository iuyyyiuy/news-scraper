"""
Add LUNCBTC Extraction Attack Data

Quick script to add the specific extraction attack case:
- Victim: User 1445939
- Attacker: User 4866868
- Symbol: LUNCBTC
"""

from add_labeled_training_data import LabeledDataManager


def main():
    """
    Add LUNCBTC extraction attack data
    """
    print("=" * 70)
    print("ADD LUNCBTC EXTRACTION ATTACK DATA")
    print("=" * 70)
    print("\nThis will add the extraction attack case:")
    print("  Victim:   User 1445939 (1445939.xlsx)")
    print("  Attacker: User 4866868 (4866868.xlsx)")
    print("  Symbol:   LUNCBTC")
    print()
    
    # Confirm
    confirm = input("Continue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # Initialize manager
    db_url = "sqlite:///trade_risk_analyzer.db"
    manager = LabeledDataManager(db_url)
    
    # Add victim data
    print("\n" + "-" * 70)
    print("Adding Victim Data (User 1445939)...")
    print("-" * 70)
    
    victim_success = manager.add_labeled_user(
        file_path="Extraction_Attack_case1/1445939.xlsx",
        user_id="1445939",
        label='victim',
        attack_type='extraction_attack',
        notes="Victim of extraction attack on LUNCBTC in spot market"
    )
    
    if not victim_success:
        print("✗ Failed to add victim data")
        return
    
    print("✓ Victim data added successfully")
    
    # Add attacker data
    print("\n" + "-" * 70)
    print("Adding Attacker Data (User 4866868)...")
    print("-" * 70)
    
    attacker_success = manager.add_labeled_user(
        file_path="Extraction_Attack_case1/4866868.xlsx",
        user_id="4866868",
        label='attacker',
        attack_type='extraction_attack',
        notes="Attacker in extraction attack on LUNCBTC, coordinated trades to extract value"
    )
    
    if not attacker_success:
        print("✗ Failed to add attacker data")
        return
    
    print("✓ Attacker data added successfully")
    
    # Ask about training
    print("\n" + "=" * 70)
    print("DATA ADDED SUCCESSFULLY")
    print("=" * 70)
    
    train_now = input("\nTrain models with this data now? (y/n): ").strip().lower()
    
    if train_now == 'y':
        print("\nTraining models with labeled data...")
        print("This may take a few minutes...\n")
        
        results = manager.train_with_labeled_data(output_dir="models_labeled")
        
        if results:
            print("\n" + "=" * 70)
            print("✓ MODEL TRAINING COMPLETE")
            print("=" * 70)
            print("\nModels saved to: models_labeled")
            print("\nThe models can now detect extraction attacks similar to")
            print("the LUNCBTC case (victim: 1445939, attacker: 4866868)")
        else:
            print("\n✗ Model training failed")
    else:
        print("\nYou can train the models later by running:")
        print("  python add_labeled_training_data.py train")
    
    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
