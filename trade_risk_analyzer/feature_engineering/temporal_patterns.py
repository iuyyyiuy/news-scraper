"""
Temporal Pattern Analyzer

Analyzes temporal patterns in trade data including hour-of-day distributions,
day-of-week patterns, trading session concentration, and time-between-trades statistics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from scipy import stats

from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


class TemporalPatternAnalyzer:
    """
    Analyzes temporal patterns in trading behavior
    """
    
    def __init__(self):
        """Initialize temporal pattern analyzer"""
        self.logger = logger
    
    def extract_hour_of_day_distribution(self, df: pd.DataFrame,
                                         group_by: str = 'user_id') -> pd.DataFrame:
        """
        Extract hour-of-day trading distributions
        
        Args:
            df: DataFrame with trade data (must have 'timestamp' column)
            group_by: Column to group by
            
        Returns:
            DataFrame with hour-of-day metrics
        """
        self.logger.info(f"Extracting hour-of-day distributions, grouped by {group_by}")
        
        if df.empty or 'timestamp' not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id]
            
            # Count trades per hour
            hour_counts = group_df['hour'].value_counts().sort_index()
            total_trades = len(group_df)
            
            # Calculate distribution metrics
            hour_distribution = np.zeros(24)
            for hour, count in hour_counts.items():
                hour_distribution[hour] = count / total_trades
            
            # Find peak hours
            peak_hour = hour_counts.idxmax() if len(hour_counts) > 0 else 0
            peak_hour_ratio = hour_counts.max() / total_trades if total_trades > 0 else 0
            
            # Calculate entropy (measure of distribution uniformity)
            nonzero_probs = hour_distribution[hour_distribution > 0]
            if len(nonzero_probs) > 0:
                entropy = -np.sum(nonzero_probs * np.log2(nonzero_probs))
                max_entropy = np.log2(24)
                normalized_entropy = entropy / max_entropy
            else:
                normalized_entropy = 0
            
            # Calculate concentration (inverse of entropy)
            concentration = 1 - normalized_entropy
            
            # Count active hours
            active_hours = len(hour_counts)
            
            # Identify trading session (business hours vs off-hours)
            business_hours = group_df[group_df['hour'].between(9, 17)].shape[0]
            business_hours_ratio = business_hours / total_trades if total_trades > 0 else 0
            
            metrics = {
                group_by: group_id,
                'peak_trading_hour': peak_hour,
                'peak_hour_ratio': peak_hour_ratio,
                'hour_entropy': normalized_entropy,
                'hour_concentration': concentration,
                'active_hours_count': active_hours,
                'business_hours_ratio': business_hours_ratio,
                'off_hours_ratio': 1 - business_hours_ratio
            }
            
            # Add individual hour percentages for top hours
            top_hours = hour_counts.nlargest(3)
            for i, (hour, count) in enumerate(top_hours.items(), 1):
                metrics[f'top_{i}_hour'] = hour
                metrics[f'top_{i}_hour_ratio'] = count / total_trades
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Extracted hour-of-day distributions for {len(result_df)} groups")
        
        return result_df
    
    def extract_day_of_week_distribution(self, df: pd.DataFrame,
                                         group_by: str = 'user_id') -> pd.DataFrame:
        """
        Extract day-of-week trading patterns
        
        Args:
            df: DataFrame with trade data
            group_by: Column to group by
            
        Returns:
            DataFrame with day-of-week metrics
        """
        self.logger.info(f"Extracting day-of-week distributions, grouped by {group_by}")
        
        if df.empty or 'timestamp' not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['day_of_week'] = df['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
        df['day_name'] = df['timestamp'].dt.day_name()
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id]
            
            # Count trades per day
            day_counts = group_df['day_of_week'].value_counts().sort_index()
            total_trades = len(group_df)
            
            # Calculate distribution
            day_distribution = np.zeros(7)
            for day, count in day_counts.items():
                day_distribution[day] = count / total_trades
            
            # Find peak day
            peak_day = day_counts.idxmax() if len(day_counts) > 0 else 0
            peak_day_ratio = day_counts.max() / total_trades if total_trades > 0 else 0
            
            # Calculate entropy
            nonzero_probs = day_distribution[day_distribution > 0]
            if len(nonzero_probs) > 0:
                entropy = -np.sum(nonzero_probs * np.log2(nonzero_probs))
                max_entropy = np.log2(7)
                normalized_entropy = entropy / max_entropy
            else:
                normalized_entropy = 0
            
            # Weekday vs weekend
            weekday_trades = group_df[group_df['day_of_week'] < 5].shape[0]
            weekend_trades = group_df[group_df['day_of_week'] >= 5].shape[0]
            weekday_ratio = weekday_trades / total_trades if total_trades > 0 else 0
            
            metrics = {
                group_by: group_id,
                'peak_trading_day': peak_day,
                'peak_day_ratio': peak_day_ratio,
                'day_entropy': normalized_entropy,
                'day_concentration': 1 - normalized_entropy,
                'active_days_count': len(day_counts),
                'weekday_ratio': weekday_ratio,
                'weekend_ratio': 1 - weekday_ratio
            }
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Extracted day-of-week distributions for {len(result_df)} groups")
        
        return result_df
    
    def calculate_session_concentration(self, df: pd.DataFrame,
                                       session_gap_minutes: int = 60,
                                       group_by: str = 'user_id') -> pd.DataFrame:
        """
        Calculate trading session concentration metrics
        
        Args:
            df: DataFrame with trade data
            session_gap_minutes: Minutes of inactivity to define session boundary
            group_by: Column to group by
            
        Returns:
            DataFrame with session concentration metrics
        """
        self.logger.info(f"Calculating session concentration (gap: {session_gap_minutes} min)")
        
        if df.empty or 'timestamp' not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id].sort_values('timestamp')
            
            if len(group_df) < 2:
                continue
            
            # Calculate time differences between consecutive trades
            time_diffs = group_df['timestamp'].diff()
            
            # Identify session boundaries (gaps > threshold)
            session_boundaries = time_diffs > pd.Timedelta(minutes=session_gap_minutes)
            session_ids = session_boundaries.cumsum()
            
            # Count sessions
            num_sessions = session_ids.max() + 1
            
            # Calculate session statistics
            session_sizes = group_df.groupby(session_ids).size()
            
            avg_session_size = session_sizes.mean()
            max_session_size = session_sizes.max()
            min_session_size = session_sizes.min()
            
            # Calculate session durations
            session_durations = []
            for session_id in session_ids.unique():
                session_trades = group_df[session_ids == session_id]
                if len(session_trades) > 1:
                    duration = (session_trades['timestamp'].max() - 
                              session_trades['timestamp'].min()).total_seconds() / 60
                    session_durations.append(duration)
            
            if session_durations:
                avg_session_duration = np.mean(session_durations)
                max_session_duration = np.max(session_durations)
            else:
                avg_session_duration = 0
                max_session_duration = 0
            
            # Calculate concentration (Gini coefficient of session sizes)
            sorted_sizes = np.sort(session_sizes.values)
            n = len(sorted_sizes)
            cumsum = np.cumsum(sorted_sizes)
            gini = (2 * np.sum((np.arange(1, n + 1)) * sorted_sizes)) / (n * np.sum(sorted_sizes)) - (n + 1) / n
            
            metrics = {
                group_by: group_id,
                'num_sessions': num_sessions,
                'avg_trades_per_session': avg_session_size,
                'max_trades_per_session': max_session_size,
                'min_trades_per_session': min_session_size,
                'avg_session_duration_minutes': avg_session_duration,
                'max_session_duration_minutes': max_session_duration,
                'session_concentration_gini': gini,
                'total_trades': len(group_df)
            }
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated session concentration for {len(result_df)} groups")
        
        return result_df
    
    def calculate_time_between_trades(self, df: pd.DataFrame,
                                     group_by: str = 'user_id') -> pd.DataFrame:
        """
        Compute time-between-trades statistics
        
        Args:
            df: DataFrame with trade data
            group_by: Column to group by
            
        Returns:
            DataFrame with time-between-trades metrics
        """
        self.logger.info(f"Calculating time-between-trades statistics")
        
        if df.empty or 'timestamp' not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id].sort_values('timestamp')
            
            if len(group_df) < 2:
                continue
            
            # Calculate time differences in seconds
            time_diffs = group_df['timestamp'].diff().dt.total_seconds().dropna()
            
            if len(time_diffs) == 0:
                continue
            
            # Basic statistics
            mean_time = time_diffs.mean()
            median_time = time_diffs.median()
            std_time = time_diffs.std()
            min_time = time_diffs.min()
            max_time = time_diffs.max()
            
            # Calculate percentiles
            p25 = time_diffs.quantile(0.25)
            p75 = time_diffs.quantile(0.75)
            p95 = time_diffs.quantile(0.95)
            
            # Identify rapid trading (< 1 second between trades)
            rapid_trades = (time_diffs < 1).sum()
            rapid_trade_ratio = rapid_trades / len(time_diffs)
            
            # Identify very fast trading (< 100ms)
            very_fast_trades = (time_diffs < 0.1).sum()
            very_fast_ratio = very_fast_trades / len(time_diffs)
            
            # Calculate coefficient of variation
            cv = std_time / mean_time if mean_time > 0 else 0
            
            metrics = {
                group_by: group_id,
                'mean_time_between_trades_sec': mean_time,
                'median_time_between_trades_sec': median_time,
                'std_time_between_trades_sec': std_time,
                'min_time_between_trades_sec': min_time,
                'max_time_between_trades_sec': max_time,
                'time_between_trades_cv': cv,
                'time_p25_sec': p25,
                'time_p75_sec': p75,
                'time_p95_sec': p95,
                'rapid_trade_count': rapid_trades,
                'rapid_trade_ratio': rapid_trade_ratio,
                'very_fast_trade_count': very_fast_trades,
                'very_fast_trade_ratio': very_fast_ratio
            }
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated time-between-trades for {len(result_df)} groups")
        
        return result_df
    
    def identify_temporal_clustering(self, df: pd.DataFrame,
                                    cluster_window_minutes: int = 5,
                                    cluster_threshold: int = 10,
                                    group_by: str = 'user_id') -> pd.DataFrame:
        """
        Identify unusual temporal clustering of trades
        
        Args:
            df: DataFrame with trade data
            cluster_window_minutes: Time window for clustering detection
            cluster_threshold: Minimum trades in window to be considered a cluster
            group_by: Column to group by
            
        Returns:
            DataFrame with clustering metrics
        """
        self.logger.info(f"Identifying temporal clustering (window: {cluster_window_minutes} min, threshold: {cluster_threshold})")
        
        if df.empty or 'timestamp' not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id].sort_values('timestamp')
            
            if len(group_df) < cluster_threshold:
                continue
            
            # Create time bins
            group_df['time_bin'] = group_df['timestamp'].dt.floor(f'{cluster_window_minutes}min')
            
            # Count trades per bin
            bin_counts = group_df.groupby('time_bin').size()
            
            # Identify clusters
            clusters = bin_counts[bin_counts >= cluster_threshold]
            num_clusters = len(clusters)
            
            if num_clusters > 0:
                max_cluster_size = clusters.max()
                avg_cluster_size = clusters.mean()
                total_clustered_trades = clusters.sum()
                cluster_ratio = total_clustered_trades / len(group_df)
            else:
                max_cluster_size = 0
                avg_cluster_size = 0
                total_clustered_trades = 0
                cluster_ratio = 0
            
            # Calculate clustering coefficient
            # (ratio of actual clusters to expected if uniformly distributed)
            expected_per_bin = len(group_df) / len(bin_counts) if len(bin_counts) > 0 else 0
            if expected_per_bin > 0:
                clustering_coefficient = (bin_counts.max() / expected_per_bin) if expected_per_bin > 0 else 0
            else:
                clustering_coefficient = 0
            
            metrics = {
                group_by: group_id,
                'num_clusters': num_clusters,
                'max_cluster_size': max_cluster_size,
                'avg_cluster_size': avg_cluster_size,
                'clustered_trades': total_clustered_trades,
                'cluster_ratio': cluster_ratio,
                'clustering_coefficient': clustering_coefficient,
                'total_time_bins': len(bin_counts)
            }
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Identified temporal clustering for {len(result_df)} groups")
        
        return result_df
    
    def calculate_temporal_regularity(self, df: pd.DataFrame,
                                     group_by: str = 'user_id') -> pd.DataFrame:
        """
        Calculate temporal regularity metrics
        
        Args:
            df: DataFrame with trade data
            group_by: Column to group by
            
        Returns:
            DataFrame with regularity metrics
        """
        self.logger.info(f"Calculating temporal regularity")
        
        if df.empty or 'timestamp' not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id].sort_values('timestamp')
            
            if len(group_df) < 3:
                continue
            
            # Calculate time differences
            time_diffs = group_df['timestamp'].diff().dt.total_seconds().dropna()
            
            if len(time_diffs) < 2:
                continue
            
            # Calculate regularity using coefficient of variation
            mean_diff = time_diffs.mean()
            std_diff = time_diffs.std()
            cv = std_diff / mean_diff if mean_diff > 0 else 0
            
            # Regularity score (inverse of CV, normalized)
            regularity_score = 1 / (1 + cv)
            
            # Calculate autocorrelation of time differences
            if len(time_diffs) >= 10:
                # Lag-1 autocorrelation
                autocorr = time_diffs.autocorr(lag=1)
            else:
                autocorr = 0
            
            # Detect periodic patterns using FFT
            if len(time_diffs) >= 20:
                # Normalize time differences
                normalized_diffs = (time_diffs - time_diffs.mean()) / time_diffs.std()
                
                # Apply FFT
                fft = np.fft.fft(normalized_diffs.values)
                power = np.abs(fft) ** 2
                
                # Find dominant frequency
                dominant_freq_idx = np.argmax(power[1:len(power)//2]) + 1
                periodicity_strength = power[dominant_freq_idx] / np.sum(power)
            else:
                periodicity_strength = 0
            
            metrics = {
                group_by: group_id,
                'regularity_score': regularity_score,
                'time_diff_cv': cv,
                'time_diff_autocorr': autocorr,
                'periodicity_strength': periodicity_strength,
                'is_regular': regularity_score > 0.7,
                'is_periodic': periodicity_strength > 0.1
            }
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated temporal regularity for {len(result_df)} groups")
        
        return result_df
