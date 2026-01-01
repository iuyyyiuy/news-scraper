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

    async def detect_manipulation_patterns(
        self,
        market_symbol: str,
        ticker_data: Dict[str, Any],
        orderbook_data: Dict[str, Any],
        klines: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect manipulation patterns in market data
        
        Args:
            market_symbol: Market symbol (e.g., "BTC/USDT")
            ticker_data: Ticker data from API
            orderbook_data: Order book data
            klines: K-line/candlestick data
            
        Returns:
            List of manipulation signals
        """
        signals = []
        
        try:
            # 1. Pump and Dump Detection
            if klines and len(klines) >= 10:
                prices = [float(k.get('close', 0)) for k in klines[-10:]]
                volumes = [float(k.get('volume', 0)) for k in klines[-10:]]
                
                if len(prices) >= 5 and len(volumes) >= 5:
                    # Check for rapid price increase with volume spike
                    recent_prices = prices[-5:]
                    recent_volumes = volumes[-5:]
                    
                    price_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
                    avg_volume = sum(volumes[:-5]) / len(volumes[:-5]) if len(volumes) > 5 else 1
                    recent_avg_volume = sum(recent_volumes) / len(recent_volumes)
                    
                    volume_ratio = recent_avg_volume / avg_volume if avg_volume > 0 else 1
                    
                    if price_change > 15 and volume_ratio > 3:
                        signals.append({
                            "pattern_name": "疑似拉盘行为",
                            "description": f"价格快速上涨{price_change:.1f}%，成交量激增{volume_ratio:.1f}倍",
                            "severity": "high",
                            "metrics": {
                                "价格涨幅": f"{price_change:.1f}%",
                                "成交量倍数": f"{volume_ratio:.1f}x",
                                "检测周期": "5分钟"
                            },
                            "analysis": "检测到典型的拉盘模式：价格快速上涨伴随成交量异常放大，可能存在人为操纵。"
                        })
                    
                    elif price_change < -15 and volume_ratio > 3:
                        signals.append({
                            "pattern_name": "疑似砸盘行为",
                            "description": f"价格快速下跌{abs(price_change):.1f}%，成交量激增{volume_ratio:.1f}倍",
                            "severity": "high",
                            "metrics": {
                                "价格跌幅": f"{abs(price_change):.1f}%",
                                "成交量倍数": f"{volume_ratio:.1f}x",
                                "检测周期": "5分钟"
                            },
                            "analysis": "检测到典型的砸盘模式：价格快速下跌伴随成交量异常放大，可能存在恶意抛售。"
                        })
            
            # 2. Order Book Spoofing Detection
            if orderbook_data:
                bids = orderbook_data.get('bids', [])
                asks = orderbook_data.get('asks', [])
                
                if bids and asks and len(bids) >= 5 and len(asks) >= 5:
                    # Check for large orders far from market price
                    best_bid = float(bids[0][0])
                    best_ask = float(asks[0][0])
                    mid_price = (best_bid + best_ask) / 2
                    
                    # Look for unusually large orders
                    large_bid_orders = []
                    large_ask_orders = []
                    
                    for bid in bids[:10]:
                        price, volume = float(bid[0]), float(bid[1])
                        if volume > 1000000:  # Large order threshold (adjust based on market)
                            distance_pct = abs(price - mid_price) / mid_price * 100
                            if distance_pct > 2:  # More than 2% from mid price
                                large_bid_orders.append((price, volume, distance_pct))
                    
                    for ask in asks[:10]:
                        price, volume = float(ask[0]), float(ask[1])
                        if volume > 1000000:  # Large order threshold
                            distance_pct = abs(price - mid_price) / mid_price * 100
                            if distance_pct > 2:  # More than 2% from mid price
                                large_ask_orders.append((price, volume, distance_pct))
                    
                    if large_bid_orders or large_ask_orders:
                        total_large_orders = len(large_bid_orders) + len(large_ask_orders)
                        signals.append({
                            "pattern_name": "疑似订单欺骗",
                            "description": f"检测到{total_large_orders}个远离市价的大额订单",
                            "severity": "medium",
                            "metrics": {
                                "大额买单": len(large_bid_orders),
                                "大额卖单": len(large_ask_orders),
                                "市场中价": f"${mid_price:.4f}"
                            },
                            "analysis": "检测到远离市价的大额订单，可能是订单欺骗(Spoofing)行为，用于误导其他交易者。"
                        })
            
            # 3. Wash Trading Detection
            if klines and len(klines) >= 20:
                # Look for suspicious volume patterns
                volumes = [float(k.get('volume', 0)) for k in klines[-20:]]
                prices = [float(k.get('close', 0)) for k in klines[-20:]]
                
                if volumes and prices:
                    # Check for high volume with minimal price movement
                    price_volatility = max(prices) - min(prices)
                    avg_price = sum(prices) / len(prices)
                    price_volatility_pct = (price_volatility / avg_price) * 100 if avg_price > 0 else 0
                    
                    total_volume = sum(volumes)
                    avg_volume = total_volume / len(volumes)
                    
                    # High volume but low volatility might indicate wash trading
                    if price_volatility_pct < 2 and avg_volume > 500000:  # Adjust thresholds
                        signals.append({
                            "pattern_name": "疑似对敲交易",
                            "description": f"高成交量但价格波动极小({price_volatility_pct:.2f}%)",
                            "severity": "medium",
                            "metrics": {
                                "价格波动": f"{price_volatility_pct:.2f}%",
                                "平均成交量": f"{avg_volume:,.0f}",
                                "检测周期": "20分钟"
                            },
                            "analysis": "检测到高成交量但价格变化微小的模式，可能存在对敲交易(Wash Trading)以虚增交易量。"
                        })
            
            # 4. Front Running Detection (based on order book changes)
            if orderbook_data and ticker_data:
                # This would require historical order book data for proper detection
                # For now, we'll check for rapid spread changes
                bids = orderbook_data.get('bids', [])
                asks = orderbook_data.get('asks', [])
                
                if bids and asks:
                    best_bid = float(bids[0][0])
                    best_ask = float(asks[0][0])
                    spread = best_ask - best_bid
                    spread_pct = (spread / best_bid) * 100
                    
                    # Unusually wide spread might indicate front-running
                    if spread_pct > 0.5:  # 0.5% spread threshold
                        signals.append({
                            "pattern_name": "异常价差",
                            "description": f"买卖价差异常扩大至{spread_pct:.3f}%",
                            "severity": "low",
                            "metrics": {
                                "买卖价差": f"{spread_pct:.3f}%",
                                "最佳买价": f"${best_bid}",
                                "最佳卖价": f"${best_ask}"
                            },
                            "analysis": "检测到异常的买卖价差，可能存在抢跑交易(Front Running)或流动性操纵。"
                        })
            
        except Exception as e:
            self.logger.error(f"Error detecting manipulation patterns for {market_symbol}: {e}")
        
        return signals


# Create a simple alias for backward compatibility
FuturesAnalyzer = FuturesMarketAnalyzer
