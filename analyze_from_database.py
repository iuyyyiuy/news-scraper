"""
Analyze User Behavior from SQL Database

This script reads trade data from the SQL database and performs analysis.
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

from trade_risk_analyzer.feature_engineering import FeatureExtractor
from trade_risk_analyzer.models import IsolationForestModel


def load_trades_from_db(db_path='trade_data.db', user_ids=None):
    """Load trades from database"""
    print("=" * 80)
    print("LOADING DATA FROM DATABASE")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    
    # Load trades
    if user_ids:
        placeholders = ','.join('?' * len(user_ids))
        query = f"SELECT * FROM trades WHERE user_id IN ({placeholders})"
        trades_df = pd.read_sql_query(query, conn, params=user_ids)
    else:
        trades_df = pd.read_sql_query("SELECT * FROM trades", conn)
    
    # Convert timestamp to datetime
    trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
    
    print(f"\n✓ Loaded {len(trades_df):,} trades")
    print(f"  Users: {trades_df['user_id'].nunique()}")
    print(f"  Date range: {trades_df['timestamp'].min()} to {trades_df['timestamp'].max()}")
    
    conn.close()
    return trades_df


def get_user_summary_from_db(db_path='trade_data.db'):
    """Get user summary from database"""
    conn = sqlite3.connect(db_path)
    
    query = '''
        SELECT 
            user_id,
            total_trades,
            first_seen,
            last_seen,
            ROUND((julianday(last_seen) - julianday(first_seen) + 0.01), 2) as time_span_days,
            ROUND(total_trades / (julianday(last_seen) - julianday(first_seen) + 0.01), 2) as trades_per_day
        FROM users
        ORDER BY trades_per_day DESC
    '''
    
    summary_df = pd.read_sql_query(query, conn)
    summary_df['first_seen'] = pd.to_datetime(summary_df['first_seen'])
    summary_df['last_seen'] = pd.to_datetime(summary_df['last_seen'])
    
    conn.close()
    return summary_df


def analyze_user_behavior(trades_df, summary_df):
    """Analyze user behavior patterns"""
    print("\n" + "=" * 80)
    print("USER BEHAVIOR ANALYSIS")
    print("=" * 80)
    
    print("\nTop 10 Most Active Users (by trades/day):")
    print("-" * 80)
    for i, row in summary_df.head(10).iterrows():
        print(f"{row['user_id']:20s} | {row['total_trades']:6.0f} trades | "
              f"{row['trades_per_day']:8.2f} trades/day")
    
    # Categorize users
    print("\nUser Categories:")
    print("-" * 80)
    
    high_freq = summary_df[summary_df['trades_per_day'] > 100]
    medium_freq = summary_df[(summary_df['trades_per_day'] >= 20) & (summary_df['trades_per_day'] <= 100)]
    low_freq = summary_df[summary_df['trades_per_day'] < 20]
    
    print(f"High Frequency (>100 trades/day): {len(high_freq)} users")
    print(f"Medium Frequency (20-100 trades/day): {len(medium_freq)} users")
    print(f"Low Frequency (<20 trades/day): {len(low_freq)} users")
    
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
    print("\nIsolation Forest Detection")
    print("-" * 80)
    
    if_model = IsolationForestModel(
        n_estimators=100,
        contamination=0.3,
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
    
    return results_df


def save_results_to_db(results_df, db_path='trade_data.db'):
    """Save analysis results back to database"""
    print("\n" + "=" * 80)
    print("SAVING RESULTS TO DATABASE")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    analysis_date = datetime.now()
    
    for _, row in results_df.iterrows():
        # Determine risk level
        if row['if_prediction'] == 'ANOMALY':
            if row['trades_per_day'] > 500:
                risk_level = 'CRITICAL'
            elif row['trades_per_day'] > 100:
                risk_level = 'HIGH'
            else:
                risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        cursor.execute('''
            INSERT INTO analysis_results 
            (user_id, analysis_date, anomaly_score, is_anomaly, trades_per_day, win_ratio, risk_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['user_id'],
            analysis_date,
            row['if_score'],
            1 if row['if_prediction'] == 'ANOMALY' else 0,
            row['trades_per_day'],
            row['win_ratio'],
            risk_level
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✓ Saved {len(results_df)} analysis results to database")


def generate_final_report(trades_df, summary_df, results_df):
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


def main():
    """Main analysis function"""
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "DATABASE-DRIVEN USER BEHAVIOR ANALYSIS".center(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    
    db_path = 'trade_data.db'
    
    try:
        # Load data from database
        trades_df = load_trades_from_db(db_path)
        summary_df = get_user_summary_from_db(db_path)
        
        if trades_df.empty:
            print("\n✗ No data in database. Run setup_database.py first.")
            return
        
        # Analyze behavior
        summary_df = analyze_user_behavior(trades_df, summary_df)
        
        # Extract features
        features_df = extract_features_for_all(trades_df)
        
        # Detect anomalies
        results_df = detect_anomalies(features_df)
        
        # Save results to database
        save_results_to_db(results_df, db_path)
        
        # Generate report
        generate_final_report(trades_df, summary_df, results_df)
        
        # Save CSV exports
        results_df.to_csv('db_analysis_results.csv', index=False)
        features_df.to_csv('db_features.csv', index=False)
        print(f"\n✓ Results also exported to CSV files")
        
    except Exception as e:
        print(f"\n✗ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
