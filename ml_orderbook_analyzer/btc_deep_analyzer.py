"""
BTC Deep Order Book Analyzer with Machine Learning
Advanced ML system for analyzing BTC order book changes and predicting market movements
"""

import numpy as np
import pandas as pd
import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import deque
import logging

# ML imports
try:
    import tensorflow as tf
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix
    import joblib
    HAS_ML_LIBS = True
except ImportError:
    HAS_ML_LIBS = False
    print("⚠️  ML libraries not installed. Install with: pip install tensorflow scikit-learn")

logger = logging.getLogger(__name__)

@dataclass
class OrderBookSnapshot:
    """Single order book snapshot with timestamp"""
    timestamp: float
    bids: List[Tuple[float, float]]  # [(price, volume), ...]
    asks: List[Tuple[float, float]]  # [(price, volume), ...]
    mid_price: float
    spread: float
    bid_volume: float
    ask_volume: float
    imbalance: float

@dataclass
class MarketEvent:
    """Market event with features and label"""
    timestamp: float
    features: Dict[str, float]
    price_change_1min: float  # Target variable
    price_change_5min: float
    manipulation_detected: bool
    event_type: str  # 'normal', 'pump', 'dump', 'spoofing', 'wash_trading'

class OrderBookFeatureExtractor:
    """Extract sophisticated features from order book data"""
    
    def __init__(self, depth: int = 20):
        self.depth = depth
        
    def extract_features(self, snapshot: OrderBookSnapshot, 
                        historical_snapshots: List[OrderBookSnapshot]) -> Dict[str, float]:
        """Extract comprehensive features from order book snapshot"""
        
        features = {}
        
        # Basic features
        features.update(self._extract_basic_features(snapshot))
        
        # Volume profile features
        features.update(self._extract_volume_features(snapshot))
        
        # Spread and liquidity features
        features.update(self._extract_liquidity_features(snapshot))
        
        # Order book shape features
        features.update(self._extract_shape_features(snapshot))
        
        # Temporal features (if historical data available)
        if len(historical_snapshots) >= 10:
            features.update(self._extract_temporal_features(snapshot, historical_snapshots))
        
        # Microstructure features
        features.update(self._extract_microstructure_features(snapshot))
        
        return features
    
    def _extract_basic_features(self, snapshot: OrderBookSnapshot) -> Dict[str, float]:
        """Basic order book features"""
        return {
            'mid_price': snapshot.mid_price,
            'spread_bps': (snapshot.spread / snapshot.mid_price) * 10000,
            'bid_ask_imbalance': snapshot.imbalance,
            'total_bid_volume': snapshot.bid_volume,
            'total_ask_volume': snapshot.ask_volume,
            'total_volume': snapshot.bid_volume + snapshot.ask_volume
        }
    
    def _extract_volume_features(self, snapshot: OrderBookSnapshot) -> Dict[str, float]:
        """Volume-based features"""
        features = {}
        
        # Volume at different price levels
        bids = snapshot.bids[:self.depth]
        asks = snapshot.asks[:self.depth]
        
        if bids and asks:
            # Volume concentration
            top_5_bid_vol = sum(vol for _, vol in bids[:5])
            top_5_ask_vol = sum(vol for _, vol in asks[:5])
            
            features['top_5_bid_volume_ratio'] = top_5_bid_vol / snapshot.bid_volume if snapshot.bid_volume > 0 else 0
            features['top_5_ask_volume_ratio'] = top_5_ask_vol / snapshot.ask_volume if snapshot.ask_volume > 0 else 0
            
            # Volume weighted average price
            bid_vwap = sum(price * vol for price, vol in bids) / snapshot.bid_volume if snapshot.bid_volume > 0 else 0
            ask_vwap = sum(price * vol for price, vol in asks) / snapshot.ask_volume if snapshot.ask_volume > 0 else 0
            
            features['bid_vwap'] = bid_vwap
            features['ask_vwap'] = ask_vwap
            features['vwap_spread'] = ask_vwap - bid_vwap
            
            # Large order detection
            bid_volumes = [vol for _, vol in bids]
            ask_volumes = [vol for _, vol in asks]
            
            features['max_bid_volume'] = max(bid_volumes) if bid_volumes else 0
            features['max_ask_volume'] = max(ask_volumes) if ask_volumes else 0
            features['bid_volume_std'] = np.std(bid_volumes) if len(bid_volumes) > 1 else 0
            features['ask_volume_std'] = np.std(ask_volumes) if len(ask_volumes) > 1 else 0
        
        return features
    
    def _extract_liquidity_features(self, snapshot: OrderBookSnapshot) -> Dict[str, float]:
        """Liquidity and market depth features"""
        features = {}
        
        bids = snapshot.bids[:self.depth]
        asks = snapshot.asks[:self.depth]
        
        if bids and asks:
            # Price impact estimation
            cumulative_bid_vol = 0
            cumulative_ask_vol = 0
            
            for i, (price, vol) in enumerate(bids):
                cumulative_bid_vol += vol
                if cumulative_bid_vol >= 1000000:  # $1M impact
                    features['bid_1m_impact_bps'] = ((snapshot.mid_price - price) / snapshot.mid_price) * 10000
                    break
            else:
                features['bid_1m_impact_bps'] = 1000  # High impact if not enough liquidity
            
            for i, (price, vol) in enumerate(asks):
                cumulative_ask_vol += vol
                if cumulative_ask_vol >= 1000000:  # $1M impact
                    features['ask_1m_impact_bps'] = ((price - snapshot.mid_price) / snapshot.mid_price) * 10000
                    break
            else:
                features['ask_1m_impact_bps'] = 1000  # High impact if not enough liquidity
            
            # Liquidity density
            price_range_1pct = snapshot.mid_price * 0.01
            
            bid_liquidity_1pct = sum(vol for price, vol in bids 
                                   if price >= snapshot.mid_price - price_range_1pct)
            ask_liquidity_1pct = sum(vol for price, vol in asks 
                                   if price <= snapshot.mid_price + price_range_1pct)
            
            features['bid_liquidity_1pct'] = bid_liquidity_1pct
            features['ask_liquidity_1pct'] = ask_liquidity_1pct
            features['liquidity_imbalance_1pct'] = (bid_liquidity_1pct - ask_liquidity_1pct) / (bid_liquidity_1pct + ask_liquidity_1pct) if (bid_liquidity_1pct + ask_liquidity_1pct) > 0 else 0
        
        return features
    
    def _extract_shape_features(self, snapshot: OrderBookSnapshot) -> Dict[str, float]:
        """Order book shape and distribution features"""
        features = {}
        
        bids = snapshot.bids[:self.depth]
        asks = snapshot.asks[:self.depth]
        
        if bids and asks:
            # Price level gaps
            bid_gaps = [bids[i][0] - bids[i+1][0] for i in range(len(bids)-1)]
            ask_gaps = [asks[i+1][0] - asks[i][0] for i in range(len(asks)-1)]
            
            features['avg_bid_gap'] = np.mean(bid_gaps) if bid_gaps else 0
            features['avg_ask_gap'] = np.mean(ask_gaps) if ask_gaps else 0
            features['bid_gap_std'] = np.std(bid_gaps) if len(bid_gaps) > 1 else 0
            features['ask_gap_std'] = np.std(ask_gaps) if len(ask_gaps) > 1 else 0
            
            # Order book slope (price vs cumulative volume)
            bid_prices = [price for price, _ in bids]
            ask_prices = [price for price, _ in asks]
            bid_cumvol = np.cumsum([vol for _, vol in bids])
            ask_cumvol = np.cumsum([vol for _, vol in asks])
            
            if len(bid_prices) > 2:
                bid_slope = np.polyfit(bid_cumvol, bid_prices, 1)[0]
                features['bid_slope'] = bid_slope
            
            if len(ask_prices) > 2:
                ask_slope = np.polyfit(ask_cumvol, ask_prices, 1)[0]
                features['ask_slope'] = ask_slope
        
        return features
    
    def _extract_temporal_features(self, current: OrderBookSnapshot, 
                                 historical: List[OrderBookSnapshot]) -> Dict[str, float]:
        """Time-series features from historical snapshots"""
        features = {}
        
        # Recent price movements
        recent_prices = [snap.mid_price for snap in historical[-10:]]
        recent_spreads = [snap.spread for snap in historical[-10:]]
        recent_imbalances = [snap.imbalance for snap in historical[-10:]]
        
        # Price momentum
        if len(recent_prices) >= 5:
            features['price_momentum_5'] = (recent_prices[-1] - recent_prices[-5]) / recent_prices[-5]
            features['price_volatility_5'] = np.std(recent_prices[-5:]) / np.mean(recent_prices[-5:])
        
        # Spread dynamics
        if len(recent_spreads) >= 5:
            features['spread_momentum'] = recent_spreads[-1] - np.mean(recent_spreads[-5:])
            features['spread_volatility'] = np.std(recent_spreads[-5:])
        
        # Imbalance persistence
        if len(recent_imbalances) >= 5:
            features['imbalance_momentum'] = recent_imbalances[-1] - np.mean(recent_imbalances[-5:])
            features['imbalance_persistence'] = sum(1 for x in recent_imbalances[-5:] if x * recent_imbalances[-1] > 0) / 5
        
        # Volume flow
        recent_bid_vols = [snap.bid_volume for snap in historical[-5:]]
        recent_ask_vols = [snap.ask_volume for snap in historical[-5:]]
        
        if len(recent_bid_vols) >= 3:
            features['bid_volume_trend'] = np.polyfit(range(len(recent_bid_vols)), recent_bid_vols, 1)[0]
            features['ask_volume_trend'] = np.polyfit(range(len(recent_ask_vols)), recent_ask_vols, 1)[0]
        
        return features
    
    def _extract_microstructure_features(self, snapshot: OrderBookSnapshot) -> Dict[str, float]:
        """Microstructure and manipulation detection features"""
        features = {}
        
        bids = snapshot.bids[:self.depth]
        asks = snapshot.asks[:self.depth]
        
        if bids and asks:
            # Spoofing detection features
            # Large orders far from mid price
            large_order_threshold = np.percentile([vol for _, vol in bids + asks], 90)
            
            large_bids = [(price, vol) for price, vol in bids if vol > large_order_threshold]
            large_asks = [(price, vol) for price, vol in asks if vol > large_order_threshold]
            
            if large_bids:
                avg_large_bid_distance = np.mean([(snapshot.mid_price - price) / snapshot.mid_price for price, _ in large_bids])
                features['large_bid_distance'] = avg_large_bid_distance
                features['large_bid_count'] = len(large_bids)
            else:
                features['large_bid_distance'] = 0
                features['large_bid_count'] = 0
            
            if large_asks:
                avg_large_ask_distance = np.mean([(price - snapshot.mid_price) / snapshot.mid_price for price, _ in large_asks])
                features['large_ask_distance'] = avg_large_ask_distance
                features['large_ask_count'] = len(large_asks)
            else:
                features['large_ask_distance'] = 0
                features['large_ask_count'] = 0
            
            # Order clustering
            bid_price_clusters = self._detect_price_clusters([price for price, _ in bids])
            ask_price_clusters = self._detect_price_clusters([price for price, _ in asks])
            
            features['bid_price_clusters'] = len(bid_price_clusters)
            features['ask_price_clusters'] = len(ask_price_clusters)
            
            # Unusual volume patterns
            bid_volumes = [vol for _, vol in bids]
            ask_volumes = [vol for _, vol in asks]
            
            # Detect volume spikes
            if len(bid_volumes) > 5:
                bid_vol_median = np.median(bid_volumes)
                bid_vol_outliers = sum(1 for vol in bid_volumes if vol > bid_vol_median * 3)
                features['bid_volume_outliers'] = bid_vol_outliers
            
            if len(ask_volumes) > 5:
                ask_vol_median = np.median(ask_volumes)
                ask_vol_outliers = sum(1 for vol in ask_volumes if vol > ask_vol_median * 3)
                features['ask_volume_outliers'] = ask_vol_outliers
        
        return features
    
    def _detect_price_clusters(self, prices: List[float], threshold: float = 0.001) -> List[List[float]]:
        """Detect price clustering (potential coordination)"""
        if not prices:
            return []
        
        sorted_prices = sorted(prices)
        clusters = []
        current_cluster = [sorted_prices[0]]
        
        for i in range(1, len(sorted_prices)):
            if (sorted_prices[i] - sorted_prices[i-1]) / sorted_prices[i-1] < threshold:
                current_cluster.append(sorted_prices[i])
            else:
                if len(current_cluster) > 1:
                    clusters.append(current_cluster)
                current_cluster = [sorted_prices[i]]
        
        if len(current_cluster) > 1:
            clusters.append(current_cluster)
        
        return clusters

