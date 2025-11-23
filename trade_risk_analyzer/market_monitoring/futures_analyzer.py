"""
Futures Market Analyzer

Analyzes futures market data for manipulation patterns using real-time data
from the MCP client.
"""

import asyncio
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass

from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.core.base import RiskLevel
from trade_risk_analyzer.market_monitoring.mcp_client import MCPClient
from trade_risk_analyzer.detection.futures_detector import FuturesDetector, FuturesAlert


logger = get_logger(__name__)


class FuturesMarketAnalyzer:
    """
    Analyzes futures markets for manipulation patterns
    
    Integrates with MCP client to fetch real-time data and applies
    futures-specific detection algorithms.
    """
    
    def __init__(
        self,
        mcp_client: MCPClient,
        detector: Optional[FuturesDetector] = None
    ):
        """
        Initialize futures market analyzer
        
        Args:
            mcp_client: MCP client for fetching market data
            detector: Futures detector (creates default if not provided)
        """
        self.mcp_client = mcp_client
        self.detector = detector or FuturesDetector()
        self.logger = logger
        self._alert_callbacks: List[Callable[[FuturesAlert], None]] = []
    
    async def analyze_futures_market(
        self,
        market: str
    ) -> List[FuturesAlert]:
        """
        Analyze a futures market for manipulation patterns
        
        Args:
            market: Futures market symbol (e.g., "BTCUSDT")
            
        Returns:
            List of detected alerts
        """
        alerts = []
        
        try:
            self.logger.debug(f"Analyzing futures market: {market}")
            
            # Fetch all required data
            funding_history = await self.mcp_client.get_futures_funding_rate_history(market, limit=100)
            liquidations = await self.mcp_client.get_futures_liquidations(market, limit=100)
            basis_history = await self.mcp_client.get_futures_basis_history(market, limit=100)
            position_tiers = await self.mcp_client.get_futures_position_tiers(market)
            klines = await self.mcp_client.get_futures_kline(market, interval="1min", limit=100)
            orderbook = await self.mcp_client.get_futures_orderbook(market, depth=20)
            
            # Get current open interest from latest kline
            current_oi = 0
            if klines and len(klines) > 0:
                current_oi = float(klines[-1].get('open_interest', 0))
            
            # Run all detection patterns
            detected_alerts = self.detector.detect_all_patterns(
                market=market,
                funding_history=funding_history or [],
                liquidations=liquidations or [],
                basis_history=basis_history or [],
                position_tiers=position_tiers or [],
                current_oi=current_oi,
                orderbook=orderbook
            )
            
            # Process alerts
            for alert in detected_alerts:
                alerts.append(alert)
                self._trigger_callbacks(alert)
            
            if alerts:
                self.logger.info(f"Detected {len(alerts)} alerts for {market}")
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error analyzing futures market {market}: {e}", exc_info=True)
            return []
    
    async def analyze_funding_rate(
        self,
        market: str
    ) -> Optional[FuturesAlert]:
        """
        Analyze funding rate for a specific market
        
        Args:
            market: Futures market symbol
            
        Returns:
            Alert if manipulation detected, None otherwise
        """
        try:
            funding_history = await self.mcp_client.get_futures_funding_rate_history(market, limit=100)
            
            if not funding_history:
                return None
            
            return self.detector.detect_funding_rate_manipulation(market, funding_history)
            
        except Exception as e:
            self.logger.error(f"Error analyzing funding rate for {market}: {e}")
            return None
    
    async def analyze_liquidations(
        self,
        market: str
    ) -> Optional[FuturesAlert]:
        """
        Analyze liquidations for a specific market
        
        Args:
            market: Futures market symbol
            
        Returns:
            Alert if liquidation hunting detected, None otherwise
        """
        try:
            liquidations = await self.mcp_client.get_futures_liquidations(market, limit=100)
            orderbook = await self.mcp_client.get_futures_orderbook(market, depth=20)
            
            if not liquidations:
                return None
            
            return self.detector.detect_liquidation_hunting(market, liquidations, orderbook)
            
        except Exception as e:
            self.logger.error(f"Error analyzing liquidations for {market}: {e}")
            return None
    
    async def analyze_basis(
        self,
        market: str
    ) -> Optional[FuturesAlert]:
        """
        Analyze basis spread for a specific market
        
        Args:
            market: Futures market symbol
            
        Returns:
            Alert if basis manipulation detected, None otherwise
        """
        try:
            basis_history = await self.mcp_client.get_futures_basis_history(market, limit=100)
            
            if not basis_history:
                return None
            
            return self.detector.detect_basis_manipulation(market, basis_history)
            
        except Exception as e:
            self.logger.error(f"Error analyzing basis for {market}: {e}")
            return None
    
    async def get_market_health(
        self,
        market: str
    ) -> Dict[str, Any]:
        """
        Get overall health metrics for a futures market
        
        Args:
            market: Futures market symbol
            
        Returns:
            Dictionary of health metrics
        """
        try:
            # Fetch current data
            ticker = await self.mcp_client.get_futures_ticker(market)
            funding_rate = await self.mcp_client.get_futures_funding_rate(market)
            premium_index = await self.mcp_client.get_futures_premium_index(market)
            liquidations = await self.mcp_client.get_futures_liquidations(market, limit=10)
            
            # Calculate health metrics
            health = {
                'market': market,
                'timestamp': datetime.now().isoformat(),
                'price': float(ticker.get('last_price', 0)) if ticker else 0,
                'volume_24h': float(ticker.get('volume_24h', 0)) if ticker else 0,
                'open_interest': float(ticker.get('open_interest', 0)) if ticker else 0,
                'funding_rate': float(funding_rate.get('funding_rate', 0)) if funding_rate else 0,
                'premium_rate': float(premium_index.get('premium_rate', 0)) if premium_index else 0,
                'recent_liquidations': len(liquidations) if liquidations else 0,
                'health_score': 100  # Default healthy
            }
            
            # Adjust health score based on metrics
            if abs(health['funding_rate']) > 0.001:  # 0.1%
                health['health_score'] -= 20
            
            if abs(health['premium_rate']) > 0.01:  # 1%
                health['health_score'] -= 15
            
            if health['recent_liquidations'] > 5:
                health['health_score'] -= 25
            
            health['health_score'] = max(0, health['health_score'])
            
            return health
            
        except Exception as e:
            self.logger.error(f"Error getting market health for {market}: {e}")
            return {
                'market': market,
                'error': str(e),
                'health_score': 0
            }
    
    def add_alert_callback(self, callback: Callable[[FuturesAlert], None]) -> None:
        """
        Add callback for alert notifications
        
        Args:
            callback: Callback function to call when alert is generated
        """
        self._alert_callbacks.append(callback)
        self.logger.info("Added alert callback")
    
    def remove_alert_callback(self, callback: Callable[[FuturesAlert], None]) -> None:
        """
        Remove alert callback
        
        Args:
            callback: Callback function to remove
        """
        if callback in self._alert_callbacks:
            self._alert_callbacks.remove(callback)
            self.logger.info("Removed alert callback")
    
    def _trigger_callbacks(self, alert: FuturesAlert) -> None:
        """
        Trigger all registered callbacks with the alert
        
        Args:
            alert: Alert to send to callbacks
        """
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")
