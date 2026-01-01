"""
Enhanced Feature Extractor with Consistent Dimensions
Ensures all feature extractions return exactly the same number of features
"""

import numpy as np
from typing import Dict, List
from btc_deep_analyzer import OrderBookSnapshot

class EnhancedFeatureExtractor:
    """Enhanced feature extractor with consistent 42 features"""
    
    def __init__(self):
        self.feature_names = self._get_feature_names()
        self.num_features = len(self.feature_names)
    
    def _get_feature_names(self) -> List[str]:
        """Define exactly 42 feature names for consistency"""
        return [
            # Basic features (6)
            'mid_price', 'spread_bps', 'bid_ask_imbalance', 
            'total_bid_volume', 'total_ask_volume', 'total_volume',
            
            # Volume features (8)
            'top_5_bid_volume_ratio', 'top_5_ask_volume_ratio',
            'bid_vwap', 'ask_vwap', 'vwap_spread',
            'max_bid_volume', 'max_ask_volume', 'volume_concentration',
            
            # Liquidity features (6)
            'bid_1m_impact_bps', 'ask_1m_impact_bps',
            'bid_liquidity_1pct', 'ask_liquidity_1pct',
            'liquidity_ratio', 'depth_ratio',
            
            # Shape features (6)
            'avg_bid_gap', 'avg_ask_gap', 'bid_slope', 'ask_slope',
            'price_clustering', 'volume_clustering',
            
            # Temporal features (8)
            'price_momentum_5', 'price_volatility_5', 'spread_momentum',
            'imbalance_persistence', 'volume_trend', 'price_acceleration',
            'volatility_trend', 'momentum_strength',
            
            # Enhanced market indicators (8)
            'market_volatility', 'market_volume_24h', 'market_rsi',
            'funding_rate', 'price_momentum_market', 'collection_priority',
            'prediction_confidence', 'bb_position'
        ]
    
    def extract_features(self, snapshot: OrderBookSnapshot, 
                        historical_snapshots: List[OrderBookSnapshot] = None,
                        market_indicators: Dict = None) -> np.ndarray:
        """Extract exactly 42 features consistently"""
        
        features = {}
        
        # Initialize all features with default values
        for name in self.feature_names:
            features[name] = 0.0
        
        # Extract basic features
        features.update(self._extract_basic_features(snapshot))
        
        # Extract volume features
        features.update(self._extract_volume_features(snapshot))
        
        # Extract liquidity features
        features.update(self._extract_liquidity_features(snapshot))
        
        # Extract shape features
        features.update(self._extract_shape_features(snapshot))
        
        # Extract temporal features
        if historical_snapshots and len(historical_snapshots) >= 5:
            features.update(self._extract_temporal_features(snapshot, historical_snapshots))
        
        # Add market indicators if available
        if market_indicators:
            features.update(self._extract_market_indicator_features(market_indicators))
        
        # Convert to numpy array in consistent order
        feature_array = np.array([features.get(name, 0.0) for name in self.feature_names])
        
        # Ensure no NaN or inf values
        feature_array = np.nan_to_num(feature_array, nan=0.0, posinf=1e6, neginf=-1e6)
        
        return feature_array
    
    def _extract_basic_features(self, snapshot: OrderBookSnapshot) -> Dict[str, float]:
        """Basic order book features (6 features)"""
        return {
            'mid_price': snapshot.mid_price,
            'spread_bps': (snapshot.spread / snapshot.mid_price) * 10000 if snapshot.mid_price > 0 else 0,
            'bid_ask_imbalance': snapshot.imbalance,
            'total_bid_volume': snapshot.bid_volume,
            'total_ask_volume': snapshot.ask_volume,
            'total_volume': snapshot.bid_volume + snapshot.ask_volume
        }
    
    def _extract_volume_features(self, snapshot: OrderBookSnapshot) -> Dict[str, float]:
        """Volume-based features (8 features)"""
        features = {}
        
        bids = snapshot.bids[:10] if snapshot.bids else []
        asks = snapshot.asks[:10] if snapshot.asks else []
        
        if bids and asks:
            # Volume concentration
            top_5_bid_vol = sum(vol for _, vol in bids[:5])
            top_5_ask_vol = sum(vol for _, vol in asks[:5])
            
            features['top_5_bid_volume_ratio'] = top_5_bid_vol / snapshot.bid_volume if snapshot.bid_volume > 0 else 0
            features['top_5_ask_volume_ratio'] = top_5_ask_vol / snapshot.ask_volume if snapshot.ask_volume > 0 else 0
            
            # VWAP
            bid_vwap = sum(price * vol for price, vol in bids) / snapshot.bid_volume if snapshot.bid_volume > 0 else snapshot.mid_price
            ask_vwap = sum(price * vol for price, vol in asks) / snapshot.ask_volume if snapshot.ask_volume > 0 else snapshot.mid_price
            
            features['bid_vwap'] = bid_vwap
            features['ask_vwap'] = ask_vwap
            features['vwap_spread'] = ask_vwap - bid_vwap
            
            # Volume stats
            bid_volumes = [vol for _, vol in bids]
            ask_volumes = [vol for _, vol in asks]
            
            features['max_bid_volume'] = max(bid_volumes) if bid_volumes else 0
            features['max_ask_volume'] = max(ask_volumes) if ask_volumes else 0
            
            # Volume concentration
            total_vol = sum(bid_volumes) + sum(ask_volumes)
            max_vol = max(max(bid_volumes) if bid_volumes else 0, max(ask_volumes) if ask_volumes else 0)
            features['volume_concentration'] = max_vol / total_vol if total_vol > 0 else 0
        
        return features
    
    def _extract_liquidity_features(self, snapshot: OrderBookSnapshot) -> Dict[str, float]:
        """Liquidity features (6 features)"""
        features = {}
        
        bids = snapshot.bids[:10] if snapshot.bids else []
        asks = snapshot.asks[:10] if snapshot.asks else []
        
        # Price impact estimation
        features['bid_1m_impact_bps'] = 0.0
        features['ask_1m_impact_bps'] = 0.0
        
        if bids:
            cumulative_vol = 0
            for price, vol in bids:
                cumulative_vol += vol * price  # Dollar volume
                if cumulative_vol >= 1000000:  # $1M
                    features['bid_1m_impact_bps'] = ((snapshot.mid_price - price) / snapshot.mid_price) * 10000
                    break
        
        if asks:
            cumulative_vol = 0
            for price, vol in asks:
                cumulative_vol += vol * price  # Dollar volume
                if cumulative_vol >= 1000000:  # $1M
                    features['ask_1m_impact_bps'] = ((price - snapshot.mid_price) / snapshot.mid_price) * 10000
                    break
        
        # Liquidity within 1% of mid price
        price_range_1pct = snapshot.mid_price * 0.01
        
        bid_liquidity_1pct = sum(vol for price, vol in bids if snapshot.mid_price - price <= price_range_1pct)
        ask_liquidity_1pct = sum(vol for price, vol in asks if price - snapshot.mid_price <= price_range_1pct)
        
        features['bid_liquidity_1pct'] = bid_liquidity_1pct
        features['ask_liquidity_1pct'] = ask_liquidity_1pct
        features['liquidity_ratio'] = bid_liquidity_1pct / ask_liquidity_1pct if ask_liquidity_1pct > 0 else 1.0
        features['depth_ratio'] = len(bids) / len(asks) if asks else 1.0
        
        return features
    
    def _extract_shape_features(self, snapshot: OrderBookSnapshot) -> Dict[str, float]:
        """Order book shape features (6 features)"""
        features = {}
        
        bids = snapshot.bids[:10] if snapshot.bids else []
        asks = snapshot.asks[:10] if snapshot.asks else []
        
        # Price gaps
        if len(bids) > 1:
            bid_gaps = [bids[i][0] - bids[i+1][0] for i in range(len(bids)-1)]
            features['avg_bid_gap'] = np.mean(bid_gaps) if bid_gaps else 0
        else:
            features['avg_bid_gap'] = 0
        
        if len(asks) > 1:
            ask_gaps = [asks[i+1][0] - asks[i][0] for i in range(len(asks)-1)]
            features['avg_ask_gap'] = np.mean(ask_gaps) if ask_gaps else 0
        else:
            features['avg_ask_gap'] = 0
        
        # Order book slopes
        if len(bids) >= 3:
            bid_prices = [price for price, _ in bids[:3]]
            bid_volumes = [vol for _, vol in bids[:3]]
            features['bid_slope'] = np.polyfit(bid_prices, bid_volumes, 1)[0] if len(bid_prices) > 1 else 0
        else:
            features['bid_slope'] = 0
        
        if len(asks) >= 3:
            ask_prices = [price for price, _ in asks[:3]]
            ask_volumes = [vol for _, vol in asks[:3]]
            features['ask_slope'] = np.polyfit(ask_prices, ask_volumes, 1)[0] if len(ask_prices) > 1 else 0
        else:
            features['ask_slope'] = 0
        
        # Clustering metrics
        features['price_clustering'] = len(set(round(price, 0) for price, _ in bids + asks)) / len(bids + asks) if bids + asks else 1.0
        features['volume_clustering'] = len(set(round(vol, 1) for _, vol in bids + asks)) / len(bids + asks) if bids + asks else 1.0
        
        return features
    
    def _extract_temporal_features(self, snapshot: OrderBookSnapshot, 
                                 historical_snapshots: List[OrderBookSnapshot]) -> Dict[str, float]:
        """Temporal features (8 features)"""
        features = {}
        
        if len(historical_snapshots) < 5:
            return features
        
        # Price momentum and volatility
        recent_prices = [s.mid_price for s in historical_snapshots[-5:]] + [snapshot.mid_price]
        
        if len(recent_prices) > 1:
            returns = [(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] for i in range(1, len(recent_prices))]
            features['price_momentum_5'] = np.mean(returns) if returns else 0
            features['price_volatility_5'] = np.std(returns) if len(returns) > 1 else 0
            features['price_acceleration'] = returns[-1] - returns[0] if len(returns) >= 2 else 0
        
        # Spread momentum
        recent_spreads = [s.spread for s in historical_snapshots[-5:]] + [snapshot.spread]
        if len(recent_spreads) > 1:
            spread_changes = [(recent_spreads[i] - recent_spreads[i-1]) / recent_spreads[i-1] for i in range(1, len(recent_spreads)) if recent_spreads[i-1] > 0]
            features['spread_momentum'] = np.mean(spread_changes) if spread_changes else 0
        
        # Imbalance persistence
        recent_imbalances = [s.imbalance for s in historical_snapshots[-5:]] + [snapshot.imbalance]
        features['imbalance_persistence'] = np.std(recent_imbalances) if len(recent_imbalances) > 1 else 0
        
        # Volume trend
        recent_volumes = [s.bid_volume + s.ask_volume for s in historical_snapshots[-5:]] + [snapshot.bid_volume + snapshot.ask_volume]
        if len(recent_volumes) > 1:
            volume_changes = [(recent_volumes[i] - recent_volumes[i-1]) / recent_volumes[i-1] for i in range(1, len(recent_volumes)) if recent_volumes[i-1] > 0]
            features['volume_trend'] = np.mean(volume_changes) if volume_changes else 0
        
        # Volatility trend
        if len(recent_prices) >= 3:
            early_vol = np.std(recent_prices[:3]) if len(recent_prices[:3]) > 1 else 0
            late_vol = np.std(recent_prices[-3:]) if len(recent_prices[-3:]) > 1 else 0
            features['volatility_trend'] = late_vol - early_vol
        
        # Momentum strength
        if 'price_momentum_5' in features and 'price_volatility_5' in features and features['price_volatility_5'] > 0:
            features['momentum_strength'] = abs(features['price_momentum_5']) / features['price_volatility_5']
        
        return features
    
    def _extract_market_indicator_features(self, indicators: Dict) -> Dict[str, float]:
        """Market indicator features (8 features)"""
        features = {}
        
        features['market_volatility'] = indicators.get('current_volatility', 0.0)
        features['market_volume_24h'] = indicators.get('current_volume', 0.0) / 1e9  # Normalize to billions
        features['market_rsi'] = indicators.get('current_rsi', 50.0) / 100.0  # Normalize to 0-1
        features['funding_rate'] = indicators.get('funding_rate', 0.0) * 100  # Convert to percentage
        features['price_momentum_market'] = indicators.get('price_momentum', 0.0)
        features['collection_priority'] = indicators.get('collection_priority', 0.0)
        features['prediction_confidence'] = indicators.get('prediction_confidence', 0.0)
        
        # Bollinger Bands position
        price = indicators.get('price', 0.0)
        bb_upper = indicators.get('bb_upper', price * 1.02)
        bb_lower = indicators.get('bb_lower', price * 0.98)
        
        if bb_upper > bb_lower:
            features['bb_position'] = (price - bb_lower) / (bb_upper - bb_lower)
        else:
            features['bb_position'] = 0.5
        
        return features