class BTCOrderBookMLModel:
    """Machine Learning model for BTC order book analysis"""
    
    def __init__(self, model_path: str = "models/btc_orderbook_model"):
        self.model_path = model_path
        # Use enhanced feature extractor for consistency
        try:
            from enhanced_feature_extractor import EnhancedFeatureExtractor
            self.feature_extractor = EnhancedFeatureExtractor()
            self.use_enhanced_features = True
        except ImportError:
            self.feature_extractor = OrderBookFeatureExtractor()
            self.use_enhanced_features = False
        
        self.scaler = StandardScaler()
        self.model = None
        self.anomaly_detector = None
        self.feature_names = []
        
        if HAS_ML_LIBS:
            self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models"""
        # Main prediction model (Random Forest for interpretability)
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        # Anomaly detection model
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42
        )
    
    def prepare_training_data(self, market_events: List[MarketEvent]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from market events"""
        if not market_events:
            return np.array([]), np.array([])
        
        # First pass: determine consistent feature set
        all_feature_names = set()
        for event in market_events:
            all_feature_names.update(event.features.keys())
        
        # Use enhanced feature names if available
        if self.use_enhanced_features:
            try:
                from enhanced_feature_extractor import EnhancedFeatureExtractor
                extractor = EnhancedFeatureExtractor()
                self.feature_names = extractor.feature_names
            except ImportError:
                self.feature_names = sorted(list(all_feature_names))
        else:
            self.feature_names = sorted(list(all_feature_names))
        
        # Extract features with consistent dimensions
        X = []
        y = []
        
        for event in market_events:
            # Create feature vector with consistent dimensions
            feature_vector = []
            for feature_name in self.feature_names:
                feature_vector.append(event.features.get(feature_name, 0.0))
            
            X.append(feature_vector)
            
            # Create label based on price change and manipulation detection
            if event.manipulation_detected:
                if event.event_type == 'pump':
                    label = 2  # Pump
                elif event.event_type == 'dump':
                    label = 3  # Dump
                elif event.event_type == 'spoofing':
                    label = 4  # Spoofing
                else:
                    label = 1  # General manipulation
            else:
                label = 0  # Normal
            
            y.append(label)
        
        X = np.array(X)
        y = np.array(y)
        
        # Handle NaN values
        X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=-1e6)
        
        print(f"Training data prepared: {X.shape[0]} samples, {X.shape[1]} features")
        print(f"Feature names: {len(self.feature_names)} features")
        
        return X, y
    
    def train(self, market_events: List[MarketEvent]) -> Dict[str, float]:
        """Train the ML model"""
        if not HAS_ML_LIBS:
            raise ImportError("ML libraries not available")
        
        X, y = self.prepare_training_data(market_events)
        
        if len(X) == 0:
            return {"error": "No training data available"}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train main model
        self.model.fit(X_train_scaled, y_train)
        
        # Train anomaly detector
        normal_data = X_train_scaled[y_train == 0]  # Only normal data
        if len(normal_data) > 10:
            self.anomaly_detector.fit(normal_data)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        
        # Calculate metrics
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average='weighted', zero_division=0),
            "recall": recall_score(y_test, y_pred, average='weighted', zero_division=0),
            "f1_score": f1_score(y_test, y_pred, average='weighted', zero_division=0),
            "training_samples": len(X_train),
            "test_samples": len(X_test)
        }
        
        # Save model
        self.save_model()
        
        return metrics
    
    def predict(self, snapshot: OrderBookSnapshot, 
                historical_snapshots: List[OrderBookSnapshot],
                market_indicators: Dict = None) -> Dict[str, float]:
        """Predict market movement and manipulation probability"""
        if not HAS_ML_LIBS or self.model is None:
            return {"error": "Model not trained or ML libraries not available"}
        
        # Extract features
        if self.use_enhanced_features:
            # Use enhanced feature extractor with market indicators
            features_array = self.feature_extractor.extract_features(
                snapshot, historical_snapshots, market_indicators
            )
            # Convert array to dictionary for compatibility
            if isinstance(features_array, np.ndarray):
                features = {name: float(features_array[i]) for i, name in enumerate(self.feature_extractor.feature_names)}
                X = features_array.reshape(1, -1)  # Use array directly
            else:
                features = features_array
                X = np.array([list(features.values())])
        else:
            # Use basic feature extractor
            features = self.feature_extractor.extract_features(snapshot, historical_snapshots)
            X = np.array([list(features.values())])
        
        # Handle NaN values
        X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=-1e6)
        
        # Check feature dimension consistency
        if len(self.feature_names) > 0 and X.shape[1] != len(self.feature_names):
            return {
                "error": f"Feature dimension mismatch: expected {len(self.feature_names)}, got {X.shape[1]}. Please retrain the model."
            }
        
        # Scale features
        try:
            X_scaled = self.scaler.transform(X)
        except Exception as e:
            return {"error": f"Feature scaling failed: {str(e)}. Please retrain the model."}
        
        # Predict
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        # Anomaly detection
        anomaly_score = self.anomaly_detector.decision_function(X_scaled)[0]
        is_anomaly = self.anomaly_detector.predict(X_scaled)[0] == -1
        
        # Feature importance
        feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "prediction": int(prediction),
            "prediction_label": self._get_prediction_label(prediction),
            "probabilities": {
                "normal": probabilities[0] if len(probabilities) > 0 else 0,
                "manipulation": probabilities[1] if len(probabilities) > 1 else 0,
                "pump": probabilities[2] if len(probabilities) > 2 else 0,
                "dump": probabilities[3] if len(probabilities) > 3 else 0,
                "spoofing": probabilities[4] if len(probabilities) > 4 else 0
            },
            "anomaly_score": float(anomaly_score),
            "is_anomaly": bool(is_anomaly),
            "confidence": float(max(probabilities)),
            "top_features": top_features,
            "features": features,
            "feature_count": X.shape[1],
            "enhanced_features": self.use_enhanced_features
        }
    
    def _get_prediction_label(self, prediction: int) -> str:
        """Convert prediction to label"""
        labels = {
            0: "normal",
            1: "manipulation",
            2: "pump",
            3: "dump",
            4: "spoofing"
        }
        return labels.get(prediction, "unknown")
    
    def save_model(self):
        """Save trained model"""
        if not HAS_ML_LIBS:
            return
        
        import os
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # Save model components
        joblib.dump(self.model, f"{self.model_path}_classifier.pkl")
        joblib.dump(self.scaler, f"{self.model_path}_scaler.pkl")
        joblib.dump(self.anomaly_detector, f"{self.model_path}_anomaly.pkl")
        joblib.dump(self.feature_names, f"{self.model_path}_features.pkl")
    
    def load_model(self):
        """Load trained model"""
        if not HAS_ML_LIBS:
            return False
        
        try:
            self.model = joblib.load(f"{self.model_path}_classifier.pkl")
            self.scaler = joblib.load(f"{self.model_path}_scaler.pkl")
            self.anomaly_detector = joblib.load(f"{self.model_path}_anomaly.pkl")
            self.feature_names = joblib.load(f"{self.model_path}_features.pkl")
            return True
        except FileNotFoundError:
            return False

