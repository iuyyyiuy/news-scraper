"""
Volume Statistics Calculator

Calculates volume-based features including mean, median, standard deviation,
percentile rankings, spike detection, and consistency scores.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats

from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


class VolumeStatisticsCalculator:
    """
    Calculates volume-based statistical features from trade data
    """
    
    def __init__(self, rolling_windows: Optional[List[str]] = None):
        """
        Initialize volume statistics calculator
        
        Args:
            rolling_windows: List of rolling window sizes (e.g., ['1H', '24H', '7D'])
        """
        self.rolling_windows = rolling_windows or ['1H', '24H', '7D']
        self.logger = logger
    
    def calculate_basic_statistics(self, df: pd.DataFrame,
                                   group_by: str = 'user_id') -> pd.DataFrame:
        """
        Calculate basic volume statistics (mean, median, std, min, max)
        
        Args:
            df: DataFrame with trade data (must have 'volume' column)
            group_by: Column to group by
            
        Returns:
            DataFrame with volume statistics per group
        """
        self.logger.info(f"Calculating basic volume statistics, grouped by {group_by}")
        
        if df.empty or 'volume' not in df.columns:
            return pd.DataFrame()
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id]
            volumes = group_df['volume'].values
            
            if len(volumes) == 0:
                continue
            
            metrics = {
                group_by: group_id,
                'volume_mean': np.mean(volumes),
                'volume_median': np.median(volumes),
                'volume_std': np.std(volumes),
                'volume_min': np.min(volumes),
                'volume_max': np.max(volumes),
                'volume_range': np.max(volumes) - np.min(volumes),
                'volume_sum': np.sum(volumes),
                'volume_count': len(volumes)
            }
            
            # Calculate coefficient of variation (std/mean)
            if metrics['volume_mean'] > 0:
                metrics['volume_cv'] = metrics['volume_std'] / metrics['volume_mean']
            else:
                metrics['volume_cv'] = 0
            
            # Calculate skewness and kurtosis
            if len(volumes) >= 3:
                metrics['volume_skewness'] = stats.skew(volumes)
                metrics['volume_kurtosis'] = stats.kurtosis(volumes)
            else:
                metrics['volume_skewness'] = 0
                metrics['volume_kurtosis'] = 0
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated basic statistics for {len(result_df)} groups")
        
        return result_df
    
    def calculate_percentile_rankings(self, df: pd.DataFrame,
                                     percentiles: Optional[List[int]] = None,
                                     group_by: str = 'user_id') -> pd.DataFrame:
        """
        Calculate percentile rankings for volume analysis
        
        Args:
            df: DataFrame with trade data
            percentiles: List of percentiles to calculate (default: [25, 50, 75, 90, 95, 99])
            group_by: Column to group by
            
        Returns:
            DataFrame with percentile rankings
        """
        percentiles = percentiles or [25, 50, 75, 90, 95, 99]
        
        self.logger.info(f"Calculating volume percentiles: {percentiles}")
        
        if df.empty or 'volume' not in df.columns:
            return pd.DataFrame()
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id]
            volumes = group_df['volume'].values
            
            if len(volumes) == 0:
                continue
            
            metrics = {group_by: group_id}
            
            # Calculate percentiles
            for p in percentiles:
                metrics[f'volume_p{p}'] = np.percentile(volumes, p)
            
            # Calculate IQR (Interquartile Range)
            q75 = np.percentile(volumes, 75)
            q25 = np.percentile(volumes, 25)
            metrics['volume_iqr'] = q75 - q25
            
            # Identify outliers using IQR method
            iqr = metrics['volume_iqr']
            lower_bound = q25 - 1.5 * iqr
            upper_bound = q75 + 1.5 * iqr
            outliers = (volumes < lower_bound) | (volumes > upper_bound)
            metrics['volume_outlier_count'] = np.sum(outliers)
            metrics['volume_outlier_ratio'] = np.sum(outliers) / len(volumes)
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated percentile rankings for {len(result_df)} groups")
        
        return result_df
    
    def detect_volume_spikes(self, df: pd.DataFrame,
                            spike_threshold: float = 3.0,
                            rolling_window: str = '1H',
                            group_by: str = 'user_id') -> pd.DataFrame:
        """
        Detect volume spikes using rolling window comparisons
        
        Args:
            df: DataFrame with trade data
            spike_threshold: Multiplier for spike detection (e.g., 3.0 = 3x average)
            rolling_window: Window for rolling average calculation
            group_by: Column to group by
            
        Returns:
            DataFrame with spike detection metrics
        """
        self.logger.info(f"Detecting volume spikes (threshold: {spike_threshold}x, window: {rolling_window})")
        
        if df.empty or 'volume' not in df.columns or 'timestamp' not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id].sort_values('timestamp')
            
            if len(group_df) < 2:
                continue
            
            # Set timestamp as index for rolling calculations
            group_df = group_df.set_index('timestamp')
            
            # Calculate rolling average
            rolling_avg = group_df['volume'].rolling(window=rolling_window, min_periods=1).mean()
            
            # Detect spikes
            spikes = group_df['volume'] > (rolling_avg * spike_threshold)
            spike_count = spikes.sum()
            
            # Calculate spike statistics
            if spike_count > 0:
                spike_volumes = group_df.loc[spikes, 'volume']
                max_spike_ratio = (spike_volumes / rolling_avg[spikes]).max()
                avg_spike_ratio = (spike_volumes / rolling_avg[spikes]).mean()
            else:
                max_spike_ratio = 0
                avg_spike_ratio = 0
            
            metrics = {
                group_by: group_id,
                'spike_count': spike_count,
                'spike_ratio': spike_count / len(group_df),
                'max_spike_multiplier': max_spike_ratio,
                'avg_spike_multiplier': avg_spike_ratio,
                'total_trades': len(group_df)
            }
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Detected volume spikes for {len(result_df)} groups")
        
        return result_df
    
    def calculate_consistency_score(self, df: pd.DataFrame,
                                    group_by: str = 'user_id') -> pd.DataFrame:
        """
        Compute volume consistency scores
        
        Args:
            df: DataFrame with trade data
            group_by: Column to group by
            
        Returns:
            DataFrame with consistency scores
        """
        self.logger.info(f"Calculating volume consistency scores, grouped by {group_by}")
        
        if df.empty or 'volume' not in df.columns:
            return pd.DataFrame()
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id]
            volumes = group_df['volume'].values
            
            if len(volumes) < 2:
                continue
            
            # Calculate consistency metrics
            mean_vol = np.mean(volumes)
            std_vol = np.std(volumes)
            
            # Consistency score: inverse of coefficient of variation (0-1 scale)
            if mean_vol > 0:
                cv = std_vol / mean_vol
                consistency_score = 1 / (1 + cv)  # Normalize to 0-1
            else:
                consistency_score = 0
            
            # Calculate consecutive volume changes
            if len(volumes) > 1:
                volume_changes = np.diff(volumes)
                abs_changes = np.abs(volume_changes)
                mean_abs_change = np.mean(abs_changes)
                max_abs_change = np.max(abs_changes)
                
                # Relative changes
                relative_changes = volume_changes / volumes[:-1]
                mean_relative_change = np.mean(np.abs(relative_changes))
            else:
                mean_abs_change = 0
                max_abs_change = 0
                mean_relative_change = 0
            
            # Calculate entropy (measure of randomness)
            # Bin volumes into deciles
            if len(volumes) >= 10:
                hist, _ = np.histogram(volumes, bins=10)
                hist = hist / len(volumes)  # Normalize
                hist = hist[hist > 0]  # Remove zeros
                entropy = -np.sum(hist * np.log2(hist))
                normalized_entropy = entropy / np.log2(10)  # Normalize to 0-1
            else:
                normalized_entropy = 0
            
            metrics = {
                group_by: group_id,
                'consistency_score': consistency_score,
                'mean_abs_volume_change': mean_abs_change,
                'max_abs_volume_change': max_abs_change,
                'mean_relative_volume_change': mean_relative_change,
                'volume_entropy': normalized_entropy,
                'volume_stability': 1 - normalized_entropy  # Inverse of entropy
            }
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated consistency scores for {len(result_df)} groups")
        
        return result_df
    
    def calculate_rolling_statistics(self, df: pd.DataFrame,
                                     group_by: str = 'user_id') -> pd.DataFrame:
        """
        Calculate rolling window statistics for volume
        
        Args:
            df: DataFrame with trade data
            group_by: Column to group by
            
        Returns:
            DataFrame with rolling statistics
        """
        self.logger.info(f"Calculating rolling volume statistics")
        
        if df.empty or 'volume' not in df.columns or 'timestamp' not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id].sort_values('timestamp')
            
            if len(group_df) < 2:
                continue
            
            group_df = group_df.set_index('timestamp')
            
            metrics = {group_by: group_id}
            
            # Calculate rolling statistics for each window
            for window in self.rolling_windows:
                rolling_mean = group_df['volume'].rolling(window=window, min_periods=1).mean()
                rolling_std = group_df['volume'].rolling(window=window, min_periods=1).std()
                rolling_max = group_df['volume'].rolling(window=window, min_periods=1).max()
                rolling_min = group_df['volume'].rolling(window=window, min_periods=1).min()
                
                # Get latest values
                metrics[f'volume_rolling_mean_{window}'] = rolling_mean.iloc[-1]
                metrics[f'volume_rolling_std_{window}'] = rolling_std.iloc[-1]
                metrics[f'volume_rolling_max_{window}'] = rolling_max.iloc[-1]
                metrics[f'volume_rolling_min_{window}'] = rolling_min.iloc[-1]
                
                # Calculate trend (current vs rolling mean)
                current_volume = group_df['volume'].iloc[-1]
                if rolling_mean.iloc[-1] > 0:
                    metrics[f'volume_trend_{window}'] = current_volume / rolling_mean.iloc[-1]
                else:
                    metrics[f'volume_trend_{window}'] = 1.0
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated rolling statistics for {len(result_df)} groups")
        
        return result_df
    
    def calculate_volume_distribution(self, df: pd.DataFrame,
                                     group_by: str = 'user_id') -> pd.DataFrame:
        """
        Calculate volume distribution characteristics
        
        Args:
            df: DataFrame with trade data
            group_by: Column to group by
            
        Returns:
            DataFrame with distribution metrics
        """
        self.logger.info(f"Calculating volume distribution characteristics")
        
        if df.empty or 'volume' not in df.columns:
            return pd.DataFrame()
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id]
            volumes = group_df['volume'].values
            
            if len(volumes) < 3:
                continue
            
            # Test for normality (Shapiro-Wilk test)
            if len(volumes) <= 5000:  # Shapiro-Wilk has sample size limit
                _, p_value = stats.shapiro(volumes)
                is_normal = p_value > 0.05
            else:
                is_normal = False
            
            # Calculate concentration (Gini coefficient)
            sorted_volumes = np.sort(volumes)
            n = len(volumes)
            cumsum = np.cumsum(sorted_volumes)
            gini = (2 * np.sum((np.arange(1, n + 1)) * sorted_volumes)) / (n * np.sum(sorted_volumes)) - (n + 1) / n
            
            # Calculate top percentile concentration
            top_10_pct = np.sum(sorted_volumes[-int(n * 0.1):]) / np.sum(volumes) if n >= 10 else 1.0
            top_20_pct = np.sum(sorted_volumes[-int(n * 0.2):]) / np.sum(volumes) if n >= 5 else 1.0
            
            metrics = {
                group_by: group_id,
                'is_normal_distribution': is_normal,
                'volume_gini_coefficient': gini,
                'top_10pct_volume_share': top_10_pct,
                'top_20pct_volume_share': top_20_pct,
                'volume_concentration': gini  # Alias for clarity
            }
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated distribution characteristics for {len(result_df)} groups")
        
        return result_df
