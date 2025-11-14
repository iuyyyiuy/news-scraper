"""Check what columns are in the Excel files"""

import pandas as pd

files = [
    "Extraction_Attack_case1/1445939.xlsx",
    "Extraction_Attack_case1/4866868.xlsx"
]

for file_path in files:
    print(f"\n{'='*70}")
    print(f"File: {file_path}")
    print(f"{'='*70}")
    
    try:
        df = pd.read_excel(file_path)
        print(f"Rows: {len(df)}")
        print(f"\nColumns:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
        
        print(f"\nFirst few rows:")
        print(df.head(3))
        
    except Exception as e:
        print(f"Error: {e}")
