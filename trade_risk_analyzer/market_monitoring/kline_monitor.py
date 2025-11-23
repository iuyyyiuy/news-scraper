"""
K-Line (Candlestick) Monitor

Monitors K-line data for price manipulation patterns including:
- Pump and dump schemes
- Price spoofing
- Abnormal volatility
- Coordinated price movements
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.core.base import RiskLevel


logger = get_logger(__name__)


class PriceAnomalyType(Enum):
    """Types of price anomalies"""
    PUMP_AND_DUMP = "pump_and_dump"
    ABNORMAL_VOLATILITY = "abnormal_volatility"
    PRICE_SPIKE = "price_spike"
    VOLUME_SPIKE = "volume_spike"
    COORDINATED_MOVEMENT = "coordinated_movement"
    SUSPICIOUS_PATTERN = "suspicious_pattern"


@dataclass
class KLineData:
    """K-line (candlestick) data point"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    market: str
    
    @property
    def body_size(self) -> float:
        """Size of candle body"""
        return abs(self.close - self.open)
    
    @property
    def upper_wick(self) -> float:
        """Upper wick size"""
        return self.high - max(self.open, self.close)
    
    @property
    def lower_wick(self) -> float:
        """Lower wick size"""
        return min(self.open, self.close) - self.low
    
    @property
    def is_bullish(self) -> bool:
        """Is bullish candle"""
        return self.close > self.open
    
    @property
    def price_change_pct(self) -> float:
        """Price change percentage"""
        if self.open == 0:
            return 0
        return ((self.close - self.open) / self.open) * 100


@dataclass
class PriceAnomaly:
    """Detected price anomaly"""
    anomaly_type: PriceAnomalyType
    market: str
    timestamp: datetime
    severity: float  # 0-100
    risk_level: RiskLevel
    description: str
    metrics: Dict[str, float]
    kline_data: List[KLineData]


