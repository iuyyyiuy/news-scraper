"""
Market Analyzer

Coordinates real-time market monitoring and generates alerts for potential manipulation.
Integrates K-line monitoring, order book analysis, and trade flow analysis.
"""

import asyncio
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.core.base import RiskLevel
from trade_risk_analyzer.market_monitoring.mcp_client import MCPClient, MCPConfig
from trade_risk_analyzer.market_monitoring.kline_monitor import KLineMonitor, PriceAnomaly
from trade_risk_analyzer.market_monitoring.orderbook_monitor import OrderBookMonitor, OrderBookAnomaly


logger = get_logger(__name__)


class MarketAlertType(Enum):
    """Types of market alerts"""
    PRICE_MANIPULATION = "price_manipulation"
    ORDER_BOOK_MANIPULATION = "orderbook_manipulation"
    VOLUME_ANOMALY = "volume_anomaly"
    LIQUIDITY_RISK = "liquidity_risk"
    MARKET_HEALTH = "market_health"


@dataclass
class MarketRiskIndicators:
    """Market risk indicators"""
    market: str
    timestamp: datetime
    health_score: float  # 0-100
    manipulation_risk: float  # 0-100
    liquidity_score: float  # 0-100
    volatility_score: float  # 0-100
    overall_risk_level: RiskLevel
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'market': self.market,
            'timestamp': self.timestamp.isoformat(),
            'health_score': self.health_score,
            'manipulation_risk': self.manipulation_risk,
            'liquidity_score': self.liquidity_score,
            'volatility_score': self.volatility_score,
            'overall_risk_level': self.overall_risk_level.value
        }


@dataclass
class MarketAlert:
    """Market manipulation alert"""
    alert_id: str
    alert_type: MarketAlertType
    market: str
    timestamp: datetime
    severity: float  # 0-100
    risk_level: RiskLevel
    title: str
    description: str
    indicators: MarketRiskIndicators
    evidence: Dict[str, Any]
    recommended_action: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'alert_type': self.alert_type.value,
            'market': self.market,
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity,
            'risk_level': self.risk_level.value,
            'title': self.title,
            'description': self.description,
            'indicators': self.indicators.to_dict(),
            'evidence': self.evidence,
            'recommended_action': self.recommended_action
        }


