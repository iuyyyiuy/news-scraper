"""
Add Extraction Attack Training Data

Simple script to add victim and attacker data from an extraction attack event.
"""

from add_labeled_training_data import LabeledDataManager


def main():
    """
    Interactive script to add extraction attack data
    """
    print("=" * 70)
    print("ADD EXTRACTION ATTACK TRAINING DATA")
    print("=" * 70)
    print("\nThis script will help you add labeled data from an extraction attack")
    print("event to improve the model's detection accuracy.\n")
    
    # Initialize manager
    db_url = input("Database URL (press Enter for default 'sqlite:///trade_risk_analyzer.db'): ").strip()
    if not db_url:
        db_url = "sqlite:///trade_risk_analyzer.db"
    
    manager = LabeledDataManager(db_url)
    
    # Add victim data
    print("\n" + "-" * 70)
    print("VICTIM DATA")
    print("-" * 70)
    
    victim_file = input("Path to victim's Excel file: ").strip()
    victim_id = input("Victim's User ID: ").strip()
    victim_notes = input("Notes about victim (optional): ").strip()
    
    print(f"\nAdding victim data...")
    victim_success = manager.add_labeled_user(
        file_path=victim_file,
        user_id=victim_id,
        label='victim',
        attack_type='extraction_attack',
        notes=victim_notes or "Victim of extraction attack in spot market"
    )
    
    if victim_success:
        print(f"✓ Victim data added successfully")
    else:
        print(f"✗ Failed to add victim data")
        return
    
    # Add attacker data
    print("\n" + "-" * 70)
    print("ATTACKER DATA")
    print("-" * 70)
    
    attacker_file = input("Path to attacker's Excel file: ").strip()
    attacker_id = input("Attacker's User ID: ").strip()
    attacker_notes = input("Notes about attacker (optional): ").strip()
    
    print(f"\nAdding attacker data...")
    attacker_success = manager.add_labeled_user(
        file_path=attacker_file,
        user_id=attacker_id,
        label='attacker',
        attack_type='extraction_attack',
        notes=attacker_notes or "Attacker in extraction attack in spot market"
    )
    
    if attacker_success:
        print(f"✓ Attacker data added successfully")
    else:
        print(f"✗ Failed to add attacker data")
        return
    
    # Ask about training
    print("\n" + "=" * 70)
    print("DATA ADDED SUCCESSFULLY")
    print("=" * 70)
    
    train_now = input("\nWould you like to train the models with this new data? (y/n): ").strip().lower()
    
    if train_now == 'y':
        print("\nTraining models with labeled data...")
        print("This may take a few minutes...\n")
        
        output_dir = input("Output directory for models (press Enter for 'models_labeled'): ").strip()
        if not output_dir:
            output_dir = "models_labeled"
        
        results = manager.train_with_labeled_data(output_dir=output_dir)
        
        if results:
            print("\n" + "=" * 70)
            print("✓ MODEL TRAINING COMPLETE")
            print("=" * 70)
            print(f"\nModels saved to: {output_dir}")
            print("\nYou can now use these models for improved detection of")
            print("extraction attacks and similar manipulation patterns.")
        else:
            print("\n✗ Model training failed")
    else:
        print("\nYou can train the models later by running:")
        print(f"  python add_labeled_training_data.py train --output-dir models_labeled")
    
    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
