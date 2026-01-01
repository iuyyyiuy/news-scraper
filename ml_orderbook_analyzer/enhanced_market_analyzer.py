"""
Enhanced Market Analyzer with Volatility, Open Interest, and Volume
Comprehensive market analysis system that combines order book data with key market indicators
"""

import numpy as np
import pandas as pd
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import deque
import logging

# Import existing ML components
from btc_deep_analyzer import OrderBookSnapshot, MarketEvent, BTCOrderBookMLModel, BTCDataCollector

logger = logging.getLogger(__name__)

@dataclass
class MarketIndicators:
    """Market indicators for enhanced analysis"""
    timestamp: float
    price: float
    volume_24h: float
    volatility: float
    open_interest: Optional[float] = None
    funding_rate: Optional[float] = None
    volume_profile: Optional[Dict[str, float]] = None
    price_momentum: Optional[float] = None
    rsi: Optional[float] = None
    bollinger_bands: Optional[Dict[str, float]] = None

@dataclass
class EnhancedMarketSnapshot:
    """Enhanced snapshot combining order book and market indicators"""
    orderbook: OrderBookSnapshot
    indicators: MarketIndicators
    collection_priority: float  # 0-1 score for data collection priority
    prediction_confidence: float  # Expected ML prediction confidence

class MarketIndicatorCalculator:
    """Calculate various market indicators"""
    
    def __init__(self, lookback_periods: int = 100):
        self.lookback_periods = lookback_periods
        self.price_history = deque(maxlen=lookback_periods)
        self.volume_history = deque(maxlen=lookback_periods)
        self.oi_history = deque(maxlen=lookback_periods)
    
    def calculate_volatility(self, prices: List[float], period: int = 20) -> float:
        """Calculate price volatility (standard deviation of returns)"""
        if len(prices) < period:
            return 0.0
        
        returns = []
        for i in range(1, len(prices)):
            returns.append((prices[i] - prices[i-1]) / prices[i-1])
        
        if len(returns) < 2:
            return 0.0
        
        return np.std(returns[-period:]) * np.sqrt(24)  # Annualized volatility
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0  # Neutral RSI
        
        deltas = np.diff(prices[-period-1:])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            current_price = prices[-1] if prices else 0
            return {
                'upper': current_price * 1.02,
                'middle': current_price,
                'lower': current_price * 0.98,
                'bandwidth': 0.04
            }
        
        recent_prices = prices[-period:]
        middle = np.mean(recent_prices)
        std = np.std(recent_prices)
        
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        bandwidth = (upper - lower) / middle
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower,
            'bandwidth': bandwidth
        }
    
    def calculate_volume_profile(self, prices: List[float], volumes: List[float], bins: int = 10) -> Dict[str, float]:
        """Calculate volume profile"""
        if len(prices) != len(volumes) or len(prices) < bins:
            return {'high_volume_price': prices[-1] if prices else 0, 'volume_concentration': 0.5}
        
        # Create price bins
        price_min, price_max = min(prices), max(prices)
        price_range = price_max - price_min
        
        if price_range == 0:
            return {'high_volume_price': prices[-1], 'volume_concentration': 1.0}
        
        bin_size = price_range / bins
        volume_by_price = {}
        
        for price, volume in zip(prices, volumes):
            bin_index = min(int((price - price_min) / bin_size), bins - 1)
            bin_price = price_min + (bin_index + 0.5) * bin_size
            volume_by_price[bin_price] = volume_by_price.get(bin_price, 0) + volume
        
        # Find high volume price level
        high_volume_price = max(volume_by_price.items(), key=lambda x: x[1])[0]
        
        # Calculate volume concentration (how concentrated volume is)
        total_volume = sum(volume_by_price.values())
        max_volume = max(volume_by_price.values())
        concentration = max_volume / total_volume if total_volume > 0 else 0
        
        return {
            'high_volume_price': high_volume_price,
            'volume_concentration': concentration
        }

