"""
Order Book Monitor

Monitors order book depth for manipulation patterns including:
- Spoofing (fake orders)
- Layering
- Order book imbalance
- Spread manipulation
- Wash trading indicators
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.core.base import RiskLevel


logger = get_logger(__name__)


class OrderBookAnomalyType(Enum):
    """Types of order book anomalies"""
    SPOOFING = "spoofing"
    LAYERING = "layering"
    IMBALANCE = "imbalance"
    SPREAD_MANIPULATION = "spread_manipulation"
    WASH_TRADING_INDICATOR = "wash_trading_indicator"
    THIN_LIQUIDITY = "thin_liquidity"


@dataclass
class OrderBookLevel:
    """Single order book level"""
    price: float
    volume: float
    
    @property
    def value(self) -> float:
        """Total value at this level"""
        return self.price * self.volume


@dataclass
class OrderBookSnapshot:
    """Order book snapshot"""
    timestamp: datetime
    market: str
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    
    @property
    def best_bid(self) -> Optional[OrderBookLevel]:
        """Best bid price"""
        return self.bids[0] if self.bids else None
    
    @property
    def best_ask(self) -> Optional[OrderBookLevel]:
        """Best ask price"""
        return self.asks[0] if self.asks else None
    
    @property
    def spread(self) -> float:
        """Bid-ask spread"""
        if self.best_bid and self.best_ask:
            return self.best_ask.price - self.best_bid.price
        return 0
    
    @property
    def spread_pct(self) -> float:
        """Spread as percentage of mid price"""
        if self.best_bid and self.best_ask:
            mid_price = (self.best_bid.price + self.best_ask.price) / 2
            if mid_price > 0:
                return (self.spread / mid_price) * 100
        return 0
    
    @property
    def mid_price(self) -> float:
        """Mid price"""
        if self.best_bid and self.best_ask:
            return (self.best_bid.price + self.best_ask.price) / 2
        return 0
    
    @property
    def bid_volume(self) -> float:
        """Total bid volume"""
        return sum(level.volume for level in self.bids)
    
    @property
    def ask_volume(self) -> float:
        """Total ask volume"""
        return sum(level.volume for level in self.asks)
    
    @property
    def imbalance_ratio(self) -> float:
        """Order book imbalance ratio"""
        total = self.bid_volume + self.ask_volume
        if total > 0:
            return (self.bid_volume - self.ask_volume) / total
        return 0


@dataclass
class OrderBookAnomaly:
    """Detected order book anomaly"""
    anomaly_type: OrderBookAnomalyType
    market: str
    timestamp: datetime
    severity: float  # 0-100
    risk_level: RiskLevel
    description: str
    metrics: Dict[str, float]
    snapshot: OrderBookSnapshot


class OrderBookMonitor:
    """
    Monitors order book for manipulation patterns
    """
    
    def __init__(
        self,
        spoofing_threshold: float = 5.0,  # Volume ratio
        imbalance_threshold: float = 0.7,  # Imbalance ratio
        spread_threshold: float = 1.0,  # Spread percentage
        thin_liquidity_threshold: float = 1000.0,  # Min total volume
        layering_levels: int = 5  # Number of levels to check
    ):
        """
        Initialize order book monitor
        
        Args:
            spoofing_threshold: Threshold for spoofing detection
            imbalance_threshold: Threshold for imbalance detection
            spread_threshold: Threshold for spread manipulation
            thin_liquidity_threshold: Minimum liquidity threshold
            layering_levels: Number of levels to analyze for layering
        """
        self.spoofing_threshold = spoofing_threshold
        self.imbalance_threshold = imbalance_threshold
        self.spread_threshold = spread_threshold
        self.thin_liquidity_threshold = thin_liquidity_threshold
        self.layering_levels = layering_levels
        self.logger = logger
        
        # Historical snapshots for comparison
        self._history: List[OrderBookSnapshot] = []
        self._max_history = 100
    
    def analyze_orderbook(
        self,
        orderbook_data: Dict[str, Any],
        market: str
    ) -> List[OrderBookAnomaly]:
        """
        Analyze order book for anomalies
        
        Args:
            orderbook_data: Order book data from MCP
            market: Market symbol
            
        Returns:
            List of detected anomalies
        """
        # Parse order book
        snapshot = self._parse_orderbook(orderbook_data, market)
        
        if not snapshot:
            return []
        
        # Add to history
        self._add_to_history(snapshot)
        
        anomalies = []
        
        # Detect spoofing
        spoofing = self._detect_spoofing(snapshot)
        if spoofing:
            anomalies.append(spoofing)
        
        # Detect layering
        layering = self._detect_layering(snapshot)
        if layering:
            anomalies.append(layering)
        
        # Detect imbalance
        imbalance = self._detect_imbalance(snapshot)
        if imbalance:
            anomalies.append(imbalance)
        
        # Detect spread manipulation
        spread_manip = self._detect_spread_manipulation(snapshot)
        if spread_manip:
            anomalies.append(spread_manip)
        
        # Detect thin liquidity
        thin_liq = self._detect_thin_liquidity(snapshot)
        if thin_liq:
            anomalies.append(thin_liq)
        
        # Detect wash trading indicators
        wash_indicator = self._detect_wash_trading_indicator(snapshot)
        if wash_indicator:
            anomalies.append(wash_indicator)
        
        return anomalies
    
    def _parse_orderbook(
        self,
        data: Dict[str, Any],
        market: str
    ) -> Optional[OrderBookSnapshot]:
        """Parse order book data from MCP format"""
        try:
            bids = []
            asks = []
            
            # Parse bids
            for bid in data.get('bids', []):
                bids.append(OrderBookLevel(
                    price=float(bid[0]),
                    volume=float(bid[1])
                ))
            
            # Parse asks
            for ask in data.get('asks', []):
                asks.append(OrderBookLevel(
                    price=float(ask[0]),
                    volume=float(ask[1])
                ))
            
            return OrderBookSnapshot(
                timestamp=datetime.now(),
                market=market,
                bids=bids,
                asks=asks
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse order book: {e}")
            return None
    
    def _detect_spoofing(
        self,
        snapshot: OrderBookSnapshot
    ) -> Optional[OrderBookAnomaly]:
        """
        Detect spoofing (large fake orders)
        
        Spoofing is placing large orders with no intention to execute,
        to manipulate price perception
        """
        if len(snapshot.bids) < 3 or len(snapshot.asks) < 3:
            return None
        
        # Check for unusually large orders compared to nearby levels
        # Check bids
        bid_volumes = [level.volume for level in snapshot.bids[:5]]
        max_bid_volume = max(bid_volumes)
        avg_bid_volume = np.mean(bid_volumes[1:])  # Exclude the largest
        
        if avg_bid_volume > 0:
            bid_ratio = max_bid_volume / avg_bid_volume
            
            if bid_ratio > self.spoofing_threshold:
                severity = min(100, bid_ratio * 15)
                
                return OrderBookAnomaly(
                    anomaly_type=OrderBookAnomalyType.SPOOFING,
                    market=snapshot.market,
                    timestamp=datetime.now(),
                    severity=severity,
                    risk_level=self._calculate_risk_level(severity),
                    description=f"Potential spoofing detected on bid side: {bid_ratio:.2f}x average volume",
                    metrics={
                        'side': 'bid',
                        'volume_ratio': bid_ratio,
                        'max_volume': max_bid_volume,
                        'avg_volume': avg_bid_volume
                    },
                    snapshot=snapshot
                )
        
        # Check asks
        ask_volumes = [level.volume for level in snapshot.asks[:5]]
        max_ask_volume = max(ask_volumes)
        avg_ask_volume = np.mean(ask_volumes[1:])
        
        if avg_ask_volume > 0:
            ask_ratio = max_ask_volume / avg_ask_volume
            
            if ask_ratio > self.spoofing_threshold:
                severity = min(100, ask_ratio * 15)
                
                return OrderBookAnomaly(
                    anomaly_type=OrderBookAnomalyType.SPOOFING,
                    market=snapshot.market,
                    timestamp=datetime.now(),
                    severity=severity,
                    risk_level=self._calculate_risk_level(severity),
                    description=f"Potential spoofing detected on ask side: {ask_ratio:.2f}x average volume",
                    metrics={
                        'side': 'ask',
                        'volume_ratio': ask_ratio,
                        'max_volume': max_ask_volume,
                        'avg_volume': avg_ask_volume
                    },
                    snapshot=snapshot
                )
        
        return None
    
    def _detect_layering(
        self,
        snapshot: OrderBookSnapshot
    ) -> Optional[OrderBookAnomaly]:
        """
        Detect layering (multiple orders at different price levels)
        
        Layering is placing multiple orders at different price levels
        to create false impression of supply/demand
        """
        if len(snapshot.bids) < self.layering_levels or len(snapshot.asks) < self.layering_levels:
            return None
        
        # Check for uniform order sizes across multiple levels
        bid_volumes = [level.volume for level in snapshot.bids[:self.layering_levels]]
        ask_volumes = [level.volume for level in snapshot.asks[:self.layering_levels]]
        
        # Calculate coefficient of variation (lower = more uniform)
        bid_cv = np.std(bid_volumes) / np.mean(bid_volumes) if np.mean(bid_volumes) > 0 else 1
        ask_cv = np.std(ask_volumes) / np.mean(ask_volumes) if np.mean(ask_volumes) > 0 else 1
        
        # Layering typically has very uniform order sizes
        if bid_cv < 0.2 or ask_cv < 0.2:
            side = 'bid' if bid_cv < ask_cv else 'ask'
            cv = min(bid_cv, ask_cv)
            severity = min(100, (1 - cv) * 100)
            
            return OrderBookAnomaly(
                anomaly_type=OrderBookAnomalyType.LAYERING,
                market=snapshot.market,
                timestamp=datetime.now(),
                severity=severity,
                risk_level=self._calculate_risk_level(severity),
                description=f"Potential layering detected on {side} side: uniform orders across {self.layering_levels} levels",
                metrics={
                    'side': side,
                    'coefficient_of_variation': cv,
                    'levels_analyzed': self.layering_levels
                },
                snapshot=snapshot
            )
        
        return None
    
    def _detect_imbalance(
        self,
        snapshot: OrderBookSnapshot
    ) -> Optional[OrderBookAnomaly]:
        """Detect order book imbalance"""
        imbalance = abs(snapshot.imbalance_ratio)
        
        if imbalance > self.imbalance_threshold:
            severity = min(100, imbalance * 100)
            side = 'bid' if snapshot.imbalance_ratio > 0 else 'ask'
            
            return OrderBookAnomaly(
                anomaly_type=OrderBookAnomalyType.IMBALANCE,
                market=snapshot.market,
                timestamp=datetime.now(),
                severity=severity,
                risk_level=self._calculate_risk_level(severity),
                description=f"Significant order book imbalance: {imbalance:.2%} towards {side} side",
                metrics={
                    'imbalance_ratio': snapshot.imbalance_ratio,
                    'bid_volume': snapshot.bid_volume,
                    'ask_volume': snapshot.ask_volume,
                    'dominant_side': side
                },
                snapshot=snapshot
            )
        
        return None
    
    def _detect_spread_manipulation(
        self,
        snapshot: OrderBookSnapshot
    ) -> Optional[OrderBookAnomaly]:
        """Detect spread manipulation"""
        spread_pct = snapshot.spread_pct
        
        if spread_pct > self.spread_threshold:
            severity = min(100, spread_pct * 50)
            
            return OrderBookAnomaly(
                anomaly_type=OrderBookAnomalyType.SPREAD_MANIPULATION,
                market=snapshot.market,
                timestamp=datetime.now(),
                severity=severity,
                risk_level=self._calculate_risk_level(severity),
                description=f"Abnormally wide spread: {spread_pct:.3f}%",
                metrics={
                    'spread': snapshot.spread,
                    'spread_pct': spread_pct,
                    'best_bid': snapshot.best_bid.price if snapshot.best_bid else 0,
                    'best_ask': snapshot.best_ask.price if snapshot.best_ask else 0
                },
                snapshot=snapshot
            )
        
        return None
    
    def _detect_thin_liquidity(
        self,
        snapshot: OrderBookSnapshot
    ) -> Optional[OrderBookAnomaly]:
        """Detect thin liquidity (easy to manipulate)"""
        total_volume = snapshot.bid_volume + snapshot.ask_volume
        
        if total_volume < self.thin_liquidity_threshold:
            severity = min(100, (1 - total_volume / self.thin_liquidity_threshold) * 100)
            
            return OrderBookAnomaly(
                anomaly_type=OrderBookAnomalyType.THIN_LIQUIDITY,
                market=snapshot.market,
                timestamp=datetime.now(),
                severity=severity,
                risk_level=self._calculate_risk_level(severity),
                description=f"Thin liquidity detected: {total_volume:.2f} total volume",
                metrics={
                    'total_volume': total_volume,
                    'bid_volume': snapshot.bid_volume,
                    'ask_volume': snapshot.ask_volume,
                    'threshold': self.thin_liquidity_threshold
                },
                snapshot=snapshot
            )
        
        return None
    
    def _detect_wash_trading_indicator(
        self,
        snapshot: OrderBookSnapshot
    ) -> Optional[OrderBookAnomaly]:
        """
        Detect indicators of wash trading
        
        Wash trading indicators in order book:
        - Matching orders on both sides at same price levels
        - Symmetric order book
        """
        if len(snapshot.bids) < 5 or len(snapshot.asks) < 5:
            return None
        
        # Check for matching volumes at similar price distances
        bid_volumes = [level.volume for level in snapshot.bids[:5]]
        ask_volumes = [level.volume for level in snapshot.asks[:5]]
        
        # Calculate similarity
        similarity = 0
        for i in range(min(len(bid_volumes), len(ask_volumes))):
            if bid_volumes[i] > 0 and ask_volumes[i] > 0:
                ratio = min(bid_volumes[i], ask_volumes[i]) / max(bid_volumes[i], ask_volumes[i])
                similarity += ratio
        
        similarity /= min(len(bid_volumes), len(ask_volumes))
        
        # High similarity might indicate wash trading setup
        if similarity > 0.8:
            severity = min(100, similarity * 80)
            
            return OrderBookAnomaly(
                anomaly_type=OrderBookAnomalyType.WASH_TRADING_INDICATOR,
                market=snapshot.market,
                timestamp=datetime.now(),
                severity=severity,
                risk_level=self._calculate_risk_level(severity),
                description=f"Wash trading indicator: {similarity:.2%} order book symmetry",
                metrics={
                    'symmetry_score': similarity,
                    'bid_volumes': bid_volumes,
                    'ask_volumes': ask_volumes
                },
                snapshot=snapshot
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
    
    def _add_to_history(self, snapshot: OrderBookSnapshot) -> None:
        """Add snapshot to history"""
        self._history.append(snapshot)
        
        # Limit history size
        if len(self._history) > self._max_history:
            self._history.pop(0)
    
    def get_liquidity_metrics(
        self,
        snapshot: OrderBookSnapshot,
        depth_levels: int = 10
    ) -> Dict[str, float]:
        """
        Calculate liquidity metrics
        
        Args:
            snapshot: Order book snapshot
            depth_levels: Number of levels to analyze
            
        Returns:
            Liquidity metrics
        """
        bid_levels = snapshot.bids[:depth_levels]
        ask_levels = snapshot.asks[:depth_levels]
        
        # Total liquidity
        bid_liquidity = sum(level.value for level in bid_levels)
        ask_liquidity = sum(level.value for level in ask_levels)
        total_liquidity = bid_liquidity + ask_liquidity
        
        # Average order size
        avg_bid_size = np.mean([level.volume for level in bid_levels]) if bid_levels else 0
        avg_ask_size = np.mean([level.volume for level in ask_levels]) if ask_levels else 0
        
        # Depth (price range)
        bid_depth = bid_levels[0].price - bid_levels[-1].price if len(bid_levels) > 1 else 0
        ask_depth = ask_levels[-1].price - ask_levels[0].price if len(ask_levels) > 1 else 0
        
        return {
            'total_liquidity': total_liquidity,
            'bid_liquidity': bid_liquidity,
            'ask_liquidity': ask_liquidity,
            'avg_bid_size': avg_bid_size,
            'avg_ask_size': avg_ask_size,
            'bid_depth': bid_depth,
            'ask_depth': ask_depth,
            'spread': snapshot.spread,
            'spread_pct': snapshot.spread_pct,
            'imbalance_ratio': snapshot.imbalance_ratio
        }
