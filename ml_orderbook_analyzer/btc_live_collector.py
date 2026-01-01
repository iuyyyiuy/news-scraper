"""
BTC Live Data Collector
Real-time BTC order book data collection with ML integration
"""

import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

# Import our ML components
from btc_deep_analyzer import (
    OrderBookSnapshot, MarketEvent, BTCOrderBookMLModel, 
    BTCDataCollector, OrderBookFeatureExtractor
)

# Import MCP client (if available)
try:
    from trade_risk_analyzer.market_monitoring.mcp_client import MCPClient, MCPConfig
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("⚠️  MCP client not available. Using simulated data.")

logger = logging.getLogger(__name__)

class BTCLiveCollector:
    """Live BTC order book data collector with ML analysis"""
    
    def __init__(self):
        self.data_collector = BTCDataCollector()
        self.ml_model = BTCOrderBookMLModel()
        self.feature_extractor = OrderBookFeatureExtractor()
        self.mcp_client = None
        
        # State tracking
        self.is_collecting = False
        self.collection_interval = 5  # seconds
        self.last_price = None
        self.price_history = []
        
        # ML training state
        self.training_data_count = 0
        self.last_training_time = 0
        self.min_training_samples = 100
        
        if HAS_MCP:
            self.mcp_client = MCPClient(MCPConfig())
    
    async def start_collection(self, interval: int = 5):
        """Start live data collection"""
        self.collection_interval = interval
        self.is_collecting = True
        
        logger.info(f"Starting BTC live data collection (interval: {interval}s)")
        
        if HAS_MCP and self.mcp_client:
            await self.mcp_client.connect()
        
        try:
            while self.is_collecting:
                await self._collect_snapshot()
                await asyncio.sleep(self.collection_interval)
        finally:
            if HAS_MCP and self.mcp_client:
                await self.mcp_client.disconnect()
    
    def stop_collection(self):
        """Stop data collection"""
        self.is_collecting = False
        logger.info("Stopped BTC data collection")
    
    async def _collect_snapshot(self):
        """Collect single order book snapshot"""
        try:
            # Get order book data
            if HAS_MCP and self.mcp_client:
                orderbook_data = await self._get_real_orderbook()
            else:
                orderbook_data = self._get_simulated_orderbook()
            
            if not orderbook_data:
                return
            
            # Create snapshot
            snapshot = self._create_snapshot(orderbook_data)
            
            # Store snapshot
            self.data_collector.store_snapshot(snapshot)
            
            # Update price history
            self._update_price_history(snapshot.mid_price)
            
            # Analyze with ML (if model is trained)
            await self._analyze_snapshot(snapshot)
            
            # Check if we should create a training event
            await self._maybe_create_training_event(snapshot)
            
            # Periodic model retraining
            await self._maybe_retrain_model()
            
            logger.debug(f"Collected snapshot: price=${snapshot.mid_price:.2f}, spread={snapshot.spread:.4f}")
            
        except Exception as e:
            logger.error(f"Error collecting snapshot: {e}")
    
    async def _get_real_orderbook(self) -> Optional[Dict]:
        """Get real order book data from CoinEx"""
        try:
            response = await self.mcp_client.call_tool("mcp_coinex_get_orderbook", {
                "base": "BTC",
                "quote": "USDT",
                "market_type": "futures",
                "limit": 20
            })
            
            if response and response.get("code") == 0:
                return response.get("data", {})
            
        except Exception as e:
            logger.warning(f"Failed to get real orderbook: {e}")
        
        return None
    
    def _get_simulated_orderbook(self) -> Dict:
        """Generate simulated order book data for testing"""
        import random
        
        # Simulate BTC price around current levels
        base_price = 88000 + random.uniform(-1000, 1000)
        spread = random.uniform(0.5, 2.0)
        
        # Generate bids and asks
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
    
    def _create_snapshot(self, orderbook_data: Dict) -> OrderBookSnapshot:
        """Create OrderBookSnapshot from raw data"""
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
    
    def _update_price_history(self, price: float):
        """Update price history for change calculations"""
        self.price_history.append((time.time(), price))
        
        # Keep only last hour of data
        cutoff_time = time.time() - 3600
        self.price_history = [(t, p) for t, p in self.price_history if t > cutoff_time]
        
        self.last_price = price
    
    async def _analyze_snapshot(self, snapshot: OrderBookSnapshot):
        """Analyze snapshot with ML model"""
        try:
            # Get recent snapshots for temporal features
            recent_snapshots = self.data_collector.get_recent_snapshots(20)
            
            if len(recent_snapshots) < 10:
                return  # Need more historical data
            
            # Try to load model if not already loaded
            if self.ml_model.model is None:
                if not self.ml_model.load_model():
                    return  # Model not trained yet
            
            # Make prediction
            prediction = self.ml_model.predict(snapshot, recent_snapshots)
            
            if "error" not in prediction:
                # Log interesting predictions
                if prediction["is_anomaly"] or prediction["confidence"] > 0.8:
                    logger.info(f"ML Prediction: {prediction['prediction_label']} "
                              f"(confidence: {prediction['confidence']:.2f}, "
                              f"anomaly: {prediction['is_anomaly']})")
                    
                    # Log top features
                    top_features = prediction.get("top_features", [])[:3]
                    if top_features:
                        features_str = ", ".join([f"{name}: {importance:.3f}" 
                                                for name, importance in top_features])
                        logger.info(f"Top features: {features_str}")
        
        except Exception as e:
            logger.error(f"Error in ML analysis: {e}")
    
    async def _maybe_create_training_event(self, snapshot: OrderBookSnapshot):
        """Create training event if conditions are met"""
        try:
            # Need at least 5 minutes of price history
            if len(self.price_history) < 60:  # 5 minutes at 5-second intervals
                return
            
            # Calculate price changes
            current_time = snapshot.timestamp
            
            # Find prices from 1 and 5 minutes ago
            price_1min_ago = self._get_price_at_time(current_time - 60)
            price_5min_ago = self._get_price_at_time(current_time - 300)
            
            if price_1min_ago is None or price_5min_ago is None:
                return
            
            price_change_1min = (snapshot.mid_price - price_1min_ago) / price_1min_ago
            price_change_5min = (snapshot.mid_price - price_5min_ago) / price_5min_ago
            
            # Extract features
            recent_snapshots = self.data_collector.get_recent_snapshots(20)
            features = self.feature_extractor.extract_features(snapshot, recent_snapshots)
            
            # Detect manipulation (simple heuristics for now)
            manipulation_detected = self._detect_manipulation_heuristic(
                price_change_1min, price_change_5min, features
            )
            
            event_type = self._classify_event_type(
                price_change_1min, price_change_5min, manipulation_detected, features
            )
            
            # Create and store training event
            event = MarketEvent(
                timestamp=snapshot.timestamp,
                features=features,
                price_change_1min=price_change_1min,
                price_change_5min=price_change_5min,
                manipulation_detected=manipulation_detected,
                event_type=event_type
            )
            
            self.data_collector.store_market_event(event)
            self.training_data_count += 1
            
            if manipulation_detected:
                logger.info(f"Detected {event_type} event: "
                          f"1min change: {price_change_1min:.3f}, "
                          f"5min change: {price_change_5min:.3f}")
        
        except Exception as e:
            logger.error(f"Error creating training event: {e}")
    
    def _get_price_at_time(self, target_time: float) -> Optional[float]:
        """Get price closest to target time"""
        if not self.price_history:
            return None
        
        # Find closest price
        closest_price = None
        min_diff = float('inf')
        
        for timestamp, price in self.price_history:
            diff = abs(timestamp - target_time)
            if diff < min_diff:
                min_diff = diff
                closest_price = price
        
        # Only return if within 30 seconds of target
        return closest_price if min_diff < 30 else None
    
    def _detect_manipulation_heuristic(self, price_change_1min: float, 
                                     price_change_5min: float, 
                                     features: Dict[str, float]) -> bool:
        """Simple heuristic manipulation detection"""
        
        # Large price movements
        if abs(price_change_1min) > 0.02 or abs(price_change_5min) > 0.05:  # 2% or 5%
            return True
        
        # Large order book imbalance
        if abs(features.get('bid_ask_imbalance', 0)) > 0.7:
            return True
        
        # Unusual spread
        if features.get('spread_bps', 0) > 50:  # 5 bps
            return True
        
        # Large orders far from mid price
        if (features.get('large_bid_distance', 0) > 0.01 or 
            features.get('large_ask_distance', 0) > 0.01):
            return True
        
        return False
    
    def _classify_event_type(self, price_change_1min: float, 
                           price_change_5min: float,
                           manipulation_detected: bool,
                           features: Dict[str, float]) -> str:
        """Classify the type of market event"""
        
        if not manipulation_detected:
            return 'normal'
        
        # Pump detection
        if price_change_1min > 0.015 or price_change_5min > 0.03:
            return 'pump'
        
        # Dump detection
        if price_change_1min < -0.015 or price_change_5min < -0.03:
            return 'dump'
        
        # Spoofing detection (large orders, small price movement)
        if (features.get('large_bid_count', 0) > 2 or 
            features.get('large_ask_count', 0) > 2) and abs(price_change_1min) < 0.005:
            return 'spoofing'
        
        # Wash trading (high volume, low volatility)
        if (features.get('total_volume', 0) > 1000 and 
            abs(price_change_1min) < 0.002):
            return 'wash_trading'
        
        return 'manipulation'
    
    async def _maybe_retrain_model(self):
        """Retrain model if enough new data is available"""
        current_time = time.time()
        
        # Retrain every hour if we have enough data
        if (current_time - self.last_training_time > 3600 and 
            self.training_data_count >= self.min_training_samples):
            
            logger.info(f"Retraining ML model with {self.training_data_count} samples")
            
            try:
                # Get training data
                training_events = self.data_collector.get_training_events(1000)
                
                if len(training_events) >= self.min_training_samples:
                    # Train model
                    metrics = self.ml_model.train(training_events)
                    
                    logger.info(f"Model retrained - Accuracy: {metrics.get('accuracy', 0):.3f}, "
                              f"F1: {metrics.get('f1_score', 0):.3f}")
                    
                    self.last_training_time = current_time
                
            except Exception as e:
                logger.error(f"Error retraining model: {e}")
    
    def get_status(self) -> Dict:
        """Get collector status"""
        return {
            "is_collecting": self.is_collecting,
            "collection_interval": self.collection_interval,
            "training_data_count": self.training_data_count,
            "last_price": self.last_price,
            "price_history_length": len(self.price_history),
            "model_trained": self.ml_model.model is not None,
            "has_mcp": HAS_MCP
        }

