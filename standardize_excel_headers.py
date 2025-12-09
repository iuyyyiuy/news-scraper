"""
Standardize Excel Column Headers

This script converts Chinese column headers to English headers
to match the format of 8429394.xlsx
"""

import pandas as pd
from pathlib import Path
import shutil
from datetime import datetime


# Column mapping from Chinese to English
COLUMN_MAPPING = {
    # Chinese -> English
    '开仓时间': 'open_time',
    '平仓时间': 'close_time',
    '合约': 'symbol',
    '类型': 'side',
    '开仓均价': 'avg_entry_price',
    '进入价格': 'entry_price',
    '离开价格': 'exit_price',
    '平仓类型': 'close_type',
    '历史最高数量': 'max_qty',
    '历史最高价值': 'max_notional',
    '已实现盈亏': 'realized_pnl',
    '手续费': 'fees',
    '资金费用': 'funding_fee',
}

# Also map the side values
SIDE_MAPPING = {
    '多仓': 'long',
    '空仓': 'short',
    'LONG': 'long',  # Convert existing uppercase to lowercase
    'SHORT': 'short',  # Convert existing uppercase to lowercase
}

# Map close_type values
CLOSE_TYPE_MAPPING = {
    '限价': 'limit',
    '市价': 'market',
    'Limit': 'limit',  # Convert existing capitalized to lowercase
    'Market': 'market',  # Convert existing capitalized to lowercase
}


def find_all_excel_files(directories=['商務大使09.22', '商務大使09.28']):
    """Find all Excel files"""
    all_files = []
    
    for directory in directories:
        if Path(directory).exists():
            files = list(Path(directory).rglob("*.xlsx"))
            all_files.extend(files)
    
    return all_files


def backup_file(file_path):
    """Create a backup of the original file"""
    backup_dir = Path('excel_backups')
    backup_dir.mkdir(exist_ok=True)
    
    # Create backup with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
    backup_path = backup_dir / backup_name
    
    shutil.copy2(file_path, backup_path)
    return backup_path


def standardize_excel_file(file_path, create_backup=True):
    """
    Standardize column headers in an Excel file
    
    Returns:
        True if file was modified
        False if file already had English headers
    """
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Check if needs standardization
        needs_standardization = False
        
        # Check if column headers need translation
        if any(col in COLUMN_MAPPING for col in df.columns):
            needs_standardization = True
        
        # Check if side values need translation
        if 'side' in df.columns and any(val in SIDE_MAPPING for val in df['side'].unique() if pd.notna(val)):
            needs_standardization = True
        
        # Check if close_type values need translation
        if 'close_type' in df.columns and any(val in CLOSE_TYPE_MAPPING for val in df['close_type'].unique() if pd.notna(val)):
            needs_standardization = True
        
        if not needs_standardization:
            return False, "Already standardized"
        
        # Create backup if requested
        if create_backup:
            backup_path = backup_file(file_path)
        
        # Rename columns
        df = df.rename(columns=COLUMN_MAPPING)
        
        # Standardize side values if 'side' column exists
        if 'side' in df.columns:
            df['side'] = df['side'].map(SIDE_MAPPING).fillna(df['side'])
        
        # Standardize close_type values if 'close_type' column exists
        if 'close_type' in df.columns:
            df['close_type'] = df['close_type'].map(CLOSE_TYPE_MAPPING).fillna(df['close_type'])
        
        # Save back to the same file
        df.to_excel(file_path, index=False)
        
        return True, "Standardized"
        
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Main function"""
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "STANDARDIZE EXCEL COLUMN HEADERS".center(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    
    print("\n" + "=" * 80)
    print("FINDING EXCEL FILES")
    print("=" * 80)
    
    files = find_all_excel_files()
    print(f"\nFound {len(files)} Excel files")
    
    print("\n" + "=" * 80)
    print("STANDARDIZING FILES")
    print("=" * 80)
    print("\nColumn mapping:")
    for chinese, english in COLUMN_MAPPING.items():
        print(f"  {chinese:12s} -> {english}")
    
    print("\nSide value mapping:")
    for chinese, english in SIDE_MAPPING.items():
        print(f"  {chinese:6s} -> {english}")
    
    print("\nClose type mapping:")
    for chinese, english in CLOSE_TYPE_MAPPING.items():
        print(f"  {chinese:6s} -> {english}")
    
    print("\n" + "-" * 80)
    
    modified_count = 0
    already_standard_count = 0
    error_count = 0
    
    for i, file_path in enumerate(files, 1):
        filename = file_path.name
        print(f"\n[{i}/{len(files)}] {filename}")
        
        was_modified, message = standardize_excel_file(file_path, create_backup=True)
        
        if was_modified:
            print(f"  ✓ {message}")
            modified_count += 1
        elif "Already" in message:
            print(f"  ○ {message}")
            already_standard_count += 1
        else:
            print(f"  ✗ {message}")
            error_count += 1
    
    print("\n" + "=" * 80)
    print("STANDARDIZATION COMPLETE")
    print("=" * 80)
    print(f"Files modified: {modified_count}")
    print(f"Already standardized: {already_standard_count}")
    print(f"Errors: {error_count}")
    print(f"Total files: {len(files)}")
    
    if modified_count > 0:
        print(f"\n✓ Backups saved in: ./excel_backups/")
    
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    # Verify a few files
    print("\nChecking first 3 files:")
    for file_path in files[:3]:
        df = pd.read_excel(file_path)
        print(f"\n{file_path.name}:")
        print(f"  Columns: {list(df.columns)}")
        if 'side' in df.columns:
            print(f"  Side values: {df['side'].unique().tolist()}")
        if 'close_type' in df.columns:
            print(f"  Close type values: {df['close_type'].unique().tolist()}")
    
    print("\n✓ All files have been standardized!")
    print("\nNext step: Run import script to load data into database")


if __name__ == "__main__":
    main()
