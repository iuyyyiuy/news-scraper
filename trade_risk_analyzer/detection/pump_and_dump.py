"""
Pump-and-Dump Detector

Detects pump-and-dump schemes including sudden volume spikes,
coordinated buying patterns, and rapid price increases followed by declines.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import timedelta

from trade_risk_analyzer.core.base import BaseDetector, Alert, PatternType, RiskLevel
from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


class PumpAndDumpDetector(BaseDetector):
    """
    Detects pump-and-dump schemes in trade data
    """
    
    def __init__(self,
                 volume_spike_threshold: float = 3.0,
                 price_increase_threshold: float = 0.5,
                 price_decline_threshold: float = 0.3,
                 lookback_days: int = 7,
                 pump_window_hours: int = 24,
                 dump_window_hours: int = 48,
                 coordinated_accounts_threshold: int = 3,
                 coordinated_time_window_minutes: int = 30):
        """
        Initialize pump-and-dump detector
        
        Args:
            volume_spike_threshold: Volume spike multiplier (3.0 = 300%)
            price_increase_threshold: Price increase threshold (0.5 = 50%)
            price_decline_threshold: Price decline threshold after pump (0.3 = 30%)
            lookback_days: Days to look back for baseline calculation
            pump_window_hours: Time window for detecting pump phase
            dump_window_hours: Time window for detecting dump phase after pump
            coordinated_accounts_threshold: Min accounts for coordinated buying
            coordinated_time_window_minutes: Time window for coordinated detection
        """
        self.volume_spike_threshold = volume_spike_threshold
        self.price_increase_threshold = price_increase_threshold
        self.price_decline_threshold = price_decline_threshold
        self.lookback_days = lookback_days
        self.pump_window_hours = pump_window_hours
        self.dump_window_hours = dump_window_hours
        self.coordinated_accounts_threshold = coordinated_accounts_threshold
        self.coordinated_time_window_minutes = coordinated_time_window_minutes
        
        self.logger = logger
    
    def detect(self, trades: pd.DataFrame) -> List[Alert]:
        """
        Detect pump-and-dump patterns
        
        Args:
            trades: DataFrame with trade data
            
        Returns:
            List of alerts for detected pump-and-dump schemes
        """
        self.logger.info(f"Detecting pump-and-dump patterns in {len(trades)} trades")
        
        if trades.empty:
            return []
        
        alerts = []
        
        # Detect sudden volume spikes
        volume_spike_alerts = self._detect_volume_spikes(trades)
        alerts.extend(volume_spike_alerts)
        
        # Detect coordinated buying patterns
        coordinated_alerts = self._detect_coordinated_buying(trades)
        alerts.extend(coordinated_alerts)
        
        # Detect pump-and-dump price patterns
        price_pattern_alerts = self._detect_price_patterns(trades)
        alerts.extend(price_pattern_alerts)
        
        self.logger.info(f"Detected {len(alerts)} pump-and-dump alerts")
        
        return alerts
    
    def _detect_volume_spikes(self, trades: pd.DataFrame) -> List[Alert]:
        """
        Detect sudden volume spikes exceeding threshold multiplier
        
        Args:
            trades: Trade data
            
        Returns:
            List of alerts
        """
        alerts = []
        
        # Analyze by symbol
        for symbol in trades['symbol'].unique():
            symbol_trades = trades[trades['symbol'] == symbol].sort_values('timestamp')
            
            if len(symbol_trades) < 2:
                continue
            
            # Calculate rolling baseline volume (7-day average)
            symbol_trades['date'] = symbol_trades['timestamp'].dt.date
            daily_volumes = symbol_trades.groupby('date')['volume'].sum()
            
            if len(daily_volumes) < self.lookback_days:
                continue
            
            # Calculate baseline (7-day average)
            baseline_volume = daily_volumes.rolling(
                window=self.lookback_days, 
                min_periods=1
            ).mean()
            
            # Check for volume spikes
            for date, volume in daily_volumes.items():
                if date not in baseline_volume.index:
                    continue
                
                baseline = baseline_volume[date]
                
                if baseline > 0 and volume > baseline * self.volume_spike_threshold:
                    # Volume spike detected
                    spike_ratio = volume / baseline
                    spike_trades = symbol_trades[symbol_trades['date'] == date]
                    
                    # Get involved users
                    involved_users = spike_trades['user_id'].unique()
                    trade_ids = spike_trades['trade_id'].tolist()
                    
                    # Calculate score based on spike magnitude
                    score = min(100, 50 + (spike_ratio - self.volume_spike_threshold) * 10)
                    risk_level = self._score_to_risk_level(score)
                    
                    alert = Alert(
                        alert_id=f"pump_volume_{symbol}_{pd.Timestamp(date).timestamp()}",
                        timestamp=pd.Timestamp.now(),
                        user_id=','.join(map(str, involved_users[:10])),  # Limit to first 10
                        trade_ids=trade_ids,
                        anomaly_score=score,
                        risk_level=risk_level,
                        pattern_type=PatternType.PUMP_AND_DUMP,
                        explanation=f"Volume spike detected for {symbol}: {spike_ratio:.1f}x baseline ({volume:.2f} vs {baseline:.2f})",
                        recommended_action="Investigate sudden volume increase and user coordination"
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _detect_coordinated_buying(self, trades: pd.DataFrame) -> List[Alert]:
        """
        Identify coordinated buying patterns from multiple accounts
        
        Args:
            trades: Trade data
            
        Returns:
            List of alerts
        """
        alerts = []
        
        # Analyze by symbol
        for symbol in trades['symbol'].unique():
            symbol_trades = trades[trades['symbol'] == symbol].sort_values('timestamp')
            
            # Focus on buy orders
            buy_trades = symbol_trades[symbol_trades['trade_type'] == 'BUY']
            
            if len(buy_trades) < self.coordinated_accounts_threshold:
                continue
            
            # Create time windows
            buy_trades = buy_trades.copy()
            buy_trades['time_window'] = buy_trades['timestamp'].dt.floor(
                f'{self.coordinated_time_window_minutes}min'
            )
            
            # Check each time window for coordinated activity
            for time_window in buy_trades['time_window'].unique():
                window_trades = buy_trades[buy_trades['time_window'] == time_window]
                
                unique_users = window_trades['user_id'].nunique()
                
                if unique_users >= self.coordinated_accounts_threshold:
                    # Check if prices are similar (coordinated buying)
                    price_std = window_trades['price'].std()
                    price_mean = window_trades['price'].mean()
                    
                    # Low price variance indicates coordination
                    if price_mean > 0:
                        price_cv = price_std / price_mean
                        
                        # If coefficient of variation is low, it's suspicious
                        if price_cv < 0.05:  # Less than 5% variation
                            total_volume = window_trades['volume'].sum()
                            involved_users = window_trades['user_id'].unique()
                            trade_ids = window_trades['trade_id'].tolist()
                            
                            # Calculate score based on number of accounts and volume
                            coordination_factor = min(unique_users / self.coordinated_accounts_threshold, 3)
                            score = min(100, 60 + coordination_factor * 10)
                            risk_level = self._score_to_risk_level(score)
                            
                            alert = Alert(
                                alert_id=f"pump_coordinated_{symbol}_{time_window.timestamp()}",
                                timestamp=pd.Timestamp.now(),
                                user_id=','.join(map(str, involved_users[:10])),
                                trade_ids=trade_ids,
                                anomaly_score=score,
                                risk_level=risk_level,
                                pattern_type=PatternType.PUMP_AND_DUMP,
                                explanation=f"Coordinated buying detected for {symbol}: {unique_users} accounts buying within {self.coordinated_time_window_minutes}min window (total volume: {total_volume:.2f})",
                                recommended_action="Investigate potential coordinated pump scheme"
                            )
                            alerts.append(alert)
        
        return alerts
    
    def _detect_price_patterns(self, trades: pd.DataFrame) -> List[Alert]:
        """
        Flag rapid price increases followed by declines
        
        Args:
            trades: Trade data
            
        Returns:
            List of alerts
        """
        alerts = []
        
        # Analyze by symbol
        for symbol in trades['symbol'].unique():
            symbol_trades = trades[trades['symbol'] == symbol].sort_values('timestamp')
            
            if len(symbol_trades) < 10:
                continue
            
            # Calculate price changes over time
            symbol_trades = symbol_trades.copy()
            symbol_trades['hour'] = symbol_trades['timestamp'].dt.floor('h')
            hourly_prices = symbol_trades.groupby('hour')['price'].agg(['mean', 'min', 'max', 'count'])
            
            if len(hourly_prices) < 2:
                continue
            
            # Look for pump-and-dump patterns
            for i in range(len(hourly_prices) - 1):
                current_hour = hourly_prices.index[i]
                
                # Get price at current hour
                base_price = hourly_prices.iloc[i]['mean']
                
                # Look ahead for pump phase (price increase)
                pump_end_idx = min(i + self.pump_window_hours, len(hourly_prices))
                pump_window = hourly_prices.iloc[i:pump_end_idx]
                
                if len(pump_window) < 2:
                    continue
                
                max_price = pump_window['max'].max()
                max_price_idx = pump_window['max'].idxmax()
                
                # Check if price increased significantly
                if base_price > 0:
                    price_increase = (max_price - base_price) / base_price
                    
                    if price_increase >= self.price_increase_threshold:
                        # Pump detected, now look for dump
                        max_price_hour_idx = hourly_prices.index.get_loc(max_price_idx)
                        dump_end_idx = min(max_price_hour_idx + self.dump_window_hours, len(hourly_prices))
                        dump_window = hourly_prices.iloc[max_price_hour_idx:dump_end_idx]
                        
                        if len(dump_window) > 1:
                            min_price_after_pump = dump_window['min'].min()
                            price_decline = (max_price - min_price_after_pump) / max_price
                            
                            # Check if price declined significantly after pump
                            if price_decline >= self.price_decline_threshold:
                                # Pump-and-dump pattern detected
                                pump_start = current_hour
                                pump_peak = max_price_idx
                                dump_end = dump_window.index[-1]
                                
                                # Get trades in this period
                                pattern_trades = symbol_trades[
                                    (symbol_trades['timestamp'] >= pump_start) &
                                    (symbol_trades['timestamp'] <= dump_end)
                                ]
                                
                                involved_users = pattern_trades['user_id'].unique()
                                trade_ids = pattern_trades['trade_id'].tolist()
                                
                                # Calculate score based on magnitude
                                magnitude_score = (price_increase + price_decline) * 50
                                score = min(100, 70 + magnitude_score)
                                risk_level = self._score_to_risk_level(score)
                                
                                alert = Alert(
                                    alert_id=f"pump_pattern_{symbol}_{pump_start.timestamp()}",
                                    timestamp=pd.Timestamp.now(),
                                    user_id=','.join(map(str, involved_users[:10])),
                                    trade_ids=trade_ids,
                                    anomaly_score=score,
                                    risk_level=risk_level,
                                    pattern_type=PatternType.PUMP_AND_DUMP,
                                    explanation=f"Pump-and-dump pattern detected for {symbol}: Price increased {price_increase*100:.1f}% from {base_price:.2f} to {max_price:.2f}, then declined {price_decline*100:.1f}% to {min_price_after_pump:.2f}",
                                    recommended_action="Investigate price manipulation and user involvement"
                                )
                                alerts.append(alert)
                                
                                # Skip ahead to avoid duplicate alerts
                                break
        
        return alerts
    
    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert score to risk level"""
        if score >= 80:
            return RiskLevel.HIGH
        elif score >= 50:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def calculate_pump_and_dump_probability(self, trades: pd.DataFrame, symbol: str) -> float:
        """
        Calculate pump-and-dump probability score for a symbol
        
        Args:
            trades: Trade data
            symbol: Symbol to analyze
            
        Returns:
            Probability score (0-1)
        """
        symbol_trades = trades[trades['symbol'] == symbol].sort_values('timestamp')
        
        if len(symbol_trades) < 10:
            return 0.0
        
        indicators = []
        
        # 1. Volume volatility (high volatility indicates manipulation)
        symbol_trades['date'] = symbol_trades['timestamp'].dt.date
        daily_volumes = symbol_trades.groupby('date')['volume'].sum()
        
        if len(daily_volumes) > 1:
            volume_cv = daily_volumes.std() / daily_volumes.mean() if daily_volumes.mean() > 0 else 0
            volume_indicator = min(1.0, volume_cv / 2)  # Normalize
            indicators.append(volume_indicator)
        
        # 2. Price volatility
        hourly_prices = symbol_trades.groupby(symbol_trades['timestamp'].dt.floor('h'))['price'].mean()
        
        if len(hourly_prices) > 1:
            price_cv = hourly_prices.std() / hourly_prices.mean() if hourly_prices.mean() > 0 else 0
            price_indicator = min(1.0, price_cv / 0.5)  # Normalize
            indicators.append(price_indicator)
        
        # 3. Buy-sell imbalance during price increases
        symbol_trades['price_change'] = symbol_trades['price'].diff()
        increasing_periods = symbol_trades[symbol_trades['price_change'] > 0]
        
        if len(increasing_periods) > 0:
            buy_count = len(increasing_periods[increasing_periods['trade_type'] == 'BUY'])
            total_count = len(increasing_periods)
            buy_ratio = buy_count / total_count if total_count > 0 else 0
            indicators.append(buy_ratio)
        
        # 4. Account concentration (few accounts with high volume)
        user_volumes = symbol_trades.groupby('user_id')['volume'].sum().sort_values(ascending=False)
        
        if len(user_volumes) > 0:
            top_3_volume = user_volumes.head(3).sum()
            total_volume = user_volumes.sum()
            concentration = top_3_volume / total_volume if total_volume > 0 else 0
            indicators.append(concentration)
        
        # Average all indicators
        if indicators:
            return np.mean(indicators)
        else:
            return 0.0
    
    def get_pattern_type(self) -> PatternType:
        """Get pattern type this detector identifies"""
        return PatternType.PUMP_AND_DUMP
