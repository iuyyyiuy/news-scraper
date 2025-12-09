"""
Price Impact Calculator

Calculates price impact features including price deviation from market averages,
slippage metrics, price reversal patterns, and bid-ask spread analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


class PriceImpactCalculator:
    """
    Calculates price impact and market microstructure features
    """
    
    def __init__(self):
        """Initialize price impact calculator"""
        self.logger = logger
    
    def calculate_price_deviation(self, trades_df: pd.DataFrame,
                                  market_data_df: Optional[pd.DataFrame] = None,
                                  group_by: str = 'user_id') -> pd.DataFrame:
        """
        Calculate price deviation from market averages
        
        Args:
            trades_df: DataFrame with trade data (must have 'price', 'symbol', 'timestamp')
            market_data_df: DataFrame with market prices (if None, uses symbol-level averages)
            group_by: Column to group by
            
        Returns:
            DataFrame with price deviation metrics
        """
        self.logger.info(f"Calculating price deviation, grouped by {group_by}")
        
        if trades_df.empty or 'price' not in trades_df.columns:
            return pd.DataFrame()
        
        trades_df = trades_df.copy()
        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
        
        results = []
        
        for group_id in trades_df[group_by].unique():
            group_df = trades_df[trades_df[group_by] == group_id]
            
            # Calculate deviations for each symbol
            symbol_deviations = []
            
            for symbol in group_df['symbol'].unique():
                symbol_trades = group_df[group_df['symbol'] == symbol]
                
                # Calculate market average price
                if market_data_df is not None and not market_data_df.empty:
                    # Use provided market data
                    symbol_market = market_data_df[market_data_df['symbol'] == symbol]
                    if not symbol_market.empty:
                        market_avg = symbol_market['price'].mean()
                    else:
                        market_avg = symbol_trades['price'].mean()
                else:
                    # Use all trades for this symbol as market average
                    all_symbol_trades = trades_df[trades_df['symbol'] == symbol]
                    market_avg = all_symbol_trades['price'].mean()
                
                # Calculate deviations
                deviations = (symbol_trades['price'] - market_avg) / market_avg
                symbol_deviations.extend(deviations.values)
            
            if not symbol_deviations:
                continue
            
            symbol_deviations = np.array(symbol_deviations)
            
            metrics = {
                group_by: group_id,
                'mean_price_deviation': np.mean(symbol_deviations),
                'abs_mean_price_deviation': np.mean(np.abs(symbol_deviations)),
                'std_price_deviation': np.std(symbol_deviations),
                'max_price_deviation': np.max(np.abs(symbol_deviations)),
                'positive_deviation_ratio': np.sum(symbol_deviations > 0) / len(symbol_deviations),
                'extreme_deviation_count': np.sum(np.abs(symbol_deviations) > 0.05)  # >5% deviation
            }
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated price deviation for {len(result_df)} groups")
        
        return result_df
    
    def calculate_slippage_metrics(self, trades_df: pd.DataFrame,
                                   orders_df: Optional[pd.DataFrame] = None,
                                   group_by: str = 'user_id') -> pd.DataFrame:
        """
        Calculate slippage metrics (difference between order price and execution price)
        
        Args:
            trades_df: DataFrame with executed trades
            orders_df: DataFrame with orders (must have 'order_price' or 'limit_price')
            group_by: Column to group by
            
        Returns:
            DataFrame with slippage metrics
        """
        self.logger.info(f"Calculating slippage metrics, grouped by {group_by}")
        
        if trades_df.empty:
            return pd.DataFrame()
        
        results = []
        
        for group_id in trades_df[group_by].unique():
            group_trades = trades_df[trades_df[group_by] == group_id]
            
            # If orders data is provided, calculate actual slippage
            if orders_df is not None and not orders_df.empty and 'order_id' in group_trades.columns:
                group_orders = orders_df[orders_df[group_by] == group_id]
                
                # Merge trades with orders
                merged = group_trades.merge(
                    group_orders[['order_id', 'order_price']],
                    on='order_id',
                    how='left'
                )
                
                # Calculate slippage
                merged['slippage'] = (merged['price'] - merged['order_price']) / merged['order_price']
                slippages = merged['slippage'].dropna()
                
                if len(slippages) > 0:
                    mean_slippage = slippages.mean()
                    abs_mean_slippage = slippages.abs().mean()
                    max_slippage = slippages.abs().max()
                    slippage_std = slippages.std()
                else:
                    mean_slippage = 0
                    abs_mean_slippage = 0
                    max_slippage = 0
                    slippage_std = 0
            else:
                # Estimate slippage using price volatility
                prices = group_trades['price'].values
                if len(prices) > 1:
                    price_changes = np.diff(prices) / prices[:-1]
                    mean_slippage = np.mean(price_changes)
                    abs_mean_slippage = np.mean(np.abs(price_changes))
                    max_slippage = np.max(np.abs(price_changes))
                    slippage_std = np.std(price_changes)
                else:
                    mean_slippage = 0
                    abs_mean_slippage = 0
                    max_slippage = 0
                    slippage_std = 0
            
            metrics = {
                group_by: group_id,
                'mean_slippage': mean_slippage,
                'abs_mean_slippage': abs_mean_slippage,
                'max_slippage': max_slippage,
                'slippage_std': slippage_std,
                'high_slippage_count': np.sum(np.abs(slippages) > 0.01) if 'slippages' in locals() and len(slippages) > 0 else 0
            }
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated slippage metrics for {len(result_df)} groups")
        
        return result_df
    
    def detect_price_reversal_patterns(self, df: pd.DataFrame,
                                      reversal_threshold: float = 0.02,
                                      time_window: str = '5min',
                                      group_by: str = 'user_id') -> pd.DataFrame:
        """
        Detect price reversal patterns (pump and dump indicators)
        
        Args:
            df: DataFrame with trade data
            reversal_threshold: Minimum price change to consider a reversal (e.g., 0.02 = 2%)
            time_window: Time window for reversal detection
            group_by: Column to group by
            
        Returns:
            DataFrame with reversal pattern metrics
        """
        self.logger.info(f"Detecting price reversal patterns (threshold: {reversal_threshold})")
        
        if df.empty or 'price' not in df.columns or 'timestamp' not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id].sort_values('timestamp')
            
            reversal_count = 0
            max_reversal = 0
            reversal_magnitudes = []
            
            # Analyze each symbol separately
            for symbol in group_df['symbol'].unique():
                symbol_df = group_df[group_df['symbol'] == symbol].sort_values('timestamp')
                
                if len(symbol_df) < 3:
                    continue
                
                # Set timestamp as index
                symbol_df = symbol_df.set_index('timestamp')
                
                # Calculate rolling price changes
                rolling_max = symbol_df['price'].rolling(window=time_window).max()
                rolling_min = symbol_df['price'].rolling(window=time_window).min()
                
                # Detect reversals (price goes up then down, or down then up)
                for i in range(2, len(symbol_df)):
                    current_price = symbol_df['price'].iloc[i]
                    prev_max = rolling_max.iloc[i-1]
                    prev_min = rolling_min.iloc[i-1]
                    
                    # Check for reversal from high
                    if prev_max > 0:
                        drop_from_high = (prev_max - current_price) / prev_max
                        if drop_from_high > reversal_threshold:
                            reversal_count += 1
                            reversal_magnitudes.append(drop_from_high)
                            max_reversal = max(max_reversal, drop_from_high)
                    
                    # Check for reversal from low
                    if prev_min > 0:
                        rise_from_low = (current_price - prev_min) / prev_min
                        if rise_from_low > reversal_threshold:
                            reversal_count += 1
                            reversal_magnitudes.append(rise_from_low)
                            max_reversal = max(max_reversal, rise_from_low)
            
            avg_reversal = np.mean(reversal_magnitudes) if reversal_magnitudes else 0
            
            metrics = {
                group_by: group_id,
                'reversal_count': reversal_count,
                'max_reversal_magnitude': max_reversal,
                'avg_reversal_magnitude': avg_reversal,
                'reversal_ratio': reversal_count / len(group_df) if len(group_df) > 0 else 0
            }
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Detected price reversals for {len(result_df)} groups")
        
        return result_df
    
    def analyze_spread_impact(self, df: pd.DataFrame,
                             market_data_df: Optional[pd.DataFrame] = None,
                             group_by: str = 'user_id') -> pd.DataFrame:
        """
        Analyze bid-ask spread impact
        
        Args:
            df: DataFrame with trade data
            market_data_df: DataFrame with market data (bid/ask prices)
            group_by: Column to group by
            
        Returns:
            DataFrame with spread impact metrics
        """
        self.logger.info(f"Analyzing spread impact, grouped by {group_by}")
        
        if df.empty:
            return pd.DataFrame()
        
        results = []
        
        for group_id in df[group_by].unique():
            group_df = df[df[group_by] == group_id]
            
            # If market data with bid/ask is provided
            if market_data_df is not None and 'bid' in market_data_df.columns and 'ask' in market_data_df.columns:
                spread_impacts = []
                
                for _, trade in group_df.iterrows():
                    # Find corresponding market data
                    market_row = market_data_df[
                        (market_data_df['symbol'] == trade['symbol']) &
                        (market_data_df['timestamp'] <= trade['timestamp'])
                    ].tail(1)
                    
                    if not market_row.empty:
                        bid = market_row['bid'].values[0]
                        ask = market_row['ask'].values[0]
                        mid = (bid + ask) / 2
                        spread = ask - bid
                        
                        # Calculate impact
                        if trade['trade_type'] == 'BUY':
                            impact = (trade['price'] - mid) / spread if spread > 0 else 0
                        else:
                            impact = (mid - trade['price']) / spread if spread > 0 else 0
                        
                        spread_impacts.append(impact)
                
                if spread_impacts:
                    mean_impact = np.mean(spread_impacts)
                    max_impact = np.max(np.abs(spread_impacts))
                    beyond_spread_ratio = np.sum(np.abs(spread_impacts) > 1) / len(spread_impacts)
                else:
                    mean_impact = 0
                    max_impact = 0
                    beyond_spread_ratio = 0
            else:
                # Estimate spread impact using price volatility
                prices = group_df['price'].values
                if len(prices) > 1:
                    price_std = np.std(prices)
                    price_mean = np.mean(prices)
                    estimated_spread = 2 * price_std  # Rough estimate
                    
                    mean_impact = price_std / estimated_spread if estimated_spread > 0 else 0
                    max_impact = (np.max(prices) - np.min(prices)) / estimated_spread if estimated_spread > 0 else 0
                    beyond_spread_ratio = 0
                else:
                    mean_impact = 0
                    max_impact = 0
                    beyond_spread_ratio = 0
            
            metrics = {
                group_by: group_id,
                'mean_spread_impact': mean_impact,
                'max_spread_impact': max_impact,
                'beyond_spread_ratio': beyond_spread_ratio,
                'total_trades': len(group_df)
            }
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Analyzed spread impact for {len(result_df)} groups")
        
        return result_df
    
    def calculate_price_momentum(self, df: pd.DataFrame,
                                 windows: Optional[List[str]] = None,
                                 group_by: str = 'user_id') -> pd.DataFrame:
        """
        Calculate price momentum indicators
        
        Args:
            df: DataFrame with trade data
            windows: List of time windows for momentum calculation
            group_by: Column to group by
            
        Returns:
            DataFrame with momentum metrics
        """
        windows = windows or ['5min', '1H', '24H']
        
        self.logger.info(f"Calculating price momentum for windows: {windows}")
        
        if df.empty or 'price' not in df.columns or 'timestamp' not in df.columns:
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
            
            # Calculate momentum for each window
            for window in windows:
                # Calculate returns
                returns = group_df['price'].pct_change()
                
                # Rolling momentum (cumulative return)
                rolling_return = group_df['price'].pct_change(periods=1).rolling(window=window).sum()
                
                if len(rolling_return.dropna()) > 0:
                    metrics[f'momentum_{window}'] = rolling_return.iloc[-1]
                    metrics[f'momentum_mean_{window}'] = rolling_return.mean()
                    metrics[f'momentum_std_{window}'] = rolling_return.std()
                else:
                    metrics[f'momentum_{window}'] = 0
                    metrics[f'momentum_mean_{window}'] = 0
                    metrics[f'momentum_std_{window}'] = 0
            
            results.append(metrics)
        
        result_df = pd.DataFrame(results)
        self.logger.info(f"Calculated price momentum for {len(result_df)} groups")
        
        return result_df
