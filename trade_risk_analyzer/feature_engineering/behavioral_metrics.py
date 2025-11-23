"""
Behavioral Metrics Calculator

Calculates user behavioral features including position holding time,
win/loss ratios, trading pair diversity, and velocity metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


class BehavioralMetricsCalculator:
    """
    Calculates behavioral and trading pattern metrics
    """
    
    def __init__(self):
        """Initialize behavioral metrics calculator"""
        self.logger = logger
    
    def calculate_holding_time_statistics(self, df: pd.DataFrame,
                                         group_by: str = 'user_id') -> pd.DataFrame:
        """
        Calculate position holding time statistics
        
        Args:
            df: DataFrame with trade data (must have 'trade_type', 'symbol', 'timestamp')
            group_by: Column to group by
            
        Returns:
            DataFrame with holding time metrics
        """
        self.logger.info(f"Calculating holding time statistics, grouped by {group_by}")
        
        if df.empty or 'trade_type' not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['trade_type'] = df['trade_type'].str.upper()
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id].sort_values('timestamp')
            
            holding_times = []
            
            # Track positions for each symbol
            for symbol in group_df['symbol'].unique():
                symbol_df = group_df[group_df['symbol'] == symbol].sort_values('timestamp')
                
                # Track open positions
                position_open_time = None
                position_size = 0
                
                for _, trade in symbol_df.iterrows():
                    if trade['trade_type'] == 'BUY':
                        if position_size == 0:
                            # Opening new position
                            position_open_time = trade['timestamp']
                        position_size += trade['volume']
                    elif trade['trade_type'] == 'SELL':
                        if position_size > 0 and position_open_time is not None:
                            # Closing position (at least partially)
                            holding_time = (trade['timestamp'] - position_open_time).total_seconds()
                            holding_times.append(holding_time)
                            
                            position_size -= trade['volume']
                            if position_size <= 0:
                                position_size = 0
                                position_open_time = None
            
            if holding_times:
                # Convert to hours
                holding_times_hours = np.array(holding_times) / 3600
                
                metrics = {
                    group_by: group_id,
                    'mean_holding_time_hours': np.mean(holding_times_hours),
                    'median_holding_time_hours': np.median(holding_times_hours),
                    'std_holding_time_hours': np.std(holding_times_hours),
                    'min_holding_time_hours': np.min(holding_times_hours),
                    'max_holding_time_hours': np.max(holding_times_hours),
                    'short_term_holds_ratio': np.sum(holding_times_hours < 1) / len(holding_times_hours),  # < 1 hour
                    'day_trading_ratio': np.sum(holding_times_hours < 24) / len(holding_times_hours),  # < 1 day
                    'swing_trading_ratio': np.sum((holding_times_hours >= 24) & (holding_times_hours < 168)) / len(holding_times_hours),  # 1-7 days
                    'position_count': len(holding_times)
                }
            else:
                # No closed positions found
                metrics = {
                    group_by: group_id,
                    'mean_holding_time_hours': 0,
                    'median_holding_time_hours': 0,
                    'std_holding_time_hours': 0,
                    'min_holding_time_hours': 0,
                    'max_holding_time_hours': 0,
                    'short_term_holds_ratio': 0,
                    'day_trading_ratio': 0,
                    'swing_trading_ratio': 0,
                    'position_count': 0
                }
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated holding time statistics for {len(result_df)} groups")
        
        return result_df
    
    def calculate_win_loss_ratio(self, df: pd.DataFrame,
                                 group_by: str = 'user_id') -> pd.DataFrame:
        """
        Compute win/loss ratio for users
        
        Args:
            df: DataFrame with trade data
            group_by: Column to group by
            
        Returns:
            DataFrame with win/loss metrics
        """
        self.logger.info(f"Calculating win/loss ratio, grouped by {group_by}")
        
        if df.empty or 'trade_type' not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['trade_type'] = df['trade_type'].str.upper()
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id].sort_values('timestamp')
            
            wins = 0
            losses = 0
            total_profit = 0
            total_loss = 0
            
            # Track positions for each symbol
            for symbol in group_df['symbol'].unique():
                symbol_df = group_df[group_df['symbol'] == symbol].sort_values('timestamp')
                
                # Track open positions
                buy_price = 0
                buy_volume = 0
                
                for _, trade in symbol_df.iterrows():
                    if trade['trade_type'] == 'BUY':
                        # Accumulate position
                        total_cost = buy_price * buy_volume + trade['price'] * trade['volume']
                        buy_volume += trade['volume']
                        buy_price = total_cost / buy_volume if buy_volume > 0 else 0
                    elif trade['trade_type'] == 'SELL' and buy_volume > 0:
                        # Close position (at least partially)
                        sell_volume = min(trade['volume'], buy_volume)
                        pnl = (trade['price'] - buy_price) * sell_volume
                        
                        if pnl > 0:
                            wins += 1
                            total_profit += pnl
                        elif pnl < 0:
                            losses += 1
                            total_loss += abs(pnl)
                        
                        buy_volume -= sell_volume
                        if buy_volume <= 0:
                            buy_price = 0
                            buy_volume = 0
            
            total_trades = wins + losses
            win_ratio = wins / total_trades if total_trades > 0 else 0
            loss_ratio = losses / total_trades if total_trades > 0 else 0
            
            # Calculate profit factor (total profit / total loss)
            profit_factor = total_profit / total_loss if total_loss > 0 else (total_profit if total_profit > 0 else 0)
            
            # Calculate average win/loss
            avg_win = total_profit / wins if wins > 0 else 0
            avg_loss = total_loss / losses if losses > 0 else 0
            
            metrics = {
                group_by: group_id,
                'win_count': wins,
                'loss_count': losses,
                'win_ratio': win_ratio,
                'loss_ratio': loss_ratio,
                'profit_factor': profit_factor,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'total_profit': total_profit,
                'total_loss': total_loss,
                'net_pnl': total_profit - total_loss
            }
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated win/loss ratios for {len(result_df)} groups")
        
        return result_df
    
    def measure_trading_pair_diversity(self, df: pd.DataFrame,
                                      group_by: str = 'user_id') -> pd.DataFrame:
        """
        Measure trading pair diversity
        
        Args:
            df: DataFrame with trade data
            group_by: Column to group by
            
        Returns:
            DataFrame with diversity metrics
        """
        self.logger.info(f"Measuring trading pair diversity, grouped by {group_by}")
        
        if df.empty or 'symbol' not in df.columns:
            return pd.DataFrame()
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id]
            
            # Count unique symbols
            unique_symbols = group_df['symbol'].nunique()
            total_trades = len(group_df)
            
            # Calculate symbol distribution
            symbol_counts = group_df['symbol'].value_counts()
            symbol_probs = symbol_counts / total_trades
            
            # Calculate entropy (measure of diversity)
            entropy = -np.sum(symbol_probs * np.log2(symbol_probs))
            max_entropy = np.log2(unique_symbols) if unique_symbols > 1 else 1
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
            
            # Calculate concentration (Herfindahl index)
            herfindahl = np.sum(symbol_probs ** 2)
            
            # Top symbol concentration
            top_symbol_ratio = symbol_counts.iloc[0] / total_trades if len(symbol_counts) > 0 else 0
            top_3_ratio = symbol_counts.head(3).sum() / total_trades if len(symbol_counts) > 0 else 0
            
            metrics = {
                group_by: group_id,
                'unique_symbols': unique_symbols,
                'symbol_diversity_entropy': normalized_entropy,
                'symbol_concentration_herfindahl': herfindahl,
                'top_symbol_ratio': top_symbol_ratio,
                'top_3_symbols_ratio': top_3_ratio,
                'is_diversified': unique_symbols >= 5 and normalized_entropy > 0.7
            }
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Measured trading pair diversity for {len(result_df)} groups")
        
        return result_df
    
    def calculate_velocity_metrics(self, df: pd.DataFrame,
                                   windows: Optional[List[str]] = None,
                                   group_by: str = 'user_id') -> pd.DataFrame:
        """
        Calculate velocity metrics (rate of change in activity)
        
        Args:
            df: DataFrame with trade data
            windows: List of time windows for velocity calculation
            group_by: Column to group by
            
        Returns:
            DataFrame with velocity metrics
        """
        windows = windows or ['1H', '24H', '7D']
        
        self.logger.info(f"Calculating velocity metrics for windows: {windows}")
        
        if df.empty or 'timestamp' not in df.columns:
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
            
            # Calculate velocity for each window
            for window in windows:
                # Count trades in rolling windows
                trade_counts = group_df.resample(window).size()
                
                if len(trade_counts) > 1:
                    # Calculate rate of change
                    velocity = trade_counts.diff()
                    
                    metrics[f'velocity_mean_{window}'] = velocity.mean()
                    metrics[f'velocity_std_{window}'] = velocity.std()
                    metrics[f'velocity_max_{window}'] = velocity.max()
                    metrics[f'velocity_min_{window}'] = velocity.min()
                    
                    # Acceleration (rate of change of velocity)
                    acceleration = velocity.diff()
                    metrics[f'acceleration_mean_{window}'] = acceleration.mean()
                    
                    # Trend (increasing or decreasing activity)
                    if len(trade_counts) >= 3:
                        # Simple linear trend
                        x = np.arange(len(trade_counts))
                        y = trade_counts.values
                        trend = np.polyfit(x, y, 1)[0]  # Slope
                        metrics[f'activity_trend_{window}'] = trend
                    else:
                        metrics[f'activity_trend_{window}'] = 0
                else:
                    metrics[f'velocity_mean_{window}'] = 0
                    metrics[f'velocity_std_{window}'] = 0
                    metrics[f'velocity_max_{window}'] = 0
                    metrics[f'velocity_min_{window}'] = 0
                    metrics[f'acceleration_mean_{window}'] = 0
                    metrics[f'activity_trend_{window}'] = 0
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated velocity metrics for {len(result_df)} groups")
        
        return result_df
    
    def calculate_trading_style_indicators(self, df: pd.DataFrame,
                                          group_by: str = 'user_id') -> pd.DataFrame:
        """
        Calculate indicators of trading style
        
        Args:
            df: DataFrame with trade data
            group_by: Column to group by
            
        Returns:
            DataFrame with trading style indicators
        """
        self.logger.info(f"Calculating trading style indicators")
        
        if df.empty:
            return pd.DataFrame()
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['trade_type'] = df['trade_type'].str.upper()
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id]
            
            total_trades = len(group_df)
            
            # Buy/Sell ratio
            buy_count = len(group_df[group_df['trade_type'] == 'BUY'])
            sell_count = len(group_df[group_df['trade_type'] == 'SELL'])
            buy_sell_ratio = buy_count / sell_count if sell_count > 0 else buy_count
            
            # Volume characteristics
            if 'volume' in group_df.columns:
                avg_trade_size = group_df['volume'].mean()
                trade_size_cv = group_df['volume'].std() / avg_trade_size if avg_trade_size > 0 else 0
                
                # Large trade indicator
                large_trade_threshold = group_df['volume'].quantile(0.9)
                large_trade_ratio = len(group_df[group_df['volume'] > large_trade_threshold]) / total_trades
            else:
                avg_trade_size = 0
                trade_size_cv = 0
                large_trade_ratio = 0
            
            # Time-based characteristics
            group_df_sorted = group_df.sort_values('timestamp')
            time_span_days = (group_df_sorted['timestamp'].max() - 
                            group_df_sorted['timestamp'].min()).total_seconds() / 86400
            
            trades_per_day = total_trades / time_span_days if time_span_days > 0 else 0
            
            # Classify trading style
            if trades_per_day > 50:
                style = 'high_frequency'
            elif trades_per_day > 10:
                style = 'day_trader'
            elif trades_per_day > 1:
                style = 'active_trader'
            else:
                style = 'casual_trader'
            
            metrics = {
                group_by: group_id,
                'buy_count': buy_count,
                'sell_count': sell_count,
                'buy_sell_ratio': buy_sell_ratio,
                'avg_trade_size': avg_trade_size,
                'trade_size_cv': trade_size_cv,
                'large_trade_ratio': large_trade_ratio,
                'trades_per_day': trades_per_day,
                'trading_style': style,
                'is_high_frequency': style == 'high_frequency',
                'is_day_trader': style == 'day_trader'
            }
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated trading style indicators for {len(result_df)} groups")
        
        return result_df
