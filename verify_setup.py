#!/usr/bin/env python3
"""
Verification script for Trade Risk Analyzer setup
"""

import sys
from trade_risk_analyzer.core.init import initialize_system
from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.core.base import (
    RiskLevel, TradeType, PatternType, 
    Trade, Alert, ValidationResult
)
from datetime import datetime


def main():
    print("=" * 60)
    print("Trade Risk Analyzer - Setup Verification")
    print("=" * 60)
    
    # Test 1: Initialize system
    print("\n[1] Initializing system...")
    try:
        config = initialize_system()
        print("    ✓ System initialized successfully")
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        return False
    
    # Test 2: Configuration
    print("\n[2] Testing configuration...")
    try:
        assert config.detection.thresholds.high_risk_score == 80.0
        assert config.detection.model_weights.isolation_forest == 0.3
        assert len(config.detection.feature_windows) == 3
        print("    ✓ Configuration loaded correctly")
        print(f"      - High risk threshold: {config.detection.thresholds.high_risk_score}")
        print(f"      - Feature windows: {', '.join(config.detection.feature_windows)}")
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        return False
    
    # Test 3: Logging
    print("\n[3] Testing logging system...")
    try:
        logger = get_logger('verification')
        logger.info("Verification test", test_id=1, status="running")
        print("    ✓ Logging system working")
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        return False
    
    # Test 4: Base classes
    print("\n[4] Testing base classes and enums...")
    try:
        # Test enums
        risk = RiskLevel.HIGH
        trade_type = TradeType.BUY
        pattern = PatternType.WASH_TRADING
        
        # Test Trade dataclass
        trade = Trade(
            trade_id="T001",
            user_id="U001",
            timestamp=datetime.now(),
            symbol="BTC/USDT",
            price=50000.0,
            volume=1.5,
            trade_type=TradeType.BUY
        )
        
        # Test Alert dataclass
        alert = Alert(
            alert_id="A001",
            timestamp=datetime.now(),
            user_id="U001",
            trade_ids=["T001"],
            anomaly_score=85.5,
            risk_level=RiskLevel.HIGH,
            pattern_type=PatternType.WASH_TRADING,
            explanation="Suspicious trading pattern detected",
            recommended_action="Review user activity"
        )
        
        print("    ✓ Base classes working correctly")
        print(f"      - Trade: {trade.symbol} @ ${trade.price}")
        print(f"      - Alert: {alert.risk_level.value} risk (score: {alert.anomaly_score})")
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        return False
    
    # Test 5: Module structure
    print("\n[5] Verifying module structure...")
    try:
        modules = [
            'trade_risk_analyzer.data_ingestion',
            'trade_risk_analyzer.feature_engineering',
            'trade_risk_analyzer.detection',
            'trade_risk_analyzer.models',
            'trade_risk_analyzer.reporting',
            'trade_risk_analyzer.api',
        ]
        
        for module in modules:
            __import__(module)
        
        print("    ✓ All modules present and importable")
        for module in modules:
            print(f"      - {module.split('.')[-1]}")
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("✓ All verification tests passed!")
    print("=" * 60)
    print("\nProject structure is ready for implementation.")
    print("Next steps:")
    print("  1. Implement data ingestion module (Task 2)")
    print("  2. Implement feature engineering module (Task 3)")
    print("  3. Implement ML models (Task 4)")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
