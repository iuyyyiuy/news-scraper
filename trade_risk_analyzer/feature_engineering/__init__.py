"""
Feature Engineering Module

Extracts meaningful features from raw trade data for ML model input.
"""

from trade_risk_analyzer.feature_engineering.frequency_metrics import FrequencyMetricsCalculator
from trade_risk_analyzer.feature_engineering.volume_statistics import VolumeStatisticsCalculator
from trade_risk_analyzer.feature_engineering.temporal_patterns import TemporalPatternAnalyzer
from trade_risk_analyzer.feature_engineering.price_impact import PriceImpactCalculator
from trade_risk_analyzer.feature_engineering.behavioral_metrics import BehavioralMetricsCalculator
from trade_risk_analyzer.feature_engineering.extractor import FeatureExtractor


__all__ = [
    'FrequencyMetricsCalculator',
    'VolumeStatisticsCalculator',
    'TemporalPatternAnalyzer',
    'PriceImpactCalculator',
    'BehavioralMetricsCalculator',
    'FeatureExtractor',
]
