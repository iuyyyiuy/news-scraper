"""
Feature Extractor

Main feature extraction class that combines frequency, volume, and temporal
feature extractors to build comprehensive feature vectors for ML models.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any

from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

from trade_risk_analyzer.core.base import BaseFeatureExtractor
from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.feature_engineering.frequency_metrics import FrequencyMetricsCalculator
from trade_risk_analyzer.feature_engineering.volume_statistics import VolumeStatisticsCalculator
from trade_risk_analyzer.feature_engineering.temporal_patterns import TemporalPatternAnalyzer
from trade_risk_analyzer.feature_engineering.price_impact import PriceImpactCalculator
from trade_risk_analyzer.feature_engineering.behavioral_metrics import BehavioralMetricsCalculator


logger = get_logger(__name__)


class FeatureExtractor(BaseFeatureExtractor):
    """
    Main feature extractor that combines all feature calculation modules
    """
    
    def __init__(self, time_windows: Optional[List[str]] = None,
                 scaler_type: str = 'standard'):
        """
        Initialize feature extractor
        
        Args:
            time_windows: List of time windows for calculations (e.g., ['1H', '24H', '7D'])
            scaler_type: Type of scaler ('standard', 'minmax', 'robust', or None)
        """
        self.time_windows = time_windows or ['1H', '24H', '7D']
        self.scaler_type = scaler_type
        
        # Initialize sub-extractors
        self.frequency_calculator = FrequencyMetricsCalculator(self.time_windows)
        self.volume_calculator = VolumeStatisticsCalculator(self.time_windows)
        self.temporal_analyzer = TemporalPatternAnalyzer()
        self.price_calculator = PriceImpactCalculator()
        self.behavioral_calculator = BehavioralMetricsCalculator()
        
        # Initialize scaler
        self.scaler = self._create_scaler()
        self._scaler_fitted = False
        
        self.logger = logger
        self._feature_names = None
    
    def extract_features(self, trades: pd.DataFrame, 
                        group_by: str = 'user_id',
                        include_frequency: bool = True,
                        include_volume: bool = True,
                        include_temporal: bool = True,
                        include_price: bool = True,
                        include_behavioral: bool = True,
                        market_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Extract all features from trade data
        
        Args:
            trades: DataFrame with trade data
            group_by: Column to group by ('user_id' or 'symbol')
            include_frequency: Include frequency-based features
            include_volume: Include volume-based features
            include_temporal: Include temporal features
            include_price: Include price impact features
            include_behavioral: Include behavioral features
            market_data: Optional market data for price impact calculations
            
        Returns:
            DataFrame with extracted features
        """
        self.logger.info(f"Extracting features from {len(trades)} trades, grouped by {group_by}")
        
        if trades.empty:
            return pd.DataFrame()
        
        # Start with group identifiers
        feature_dfs = []
        
        # Extract frequency features
        if include_frequency:
            self.logger.info("Extracting frequency features...")
            freq_features = self._extract_frequency_features(trades, group_by)
            if not freq_features.empty:
                feature_dfs.append(freq_features)
        
        # Extract volume features
        if include_volume:
            self.logger.info("Extracting volume features...")
            volume_features = self._extract_volume_features(trades, group_by)
            if not volume_features.empty:
                feature_dfs.append(volume_features)
        
        # Extract temporal features
        if include_temporal:
            self.logger.info("Extracting temporal features...")
            temporal_features = self._extract_temporal_features(trades, group_by)
            if not temporal_features.empty:
                feature_dfs.append(temporal_features)
        
        # Extract price impact features
        if include_price:
            self.logger.info("Extracting price impact features...")
            price_features = self._extract_price_features(trades, group_by, market_data)
            if not price_features.empty:
                feature_dfs.append(price_features)
        
        # Extract behavioral features
        if include_behavioral:
            self.logger.info("Extracting behavioral features...")
            behavioral_features = self._extract_behavioral_features(trades, group_by)
            if not behavioral_features.empty:
                feature_dfs.append(behavioral_features)
        
        # Merge all features
        if not feature_dfs:
            return pd.DataFrame()
        
        result_df = feature_dfs[0]
        for df in feature_dfs[1:]:
            result_df = result_df.merge(df, on=group_by, how='outer', suffixes=('', '_dup'))
            # Drop duplicate columns
            dup_cols = [col for col in result_df.columns if col.endswith('_dup')]
            if dup_cols:
                result_df = result_df.drop(columns=dup_cols)
        
        # Fill NaN values with 0
        result_df = result_df.fillna(0)
        
        self.logger.info(f"Extracted {len(result_df.columns) - 1} features for {len(result_df)} groups")
        
        return result_df
    
    def _extract_frequency_features(self, trades: pd.DataFrame, 
                                   group_by: str) -> pd.DataFrame:
        """Extract frequency-based features"""
        features = []
        
        # Trades per window
        trades_per_window = self.frequency_calculator.calculate_trades_per_window(trades, group_by)
        if not trades_per_window.empty:
            features.append(trades_per_window)
        
        # Burst metrics
        burst_metrics = self.frequency_calculator.calculate_burst_metrics(trades, group_by=group_by)
        if not burst_metrics.empty:
            features.append(burst_metrics)
        
        # Quote stuffing detection
        quote_stuffing = self.frequency_calculator.detect_quote_stuffing(trades, group_by=group_by)
        if not quote_stuffing.empty:
            features.append(quote_stuffing)
        
        # Merge frequency features
        if not features:
            return pd.DataFrame()
        
        result = features[0]
        for df in features[1:]:
            result = result.merge(df, on=group_by, how='outer')
        
        return result
    
    def _extract_volume_features(self, trades: pd.DataFrame,
                                group_by: str) -> pd.DataFrame:
        """Extract volume-based features"""
        features = []
        
        # Basic statistics
        basic_stats = self.volume_calculator.calculate_basic_statistics(trades, group_by)
        if not basic_stats.empty:
            features.append(basic_stats)
        
        # Percentile rankings
        percentiles = self.volume_calculator.calculate_percentile_rankings(trades, group_by=group_by)
        if not percentiles.empty:
            features.append(percentiles)
        
        # Volume spikes
        spikes = self.volume_calculator.detect_volume_spikes(trades, group_by=group_by)
        if not spikes.empty:
            features.append(spikes)
        
        # Consistency scores
        consistency = self.volume_calculator.calculate_consistency_score(trades, group_by)
        if not consistency.empty:
            features.append(consistency)
        
        # Rolling statistics
        rolling_stats = self.volume_calculator.calculate_rolling_statistics(trades, group_by)
        if not rolling_stats.empty:
            features.append(rolling_stats)
        
        # Distribution characteristics
        distribution = self.volume_calculator.calculate_volume_distribution(trades, group_by)
        if not distribution.empty:
            features.append(distribution)
        
        # Merge volume features
        if not features:
            return pd.DataFrame()
        
        result = features[0]
        for df in features[1:]:
            result = result.merge(df, on=group_by, how='outer')
        
        return result
    
    def _extract_temporal_features(self, trades: pd.DataFrame,
                                  group_by: str) -> pd.DataFrame:
        """Extract temporal features"""
        features = []
        
        # Hour of day distribution
        hour_dist = self.temporal_analyzer.extract_hour_of_day_distribution(trades, group_by)
        if not hour_dist.empty:
            features.append(hour_dist)
        
        # Day of week distribution
        day_dist = self.temporal_analyzer.extract_day_of_week_distribution(trades, group_by)
        if not day_dist.empty:
            features.append(day_dist)
        
        # Session concentration
        session_conc = self.temporal_analyzer.calculate_session_concentration(trades, group_by=group_by)
        if not session_conc.empty:
            features.append(session_conc)
        
        # Time between trades
        time_between = self.temporal_analyzer.calculate_time_between_trades(trades, group_by)
        if not time_between.empty:
            features.append(time_between)
        
        # Temporal clustering
        clustering = self.temporal_analyzer.identify_temporal_clustering(trades, group_by=group_by)
        if not clustering.empty:
            features.append(clustering)
        
        # Temporal regularity
        regularity = self.temporal_analyzer.calculate_temporal_regularity(trades, group_by)
        if not regularity.empty:
            features.append(regularity)
        
        # Merge temporal features
        if not features:
            return pd.DataFrame()
        
        result = features[0]
        for df in features[1:]:
            result = result.merge(df, on=group_by, how='outer')
        
        return result
    
    def get_feature_names(self) -> List[str]:
        """
        Get list of feature names
        
        Returns:
            List of feature names
        """
        if self._feature_names is not None:
            return self._feature_names
        
        # Generate feature names based on configuration
        feature_names = []
        
        # Frequency features
        for window in self.time_windows:
            feature_names.extend([
                f'trades_count_{window}',
                f'trades_per_hour_{window}'
            ])
        feature_names.extend([
            'total_trades', 'avg_trades_per_day',
            'mean_trades_per_window', 'std_trades_per_window',
            'max_trades_per_window', 'burst_windows_detected',
            'max_orders_per_minute', 'avg_orders_per_minute',
            'quote_stuffing_detected'
        ])
        
        # Volume features
        feature_names.extend([
            'volume_mean', 'volume_median', 'volume_std',
            'volume_min', 'volume_max', 'volume_cv',
            'volume_skewness', 'volume_kurtosis',
            'volume_p25', 'volume_p50', 'volume_p75',
            'volume_p90', 'volume_p95', 'volume_p99',
            'spike_count', 'spike_ratio',
            'consistency_score', 'volume_entropy'
        ])
        
        # Temporal features
        feature_names.extend([
            'peak_trading_hour', 'peak_hour_ratio',
            'hour_entropy', 'active_hours_count',
            'business_hours_ratio',
            'peak_trading_day', 'weekday_ratio',
            'num_sessions', 'avg_trades_per_session',
            'mean_time_between_trades_sec',
            'rapid_trade_ratio',
            'num_clusters', 'cluster_ratio',
            'regularity_score'
        ])
        
        self._feature_names = feature_names
        return feature_names
    
    def build_feature_vector(self, features_df: pd.DataFrame,
                            exclude_columns: Optional[List[str]] = None) -> np.ndarray:
        """
        Build feature vector array from features DataFrame
        
        Args:
            features_df: DataFrame with extracted features
            exclude_columns: Columns to exclude (e.g., identifiers)
            
        Returns:
            NumPy array of feature vectors
        """
        exclude_columns = exclude_columns or ['user_id', 'symbol', 'trade_id']
        
        # Select numeric columns only
        numeric_cols = features_df.select_dtypes(include=[np.number]).columns
        
        # Exclude specified columns
        feature_cols = [col for col in numeric_cols if col not in exclude_columns]
        
        # Extract values
        feature_array = features_df[feature_cols].values
        
        self.logger.info(f"Built feature vector with shape {feature_array.shape}")
        
        return feature_array
    
    def _extract_price_features(self, trades: pd.DataFrame,
                               group_by: str,
                               market_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Extract price impact features"""
        features = []
        
        # Price deviation
        price_dev = self.price_calculator.calculate_price_deviation(trades, market_data, group_by)
        if not price_dev.empty:
            features.append(price_dev)
        
        # Slippage metrics
        slippage = self.price_calculator.calculate_slippage_metrics(trades, group_by=group_by)
        if not slippage.empty:
            features.append(slippage)
        
        # Price reversals
        reversals = self.price_calculator.detect_price_reversal_patterns(trades, group_by=group_by)
        if not reversals.empty:
            features.append(reversals)
        
        # Spread impact
        spread = self.price_calculator.analyze_spread_impact(trades, market_data, group_by)
        if not spread.empty:
            features.append(spread)
        
        # Price momentum
        momentum = self.price_calculator.calculate_price_momentum(trades, group_by=group_by)
        if not momentum.empty:
            features.append(momentum)
        
        # Merge price features
        if not features:
            return pd.DataFrame()
        
        result = features[0]
        for df in features[1:]:
            result = result.merge(df, on=group_by, how='outer')
        
        return result
    
    def _extract_behavioral_features(self, trades: pd.DataFrame,
                                    group_by: str) -> pd.DataFrame:
        """Extract behavioral features"""
        features = []
        
        # Holding time statistics
        holding_time = self.behavioral_calculator.calculate_holding_time_statistics(trades, group_by)
        if not holding_time.empty:
            features.append(holding_time)
        
        # Win/loss ratio
        win_loss = self.behavioral_calculator.calculate_win_loss_ratio(trades, group_by)
        if not win_loss.empty:
            features.append(win_loss)
        
        # Trading pair diversity
        diversity = self.behavioral_calculator.measure_trading_pair_diversity(trades, group_by)
        if not diversity.empty:
            features.append(diversity)
        
        # Velocity metrics
        velocity = self.behavioral_calculator.calculate_velocity_metrics(trades, group_by=group_by)
        if not velocity.empty:
            features.append(velocity)
        
        # Trading style indicators
        style = self.behavioral_calculator.calculate_trading_style_indicators(trades, group_by)
        if not style.empty:
            features.append(style)
        
        # Merge behavioral features
        if not features:
            return pd.DataFrame()
        
        result = features[0]
        for df in features[1:]:
            result = result.merge(df, on=group_by, how='outer')
        
        return result
    
    def _create_scaler(self):
        """Create scaler based on configuration"""
        if self.scaler_type == 'standard':
            return StandardScaler()
        elif self.scaler_type == 'minmax':
            return MinMaxScaler()
        elif self.scaler_type == 'robust':
            return RobustScaler()
        else:
            return None
    
    def normalize_features(self, features_df: pd.DataFrame,
                          exclude_columns: Optional[List[str]] = None,
                          fit: bool = True) -> pd.DataFrame:
        """
        Normalize/scale features
        
        Args:
            features_df: DataFrame with features
            exclude_columns: Columns to exclude from scaling
            fit: Whether to fit the scaler (True for training, False for inference)
            
        Returns:
            DataFrame with normalized features
        """
        if self.scaler is None:
            return features_df
        
        exclude_columns = exclude_columns or ['user_id', 'symbol', 'trade_id']
        
        # Select numeric columns only
        numeric_cols = features_df.select_dtypes(include=[np.number]).columns
        feature_cols = [col for col in numeric_cols if col not in exclude_columns]
        
        # Create copy
        result_df = features_df.copy()
        
        if fit:
            # Fit and transform
            result_df[feature_cols] = self.scaler.fit_transform(features_df[feature_cols])
            self._scaler_fitted = True
            self.logger.info("Fitted and transformed features with scaler")
        else:
            # Transform only
            if not self._scaler_fitted:
                self.logger.warning("Scaler not fitted yet, fitting now")
                result_df[feature_cols] = self.scaler.fit_transform(features_df[feature_cols])
                self._scaler_fitted = True
            else:
                result_df[feature_cols] = self.scaler.transform(features_df[feature_cols])
            self.logger.info("Transformed features with fitted scaler")
        
        return result_df
    
    def extract_and_build(self, trades: pd.DataFrame,
                         group_by: str = 'user_id',
                         normalize: bool = True,
                         market_data: Optional[pd.DataFrame] = None) -> tuple[pd.DataFrame, np.ndarray]:
        """
        Extract features and build feature vectors in one call
        
        Args:
            trades: DataFrame with trade data
            group_by: Column to group by
            normalize: Whether to normalize features
            market_data: Optional market data for price calculations
            
        Returns:
            Tuple of (features DataFrame, feature array)
        """
        features_df = self.extract_features(trades, group_by, market_data=market_data)
        
        if normalize:
            features_df = self.normalize_features(features_df, exclude_columns=[group_by])
        
        feature_array = self.build_feature_vector(features_df, exclude_columns=[group_by])
        
        return features_df, feature_array
