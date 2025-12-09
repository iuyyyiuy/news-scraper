"""
Comprehensive User Behavior Analysis

Loads and analyzes all users from both data directories:
- 商務大使09.22 (10 users)
- 商務大使09.28 (7 users)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import glob

from trade_risk_analyzer.data_ingestion import TradeDataImporter, TradeDataValidator
from trade_risk_analyzer.feature_engineering import FeatureExtractor
from trade_risk_analyzer.models import IsolationForestModel, RandomForestModel


def find_all_excel_files():
    """Find all Excel files in both directories"""
    print("=" * 80, flush=True)
    print("DISCOVERING USER DATA FILES", flush=True)
    print("=" * 80, flush=True)
    
    directories = [
        "商務大使09.22",
        "商務大使09.28"
    ]
    
    all_files = []
    
    for directory in directories:
        print(f"\nChecking {directory}...", flush=True)
        if Path(directory).exists():
            # Find all xlsx files recursively
            files = list(Path(directory).rglob("*.xlsx"))
            print(f"  Found {len(files)} files", flush=True)
            all_files.extend(files)
        else:
            print(f"  Directory not found", flush=True)
    
    print(f"\nTotal files found: {len(all_files)}", flush=True)
    
    return all_files


def extract_user_id_from_filename(filepath):
    """Extract UID from filename"""
    filename = Path(filepath).stem
    if filename.startswith("UID "):
        return f"user_{filename.split()[1]}"
    return None


def load_all_users():
    """Load all user data"""
    print("\n" + "=" * 80)
    print("LOADING ALL USER DATA")
    print("=" * 80)
    
    files = find_all_excel_files()
    
    importer = TradeDataImporter()
    validator = TradeDataValidator()
    
    column_mapping = {
        '开仓时间': 'open_time',
        '平仓时间': 'close_time',
        '合约': 'symbol',
        '类型': 'position_type',
        '开仓均价': 'open_price',
        '进入价格': 'entry_price',
        '离开价格': 'exit_price',
        '历史最高数量': 'max_quantity'
    }
    
    all_trades = []
    user_summary = []
    
    for i, file_path in enumerate(files, 1):
        user_id = extract_user_id_from_filename(file_path)
        
        if not user_id:
            continue
        
        print(f"\n[{i}/{len(files)}] Loading {user_id}...")
        
        try:
            df = importer.import_excel(str(file_path))
            df = df.rename(columns=column_mapping)
            
            # Transform to trade format
            trades = []
            for idx, row in df.iterrows():
                # Opening trade
                trades.append({
                    'trade_id': f"{user_id}_open_{idx}",
                    'user_id': user_id,
                    'timestamp': pd.to_datetime(row['open_time']),
                    'symbol': row['symbol'],
                    'price': float(row['entry_price']),
                    'volume': float(row['max_quantity']),
                    'trade_type': 'BUY' if row['position_type'] == '多仓' else 'SELL',
                    'order_id': f"{user_id}_order_open_{idx}"
                })
                
                # Closing trade
                trades.append({
                    'trade_id': f"{user_id}_close_{idx}",
                    'user_id': user_id,
                    'timestamp': pd.to_datetime(row['close_time']),
                    'symbol': row['symbol'],
                    'price': float(row['exit_price']),
                    'volume': float(row['max_quantity']),
                    'trade_type': 'SELL' if row['position_type'] == '多仓' else 'BUY',
                    'order_id': f"{user_id}_order_close_{idx}"
                })
            
            trades_df = pd.DataFrame(trades)
            
            # Validate
            result = validator.validate(trades_df, strict=False)
            
            if result.valid_records > 0:
                valid_df = validator.get_valid_records(trades_df, result)
                all_trades.append(valid_df)
                
                # Calculate summary stats
                time_span = (valid_df['timestamp'].max() - valid_df['timestamp'].min()).total_seconds() / 86400
                
                user_summary.append({
                    'user_id': user_id,
                    'total_trades': len(valid_df),
                    'unique_symbols': valid_df['symbol'].nunique(),
                    'time_span_days': time_span,
                    'trades_per_day': len(valid_df) / time_span if time_span > 0 else 0,
                    'first_trade': valid_df['timestamp'].min(),
                    'last_trade': valid_df['timestamp'].max()
                })
                
                print(f"  ✓ {len(valid_df)} trades, {time_span:.1f} days, {len(valid_df)/time_span if time_span > 0 else 0:.1f} trades/day")
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
    
    combined_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    summary_df = pd.DataFrame(user_summary)
    
    print(f"\n{'=' * 80}")
    print("DATA LOADING COMPLETE")
    print(f"{'=' * 80}")
    print(f"Total users loaded: {len(all_trades)}")
    print(f"Total trades: {len(combined_df)}")
    print(f"Date range: {combined_df['timestamp'].min()} to {combined_df['timestamp'].max()}")
    print(f"Symbols: {combined_df['symbol'].unique().tolist()}")
    
    return combined_df, summary_df


def analyze_user_behavior(trades_df, summary_df):
    """Analyze user behavior patterns"""
    print("\n" + "=" * 80)
    print("USER BEHAVIOR ANALYSIS")
    print("=" * 80)
    
    # Sort by trades per day
    summary_df = summary_df.sort_values('trades_per_day', ascending=False)
    
    print("\nTop 10 Most Active Users (by trades/day):")
    print("-" * 80)
    for i, row in summary_df.head(10).iterrows():
        print(f"{row['user_id']:20s} | {row['total_trades']:6.0f} trades | "
              f"{row['trades_per_day']:8.2f} trades/day | {row['unique_symbols']:.0f} symbols")
    
    # Categorize users
    print("\nUser Categories:")
    print("-" * 80)
    
    high_freq = summary_df[summary_df['trades_per_day'] > 100]
    medium_freq = summary_df[(summary_df['trades_per_day'] >= 20) & (summary_df['trades_per_day'] <= 100)]
    low_freq = summary_df[summary_df['trades_per_day'] < 20]
    
    print(f"High Frequency (>100 trades/day): {len(high_freq)} users")
    for _, row in high_freq.iterrows():
        print(f"  - {row['user_id']}: {row['trades_per_day']:.1f} trades/day")
    
    print(f"\nMedium Frequency (20-100 trades/day): {len(medium_freq)} users")
    for _, row in medium_freq.iterrows():
        print(f"  - {row['user_id']}: {row['trades_per_day']:.1f} trades/day")
    
    print(f"\nLow Frequency (<20 trades/day): {len(low_freq)} users")
    for _, row in low_freq.iterrows():
        print(f"  - {row['user_id']}: {row['trades_per_day']:.1f} trades/day")
    
    return summary_df


def extract_features_for_all(trades_df):
    """Extract features for all users"""
    print("\n" + "=" * 80)
    print("FEATURE EXTRACTION")
    print("=" * 80)
    
    extractor = FeatureExtractor(
        time_windows=['1H', '24H', '7D'],
        scaler_type='standard'
    )
    
    print("\nExtracting features for all users...")
    features_df = extractor.extract_features(
        trades_df,
        group_by='user_id',
        include_frequency=True,
        include_volume=True,
        include_temporal=True,
        include_price=True,
        include_behavioral=True
    )
    
    print(f"\n✓ Feature extraction complete")
    print(f"  Users: {len(features_df)}")
    print(f"  Features: {len(features_df.columns) - 1}")
    
    # Save features
    features_df.to_csv('all_users_features.csv', index=False)
    print(f"  ✓ Saved to all_users_features.csv")
    
    return features_df


def detect_anomalies(features_df):
    """Detect anomalies using ML models"""
    print("\n" + "=" * 80)
    print("ANOMALY DETECTION")
    print("=" * 80)
    
    # Prepare data
    user_ids = features_df['user_id'].values
    numeric_cols = features_df.select_dtypes(include=[np.number]).columns
    feature_cols = [col for col in numeric_cols if col != 'user_id']
    X = features_df[feature_cols].values
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    
    # Isolation Forest
    print("\n1. Isolation Forest Detection")
    print("-" * 80)
    
    if_model = IsolationForestModel(
        n_estimators=100,
        contamination=0.3,  # Expect 30% anomalies
        random_state=42
    )
    
    if_model.train(X)
    if_predictions = if_model.predict(X)
    if_scores = if_model.predict_proba(X)
    
    anomaly_count = np.sum(if_predictions == -1)
    print(f"Anomalies detected: {anomaly_count}/{len(user_ids)}")
    
    # Create results DataFrame
    results_df = pd.DataFrame({
        'user_id': user_ids,
        'if_prediction': ['ANOMALY' if p == -1 else 'NORMAL' for p in if_predictions],
        'if_score': if_scores,
        'total_trades': features_df['total_trades'].values,
        'trades_per_day': features_df['avg_trades_per_day'].values,
        'win_ratio': features_df['win_ratio'].values,
        'unique_symbols': features_df['unique_symbols'].values
    })
    
    # Sort by anomaly score
    results_df = results_df.sort_values('if_score', ascending=False)
    
    print("\nTop 10 Most Suspicious Users:")
    print("-" * 80)
    for i, row in results_df.head(10).iterrows():
        print(f"{row['user_id']:20s} | {row['if_prediction']:8s} | "
              f"Score: {row['if_score']:.4f} | {row['total_trades']:6.0f} trades | "
              f"{row['trades_per_day']:8.2f} trades/day")
    
    # Save results
    results_df.to_csv('anomaly_detection_results.csv', index=False)
    print(f"\n✓ Results saved to anomaly_detection_results.csv")
    
    return results_df


def generate_final_report(trades_df, summary_df, features_df, results_df):
    """Generate final analysis report"""
    print("\n" + "=" * 80)
    print("FINAL ANALYSIS REPORT")
    print("=" * 80)
    
    print(f"\nDataset Overview:")
    print(f"  Total users analyzed: {len(summary_df)}")
    print(f"  Total trades: {len(trades_df):,}")
    print(f"  Date range: {trades_df['timestamp'].min().date()} to {trades_df['timestamp'].max().date()}")
    print(f"  Symbols traded: {', '.join(trades_df['symbol'].unique())}")
    
    print(f"\nTrading Activity Distribution:")
    print(f"  High frequency users (>100 trades/day): {len(summary_df[summary_df['trades_per_day'] > 100])}")
    print(f"  Medium frequency users (20-100 trades/day): {len(summary_df[(summary_df['trades_per_day'] >= 20) & (summary_df['trades_per_day'] <= 100)])}")
    print(f"  Low frequency users (<20 trades/day): {len(summary_df[summary_df['trades_per_day'] < 20])}")
    
    print(f"\nAnomaly Detection Results:")
    anomalies = results_df[results_df['if_prediction'] == 'ANOMALY']
    print(f"  Anomalous users detected: {len(anomalies)}/{len(results_df)}")
    print(f"  Percentage flagged: {len(anomalies)/len(results_df)*100:.1f}%")
    
    print(f"\nHigh-Risk Users (Anomalies with >50 trades/day):")
    high_risk = anomalies[anomalies['trades_per_day'] > 50]
    for _, row in high_risk.iterrows():
        print(f"  - {row['user_id']}: {row['trades_per_day']:.1f} trades/day, score: {row['if_score']:.4f}")
    
    print(f"\n{'=' * 80}")
    print("ANALYSIS COMPLETE")
    print(f"{'=' * 80}")
    
    print(f"\nOutput Files:")
    print(f"  - all_users_features.csv (feature matrix)")
    print(f"  - anomaly_detection_results.csv (detection results)")


def main():
    """Main analysis function"""
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "COMPREHENSIVE USER BEHAVIOR ANALYSIS".center(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    
    try:
        # Load all data
        trades_df, summary_df = load_all_users()
        
        if trades_df.empty:
            print("\n✗ No data loaded. Exiting.")
            return
        
        # Analyze behavior
        summary_df = analyze_user_behavior(trades_df, summary_df)
        
        # Extract features
        features_df = extract_features_for_all(trades_df)
        
        # Detect anomalies
        results_df = detect_anomalies(features_df)
        
        # Generate report
        generate_final_report(trades_df, summary_df, features_df, results_df)
        
    except Exception as e:
        print(f"\n✗ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