class KLineMonitor:
    """
    Monitors K-line data for manipulation patterns
    """
    
    def __init__(
        self,
        pump_threshold: float = 10.0,  # % price increase
        dump_threshold: float = -10.0,  # % price decrease
        volatility_threshold: float = 5.0,  # Standard deviations
        volume_spike_threshold: float = 3.0,  # Multiplier
        window_size: int = 20  # Number of candles for analysis
    ):
        """
        Initialize K-line monitor
        
        Args:
            pump_threshold: Threshold for pump detection (%)
            dump_threshold: Threshold for dump detection (%)
            volatility_threshold: Volatility threshold (std devs)
            volume_spike_threshold: Volume spike threshold (multiplier)
            window_size: Analysis window size
        """
        self.pump_threshold = pump_threshold
        self.dump_threshold = dump_threshold
        self.volatility_threshold = volatility_threshold
        self.volume_spike_threshold = volume_spike_threshold
        self.window_size = window_size
        self.logger = logger
    
    def analyze_klines(
        self,
        klines: List[Dict[str, Any]],
        market: str
    ) -> List[PriceAnomaly]:
        """
        Analyze K-line data for anomalies
        
        Args:
            klines: List of K-line data from MCP
            market: Market symbol
            
        Returns:
            List of detected anomalies
        """
        if not klines or len(klines) < self.window_size:
            return []
        
        # Convert to KLineData objects
        kline_data = self._parse_klines(klines, market)
        
        anomalies = []
        
        # Detect pump and dump
        pump_dump = self._detect_pump_and_dump(kline_data)
        if pump_dump:
            anomalies.append(pump_dump)
        
        # Detect abnormal volatility
        volatility = self._detect_abnormal_volatility(kline_data)
        if volatility:
            anomalies.append(volatility)
        
        # Detect volume spikes
        volume_spike = self._detect_volume_spike(kline_data)
        if volume_spike:
            anomalies.append(volume_spike)
        
        # Detect price spikes
        price_spike = self._detect_price_spike(kline_data)
        if price_spike:
            anomalies.append(price_spike)
        
        # Detect coordinated movements
        coordinated = self._detect_coordinated_movement(kline_data)
        if coordinated:
            anomalies.append(coordinated)
        
        return anomalies
    
    def _parse_klines(
        self,
        klines: List[Dict[str, Any]],
        market: str
    ) -> List[KLineData]:
        """Parse K-line data from MCP format"""
        parsed = []
        
        for kline in klines:
            try:
                parsed.append(KLineData(
                    timestamp=datetime.fromtimestamp(kline.get('timestamp', 0) / 1000),
                    open=float(kline.get('open', 0)),
                    high=float(kline.get('high', 0)),
                    low=float(kline.get('low', 0)),
                    close=float(kline.get('close', 0)),
                    volume=float(kline.get('volume', 0)),
                    market=market
                ))
            except Exception as e:
                self.logger.error(f"Failed to parse K-line: {e}")
        
        return parsed
    
    def _detect_pump_and_dump(
        self,
        klines: List[KLineData]
    ) -> Optional[PriceAnomaly]:
        """Detect pump and dump patterns"""
        if len(klines) < 10:
            return None
        
        # Look for rapid price increase followed by rapid decrease
        recent = klines[-10:]
        
        # Calculate cumulative price changes
        price_changes = [k.price_change_pct for k in recent]
        cumulative_change = sum(price_changes)
        
        # Check for pump (rapid increase)
        max_increase = max(price_changes)
        if max_increase > self.pump_threshold:
            # Check if followed by dump
            pump_idx = price_changes.index(max_increase)
            if pump_idx < len(price_changes) - 2:
                subsequent_changes = price_changes[pump_idx + 1:]
                if any(change < self.dump_threshold for change in subsequent_changes):
                    # Pump and dump detected
                    severity = min(100, abs(max_increase) + abs(min(subsequent_changes)))
                    
                    return PriceAnomaly(
                        anomaly_type=PriceAnomalyType.PUMP_AND_DUMP,
                        market=klines[0].market,
                        timestamp=datetime.now(),
                        severity=severity,
                        risk_level=self._calculate_risk_level(severity),
                        description=f"Pump and dump detected: {max_increase:.2f}% pump followed by {min(subsequent_changes):.2f}% dump",
                        metrics={
                            'pump_pct': max_increase,
                            'dump_pct': min(subsequent_changes),
                            'cumulative_change': cumulative_change
                        },
                        kline_data=recent
                    )
        
        return None
    
    def _detect_abnormal_volatility(
        self,
        klines: List[KLineData]
    ) -> Optional[PriceAnomaly]:
        """Detect abnormal volatility"""
        if len(klines) < self.window_size:
            return None
        
        # Calculate price changes
        price_changes = [k.price_change_pct for k in klines[-self.window_size:]]
        
        # Calculate volatility (standard deviation)
        volatility = np.std(price_changes)
        mean_volatility = np.mean([abs(pc) for pc in price_changes])
        
        # Calculate z-score for recent volatility
        recent_volatility = np.std(price_changes[-5:])
        
        if volatility > 0:
            z_score = (recent_volatility - volatility) / volatility
            
            if z_score > self.volatility_threshold:
                severity = min(100, z_score * 20)
                
                return PriceAnomaly(
                    anomaly_type=PriceAnomalyType.ABNORMAL_VOLATILITY,
                    market=klines[0].market,
                    timestamp=datetime.now(),
                    severity=severity,
                    risk_level=self._calculate_risk_level(severity),
                    description=f"Abnormal volatility detected: {z_score:.2f} standard deviations above normal",
                    metrics={
                        'volatility': volatility,
                        'recent_volatility': recent_volatility,
                        'z_score': z_score
                    },
                    kline_data=klines[-10:]
                )
        
        return None
    
    def _detect_volume_spike(
        self,
        klines: List[KLineData]
    ) -> Optional[PriceAnomaly]:
        """Detect volume spikes"""
        if len(klines) < self.window_size:
            return None
        
        # Calculate average volume
        volumes = [k.volume for k in klines[-self.window_size:]]
        avg_volume = np.mean(volumes[:-1])  # Exclude most recent
        
        if avg_volume == 0:
            return None
        
        # Check recent volume
        recent_volume = klines[-1].volume
        volume_ratio = recent_volume / avg_volume
        
        if volume_ratio > self.volume_spike_threshold:
            severity = min(100, volume_ratio * 20)
            
            return PriceAnomaly(
                anomaly_type=PriceAnomalyType.VOLUME_SPIKE,
                market=klines[0].market,
                timestamp=datetime.now(),
                severity=severity,
                risk_level=self._calculate_risk_level(severity),
                description=f"Volume spike detected: {volume_ratio:.2f}x average volume",
                metrics={
                    'avg_volume': avg_volume,
                    'recent_volume': recent_volume,
                    'volume_ratio': volume_ratio
                },
                kline_data=klines[-10:]
            )
        
        return None
    
    def _detect_price_spike(
        self,
        klines: List[KLineData]
    ) -> Optional[PriceAnomaly]:
        """Detect sudden price spikes"""
        if len(klines) < 5:
            return None
        
        recent = klines[-5:]
        
        # Check for large single-candle moves
        for kline in recent:
            if abs(kline.price_change_pct) > self.pump_threshold:
                severity = min(100, abs(kline.price_change_pct) * 5)
                
                return PriceAnomaly(
                    anomaly_type=PriceAnomalyType.PRICE_SPIKE,
                    market=kline.market,
                    timestamp=datetime.now(),
                    severity=severity,
                    risk_level=self._calculate_risk_level(severity),
                    description=f"Price spike detected: {kline.price_change_pct:.2f}% in single candle",
                    metrics={
                        'price_change_pct': kline.price_change_pct,
                        'open': kline.open,
                        'close': kline.close,
                        'volume': kline.volume
                    },
                    kline_data=[kline]
                )
        
        return None
    
    def _detect_coordinated_movement(
        self,
        klines: List[KLineData]
    ) -> Optional[PriceAnomaly]:
        """Detect coordinated price movements"""
        if len(klines) < 10:
            return None
        
        recent = klines[-10:]
        
        # Check for unusual patterns
        # 1. All candles moving in same direction
        all_bullish = all(k.is_bullish for k in recent)
        all_bearish = all(not k.is_bullish for k in recent)
        
        if all_bullish or all_bearish:
            direction = "bullish" if all_bullish else "bearish"
            total_change = sum(k.price_change_pct for k in recent)
            
            if abs(total_change) > 15:  # Significant coordinated move
                severity = min(100, abs(total_change) * 3)
                
                return PriceAnomaly(
                    anomaly_type=PriceAnomalyType.COORDINATED_MOVEMENT,
                    market=klines[0].market,
                    timestamp=datetime.now(),
                    severity=severity,
                    risk_level=self._calculate_risk_level(severity),
                    description=f"Coordinated {direction} movement: {total_change:.2f}% over 10 candles",
                    metrics={
                        'direction': direction,
                        'total_change': total_change,
                        'candle_count': len(recent)
                    },
                    kline_data=recent
                )
        
        return None
    
    def _calculate_risk_level(self, severity: float) -> RiskLevel:
        """Calculate risk level from severity"""
        if severity >= 80:
            return RiskLevel.HIGH
        elif severity >= 50:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def get_market_health_score(
        self,
        klines: List[Dict[str, Any]],
        market: str
    ) -> Dict[str, Any]:
        """
        Calculate overall market health score
        
        Args:
            klines: K-line data
            market: Market symbol
            
        Returns:
            Health score and metrics
        """
        if not klines:
            return {'health_score': 0, 'status': 'unknown'}
        
        kline_data = self._parse_klines(klines, market)
        
        if len(kline_data) < self.window_size:
            return {'health_score': 50, 'status': 'insufficient_data'}
        
        # Calculate various health metrics
        price_changes = [k.price_change_pct for k in kline_data[-self.window_size:]]
        volumes = [k.volume for k in kline_data[-self.window_size:]]
        
        # Volatility score (lower is better)
        volatility = np.std(price_changes)
        volatility_score = max(0, 100 - (volatility * 10))
        
        # Volume consistency score
        volume_cv = np.std(volumes) / np.mean(volumes) if np.mean(volumes) > 0 else 0
        volume_score = max(0, 100 - (volume_cv * 100))
        
        # Price trend score (penalize extreme movements)
        trend = np.mean(price_changes)
        trend_score = max(0, 100 - (abs(trend) * 5))
        
        # Overall health score
        health_score = (volatility_score * 0.4 + volume_score * 0.3 + trend_score * 0.3)
        
        # Determine status
        if health_score >= 80:
            status = 'healthy'
        elif health_score >= 60:
            status = 'moderate'
        elif health_score >= 40:
            status = 'concerning'
        else:
            status = 'high_risk'
        
        return {
            'health_score': health_score,
            'status': status,
            'volatility': volatility,
            'volume_cv': volume_cv,
            'trend': trend,
            'metrics': {
                'volatility_score': volatility_score,
                'volume_score': volume_score,
                'trend_score': trend_score
            }
        }