class MarketAnalyzer:
    """
    Real-time market analyzer
    
    Monitors markets for manipulation patterns using:
    - K-line (candlestick) analysis
    - Order book depth analysis
    - Trade flow analysis
    - Market microstructure analysis
    """
    
    def __init__(
        self,
        mcp_config: Optional[MCPConfig] = None,
        kline_monitor: Optional[KLineMonitor] = None,
        orderbook_monitor: Optional[OrderBookMonitor] = None
    ):
        """
        Initialize market analyzer
        
        Args:
            mcp_config: MCP client configuration
            kline_monitor: K-line monitor instance
            orderbook_monitor: Order book monitor instance
        """
        self.mcp_client = MCPClient(mcp_config or MCPConfig())
        self.kline_monitor = kline_monitor or KLineMonitor()
        self.orderbook_monitor = orderbook_monitor or OrderBookMonitor()
        self.logger = logger
        
        # Alert callbacks
        self._alert_callbacks: List[Callable[[MarketAlert], None]] = []
        
        # Monitoring state
        self._monitoring = False
        self._monitored_markets: List[str] = []
    
    async def start_monitoring(
        self,
        markets: List[str],
        interval_seconds: int = 60
    ) -> None:
        """
        Start continuous market monitoring
        
        Args:
            markets: List of markets to monitor (e.g., ["BTCUSDT", "ETHUSDT"])
            interval_seconds: Monitoring interval in seconds
        """
        self.logger.info(f"Starting market monitoring for {len(markets)} markets")
        
        # Connect to MCP server
        connected = await self.mcp_client.connect()
        if not connected:
            self.logger.error("Failed to connect to MCP server")
            return
        
        self._monitoring = True
        self._monitored_markets = markets
        
        try:
            while self._monitoring:
                # Analyze each market
                for market in markets:
                    try:
                        await self.analyze_market(market)
                    except Exception as e:
                        self.logger.error(f"Error analyzing {market}: {e}")
                
                # Wait for next interval
                await asyncio.sleep(interval_seconds)
                
        finally:
            await self.mcp_client.disconnect()
            self._monitoring = False
    
    def stop_monitoring(self) -> None:
        """Stop market monitoring"""
        self.logger.info("Stopping market monitoring")
        self._monitoring = False
    
    async def analyze_market(self, market: str) -> List[MarketAlert]:
        """
        Analyze a single market for manipulation
        
        Args:
            market: Market symbol (e.g., "BTCUSDT")
            
        Returns:
            List of generated alerts
        """
        self.logger.info(f"Analyzing market: {market}")
        
        alerts = []
        
        try:
            # Get market data
            kline_data = await self.mcp_client.get_kline(market, interval="1min", limit=100)
            orderbook_data = await self.mcp_client.get_orderbook(market, depth=20)
            ticker_data = await self.mcp_client.get_ticker(market)
            
            # Analyze K-line data
            if kline_data:
                price_anomalies = self.kline_monitor.analyze_klines(kline_data, market)
                
                for anomaly in price_anomalies:
                    alert = self._create_alert_from_price_anomaly(anomaly, ticker_data)
                    alerts.append(alert)
                    self._trigger_alert(alert)
            
            # Analyze order book
            if orderbook_data:
                orderbook_anomalies = self.orderbook_monitor.analyze_orderbook(orderbook_data, market)
                
                for anomaly in orderbook_anomalies:
                    alert = self._create_alert_from_orderbook_anomaly(anomaly, ticker_data)
                    alerts.append(alert)
                    self._trigger_alert(alert)
            
            # Calculate market risk indicators
            if kline_data and orderbook_data:
                indicators = self._calculate_risk_indicators(
                    market, kline_data, orderbook_data
                )
                
                # Generate health alert if needed
                if indicators.overall_risk_level in [RiskLevel.HIGH, RiskLevel.MEDIUM]:
                    health_alert = self._create_health_alert(indicators, ticker_data)
                    alerts.append(health_alert)
                    self._trigger_alert(health_alert)
            
        except Exception as e:
            self.logger.error(f"Error analyzing market {market}: {e}", exc_info=True)
        
        return alerts
    
    def add_alert_callback(self, callback: Callable[[MarketAlert], None]) -> None:
        """
        Add callback for alert notifications
        
        Args:
            callback: Callback function
        """
        self._alert_callbacks.append(callback)
        self.logger.info("Added alert callback")
    
    def _create_alert_from_price_anomaly(
        self,
        anomaly: PriceAnomaly,
        ticker_data: Optional[Dict[str, Any]]
    ) -> MarketAlert:
        """Create market alert from price anomaly"""
        # Calculate indicators
        indicators = MarketRiskIndicators(
            market=anomaly.market,
            timestamp=datetime.now(),
            health_score=max(0, 100 - anomaly.severity),
            manipulation_risk=anomaly.severity,
            liquidity_score=50,  # Default
            volatility_score=anomaly.metrics.get('volatility', 50),
            overall_risk_level=anomaly.risk_level
        )
        
        # Generate alert ID
        alert_id = f"market_{anomaly.market}_{int(datetime.now().timestamp())}"
        
        # Determine alert type
        alert_type = MarketAlertType.PRICE_MANIPULATION
        if anomaly.anomaly_type.value == "volume_spike":
            alert_type = MarketAlertType.VOLUME_ANOMALY
        
        # Create alert
        alert = MarketAlert(
            alert_id=alert_id,
            alert_type=alert_type,
            market=anomaly.market,
            timestamp=datetime.now(),
            severity=anomaly.severity,
            risk_level=anomaly.risk_level,
            title=f"{anomaly.anomaly_type.value.replace('_', ' ').title()} Detected",
            description=anomaly.description,
            indicators=indicators,
            evidence={
                'anomaly_type': anomaly.anomaly_type.value,
                'metrics': anomaly.metrics,
                'current_price': ticker_data.get('last', 0) if ticker_data else 0
            },
            recommended_action=self._get_recommended_action(anomaly.risk_level, alert_type)
        )
        
        return alert
    
    def _create_alert_from_orderbook_anomaly(
        self,
        anomaly: OrderBookAnomaly,
        ticker_data: Optional[Dict[str, Any]]
    ) -> MarketAlert:
        """Create market alert from order book anomaly"""
        # Calculate indicators
        snapshot = anomaly.snapshot
        liquidity_metrics = self.orderbook_monitor.get_liquidity_metrics(snapshot)
        
        indicators = MarketRiskIndicators(
            market=anomaly.market,
            timestamp=datetime.now(),
            health_score=max(0, 100 - anomaly.severity),
            manipulation_risk=anomaly.severity,
            liquidity_score=min(100, liquidity_metrics['total_liquidity'] / 1000),
            volatility_score=50,  # Default
            overall_risk_level=anomaly.risk_level
        )
        
        # Generate alert ID
        alert_id = f"market_{anomaly.market}_{int(datetime.now().timestamp())}"
        
        # Determine alert type
        alert_type = MarketAlertType.ORDER_BOOK_MANIPULATION
        if anomaly.anomaly_type.value == "thin_liquidity":
            alert_type = MarketAlertType.LIQUIDITY_RISK
        
        # Create alert
        alert = MarketAlert(
            alert_id=alert_id,
            alert_type=alert_type,
            market=anomaly.market,
            timestamp=datetime.now(),
            severity=anomaly.severity,
            risk_level=anomaly.risk_level,
            title=f"{anomaly.anomaly_type.value.replace('_', ' ').title()} Detected",
            description=anomaly.description,
            indicators=indicators,
            evidence={
                'anomaly_type': anomaly.anomaly_type.value,
                'metrics': anomaly.metrics,
                'liquidity_metrics': liquidity_metrics,
                'current_price': ticker_data.get('last', 0) if ticker_data else 0
            },
            recommended_action=self._get_recommended_action(anomaly.risk_level, alert_type)
        )
        
        return alert
    
    def _create_health_alert(
        self,
        indicators: MarketRiskIndicators,
        ticker_data: Optional[Dict[str, Any]]
    ) -> MarketAlert:
        """Create market health alert"""
        alert_id = f"health_{indicators.market}_{int(datetime.now().timestamp())}"
        
        # Determine severity
        severity = indicators.manipulation_risk
        
        # Create description
        description = f"Market health score: {indicators.health_score:.1f}/100. "
        if indicators.manipulation_risk > 70:
            description += "High manipulation risk detected. "
        if indicators.liquidity_score < 30:
            description += "Low liquidity. "
        if indicators.volatility_score > 70:
            description += "High volatility. "
        
        alert = MarketAlert(
            alert_id=alert_id,
            alert_type=MarketAlertType.MARKET_HEALTH,
            market=indicators.market,
            timestamp=datetime.now(),
            severity=severity,
            risk_level=indicators.overall_risk_level,
            title=f"Market Health Alert: {indicators.market}",
            description=description,
            indicators=indicators,
            evidence={
                'health_score': indicators.health_score,
                'manipulation_risk': indicators.manipulation_risk,
                'liquidity_score': indicators.liquidity_score,
                'volatility_score': indicators.volatility_score,
                'current_price': ticker_data.get('last', 0) if ticker_data else 0
            },
            recommended_action=self._get_recommended_action(indicators.overall_risk_level, MarketAlertType.MARKET_HEALTH)
        )
        
        return alert
    
    def _calculate_risk_indicators(
        self,
        market: str,
        kline_data: List[Dict[str, Any]],
        orderbook_data: Dict[str, Any]
    ) -> MarketRiskIndicators:
        """Calculate comprehensive risk indicators"""
        # Get health score from K-line
        health_data = self.kline_monitor.get_market_health_score(kline_data, market)
        health_score = health_data.get('health_score', 50)
        
        # Parse order book
        snapshot = self.orderbook_monitor._parse_orderbook(orderbook_data, market)
        
        # Get liquidity metrics
        if snapshot:
            liquidity_metrics = self.orderbook_monitor.get_liquidity_metrics(snapshot)
            liquidity_score = min(100, liquidity_metrics['total_liquidity'] / 1000)
        else:
            liquidity_score = 50
        
        # Calculate manipulation risk (inverse of health)
        manipulation_risk = 100 - health_score
        
        # Volatility score from health data
        volatility_score = health_data.get('metrics', {}).get('volatility_score', 50)
        
        # Overall risk level
        avg_risk = (manipulation_risk + (100 - liquidity_score) + (100 - volatility_score)) / 3
        
        if avg_risk >= 70:
            risk_level = RiskLevel.HIGH
        elif avg_risk >= 40:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return MarketRiskIndicators(
            market=market,
            timestamp=datetime.now(),
            health_score=health_score,
            manipulation_risk=manipulation_risk,
            liquidity_score=liquidity_score,
            volatility_score=volatility_score,
            overall_risk_level=risk_level
        )
    
    def _get_recommended_action(
        self,
        risk_level: RiskLevel,
        alert_type: MarketAlertType
    ) -> str:
        """Get recommended action based on risk level and alert type"""
        if risk_level == RiskLevel.HIGH:
            if alert_type == MarketAlertType.PRICE_MANIPULATION:
                return "URGENT: Investigate immediately. Potential price manipulation in progress. Consider halting trading."
            elif alert_type == MarketAlertType.ORDER_BOOK_MANIPULATION:
                return "URGENT: Review order book activity. Potential spoofing or layering detected. Monitor for order cancellations."
            elif alert_type == MarketAlertType.LIQUIDITY_RISK:
                return "URGENT: Market has thin liquidity and is vulnerable to manipulation. Increase monitoring frequency."
            else:
                return "URGENT: Manual review required. High risk of market manipulation detected."
        
        elif risk_level == RiskLevel.MEDIUM:
            return "Monitor closely. Suspicious activity detected that warrants further investigation."
        
        else:
            return "Continue monitoring. Minor anomaly detected."
    
    def _trigger_alert(self, alert: MarketAlert) -> None:
        """Trigger alert callbacks"""
        self.logger.info(
            f"Market alert: {alert.title} - {alert.market} "
            f"(severity: {alert.severity:.1f}, risk: {alert.risk_level.value})"
        )
        
        # Call all callbacks
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")
