"""
High-Frequency Trading Manipulation Detector

Detects HFT manipulation patterns including excessive trade frequency,
layering, and spoofing behaviors.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import timedelta
from collections import defaultdict

from trade_risk_analyzer.core.base import BaseDetector, Alert, PatternType, RiskLevel
from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


class HFTManipulationDetector(BaseDetector):
    """
    Detects high-frequency trading manipulation patterns in trade data
    """
    
    def __init__(self,
                 trade_frequency_threshold: int = 100,
                 frequency_window_hours: int = 1,
                 cancellation_ratio_threshold: float = 0.8,
                 quote_stuffing_threshold: int = 50,
                 quote_stuffing_window_minutes: int = 1,
                 layering_price_levels: int = 3,
                 layering_time_window_seconds: int = 60,
                 spoofing_cancel_time_seconds: int = 5,
                 min_pattern_occurrences: int = 3):
        """
        Initialize HFT manipulation detector
        
        Args:
            trade_frequency_threshold: Max trades per hour before flagging
            frequency_window_hours: Time window for frequency calculation
            cancellation_ratio_threshold: Trade-to-cancellation ratio threshold
            quote_stuffing_threshold: Orders per minute threshold
            quote_stuffing_window_minutes: Time window for quote stuffing
            layering_price_levels: Min price levels for layering detection
            layering_time_window_seconds: Time window for layering detection
            spoofing_cancel_time_seconds: Max time before cancel for spoofing
            min_pattern_occurrences: Min occurrences to flag pattern
        """
        self.trade_frequency_threshold = trade_frequency_threshold
        self.frequency_window_hours = frequency_window_hours
        self.cancellation_ratio_threshold = cancellation_ratio_threshold
        self.quote_stuffing_threshold = quote_stuffing_threshold
        self.quote_stuffing_window_minutes = quote_stuffing_window_minutes
        self.layering_price_levels = layering_price_levels
        self.layering_time_window_seconds = layering_time_window_seconds
        self.spoofing_cancel_time_seconds = spoofing_cancel_time_seconds
        self.min_pattern_occurrences = min_pattern_occurrences
        
        self.logger = logger
    
    def detect(self, trades: pd.DataFrame) -> List[Alert]:
        """
        Detect HFT manipulation patterns
        
        Args:
            trades: DataFrame with trade data
            
        Returns:
            List of alerts for detected HFT manipulation
        """
        self.logger.info(f"Detecting HFT manipulation in {len(trades)} trades")
        
        if trades.empty:
            return []
        
        alerts = []
        
        # Detect excessive trade frequency
        frequency_alerts = self._detect_excessive_frequency(trades)
        alerts.extend(frequency_alerts)
        
        # Detect quote stuffing patterns
        quote_stuffing_alerts = self._detect_quote_stuffing(trades)
        alerts.extend(quote_stuffing_alerts)
        
        # Detect layering patterns
        layering_alerts = self._detect_layering(trades)
        alerts.extend(layering_alerts)
        
        # Detect spoofing behavior
        spoofing_alerts = self._detect_spoofing(trades)
        alerts.extend(spoofing_alerts)
        
        self.logger.info(f"Detected {len(alerts)} HFT manipulation alerts")
        
        return alerts
    
    def _detect_excessive_frequency(self, trades: pd.DataFrame) -> List[Alert]:
        """
        Flag users exceeding trade frequency thresholds
        
        Args:
            trades: Trade data
            
        Returns:
            List of alerts
        """
        alerts = []
        
        # Analyze by user
        for user_id in trades['user_id'].unique():
            user_trades = trades[trades['user_id'] == user_id].sort_values('timestamp')
            
            if len(user_trades) < self.trade_frequency_threshold:
                continue
            
            # Create rolling time windows
            user_trades = user_trades.copy()
            user_trades['hour_window'] = user_trades['timestamp'].dt.floor(
                f'{self.frequency_window_hours}h'
            )
            
            # Count trades per window
            window_counts = user_trades.groupby('hour_window').size()
            
            # Find windows exceeding threshold
            excessive_windows = window_counts[window_counts >= self.trade_frequency_threshold]
            
            if len(excessive_windows) > 0:
                max_count = excessive_windows.max()
                max_window = excessive_windows.idxmax()
                
                # Get trades in the most excessive window
                window_trades = user_trades[user_trades['hour_window'] == max_window]
                trade_ids = window_trades['trade_id'].tolist()
                symbols = window_trades['symbol'].unique()
                
                # Calculate score based on how much threshold is exceeded
                excess_ratio = max_count / self.trade_frequency_threshold
                score = min(100, 60 + (excess_ratio - 1) * 20)
                risk_level = self._score_to_risk_level(score)
                
                alert = Alert(
                    alert_id=f"hft_frequency_{user_id}_{max_window.timestamp()}",
                    timestamp=pd.Timestamp.now(),
                    user_id=user_id,
                    trade_ids=trade_ids,
                    anomaly_score=score,
                    risk_level=risk_level,
                    pattern_type=PatternType.HFT_MANIPULATION,
                    explanation=f"Excessive trade frequency detected: {max_count} trades in {self.frequency_window_hours}h window (threshold: {self.trade_frequency_threshold}). Symbols: {', '.join(symbols[:5])}",
                    recommended_action="Review user trading patterns for potential HFT manipulation"
                )
                alerts.append(alert)
        
        return alerts
    
    def _detect_quote_stuffing(self, trades: pd.DataFrame) -> List[Alert]:
        """
        Detect quote stuffing patterns (rapid order placement)
        
        Args:
            trades: Trade data
            
        Returns:
            List of alerts
        """
        alerts = []
        
        # Analyze by user and symbol
        for user_id in trades['user_id'].unique():
            user_trades = trades[trades['user_id'] == user_id].sort_values('timestamp')
            
            for symbol in user_trades['symbol'].unique():
                symbol_trades = user_trades[user_trades['symbol'] == symbol].copy()
                
                if len(symbol_trades) < self.quote_stuffing_threshold:
                    continue
                
                # Create minute windows
                symbol_trades['minute_window'] = symbol_trades['timestamp'].dt.floor(
                    f'{self.quote_stuffing_window_minutes}min'
                )
                
                # Count orders per minute
                minute_counts = symbol_trades.groupby('minute_window').size()
                
                # Find minutes with quote stuffing
                stuffing_minutes = minute_counts[minute_counts >= self.quote_stuffing_threshold]
                
                if len(stuffing_minutes) >= self.min_pattern_occurrences:
                    max_count = stuffing_minutes.max()
                    max_minute = stuffing_minutes.idxmax()
                    
                    # Get trades in the most excessive minute
                    window_trades = symbol_trades[symbol_trades['minute_window'] == max_minute]
                    trade_ids = window_trades['trade_id'].tolist()
                    
                    # Calculate score
                    excess_ratio = max_count / self.quote_stuffing_threshold
                    score = min(100, 70 + (excess_ratio - 1) * 15)
                    risk_level = self._score_to_risk_level(score)
                    
                    alert = Alert(
                        alert_id=f"hft_stuffing_{user_id}_{symbol}_{max_minute.timestamp()}",
                        timestamp=pd.Timestamp.now(),
                        user_id=user_id,
                        trade_ids=trade_ids,
                        anomaly_score=score,
                        risk_level=risk_level,
                        pattern_type=PatternType.HFT_MANIPULATION,
                        explanation=f"Quote stuffing detected for {symbol}: {max_count} orders in {self.quote_stuffing_window_minutes}min (threshold: {self.quote_stuffing_threshold}). Pattern occurred {len(stuffing_minutes)} times.",
                        recommended_action="Investigate potential market manipulation through quote stuffing"
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _detect_layering(self, trades: pd.DataFrame) -> List[Alert]:
        """
        Detect layering patterns (multiple orders at different prices)
        
        Args:
            trades: Trade data
            
        Returns:
            List of alerts
        """
        alerts = []
        
        # Analyze by user and symbol
        for user_id in trades['user_id'].unique():
            user_trades = trades[trades['user_id'] == user_id].sort_values('timestamp')
            
            for symbol in user_trades['symbol'].unique():
                symbol_trades = user_trades[user_trades['symbol'] == symbol].copy()
                
                if len(symbol_trades) < self.layering_price_levels * 2:
                    continue
                
                # Create time windows
                symbol_trades['time_window'] = symbol_trades['timestamp'].dt.floor(
                    f'{self.layering_time_window_seconds}s'
                )
                
                # Analyze each time window
                layering_patterns = []
                
                for time_window in symbol_trades['time_window'].unique():
                    window_trades = symbol_trades[symbol_trades['time_window'] == time_window]
                    
                    if len(window_trades) < self.layering_price_levels:
                        continue
                    
                    # Count unique price levels
                    unique_prices = window_trades['price'].nunique()
                    
                    if unique_prices >= self.layering_price_levels:
                        # Check if followed by rapid cancellations or opposite trades
                        window_end = time_window + pd.Timedelta(seconds=self.layering_time_window_seconds)
                        
                        # Look for cancellations or reversals shortly after
                        next_window_trades = symbol_trades[
                            (symbol_trades['timestamp'] > window_end) &
                            (symbol_trades['timestamp'] <= window_end + pd.Timedelta(seconds=self.layering_time_window_seconds * 2))
                        ]
                        
                        # Check for trade type reversal (layering followed by opposite action)
                        window_types = window_trades['trade_type'].value_counts()
                        dominant_type = window_types.idxmax() if len(window_types) > 0 else None
                        
                        if dominant_type and len(next_window_trades) > 0:
                            next_types = next_window_trades['trade_type'].value_counts()
                            opposite_type = 'SELL' if dominant_type == 'BUY' else 'BUY'
                            
                            # If opposite trades follow, it's likely layering
                            if opposite_type in next_types.index and next_types[opposite_type] > 0:
                                layering_patterns.append({
                                    'window': time_window,
                                    'price_levels': unique_prices,
                                    'trades': window_trades,
                                    'dominant_type': dominant_type,
                                    'reversal_count': next_types[opposite_type]
                                })
                
                # Create alert if layering patterns detected
                if len(layering_patterns) >= self.min_pattern_occurrences:
                    all_trade_ids = []
                    total_price_levels = 0
                    
                    for pattern in layering_patterns:
                        all_trade_ids.extend(pattern['trades']['trade_id'].tolist())
                        total_price_levels += pattern['price_levels']
                    
                    avg_price_levels = total_price_levels / len(layering_patterns)
                    
                    # Calculate score
                    pattern_factor = min(len(layering_patterns) / self.min_pattern_occurrences, 3)
                    level_factor = avg_price_levels / self.layering_price_levels
                    score = min(100, 65 + pattern_factor * 10 + level_factor * 5)
                    risk_level = self._score_to_risk_level(score)
                    
                    alert = Alert(
                        alert_id=f"hft_layering_{user_id}_{symbol}_{pd.Timestamp.now().timestamp()}",
                        timestamp=pd.Timestamp.now(),
                        user_id=user_id,
                        trade_ids=list(set(all_trade_ids)),
                        anomaly_score=score,
                        risk_level=risk_level,
                        pattern_type=PatternType.HFT_MANIPULATION,
                        explanation=f"Layering detected for {symbol}: {len(layering_patterns)} patterns with avg {avg_price_levels:.1f} price levels, followed by reversals",
                        recommended_action="Investigate potential market manipulation through layering"
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _detect_spoofing(self, trades: pd.DataFrame) -> List[Alert]:
        """
        Identify spoofing behavior (rapid order placement and cancellation)
        
        Args:
            trades: Trade data
            
        Returns:
            List of alerts
        """
        alerts = []
        
        # Analyze by user and symbol
        for user_id in trades['user_id'].unique():
            user_trades = trades[trades['user_id'] == user_id].sort_values('timestamp')
            
            for symbol in user_trades['symbol'].unique():
                symbol_trades = user_trades[user_trades['symbol'] == symbol].copy()
                
                if len(symbol_trades) < self.min_pattern_occurrences * 2:
                    continue
                
                # Detect rapid placement and reversal patterns
                spoofing_patterns = []
                
                for i in range(len(symbol_trades) - 1):
                    current_trade = symbol_trades.iloc[i]
                    
                    # Look for quick reversals (opposite trade type within seconds)
                    time_threshold = current_trade['timestamp'] + pd.Timedelta(
                        seconds=self.spoofing_cancel_time_seconds
                    )
                    
                    nearby_trades = symbol_trades[
                        (symbol_trades['timestamp'] > current_trade['timestamp']) &
                        (symbol_trades['timestamp'] <= time_threshold)
                    ]
                    
                    # Check for opposite trade type at similar price
                    opposite_type = 'SELL' if current_trade['trade_type'] == 'BUY' else 'BUY'
                    opposite_trades = nearby_trades[nearby_trades['trade_type'] == opposite_type]
                    
                    for _, opposite_trade in opposite_trades.iterrows():
                        # Check if prices are similar (spoofing indicator)
                        price_diff = abs(opposite_trade['price'] - current_trade['price']) / current_trade['price']
                        
                        if price_diff <= 0.01:  # Within 1%
                            time_diff = (opposite_trade['timestamp'] - current_trade['timestamp']).total_seconds()
                            
                            spoofing_patterns.append({
                                'trade_id_1': current_trade['trade_id'],
                                'trade_id_2': opposite_trade['trade_id'],
                                'time_diff': time_diff,
                                'price_diff': price_diff,
                                'type_1': current_trade['trade_type'],
                                'type_2': opposite_trade['trade_type']
                            })
                
                # Create alert if spoofing patterns detected
                if len(spoofing_patterns) >= self.min_pattern_occurrences:
                    all_trade_ids = []
                    avg_time_diff = 0
                    
                    for pattern in spoofing_patterns:
                        all_trade_ids.extend([pattern['trade_id_1'], pattern['trade_id_2']])
                        avg_time_diff += pattern['time_diff']
                    
                    avg_time_diff /= len(spoofing_patterns)
                    
                    # Calculate score
                    pattern_factor = min(len(spoofing_patterns) / self.min_pattern_occurrences, 3)
                    speed_factor = 1 - (avg_time_diff / self.spoofing_cancel_time_seconds)
                    score = min(100, 70 + pattern_factor * 10 + speed_factor * 10)
                    risk_level = self._score_to_risk_level(score)
                    
                    alert = Alert(
                        alert_id=f"hft_spoofing_{user_id}_{symbol}_{pd.Timestamp.now().timestamp()}",
                        timestamp=pd.Timestamp.now(),
                        user_id=user_id,
                        trade_ids=list(set(all_trade_ids)),
                        anomaly_score=score,
                        risk_level=risk_level,
                        pattern_type=PatternType.HFT_MANIPULATION,
                        explanation=f"Spoofing detected for {symbol}: {len(spoofing_patterns)} rapid order placement and reversal patterns (avg {avg_time_diff:.2f}s)",
                        recommended_action="Investigate potential market manipulation through spoofing"
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert score to risk level"""
        if score >= 80:
            return RiskLevel.HIGH
        elif score >= 50:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def calculate_hft_manipulation_score(self, trades: pd.DataFrame, user_id: str) -> float:
        """
        Calculate HFT manipulation score for a user
        
        Args:
            trades: Trade data
            user_id: User to analyze
            
        Returns:
            Manipulation score (0-1)
        """
        user_trades = trades[trades['user_id'] == user_id].sort_values('timestamp')
        
        if len(user_trades) < 10:
            return 0.0
        
        indicators = []
        
        # 1. Trade frequency indicator
        if len(user_trades) > 0:
            time_span = (user_trades['timestamp'].max() - user_trades['timestamp'].min()).total_seconds() / 3600
            if time_span > 0:
                trades_per_hour = len(user_trades) / time_span
                frequency_score = min(1.0, trades_per_hour / self.trade_frequency_threshold)
                indicators.append(frequency_score)
        
        # 2. Price level diversity (layering indicator)
        for symbol in user_trades['symbol'].unique():
            symbol_trades = user_trades[user_trades['symbol'] == symbol]
            unique_prices = symbol_trades['price'].nunique()
            total_trades = len(symbol_trades)
            
            if total_trades > 0:
                price_diversity = unique_prices / total_trades
                # High diversity with many trades suggests layering
                if total_trades > 10:
                    layering_score = price_diversity * min(1.0, total_trades / 50)
                    indicators.append(layering_score)
        
        # 3. Rapid reversal rate (spoofing indicator)
        reversal_count = 0
        for i in range(len(user_trades) - 1):
            if user_trades.iloc[i]['trade_type'] != user_trades.iloc[i+1]['trade_type']:
                time_diff = (user_trades.iloc[i+1]['timestamp'] - user_trades.iloc[i]['timestamp']).total_seconds()
                if time_diff <= self.spoofing_cancel_time_seconds:
                    reversal_count += 1
        
        if len(user_trades) > 1:
            reversal_rate = reversal_count / (len(user_trades) - 1)
            indicators.append(reversal_rate)
        
        # 4. Order concentration in time (quote stuffing indicator)
        user_trades_copy = user_trades.copy()
        user_trades_copy['minute'] = user_trades_copy['timestamp'].dt.floor('1min')
        minute_counts = user_trades_copy.groupby('minute').size()
        
        if len(minute_counts) > 0:
            max_per_minute = minute_counts.max()
            stuffing_score = min(1.0, max_per_minute / self.quote_stuffing_threshold)
            indicators.append(stuffing_score)
        
        # Average all indicators
        if indicators:
            return np.mean(indicators)
        else:
            return 0.0
    
    def get_pattern_type(self) -> PatternType:
        """Get pattern type this detector identifies"""
        return PatternType.HFT_MANIPULATION
