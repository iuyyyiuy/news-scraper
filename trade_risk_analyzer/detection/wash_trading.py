"""
Wash Trading Detector

Detects wash trading patterns including self-trading, circular trading,
and trades with no economic benefit.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import timedelta

from trade_risk_analyzer.core.base import BaseDetector, Alert, PatternType, RiskLevel
from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


class WashTradingDetector(BaseDetector):
    """
    Detects wash trading patterns in trade data
    """
    
    def __init__(self,
                 time_window_seconds: int = 300,
                 price_tolerance: float = 0.001,
                 min_wash_trades: int = 3,
                 circular_depth: int = 3):
        """
        Initialize wash trading detector
        
        Args:
            time_window_seconds: Time window for detecting related trades
            price_tolerance: Price difference tolerance (0.001 = 0.1%)
            min_wash_trades: Minimum trades to flag as wash trading
            circular_depth: Maximum depth for circular trading detection
        """
        self.time_window_seconds = time_window_seconds
        self.price_tolerance = price_tolerance
        self.min_wash_trades = min_wash_trades
        self.circular_depth = circular_depth
        
        self.logger = logger
    
    def detect(self, trades: pd.DataFrame) -> List[Alert]:
        """
        Detect wash trading patterns
        
        Args:
            trades: DataFrame with trade data
            
        Returns:
            List of alerts for detected wash trading
        """
        self.logger.info(f"Detecting wash trading in {len(trades)} trades")
        
        if trades.empty:
            return []
        
        alerts = []
        
        # Detect self-trading (same user as buyer and seller)
        self_trade_alerts = self._detect_self_trading(trades)
        alerts.extend(self_trade_alerts)
        
        # Detect circular trading patterns
        circular_alerts = self._detect_circular_trading(trades)
        alerts.extend(circular_alerts)
        
        # Detect no-benefit trades (same buy/sell price)
        no_benefit_alerts = self._detect_no_benefit_trades(trades)
        alerts.extend(no_benefit_alerts)
        
        # Detect matched trades (suspicious timing and pricing)
        matched_alerts = self._detect_matched_trades(trades)
        alerts.extend(matched_alerts)
        
        self.logger.info(f"Detected {len(alerts)} wash trading alerts")
        
        return alerts
    
    def _detect_self_trading(self, trades: pd.DataFrame) -> List[Alert]:
        """
        Detect same user as buyer and seller within time window
        
        Args:
            trades: Trade data
            
        Returns:
            List of alerts
        """
        alerts = []
        
        # Group by user and symbol
        for user_id in trades['user_id'].unique():
            user_trades = trades[trades['user_id'] == user_id].sort_values('timestamp')
            
            for symbol in user_trades['symbol'].unique():
                symbol_trades = user_trades[user_trades['symbol'] == symbol].copy()
                
                if len(symbol_trades) < 2:
                    continue
                
                # Look for buy-sell pairs within time window
                buys = symbol_trades[symbol_trades['trade_type'] == 'BUY']
                sells = symbol_trades[symbol_trades['trade_type'] == 'SELL']
                
                wash_trade_count = 0
                wash_trade_ids = []
                
                for _, buy in buys.iterrows():
                    # Find sells within time window
                    time_diff = (sells['timestamp'] - buy['timestamp']).dt.total_seconds()
                    nearby_sells = sells[
                        (time_diff > 0) & 
                        (time_diff <= self.time_window_seconds)
                    ]
                    
                    for _, sell in nearby_sells.iterrows():
                        # Check if prices are similar (wash trading indicator)
                        price_diff = abs(sell['price'] - buy['price']) / buy['price']
                        
                        if price_diff <= self.price_tolerance:
                            wash_trade_count += 1
                            wash_trade_ids.extend([buy['trade_id'], sell['trade_id']])
                
                # Create alert if threshold exceeded
                if wash_trade_count >= self.min_wash_trades:
                    score = min(100, wash_trade_count * 20)
                    risk_level = self._score_to_risk_level(score)
                    
                    alert = Alert(
                        alert_id=f"wash_self_{user_id}_{symbol}_{pd.Timestamp.now().timestamp()}",
                        timestamp=pd.Timestamp.now(),
                        user_id=user_id,
                        trade_ids=list(set(wash_trade_ids)),
                        anomaly_score=score,
                        risk_level=risk_level,
                        pattern_type=PatternType.WASH_TRADING,
                        explanation=f"Self-trading detected: {wash_trade_count} matched buy-sell pairs within {self.time_window_seconds}s for {symbol}",
                        recommended_action="Review user trading history and consider account suspension"
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _detect_circular_trading(self, trades: pd.DataFrame) -> List[Alert]:
        """
        Identify circular trading patterns across multiple accounts
        
        Args:
            trades: Trade data
            
        Returns:
            List of alerts
        """
        alerts = []
        
        # Group by symbol and time windows
        for symbol in trades['symbol'].unique():
            symbol_trades = trades[trades['symbol'] == symbol].sort_values('timestamp')
            
            # Create time windows
            symbol_trades['time_window'] = symbol_trades['timestamp'].dt.floor(f'{self.time_window_seconds}s')
            
            for time_window in symbol_trades['time_window'].unique():
                window_trades = symbol_trades[symbol_trades['time_window'] == time_window]
                
                if len(window_trades) < 3:
                    continue
                
                # Build trading graph (who traded with whom)
                trading_pairs = []
                for _, trade in window_trades.iterrows():
                    # In real scenario, you'd have counterparty info
                    # For now, we detect patterns based on timing and pricing
                    trading_pairs.append({
                        'user': trade['user_id'],
                        'type': trade['trade_type'],
                        'price': trade['price'],
                        'volume': trade['volume'],
                        'timestamp': trade['timestamp']
                    })
                
                # Detect circular patterns (A->B->C->A)
                circular_patterns = self._find_circular_patterns(trading_pairs)
                
                if circular_patterns:
                    involved_users = set()
                    trade_ids = []
                    
                    for pattern in circular_patterns:
                        involved_users.update([p['user'] for p in pattern])
                    
                    score = min(100, len(circular_patterns) * 30)
                    risk_level = self._score_to_risk_level(score)
                    
                    alert = Alert(
                        alert_id=f"wash_circular_{symbol}_{time_window.timestamp()}",
                        timestamp=pd.Timestamp.now(),
                        user_id=','.join(involved_users),
                        trade_ids=trade_ids,
                        anomaly_score=score,
                        risk_level=risk_level,
                        pattern_type=PatternType.WASH_TRADING,
                        explanation=f"Circular trading detected: {len(circular_patterns)} patterns involving {len(involved_users)} users for {symbol}",
                        recommended_action="Investigate coordinated trading activity"
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _detect_no_benefit_trades(self, trades: pd.DataFrame) -> List[Alert]:
        """
        Flag trades with no economic benefit (same buy/sell price)
        
        Args:
            trades: Trade data
            
        Returns:
            List of alerts
        """
        alerts = []
        
        for user_id in trades['user_id'].unique():
            user_trades = trades[trades['user_id'] == user_id].sort_values('timestamp')
            
            for symbol in user_trades['symbol'].unique():
                symbol_trades = user_trades[user_trades['symbol'] == symbol]
                
                # Track positions
                positions = []
                no_benefit_count = 0
                no_benefit_trade_ids = []
                
                for _, trade in symbol_trades.iterrows():
                    if trade['trade_type'] == 'BUY':
                        positions.append({
                            'price': trade['price'],
                            'volume': trade['volume'],
                            'trade_id': trade['trade_id'],
                            'timestamp': trade['timestamp']
                        })
                    elif trade['trade_type'] == 'SELL' and positions:
                        # Check if selling at same price as buying
                        for pos in positions:
                            price_diff = abs(trade['price'] - pos['price']) / pos['price']
                            
                            if price_diff <= self.price_tolerance:
                                no_benefit_count += 1
                                no_benefit_trade_ids.extend([pos['trade_id'], trade['trade_id']])
                                positions.remove(pos)
                                break
                
                if no_benefit_count >= self.min_wash_trades:
                    score = min(100, no_benefit_count * 25)
                    risk_level = self._score_to_risk_level(score)
                    
                    alert = Alert(
                        alert_id=f"wash_nobenefit_{user_id}_{symbol}_{pd.Timestamp.now().timestamp()}",
                        timestamp=pd.Timestamp.now(),
                        user_id=user_id,
                        trade_ids=list(set(no_benefit_trade_ids)),
                        anomaly_score=score,
                        risk_level=risk_level,
                        pattern_type=PatternType.WASH_TRADING,
                        explanation=f"No-benefit trading detected: {no_benefit_count} trades with no price difference for {symbol}",
                        recommended_action="Review trading intent and potential wash trading"
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _detect_matched_trades(self, trades: pd.DataFrame) -> List[Alert]:
        """
        Detect suspiciously matched trades (timing and pricing)
        
        Args:
            trades: Trade data
            
        Returns:
            List of alerts
        """
        alerts = []
        
        for symbol in trades['symbol'].unique():
            symbol_trades = trades[trades['symbol'] == symbol].sort_values('timestamp')
            
            # Look for perfectly matched buy-sell pairs
            buys = symbol_trades[symbol_trades['trade_type'] == 'BUY']
            sells = symbol_trades[symbol_trades['trade_type'] == 'SELL']
            
            matched_pairs = []
            
            for _, buy in buys.iterrows():
                for _, sell in sells.iterrows():
                    # Check timing
                    time_diff = abs((sell['timestamp'] - buy['timestamp']).total_seconds())
                    
                    if time_diff > self.time_window_seconds:
                        continue
                    
                    # Check price match
                    price_diff = abs(sell['price'] - buy['price']) / buy['price']
                    
                    # Check volume match
                    volume_diff = abs(sell['volume'] - buy['volume']) / buy['volume']
                    
                    if price_diff <= self.price_tolerance and volume_diff <= 0.01:
                        matched_pairs.append({
                            'buy_user': buy['user_id'],
                            'sell_user': sell['user_id'],
                            'buy_trade': buy['trade_id'],
                            'sell_trade': sell['trade_id'],
                            'price': buy['price'],
                            'volume': buy['volume']
                        })
            
            if len(matched_pairs) >= self.min_wash_trades:
                involved_users = set()
                trade_ids = []
                
                for pair in matched_pairs:
                    involved_users.add(pair['buy_user'])
                    involved_users.add(pair['sell_user'])
                    trade_ids.extend([pair['buy_trade'], pair['sell_trade']])
                
                score = min(100, len(matched_pairs) * 20)
                risk_level = self._score_to_risk_level(score)
                
                alert = Alert(
                    alert_id=f"wash_matched_{symbol}_{pd.Timestamp.now().timestamp()}",
                    timestamp=pd.Timestamp.now(),
                    user_id=','.join(involved_users),
                    trade_ids=list(set(trade_ids)),
                    anomaly_score=score,
                    risk_level=risk_level,
                    pattern_type=PatternType.WASH_TRADING,
                    explanation=f"Matched trading detected: {len(matched_pairs)} perfectly matched buy-sell pairs for {symbol}",
                    recommended_action="Investigate potential coordinated wash trading"
                )
                alerts.append(alert)
        
        return alerts
    
    def _find_circular_patterns(self, trading_pairs: List[Dict]) -> List[List[Dict]]:
        """
        Find circular trading patterns in trading pairs
        
        Args:
            trading_pairs: List of trading pair dictionaries
            
        Returns:
            List of circular patterns found
        """
        # Simplified circular pattern detection
        # In production, you'd use graph algorithms
        patterns = []
        
        # Group by user
        user_trades = {}
        for pair in trading_pairs:
            user = pair['user']
            if user not in user_trades:
                user_trades[user] = []
            user_trades[user].append(pair)
        
        # Look for users with both buy and sell
        circular_users = []
        for user, trades in user_trades.items():
            has_buy = any(t['type'] == 'BUY' for t in trades)
            has_sell = any(t['type'] == 'SELL' for t in trades)
            
            if has_buy and has_sell:
                circular_users.append(user)
        
        # If multiple users have circular pattern, flag it
        if len(circular_users) >= 2:
            patterns.append(trading_pairs)
        
        return patterns
    
    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert score to risk level"""
        if score >= 80:
            return RiskLevel.HIGH
        elif score >= 50:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def calculate_wash_trading_probability(self, trades: pd.DataFrame, user_id: str) -> float:
        """
        Calculate wash trading probability score for a user
        
        Args:
            trades: Trade data
            user_id: User to analyze
            
        Returns:
            Probability score (0-1)
        """
        user_trades = trades[trades['user_id'] == user_id]
        
        if len(user_trades) < 2:
            return 0.0
        
        # Calculate various indicators
        indicators = []
        
        # 1. Buy-sell balance (perfect balance is suspicious)
        buy_count = len(user_trades[user_trades['trade_type'] == 'BUY'])
        sell_count = len(user_trades[user_trades['trade_type'] == 'SELL'])
        total = buy_count + sell_count
        
        if total > 0:
            balance_score = 1 - abs(buy_count - sell_count) / total
            indicators.append(balance_score)
        
        # 2. Price consistency (trading at same prices)
        price_std = user_trades.groupby('symbol')['price'].std().mean()
        price_mean = user_trades.groupby('symbol')['price'].mean().mean()
        
        if price_mean > 0:
            price_consistency = 1 - min(1, price_std / price_mean)
            indicators.append(price_consistency)
        
        # 3. Volume consistency
        volume_std = user_trades['volume'].std()
        volume_mean = user_trades['volume'].mean()
        
        if volume_mean > 0:
            volume_consistency = 1 - min(1, volume_std / volume_mean)
            indicators.append(volume_consistency)
        
        # 4. Rapid round-trips
        user_trades_sorted = user_trades.sort_values('timestamp')
        rapid_roundtrips = 0
        
        for i in range(len(user_trades_sorted) - 1):
            if (user_trades_sorted.iloc[i]['trade_type'] != user_trades_sorted.iloc[i+1]['trade_type']):
                time_diff = (user_trades_sorted.iloc[i+1]['timestamp'] - 
                           user_trades_sorted.iloc[i]['timestamp']).total_seconds()
                if time_diff < self.time_window_seconds:
                    rapid_roundtrips += 1
        
        if len(user_trades_sorted) > 1:
            roundtrip_score = rapid_roundtrips / (len(user_trades_sorted) - 1)
            indicators.append(roundtrip_score)
        
        # Average all indicators
        if indicators:
            return np.mean(indicators)
        else:
            return 0.0
    
    def get_pattern_type(self) -> PatternType:
        """Get pattern type this detector identifies"""
        return PatternType.WASH_TRADING