class BTCDataCollector:
    """Collect and store BTC order book data for ML training"""
    
    def __init__(self, db_path: str = "data/btc_orderbook.db"):
        self.db_path = db_path
        self.snapshots = deque(maxlen=1000)  # Keep last 1000 snapshots in memory
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database for storing order book data"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orderbook_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                mid_price REAL,
                spread REAL,
                bid_volume REAL,
                ask_volume REAL,
                imbalance REAL,
                bids TEXT,
                asks TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                features TEXT,
                price_change_1min REAL,
                price_change_5min REAL,
                manipulation_detected INTEGER,
                event_type TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_snapshot(self, snapshot: OrderBookSnapshot):
        """Store order book snapshot"""
        # Add to memory
        self.snapshots.append(snapshot)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO orderbook_snapshots 
            (timestamp, mid_price, spread, bid_volume, ask_volume, imbalance, bids, asks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            snapshot.timestamp,
            snapshot.mid_price,
            snapshot.spread,
            snapshot.bid_volume,
            snapshot.ask_volume,
            snapshot.imbalance,
            json.dumps(snapshot.bids),
            json.dumps(snapshot.asks)
        ))
        
        conn.commit()
        conn.close()
    
    def store_market_event(self, event: MarketEvent):
        """Store market event for training"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO market_events 
            (timestamp, features, price_change_1min, price_change_5min, 
             manipulation_detected, event_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            event.timestamp,
            json.dumps(event.features),
            event.price_change_1min,
            event.price_change_5min,
            int(event.manipulation_detected),
            event.event_type
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_snapshots(self, count: int = 100) -> List[OrderBookSnapshot]:
        """Get recent snapshots from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, mid_price, spread, bid_volume, ask_volume, imbalance, bids, asks
            FROM orderbook_snapshots 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (count,))
        
        rows = cursor.fetchall()
        conn.close()
        
        snapshots = []
        for row in rows:
            snapshot = OrderBookSnapshot(
                timestamp=row[0],
                mid_price=row[1],
                spread=row[2],
                bid_volume=row[3],
                ask_volume=row[4],
                imbalance=row[5],
                bids=json.loads(row[6]),
                asks=json.loads(row[7])
            )
            snapshots.append(snapshot)
        
        return list(reversed(snapshots))  # Return in chronological order
    
    def get_training_events(self, limit: int = 1000) -> List[MarketEvent]:
        """Get market events for training"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, features, price_change_1min, price_change_5min,
                   manipulation_detected, event_type
            FROM market_events 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            event = MarketEvent(
                timestamp=row[0],
                features=json.loads(row[1]),
                price_change_1min=row[2],
                price_change_5min=row[3],
                manipulation_detected=bool(row[4]),
                event_type=row[5]
            )
            events.append(event)
        
        return events