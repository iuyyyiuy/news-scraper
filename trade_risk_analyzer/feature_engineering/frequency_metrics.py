"""
Frequency Metrics Calculator

Calculates trade frequency metrics including trades per time window,
order-to-trade ratios, cancellation rates, and quote stuffing detection.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


class FrequencyMetricsCalculator:
    """
    Calculates frequency-based features from trade data
    """
    
    def __init__(self, time_windows: Optional[List[str]] = None):
        """
        Initialize frequency metrics calculator
        
        Args:
            time_windows: List of time windows for calculations (e.g., ['1H', '24H', '7D'])
        """
        self.time_windows = time_windows or ['1H', '24H', '7D']
        self.logger = logger
    
    def calculate_trades_per_window(self, df: pd.DataFrame, 
                                    group_by: str = 'user_id') -> pd.DataFrame:
        """
        Calculate trades per time window for each user/symbol
        
        Args:
            df: DataFrame with trade data (must have 'timestamp' column)
            group_by: Column to group by ('user_id' or 'symbol')
            
        Returns:
            DataFrame with frequency metrics per group
        """
        self.logger.info(f"Calculating trades per window, grouped by {group_by}")
        
        if df.empty:
            return pd.DataFrame()
        
        # Ensure timestamp is datetime
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id].sort_values('timestamp')
            
            metrics = {group_by: group_id}
            
            # Calculate for each time window
            for window in self.time_windows:
                # Get the most recent timestamp
                latest_time = group_df['timestamp'].max()
                
                # Calculate window start time
                window_start = self._get_window_start(latest_time, window)
                
                # Count trades in window
                trades_in_window = len(group_df[group_df['timestamp'] >= window_start])
                
                # Calculate rate (trades per hour)
                window_hours = self._window_to_hours(window)
                trades_per_hour = trades_in_window / window_hours if window_hours > 0 else 0
                
                metrics[f'trades_count_{window}'] = trades_in_window
                metrics[f'trades_per_hour_{window}'] = trades_per_hour
            
            # Calculate overall statistics
            metrics['total_trades'] = len(group_df)
            metrics['first_trade'] = group_df['timestamp'].min()
            metrics['last_trade'] = group_df['timestamp'].max()
            
            # Calculate average trades per day over entire period
            time_span = (group_df['timestamp'].max() - group_df['timestamp'].min()).total_seconds() / 86400
            metrics['avg_trades_per_day'] = len(group_df) / time_span if time_span > 0 else 0
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated frequency metrics for {len(result_df)} groups")
        
        return result_df
    
    def calculate_order_to_trade_ratio(self, trades_df: pd.DataFrame, 
                                       orders_df: Optional[pd.DataFrame] = None,
                                       group_by: str = 'user_id') -> pd.DataFrame:
        """
        Calculate order-to-trade ratio (orders placed vs trades executed)
        
        Args:
            trades_df: DataFrame with executed trades
            orders_df: DataFrame with all orders (if None, assumes 1:1 ratio)
            group_by: Column to group by
            
        Returns:
            DataFrame with order-to-trade ratios
        """
        self.logger.info(f"Calculating order-to-trade ratio, grouped by {group_by}")
        
        if trades_df.empty:
            return pd.DataFrame()
        
        results = []
        
        for group_id in trades_df[group_by].unique():
            group_trades = trades_df[trades_df[group_by] == group_id]
            trade_count = len(group_trades)
            
            if orders_df is not None and not orders_df.empty:
                group_orders = orders_df[orders_df[group_by] == group_id]
                order_count = len(group_orders)
            else:
                # If no orders data, assume each trade had one order
                order_count = trade_count
            
            ratio = order_count / trade_count if trade_count > 0 else 0
            
            results.append({
                group_by: group_id,
                'order_count': order_count,
                'trade_count': trade_count,
                'order_to_trade_ratio': ratio,
                'excess_orders': max(0, order_count - trade_count)
            })
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated order-to-trade ratios for {len(result_df)} groups")
        
        return result_df
    
    def calculate_cancellation_rate(self, orders_df: pd.DataFrame,
                                   trades_df: pd.DataFrame,
                                   group_by: str = 'user_id') -> pd.DataFrame:
        """
        Calculate order cancellation rate
        
        Args:
            orders_df: DataFrame with all orders (must have 'status' column)
            trades_df: DataFrame with executed trades
            group_by: Column to group by
            
        Returns:
            DataFrame with cancellation rates
        """
        self.logger.info(f"Calculating cancellation rate, grouped by {group_by}")
        
        if orders_df.empty:
            return pd.DataFrame()
        
        results = []
        
        for group_id in orders_df[group_by].unique():
            group_orders = orders_df[orders_df[group_by] == group_id]
            total_orders = len(group_orders)
            
            # Count cancelled orders (if status column exists)
            if 'status' in group_orders.columns:
                cancelled_orders = len(group_orders[
                    group_orders['status'].str.upper().isin(['CANCELLED', 'CANCELED'])
                ])
            else:
                # Estimate from order_id not in trades
                if not trades_df.empty and 'order_id' in trades_df.columns:
                    group_trades = trades_df[trades_df[group_by] == group_id]
                    executed_order_ids = set(group_trades['order_id'].dropna())
                    all_order_ids = set(group_orders['order_id'].dropna())
                    cancelled_orders = len(all_order_ids - executed_order_ids)
                else:
                    cancelled_orders = 0
            
            cancellation_rate = cancelled_orders / total_orders if total_orders > 0 else 0
            
            results.append({
                group_by: group_id,
                'total_orders': total_orders,
                'cancelled_orders': cancelled_orders,
                'executed_orders': total_orders - cancelled_orders,
                'cancellation_rate': cancellation_rate
            })
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated cancellation rates for {len(result_df)} groups")
        
        return result_df
    
    def detect_quote_stuffing(self, df: pd.DataFrame,
                             threshold_per_minute: int = 100,
                             group_by: str = 'user_id') -> pd.DataFrame:
        """
        Detect quote stuffing patterns (excessive orders per minute)
        
        Args:
            df: DataFrame with order/trade data
            threshold_per_minute: Threshold for quote stuffing detection
            group_by: Column to group by
            
        Returns:
            DataFrame with quote stuffing indicators
        """
        self.logger.info(f"Detecting quote stuffing (threshold: {threshold_per_minute}/min)")
        
        if df.empty:
            return pd.DataFrame()
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id].sort_values('timestamp')
            
            # Create 1-minute bins
            group_df['minute_bin'] = group_df['timestamp'].dt.floor('1min')
            
            # Count orders per minute
            orders_per_minute = group_df.groupby('minute_bin').size()
            
            # Calculate statistics
            max_orders_per_minute = orders_per_minute.max() if len(orders_per_minute) > 0 else 0
            avg_orders_per_minute = orders_per_minute.mean() if len(orders_per_minute) > 0 else 0
            
            # Detect quote stuffing
            stuffing_minutes = (orders_per_minute >= threshold_per_minute).sum()
            is_quote_stuffing = stuffing_minutes > 0
            
            # Calculate stuffing intensity
            if len(orders_per_minute) > 0:
                stuffing_intensity = (orders_per_minute >= threshold_per_minute).sum() / len(orders_per_minute)
            else:
                stuffing_intensity = 0
            
            results.append({
                group_by: group_id,
                'max_orders_per_minute': max_orders_per_minute,
                'avg_orders_per_minute': avg_orders_per_minute,
                'quote_stuffing_detected': is_quote_stuffing,
                'quote_stuffing_minutes': stuffing_minutes,
                'quote_stuffing_intensity': stuffing_intensity,
                'total_minutes_active': len(orders_per_minute)
            })
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Detected quote stuffing for {len(result_df)} groups")
        
        return result_df
    
    def calculate_burst_metrics(self, df: pd.DataFrame,
                                burst_window: str = '5min',
                                group_by: str = 'user_id') -> pd.DataFrame:
        """
        Calculate burst trading metrics (sudden spikes in activity)
        
        Args:
            df: DataFrame with trade data
            burst_window: Time window for burst detection
            group_by: Column to group by
            
        Returns:
            DataFrame with burst metrics
        """
        self.logger.info(f"Calculating burst metrics (window: {burst_window})")
        
        if df.empty:
            return pd.DataFrame()
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id].sort_values('timestamp')
            
            # Create time bins
            group_df['time_bin'] = group_df['timestamp'].dt.floor(burst_window)
            
            # Count trades per bin
            trades_per_bin = group_df.groupby('time_bin').size()
            
            if len(trades_per_bin) == 0:
                continue
            
            # Calculate statistics
            mean_trades = trades_per_bin.mean()
            std_trades = trades_per_bin.std()
            max_trades = trades_per_bin.max()
            
            # Detect bursts (trades > mean + 2*std)
            burst_threshold = mean_trades + 2 * std_trades if std_trades > 0 else mean_trades * 2
            burst_bins = (trades_per_bin > burst_threshold).sum()
            
            results.append({
                group_by: group_id,
                'mean_trades_per_window': mean_trades,
                'std_trades_per_window': std_trades,
                'max_trades_per_window': max_trades,
                'burst_threshold': burst_threshold,
                'burst_windows_detected': burst_bins,
                'burst_ratio': burst_bins / len(trades_per_bin) if len(trades_per_bin) > 0 else 0
            })
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated burst metrics for {len(result_df)} groups")
        
        return result_df
    
    def _get_window_start(self, end_time: pd.Timestamp, window: str) -> pd.Timestamp:
        """
        Calculate window start time from end time and window string
        
        Args:
            end_time: End timestamp
            window: Window string (e.g., '1H', '24H', '7D')
            
        Returns:
            Start timestamp
        """
        # Parse window string
        if window.endswith('H'):
            hours = int(window[:-1])
            return end_time - pd.Timedelta(hours=hours)
        elif window.endswith('D'):
            days = int(window[:-1])
            return end_time - pd.Timedelta(days=days)
        elif window.endswith('W'):
            weeks = int(window[:-1])
            return end_time - pd.Timedelta(weeks=weeks)
        elif window.endswith('M'):
            minutes = int(window[:-1])
            return end_time - pd.Timedelta(minutes=minutes)
        else:
            # Default to hours
            return end_time - pd.Timedelta(hours=1)
    
    def _window_to_hours(self, window: str) -> float:
        """
        Convert window string to hours
        
        Args:
            window: Window string (e.g., '1H', '24H', '7D')
            
        Returns:
            Number of hours
        """
        if window.endswith('H'):
            return float(window[:-1])
        elif window.endswith('D'):
            return float(window[:-1]) * 24
        elif window.endswith('W'):
            return float(window[:-1]) * 24 * 7
        elif window.endswith('M'):
            return float(window[:-1]) / 60
        else:
            return 1.0