# Standalone functions for easy testing
async def start_btc_collection(interval: int = 5, duration: int = 3600):
    """Start BTC data collection for specified duration"""
    collector = BTCLiveCollector()
    
    print(f"🚀 Starting BTC order book collection")
    print(f"   Interval: {interval} seconds")
    print(f"   Duration: {duration} seconds ({duration//60} minutes)")
    print(f"   MCP Available: {HAS_MCP}")
    
    # Start collection task
    collection_task = asyncio.create_task(collector.start_collection(interval))
    
    try:
        # Run for specified duration
        await asyncio.sleep(duration)
    except KeyboardInterrupt:
        print("\n⚠️  Collection interrupted by user")
    finally:
        collector.stop_collection()
        collection_task.cancel()
        
        # Wait for task to complete
        try:
            await collection_task
        except asyncio.CancelledError:
            pass
    
    # Print final status
    status = collector.get_status()
    print(f"\n📊 Collection Summary:")
    print(f"   Training samples collected: {status['training_data_count']}")
    print(f"   Final price: ${status['last_price']:.2f}" if status['last_price'] else "   No price data")
    print(f"   Model trained: {status['model_trained']}")

if __name__ == "__main__":
    # Run collection for 1 hour
    asyncio.run(start_btc_collection(interval=5, duration=3600))