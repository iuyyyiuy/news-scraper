"""
Futures-Specific Feature Extractors

Extracts features from futures market data including funding rates,
liquidations, basis spreads, and open interest patterns.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from trade_risk_analyzer.core.logger import get_logger


logger = get_logger(__name__)


class FuturesFeatureExtractor:
    """
    Extracts futures-specific features for anomaly detection
    
    Features include:
    - Funding rate patterns
    - Premium/basis spread anomalies
    - Liquidation metrics
    - Open interest changes
    - Mark-index price deviations
    """
    
    def __init__(self):
        """Initialize futures feature extractor"""
        self.logger = logger
    
    def calculate_funding_rate_features(
        self,
        funding_history: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate funding rate features
        
        Args:
            funding_history: List of historical funding rate data
            
        Returns:
            Dictionary of funding rate features
        """
        if not funding_history:
            return self._empty_funding_features()
        
        try:
            # Extract funding rates
            rates = [float(f.get('funding_rate', 0)) for f in funding_history]
            
            if not rates:
                return self._empty_funding_features()
            
            # Calculate statistics
            mean_rate = np.mean(rates)
            std_rate = np.std(rates)
            max_rate = np.max(rates)
            min_rate = np.min(rates)
            
            # Recent rate (last value)
            recent_rate = rates[-1] if rates else 0
            
            # Deviation from mean (in std deviations)
            deviation_std = abs(recent_rate - mean_rate) / std_rate if std_rate > 0 else 0
            
            # Volatility (rolling std of last 10 periods)
            recent_rates = rates[-10:] if len(rates) >= 10 else rates
            volatility = np.std(recent_rates)
            
            # Trend (linear regression slope)
            if len(rates) >= 3:
                x = np.arange(len(rates))
                slope, _ = np.polyfit(x, rates, 1)
                trend = slope
            else:
                trend = 0
            
            # Funding rate farming indicator (sustained high rates)
            high_rate_threshold = mean_rate + 2 * std_rate
            high_rate_count = sum(1 for r in recent_rates if r > high_rate_threshold)
            farming_indicator = high_rate_count / len(recent_rates) if recent_rates else 0
            
            return {
                'funding_rate_mean': mean_rate,
                'funding_rate_std': std_rate,
                'funding_rate_max': max_rate,
                'funding_rate_min': min_rate,
                'funding_rate_recent': recent_rate,
                'funding_rate_deviation_std': deviation_std,
                'funding_rate_volatility': volatility,
                'funding_rate_trend': trend,
                'funding_rate_farming_indicator': farming_indicator
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating funding rate features: {e}")
            return self._empty_funding_features()
    
    def calculate_premium_basis_features(
        self,
        premium_data: Optional[Dict[str, Any]],
        basis_history: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate premium and basis spread features
        
        Args:
            premium_data: Current premium index data
            basis_history: Historical basis data
            
        Returns:
            Dictionary of premium/basis features
        """
        features = {}
        
        try:
            # Premium features (mark price vs index price)
            if premium_data:
                mark_price = float(premium_data.get('mark_price', 0))
                index_price = float(premium_data.get('index_price', 0))
                premium_rate = float(premium_data.get('premium_rate', 0))
                
                # Mark-index deviation
                if index_price > 0:
                    mark_index_deviation = abs(mark_price - index_price) / index_price
                else:
                    mark_index_deviation = 0
                
                features.update({
                    'premium_rate': premium_rate,
                    'mark_index_deviation': mark_index_deviation
                })
            else:
                features.update({
                    'premium_rate': 0,
                    'mark_index_deviation': 0
                })
            
            # Basis features (futures-spot spread)
            if basis_history:
                basis_rates = [float(b.get('basis_rate', 0)) for b in basis_history]
                
                if basis_rates:
                    mean_basis = np.mean(basis_rates)
                    std_basis = np.std(basis_rates)
                    recent_basis = basis_rates[-1]
                    
                    # Basis anomaly (deviation from mean)
                    basis_anomaly = abs(recent_basis - mean_basis) / std_basis if std_basis > 0 else 0
                    
                    features.update({
                        'basis_mean': mean_basis,
                        'basis_std': std_basis,
                        'basis_recent': recent_basis,
                        'basis_anomaly': basis_anomaly
                    })
                else:
                    features.update({
                        'basis_mean': 0,
                        'basis_std': 0,
                        'basis_recent': 0,
                        'basis_anomaly': 0
                    })
            else:
                features.update({
                    'basis_mean': 0,
                    'basis_std': 0,
                    'basis_recent': 0,
                    'basis_anomaly': 0
                })
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error calculating premium/basis features: {e}")
            return {
                'premium_rate': 0,
                'mark_index_deviation': 0,
                'basis_mean': 0,
                'basis_std': 0,
                'basis_recent': 0,
                'basis_anomaly': 0
            }
    
    def calculate_liquidation_features(
        self,
        liquidations: List[Dict[str, Any]],
        time_window_minutes: int = 60
    ) -> Dict[str, float]:
        """
        Calculate liquidation-related features
        
        Args:
            liquidations: List of liquidation events
            time_window_minutes: Time window for analysis
            
        Returns:
            Dictionary of liquidation features
        """
        if not liquidations:
            return self._empty_liquidation_features()
        
        try:
            # Filter recent liquidations
            now = datetime.now()
            cutoff_time = now - timedelta(minutes=time_window_minutes)
            
            recent_liquidations = []
            for liq in liquidations:
                timestamp = liq.get('timestamp')
                if isinstance(timestamp, str):
                    liq_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif isinstance(timestamp, datetime):
                    liq_time = timestamp
                else:
                    continue
                
                if liq_time >= cutoff_time:
                    recent_liquidations.append(liq)
            
            # Liquidation frequency
            liquidation_count = len(recent_liquidations)
            liquidation_frequency = liquidation_count / (time_window_minutes / 60)  # per hour
            
            # Liquidation volume
            total_volume = sum(float(liq.get('volume', 0)) for liq in recent_liquidations)
            avg_volume = total_volume / liquidation_count if liquidation_count > 0 else 0
            
            # Side distribution (long vs short)
            long_count = sum(1 for liq in recent_liquidations if liq.get('side') == 'LONG')
            short_count = sum(1 for liq in recent_liquidations if liq.get('side') == 'SHORT')
            
            # Cascade indicator (5+ liquidations in 1 minute)
            cascade_threshold = 5
            cascade_window = 1  # minute
            
            cascade_detected = 0
            if len(recent_liquidations) >= cascade_threshold:
                # Check for cascades
                sorted_liq = sorted(recent_liquidations, key=lambda x: x.get('timestamp', ''))
                for i in range(len(sorted_liq) - cascade_threshold + 1):
                    window_liq = sorted_liq[i:i+cascade_threshold]
                    first_time = datetime.fromisoformat(window_liq[0].get('timestamp', '').replace('Z', '+00:00'))
                    last_time = datetime.fromisoformat(window_liq[-1].get('timestamp', '').replace('Z', '+00:00'))
                    
                    if (last_time - first_time).total_seconds() <= cascade_window * 60:
                        cascade_detected = 1
                        break
            
            return {
                'liquidation_count': liquidation_count,
                'liquidation_frequency': liquidation_frequency,
                'liquidation_total_volume': total_volume,
                'liquidation_avg_volume': avg_volume,
                'liquidation_long_count': long_count,
                'liquidation_short_count': short_count,
                'liquidation_cascade_detected': cascade_detected
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating liquidation features: {e}")
            return self._empty_liquidation_features()
    
    def calculate_open_interest_features(
        self,
        klines: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate open interest change features
        
        Args:
            klines: List of K-line data with open interest
            
        Returns:
            Dictionary of open interest features
        """
        if not klines:
            return self._empty_open_interest_features()
        
        try:
            # Extract open interest values
            oi_values = [float(k.get('open_interest', 0)) for k in klines if 'open_interest' in k]
            
            if not oi_values or len(oi_values) < 2:
                return self._empty_open_interest_features()
            
            # Current and previous OI
            current_oi = oi_values[-1]
            previous_oi = oi_values[-2]
            
            # OI change
            oi_change = current_oi - previous_oi
            oi_change_pct = (oi_change / previous_oi * 100) if previous_oi > 0 else 0
            
            # OI trend (slope)
            if len(oi_values) >= 3:
                x = np.arange(len(oi_values))
                slope, _ = np.polyfit(x, oi_values, 1)
                oi_trend = slope
            else:
                oi_trend = 0
            
            # OI volatility
            oi_volatility = np.std(oi_values)
            
            return {
                'open_interest_current': current_oi,
                'open_interest_change': oi_change,
                'open_interest_change_pct': oi_change_pct,
                'open_interest_trend': oi_trend,
                'open_interest_volatility': oi_volatility
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating open interest features: {e}")
            return self._empty_open_interest_features()
    
    def calculate_position_concentration_features(
        self,
        position_tiers: List[Dict[str, Any]],
        current_oi: float
    ) -> Dict[str, float]:
        """
        Calculate position concentration risk features
        
        Args:
            position_tiers: List of position tier data
            current_oi: Current open interest
            
        Returns:
            Dictionary of position concentration features
        """
        if not position_tiers or current_oi <= 0:
            return {
                'position_concentration_risk': 0,
                'max_leverage_available': 0,
                'avg_maintenance_margin': 0
            }
        
        try:
            # Calculate concentration in top tier
            tiers = position_tiers.get('tiers', []) if isinstance(position_tiers, dict) else position_tiers
            
            if not tiers:
                return {
                    'position_concentration_risk': 0,
                    'max_leverage_available': 0,
                    'avg_maintenance_margin': 0
                }
            
            # Get max position from first tier
            max_position_tier1 = float(tiers[0].get('max_position', 0))
            
            # Concentration risk (if >30% in single tier)
            concentration = max_position_tier1 / current_oi if current_oi > 0 else 0
            concentration_risk = 1 if concentration > 0.3 else 0
            
            # Max leverage
            max_leverage = float(tiers[0].get('max_leverage', 0))
            
            # Average maintenance margin
            margins = [float(t.get('maintenance_margin_rate', 0)) for t in tiers]
            avg_margin = np.mean(margins) if margins else 0
            
            return {
                'position_concentration_risk': concentration_risk,
                'max_leverage_available': max_leverage,
                'avg_maintenance_margin': avg_margin
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating position concentration features: {e}")
            return {
                'position_concentration_risk': 0,
                'max_leverage_available': 0,
                'avg_maintenance_margin': 0
            }
    
    def extract_all_futures_features(
        self,
        funding_history: List[Dict[str, Any]],
        premium_data: Optional[Dict[str, Any]],
        basis_history: List[Dict[str, Any]],
        liquidations: List[Dict[str, Any]],
        klines: List[Dict[str, Any]],
        position_tiers: List[Dict[str, Any]],
        current_oi: float = 0
    ) -> Dict[str, float]:
        """
        Extract all futures-specific features
        
        Args:
            funding_history: Historical funding rate data
            premium_data: Current premium index data
            basis_history: Historical basis data
            liquidations: Recent liquidation events
            klines: K-line data with open interest
            position_tiers: Position tier data
            current_oi: Current open interest
            
        Returns:
            Dictionary of all futures features
        """
        features = {}
        
        # Funding rate features
        features.update(self.calculate_funding_rate_features(funding_history))
        
        # Premium/basis features
        features.update(self.calculate_premium_basis_features(premium_data, basis_history))
        
        # Liquidation features
        features.update(self.calculate_liquidation_features(liquidations))
        
        # Open interest features
        features.update(self.calculate_open_interest_features(klines))
        
        # Position concentration features
        features.update(self.calculate_position_concentration_features(position_tiers, current_oi))
        
        return features
    
    def _empty_funding_features(self) -> Dict[str, float]:
        """Return empty funding rate features"""
        return {
            'funding_rate_mean': 0,
            'funding_rate_std': 0,
            'funding_rate_max': 0,
            'funding_rate_min': 0,
            'funding_rate_recent': 0,
            'funding_rate_deviation_std': 0,
            'funding_rate_volatility': 0,
            'funding_rate_trend': 0,
            'funding_rate_farming_indicator': 0
        }
    
    def _empty_liquidation_features(self) -> Dict[str, float]:
        """Return empty liquidation features"""
        return {
            'liquidation_count': 0,
            'liquidation_frequency': 0,
            'liquidation_total_volume': 0,
            'liquidation_avg_volume': 0,
            'liquidation_long_count': 0,
            'liquidation_short_count': 0,
            'liquidation_cascade_detected': 0
        }
    
    def _empty_open_interest_features(self) -> Dict[str, float]:
        """Return empty open interest features"""
        return {
            'open_interest_current': 0,
            'open_interest_change': 0,
            'open_interest_change_pct': 0,
            'open_interest_trend': 0,
            'open_interest_volatility': 0
        }
