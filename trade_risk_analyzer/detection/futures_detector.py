"""
Futures-Specific Detection Patterns

Detects manipulation patterns specific to futures markets including:
- Funding rate manipulation
- Liquidation hunting
- Basis manipulation
- Position concentration risks
"""

import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.core.base import RiskLevel


logger = get_logger(__name__)


@dataclass
class FuturesAlert:
    """Futures market alert"""
    alert_id: str
    market: str
    timestamp: datetime
    pattern_type: str
    risk_level: RiskLevel
    anomaly_score: float
    explanation: str
    data: Dict[str, Any]


class FuturesDetector:
    """
    Detects futures-specific manipulation patterns
    
    Patterns detected:
    - Funding rate manipulation
    - Liquidation hunting
    - Basis manipulation
    - Position concentration
    - Funding rate farming
    """
    
    def __init__(
        self,
        funding_rate_std_threshold: float = 3.0,
        basis_anomaly_threshold: float = 0.02,
        liquidation_cascade_threshold: int = 5,
        position_concentration_threshold: float = 0.3,
        premium_deviation_threshold: float = 0.01
    ):
        """
        Initialize futures detector
        
        Args:
            funding_rate_std_threshold: Std deviations for funding rate anomaly
            basis_anomaly_threshold: Threshold for basis spread anomaly (2%)
            liquidation_cascade_threshold: Number of liquidations for cascade
            position_concentration_threshold: Threshold for position concentration (30%)
            premium_deviation_threshold: Threshold for mark-index deviation (1%)
        """
        self.funding_rate_std_threshold = funding_rate_std_threshold
        self.basis_anomaly_threshold = basis_anomaly_threshold
        self.liquidation_cascade_threshold = liquidation_cascade_threshold
        self.position_concentration_threshold = position_concentration_threshold
        self.premium_deviation_threshold = premium_deviation_threshold
        self.logger = logger
    
    def detect_funding_rate_manipulation(
        self,
        market: str,
        funding_history: List[Dict[str, Any]]
    ) -> Optional[FuturesAlert]:
        """
        Detect funding rate manipulation
        
        Patterns:
        - Abnormal funding rate spikes (>3 std deviations)
        - Sustained high rates (funding rate farming)
        
        Args:
            market: Market symbol
            funding_history: Historical funding rate data
            
        Returns:
            Alert if manipulation detected, None otherwise
        """
        if not funding_history or len(funding_history) < 10:
            return None
        
        try:
            # Extract funding rates
            rates = [float(f.get('funding_rate', 0)) for f in funding_history]
            
            # Calculate statistics
            mean_rate = np.mean(rates)
            std_rate = np.std(rates)
            recent_rate = rates[-1]
            
            # Check for abnormal spike
            if std_rate > 0:
                deviation = abs(recent_rate - mean_rate) / std_rate
                
                if deviation > self.funding_rate_std_threshold:
                    anomaly_score = min(100, 70 + deviation * 5)
                    
                    return FuturesAlert(
                        alert_id=f"funding_rate_{market}_{datetime.now().timestamp()}",
                        market=market,
                        timestamp=datetime.now(),
                        pattern_type="FUNDING_RATE_MANIPULATION",
                        risk_level=RiskLevel.HIGH if anomaly_score > 85 else RiskLevel.MEDIUM,
                        anomaly_score=anomaly_score,
                        explanation=f"Abnormal funding rate spike detected: {recent_rate:.6f} "
                                  f"({deviation:.2f} std deviations from mean)",
                        data={
                            'recent_rate': recent_rate,
                            'mean_rate': mean_rate,
                            'std_deviation': deviation,
                            'funding_history': funding_history[-10:]
                        }
                    )
            
            # Check for funding rate farming (sustained high rates)
            recent_rates = rates[-10:]
            high_rate_threshold = mean_rate + 2 * std_rate
            high_rate_count = sum(1 for r in recent_rates if r > high_rate_threshold)
            
            if high_rate_count >= 7:  # 70% of recent periods
                anomaly_score = 75 + (high_rate_count / len(recent_rates)) * 15
                
                return FuturesAlert(
                    alert_id=f"funding_farming_{market}_{datetime.now().timestamp()}",
                    market=market,
                    timestamp=datetime.now(),
                    pattern_type="FUNDING_RATE_FARMING",
                    risk_level=RiskLevel.MEDIUM,
                    anomaly_score=anomaly_score,
                    explanation=f"Sustained high funding rates detected: {high_rate_count}/10 periods above threshold",
                    data={
                        'high_rate_count': high_rate_count,
                        'threshold': high_rate_threshold,
                        'recent_rates': recent_rates
                    }
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting funding rate manipulation: {e}")
            return None
    
    def detect_liquidation_hunting(
        self,
        market: str,
        liquidations: List[Dict[str, Any]],
        orderbook: Optional[Dict[str, Any]] = None
    ) -> Optional[FuturesAlert]:
        """
        Detect liquidation hunting patterns
        
        Patterns:
        - Cascade liquidation events (5+ in 1 minute)
        - Large orders near liquidation levels
        
        Args:
            market: Market symbol
            liquidations: Recent liquidation events
            orderbook: Current order book (optional)
            
        Returns:
            Alert if liquidation hunting detected, None otherwise
        """
        if not liquidations:
            return None
        
        try:
            # Check for cascade liquidations
            now = datetime.now()
            recent_liquidations = []
            
            for liq in liquidations:
                timestamp = liq.get('timestamp')
                if isinstance(timestamp, str):
                    liq_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif isinstance(timestamp, datetime):
                    liq_time = timestamp
                else:
                    continue
                
                # Check if within last 5 minutes
                if (now - liq_time).total_seconds() <= 300:
                    recent_liquidations.append(liq)
            
            if len(recent_liquidations) >= self.liquidation_cascade_threshold:
                # Check if they occurred within 1 minute window
                sorted_liq = sorted(recent_liquidations, key=lambda x: x.get('timestamp', ''))
                
                for i in range(len(sorted_liq) - self.liquidation_cascade_threshold + 1):
                    window_liq = sorted_liq[i:i+self.liquidation_cascade_threshold]
                    first_time = datetime.fromisoformat(window_liq[0].get('timestamp', '').replace('Z', '+00:00'))
                    last_time = datetime.fromisoformat(window_liq[-1].get('timestamp', '').replace('Z', '+00:00'))
                    
                    if (last_time - first_time).total_seconds() <= 60:
                        # Cascade detected
                        total_volume = sum(float(liq.get('volume', 0)) for liq in window_liq)
                        anomaly_score = min(100, 85 + len(window_liq))
                        
                        return FuturesAlert(
                            alert_id=f"liquidation_cascade_{market}_{datetime.now().timestamp()}",
                            market=market,
                            timestamp=datetime.now(),
                            pattern_type="LIQUIDATION_CASCADE",
                            risk_level=RiskLevel.HIGH,
                            anomaly_score=anomaly_score,
                            explanation=f"Cascade liquidation detected: {len(window_liq)} liquidations "
                                      f"in 1 minute, total volume: {total_volume:.2f}",
                            data={
                                'liquidation_count': len(window_liq),
                                'total_volume': total_volume,
                                'liquidations': window_liq
                            }
                        )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting liquidation hunting: {e}")
            return None
    
    def detect_basis_manipulation(
        self,
        market: str,
        basis_history: List[Dict[str, Any]]
    ) -> Optional[FuturesAlert]:
        """
        Detect basis manipulation (abnormal futures-spot spread)
        
        Args:
            market: Market symbol
            basis_history: Historical basis data
            
        Returns:
            Alert if basis manipulation detected, None otherwise
        """
        if not basis_history or len(basis_history) < 5:
            return None
        
        try:
            # Extract basis rates
            basis_rates = [float(b.get('basis_rate', 0)) for b in basis_history]
            
            # Calculate statistics
            mean_basis = np.mean(basis_rates)
            std_basis = np.std(basis_rates)
            recent_basis = basis_rates[-1]
            
            # Check for abnormal basis spread
            if abs(recent_basis) > self.basis_anomaly_threshold:
                anomaly_score = min(100, 70 + abs(recent_basis) * 1000)
                
                return FuturesAlert(
                    alert_id=f"basis_manipulation_{market}_{datetime.now().timestamp()}",
                    market=market,
                    timestamp=datetime.now(),
                    pattern_type="BASIS_MANIPULATION",
                    risk_level=RiskLevel.HIGH if abs(recent_basis) > 0.03 else RiskLevel.MEDIUM,
                    anomaly_score=anomaly_score,
                    explanation=f"Abnormal basis spread detected: {recent_basis*100:.2f}% "
                              f"(threshold: {self.basis_anomaly_threshold*100:.2f}%)",
                    data={
                        'basis_rate': recent_basis,
                        'mean_basis': mean_basis,
                        'threshold': self.basis_anomaly_threshold,
                        'basis_history': basis_history[-10:]
                    }
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting basis manipulation: {e}")
            return None
    
    def detect_position_manipulation(
        self,
        market: str,
        position_tiers: List[Dict[str, Any]],
        current_oi: float
    ) -> Optional[FuturesAlert]:
        """
        Detect position concentration risks
        
        Args:
            market: Market symbol
            position_tiers: Position tier data
            current_oi: Current open interest
            
        Returns:
            Alert if position manipulation detected, None otherwise
        """
        if not position_tiers or current_oi <= 0:
            return None
        
        try:
            tiers = position_tiers.get('tiers', []) if isinstance(position_tiers, dict) else position_tiers
            
            if not tiers:
                return None
            
            # Check concentration in top tier
            max_position_tier1 = float(tiers[0].get('max_position', 0))
            concentration = max_position_tier1 / current_oi if current_oi > 0 else 0
            
            if concentration > self.position_concentration_threshold:
                anomaly_score = min(100, 70 + concentration * 50)
                
                return FuturesAlert(
                    alert_id=f"position_concentration_{market}_{datetime.now().timestamp()}",
                    market=market,
                    timestamp=datetime.now(),
                    pattern_type="POSITION_CONCENTRATION",
                    risk_level=RiskLevel.MEDIUM,
                    anomaly_score=anomaly_score,
                    explanation=f"High position concentration detected: {concentration*100:.1f}% "
                              f"in top tier (threshold: {self.position_concentration_threshold*100:.1f}%)",
                    data={
                        'concentration': concentration,
                        'max_position_tier1': max_position_tier1,
                        'current_oi': current_oi,
                        'threshold': self.position_concentration_threshold
                    }
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting position manipulation: {e}")
            return None
    
    def detect_forced_liquidations(
        self,
        market: str,
        liquidations: List[Dict[str, Any]],
        orderbook: Optional[Dict[str, Any]] = None
    ) -> Optional[FuturesAlert]:
        """
        Detect forced liquidation patterns
        
        Args:
            market: Market symbol
            liquidations: Recent liquidation events
            orderbook: Current order book
            
        Returns:
            Alert if forced liquidations detected, None otherwise
        """
        if not liquidations or len(liquidations) < 3:
            return None
        
        try:
            # Analyze liquidation patterns
            now = datetime.now()
            recent_liquidations = []
            
            for liq in liquidations:
                timestamp = liq.get('timestamp')
                if isinstance(timestamp, str):
                    liq_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif isinstance(timestamp, datetime):
                    liq_time = timestamp
                else:
                    continue
                
                if (now - liq_time).total_seconds() <= 600:  # Last 10 minutes
                    recent_liquidations.append(liq)
            
            if len(recent_liquidations) >= 3:
                # Check for coordinated liquidations (same side)
                sides = [liq.get('side') for liq in recent_liquidations]
                long_count = sides.count('LONG')
                short_count = sides.count('SHORT')
                
                # If >80% are same side, might be forced
                total = len(sides)
                max_side_pct = max(long_count, short_count) / total if total > 0 else 0
                
                if max_side_pct > 0.8:
                    dominant_side = 'LONG' if long_count > short_count else 'SHORT'
                    total_volume = sum(float(liq.get('volume', 0)) for liq in recent_liquidations)
                    
                    anomaly_score = min(100, 75 + max_side_pct * 20)
                    
                    return FuturesAlert(
                        alert_id=f"forced_liquidation_{market}_{datetime.now().timestamp()}",
                        market=market,
                        timestamp=datetime.now(),
                        pattern_type="FORCED_LIQUIDATION",
                        risk_level=RiskLevel.MEDIUM,
                        anomaly_score=anomaly_score,
                        explanation=f"Coordinated {dominant_side} liquidations detected: "
                                  f"{int(max_side_pct*100)}% same side, volume: {total_volume:.2f}",
                        data={
                            'dominant_side': dominant_side,
                            'side_percentage': max_side_pct,
                            'total_volume': total_volume,
                            'liquidation_count': len(recent_liquidations)
                        }
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting forced liquidations: {e}")
            return None
    
    def detect_all_patterns(
        self,
        market: str,
        funding_history: List[Dict[str, Any]],
        liquidations: List[Dict[str, Any]],
        basis_history: List[Dict[str, Any]],
        position_tiers: List[Dict[str, Any]],
        current_oi: float,
        orderbook: Optional[Dict[str, Any]] = None
    ) -> List[FuturesAlert]:
        """
        Detect all futures manipulation patterns
        
        Args:
            market: Market symbol
            funding_history: Historical funding rate data
            liquidations: Recent liquidation events
            basis_history: Historical basis data
            position_tiers: Position tier data
            current_oi: Current open interest
            orderbook: Current order book (optional)
            
        Returns:
            List of detected alerts
        """
        alerts = []
        
        # Funding rate manipulation
        alert = self.detect_funding_rate_manipulation(market, funding_history)
        if alert:
            alerts.append(alert)
        
        # Liquidation hunting
        alert = self.detect_liquidation_hunting(market, liquidations, orderbook)
        if alert:
            alerts.append(alert)
        
        # Basis manipulation
        alert = self.detect_basis_manipulation(market, basis_history)
        if alert:
            alerts.append(alert)
        
        # Position concentration
        alert = self.detect_position_manipulation(market, position_tiers, current_oi)
        if alert:
            alerts.append(alert)
        
        # Forced liquidations
        alert = self.detect_forced_liquidations(market, liquidations, orderbook)
        if alert:
            alerts.append(alert)
        
        return alerts