class EnhancedDataCollector:
    """Enhanced data collector with market indicators"""
    
    def __init__(self):
        self.indicator_calculator = MarketIndicatorCalculator()
        self.btc_collector = BTCDataCollector()
        self.collection_history = deque(maxlen=1000)
        
        # Collection strategy parameters
        self.min_volatility_threshold = 0.02  # 2% volatility
        self.high_volume_threshold = 1.5  # 1.5x average volume
        self.priority_score_threshold = 0.6  # Collect if priority > 0.6
        
    async def collect_enhanced_snapshot(self, mcp_client=None) -> Optional[EnhancedMarketSnapshot]:
        """Collect enhanced market snapshot with indicators"""
        try:
            # Get order book data
            orderbook_data = await self._get_orderbook_data(mcp_client)
            if not orderbook_data:
                return None
            
            # Get market indicators
            indicators = await self._get_market_indicators(mcp_client)
            if not indicators:
                return None
            
            # Create order book snapshot
            orderbook_snapshot = self._create_orderbook_snapshot(orderbook_data)
            
            # Calculate collection priority
            priority_score = self._calculate_collection_priority(indicators, orderbook_snapshot)
            
            # Estimate prediction confidence
            confidence_score = self._estimate_prediction_confidence(indicators, orderbook_snapshot)
            
            # Create enhanced snapshot
            enhanced_snapshot = EnhancedMarketSnapshot(
                orderbook=orderbook_snapshot,
                indicators=indicators,
                collection_priority=priority_score,
                prediction_confidence=confidence_score
            )
            
            # Store in history
            self.collection_history.append(enhanced_snapshot)
            
            return enhanced_snapshot
            
        except Exception as e:
            logger.error(f"Error collecting enhanced snapshot: {e}")
            return None
    
    async def _get_orderbook_data(self, mcp_client) -> Optional[Dict]:
        """Get order book data from CoinEx or simulate"""
        if mcp_client:
            try:
                response = await mcp_client.call_tool("mcp_coinex_get_orderbook", {
                    "base": "BTC",
                    "quote": "USDT",
                    "market_type": "futures",
                    "limit": 20
                })
                
                if response and response.get("code") == 0:
                    return response.get("data", {})
            except Exception as e:
                logger.warning(f"Failed to get real orderbook: {e}")
        
        # Simulate order book data
        return self._simulate_orderbook_data()
    
    async def _get_market_indicators(self, mcp_client) -> Optional[MarketIndicators]:
        """Get market indicators from CoinEx or simulate"""
        try:
            current_time = time.time()
            
            if mcp_client:
                # Get real market data
                ticker_data = await self._get_ticker_data(mcp_client)
                funding_data = await self._get_funding_data(mcp_client)
                kline_data = await self._get_kline_data(mcp_client)
                
                if ticker_data:
                    return self._create_indicators_from_real_data(
                        ticker_data, funding_data, kline_data, current_time
                    )
            
            # Simulate market indicators
            return self._simulate_market_indicators(current_time)
            
        except Exception as e:
            logger.error(f"Error getting market indicators: {e}")
            return self._simulate_market_indicators(time.time())
    
    async def _get_ticker_data(self, mcp_client) -> Optional[Dict]:
        """Get ticker data from CoinEx"""
        try:
            response = await mcp_client.call_tool("mcp_coinex_get_ticker", {
                "base": "BTC",
                "quote": "USDT",
                "market_type": "futures"
            })
            
            if response and response.get("code") == 0:
                return response.get("data", {})
        except Exception as e:
            logger.warning(f"Failed to get ticker data: {e}")
        
        return None
    
    async def _get_funding_data(self, mcp_client) -> Optional[Dict]:
        """Get funding rate data from CoinEx"""
        try:
            response = await mcp_client.call_tool("mcp_coinex_get_funding_rate", {
                "base": "BTC",
                "quote": "USDT"
            })
            
            if response and response.get("code") == 0:
                return response.get("data", {})
        except Exception as e:
            logger.warning(f"Failed to get funding data: {e}")
        
        return None
    
    async def _get_kline_data(self, mcp_client) -> Optional[Dict]:
        """Get K-line data for volatility calculation"""
        try:
            response = await mcp_client.call_tool("mcp_coinex_get_kline", {
                "base": "BTC",
                "quote": "USDT",
                "period": "1hour",
                "limit": 24,  # Last 24 hours
                "market_type": "futures"
            })
            
            if response and response.get("code") == 0:
                return response.get("data", {})
        except Exception as e:
            logger.warning(f"Failed to get kline data: {e}")
        
        return None
    
    def _create_indicators_from_real_data(self, ticker_data: Dict, funding_data: Optional[Dict], 
                                        kline_data: Optional[Dict], timestamp: float) -> MarketIndicators:
        """Create indicators from real CoinEx data"""
        
        # Extract price and volume from ticker
        price = float(ticker_data.get("last", 88000))
        volume_24h = float(ticker_data.get("vol", 1000000))
        
        # Calculate volatility from kline data
        volatility = 0.05  # Default 5%
        if kline_data and isinstance(kline_data, list):
            prices = [float(candle[4]) for candle in kline_data if len(candle) > 4]  # Close prices
            if len(prices) > 1:
                volatility = self.indicator_calculator.calculate_volatility(prices)
        
        # Extract funding rate
        funding_rate = None
        if funding_data:
            funding_rate = float(funding_data.get("funding_rate", 0))
        
        # Calculate additional indicators
        price_history = [price] + [p for p in self.indicator_calculator.price_history]
        rsi = self.indicator_calculator.calculate_rsi(price_history)
        bollinger_bands = self.indicator_calculator.calculate_bollinger_bands(price_history)
        
        # Update history
        self.indicator_calculator.price_history.append(price)
        self.indicator_calculator.volume_history.append(volume_24h)
        
        return MarketIndicators(
            timestamp=timestamp,
            price=price,
            volume_24h=volume_24h,
            volatility=volatility,
            funding_rate=funding_rate,
            rsi=rsi,
            bollinger_bands=bollinger_bands,
            price_momentum=self._calculate_momentum(price_history)
        )
    
    def _simulate_market_indicators(self, timestamp: float) -> MarketIndicators:
        """Simulate market indicators for testing"""
        import random
        
        # Simulate realistic BTC market conditions
        base_price = 88000 + random.uniform(-2000, 2000)
        volume_24h = random.uniform(800000000, 1200000000)  # $800M - $1.2B
        volatility = random.uniform(0.02, 0.15)  # 2% - 15% volatility
        funding_rate = random.uniform(-0.01, 0.01)  # -1% to +1%
        
        # Add to history
        self.indicator_calculator.price_history.append(base_price)
        self.indicator_calculator.volume_history.append(volume_24h)
        
        # Calculate indicators
        price_history = list(self.indicator_calculator.price_history)
        rsi = self.indicator_calculator.calculate_rsi(price_history)
        bollinger_bands = self.indicator_calculator.calculate_bollinger_bands(price_history)
        volume_profile = self.indicator_calculator.calculate_volume_profile(
            price_history[-20:], list(self.indicator_calculator.volume_history)[-20:]
        )
        
        return MarketIndicators(
            timestamp=timestamp,
            price=base_price,
            volume_24h=volume_24h,
            volatility=volatility,
            funding_rate=funding_rate,
            volume_profile=volume_profile,
            price_momentum=self._calculate_momentum(price_history),
            rsi=rsi,
            bollinger_bands=bollinger_bands
        )
    
    def _calculate_momentum(self, prices: List[float], period: int = 10) -> float:
        """Calculate price momentum"""
        if len(prices) < period:
            return 0.0
        
        current_price = prices[-1]
        past_price = prices[-period]
        
        return (current_price - past_price) / past_price
    
    def _simulate_orderbook_data(self) -> Dict:
        """Simulate order book data"""
        import random
        
        base_price = 88000 + random.uniform(-1000, 1000)
        spread = random.uniform(0.5, 3.0)
        
        bids = []
        asks = []
        
        for i in range(20):
            bid_price = base_price - spread/2 - i * random.uniform(0.1, 1.0)
            bid_volume = random.uniform(0.1, 5.0)
            bids.append([str(bid_price), str(bid_volume)])
            
            ask_price = base_price + spread/2 + i * random.uniform(0.1, 1.0)
            ask_volume = random.uniform(0.1, 5.0)
            asks.append([str(ask_price), str(ask_volume)])
        
        return {
            "bids": bids,
            "asks": asks,
            "last": str(base_price),
            "updated_at": int(time.time() * 1000)
        }
    
    def _create_orderbook_snapshot(self, orderbook_data: Dict) -> OrderBookSnapshot:
        """Create order book snapshot from data"""
        bids = [(float(bid[0]), float(bid[1])) for bid in orderbook_data.get("bids", [])]
        asks = [(float(ask[0]), float(ask[1])) for ask in orderbook_data.get("asks", [])]
        
        if not bids or not asks:
            raise ValueError("Empty order book data")
        
        best_bid = bids[0][0]
        best_ask = asks[0][0]
        mid_price = (best_bid + best_ask) / 2
        spread = best_ask - best_bid
        
        bid_volume = sum(vol for _, vol in bids)
        ask_volume = sum(vol for _, vol in asks)
        imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume) if (bid_volume + ask_volume) > 0 else 0
        
        return OrderBookSnapshot(
            timestamp=time.time(),
            bids=bids,
            asks=asks,
            mid_price=mid_price,
            spread=spread,
            bid_volume=bid_volume,
            ask_volume=ask_volume,
            imbalance=imbalance
        )
    
    def _calculate_collection_priority(self, indicators: MarketIndicators, 
                                     orderbook: OrderBookSnapshot) -> float:
        """Calculate priority score for data collection (0-1)"""
        
        priority_factors = []
        
        # Factor 1: Volatility (higher volatility = higher priority)
        volatility_score = min(indicators.volatility / 0.1, 1.0)  # Normalize to 0-1
        priority_factors.append(('volatility', volatility_score, 0.3))
        
        # Factor 2: Volume (higher volume = higher priority)
        avg_volume = 1000000000  # $1B average
        volume_score = min(indicators.volume_24h / (avg_volume * 1.5), 1.0)
        priority_factors.append(('volume', volume_score, 0.25))
        
        # Factor 3: Order book imbalance (higher imbalance = higher priority)
        imbalance_score = abs(orderbook.imbalance)
        priority_factors.append(('imbalance', imbalance_score, 0.2))
        
        # Factor 4: Spread (wider spread = higher priority for manipulation detection)
        spread_bps = (orderbook.spread / orderbook.mid_price) * 10000
        spread_score = min(spread_bps / 50, 1.0)  # Normalize to 50 bps
        priority_factors.append(('spread', spread_score, 0.15))
        
        # Factor 5: RSI extremes (oversold/overbought = higher priority)
        rsi_extreme_score = 0
        if indicators.rsi:
            if indicators.rsi < 30 or indicators.rsi > 70:
                rsi_extreme_score = 1.0
            elif indicators.rsi < 40 or indicators.rsi > 60:
                rsi_extreme_score = 0.5
        priority_factors.append(('rsi_extreme', rsi_extreme_score, 0.1))
        
        # Calculate weighted priority score
        total_score = sum(score * weight for _, score, weight in priority_factors)
        
        return min(total_score, 1.0)
    
    def _estimate_prediction_confidence(self, indicators: MarketIndicators, 
                                      orderbook: OrderBookSnapshot) -> float:
        """Estimate expected ML prediction confidence"""
        
        confidence_factors = []
        
        # Factor 1: Data quality (complete indicators = higher confidence)
        data_completeness = 0.7  # Base score
        if indicators.funding_rate is not None:
            data_completeness += 0.1
        if indicators.volume_profile is not None:
            data_completeness += 0.1
        if indicators.bollinger_bands is not None:
            data_completeness += 0.1
        confidence_factors.append(data_completeness * 0.3)
        
        # Factor 2: Market conditions (clear trends = higher confidence)
        trend_clarity = 0.5  # Base score
        if indicators.rsi:
            if indicators.rsi < 25 or indicators.rsi > 75:
                trend_clarity = 0.9  # Very clear oversold/overbought
            elif indicators.rsi < 35 or indicators.rsi > 65:
                trend_clarity = 0.7  # Clear trend
        confidence_factors.append(trend_clarity * 0.4)
        
        # Factor 3: Volatility (moderate volatility = higher confidence)
        volatility_confidence = 1.0 - abs(indicators.volatility - 0.05) / 0.1
        volatility_confidence = max(0, min(volatility_confidence, 1.0))
        confidence_factors.append(volatility_confidence * 0.3)
        
        return sum(confidence_factors)
    
    def should_collect_data(self, enhanced_snapshot: EnhancedMarketSnapshot) -> bool:
        """Determine if data should be collected based on priority and indicators"""
        
        # Always collect if priority is high
        if enhanced_snapshot.collection_priority > self.priority_score_threshold:
            return True
        
        # Collect if volatility is high
        if enhanced_snapshot.indicators.volatility > self.min_volatility_threshold:
            return True
        
        # Collect if volume is unusually high
        avg_volume = np.mean(list(self.indicator_calculator.volume_history)) if self.indicator_calculator.volume_history else 1000000000
        if enhanced_snapshot.indicators.volume_24h > avg_volume * self.high_volume_threshold:
            return True
        
        # Collect if order book shows signs of manipulation
        if abs(enhanced_snapshot.orderbook.imbalance) > 0.6:
            return True
        
        return False
    
    def get_collection_summary(self) -> Dict:
        """Get summary of collection strategy and recent data"""
        if not self.collection_history:
            return {"message": "No collection history available"}
        
        recent_snapshots = list(self.collection_history)[-10:]
        
        avg_priority = np.mean([s.collection_priority for s in recent_snapshots])
        avg_confidence = np.mean([s.prediction_confidence for s in recent_snapshots])
        avg_volatility = np.mean([s.indicators.volatility for s in recent_snapshots])
        
        high_priority_count = sum(1 for s in recent_snapshots if s.collection_priority > 0.6)
        
        return {
            "total_snapshots": len(self.collection_history),
            "recent_snapshots": len(recent_snapshots),
            "average_priority": avg_priority,
            "average_confidence": avg_confidence,
            "average_volatility": avg_volatility,
            "high_priority_count": high_priority_count,
            "collection_rate": high_priority_count / len(recent_snapshots) if recent_snapshots else 0,
            "strategy_parameters": {
                "min_volatility_threshold": self.min_volatility_threshold,
                "high_volume_threshold": self.high_volume_threshold,
                "priority_score_threshold": self.priority_score_threshold
            }
        }