"""
Test Alert Manager

Tests alert generation, deduplication, and storage functionality.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

from trade_risk_analyzer.core.base import Alert, RiskLevel, PatternType
from trade_risk_analyzer.detection.alert_manager import AlertManager
from trade_risk_analyzer.data_ingestion.storage import DatabaseStorage


def test_alert_generation():
    """Test basic alert generation"""
    print("\n=== Testing Alert Generation ===")
    
    # Create alert manager without storage
    manager = AlertManager()
    
    # Generate an alert
    alert = manager.generate_alert(
        user_id="user_123",
        trade_ids=["trade_1", "trade_2", "trade_3"],
        anomaly_score=85.5,
        risk_level=RiskLevel.HIGH,
        pattern_type=PatternType.WASH_TRADING,
        explanation="Detected wash trading pattern with same user as buyer and seller",
        recommended_action="Review user trading history and investigate potential manipulation",
        additional_context={
            'trade_count': 3,
            'time_window': '5 minutes',
            'threshold_exceeded': 'Same user buy/sell ratio > 80%'
        }
    )
    
    print(f"Generated Alert ID: {alert.alert_id}")
    print(f"User ID: {alert.user_id}")
    print(f"Risk Level: {alert.risk_level.value}")
    print(f"Pattern Type: {alert.pattern_type.value}")
    print(f"Anomaly Score: {alert.anomaly_score}")
    print(f"Explanation: {alert.explanation}")
    print(f"Recommended Action: {alert.recommended_action}")
    print(f"Trade IDs: {alert.trade_ids}")
    
    assert alert.user_id == "user_123"
    assert alert.anomaly_score == 85.5
    assert alert.risk_level == RiskLevel.HIGH
    assert alert.pattern_type == PatternType.WASH_TRADING
    assert len(alert.trade_ids) == 3
    assert "trade_count" in alert.explanation or "3" in alert.explanation
    
    print("✓ Alert generation test passed")


def test_alert_deduplication():
    """Test alert deduplication logic"""
    print("\n=== Testing Alert Deduplication ===")
    
    manager = AlertManager(deduplication_window_hours=1)
    
    # Create first alert
    alert1 = manager.generate_alert(
        user_id="user_456",
        trade_ids=["trade_10", "trade_11"],
        anomaly_score=75.0,
        risk_level=RiskLevel.MEDIUM,
        pattern_type=PatternType.PUMP_AND_DUMP,
        explanation="Detected pump and dump pattern",
        recommended_action="Investigate coordinated trading"
    )
    
    # Add to cache
    manager._add_to_cache(alert1)
    
    # Create similar alert (should be duplicate)
    alert2 = manager.generate_alert(
        user_id="user_456",
        trade_ids=["trade_10", "trade_12"],  # Overlapping trades
        anomaly_score=78.0,
        risk_level=RiskLevel.MEDIUM,
        pattern_type=PatternType.PUMP_AND_DUMP,
        explanation="Detected pump and dump pattern",
        recommended_action="Investigate coordinated trading"
    )
    
    is_duplicate = manager._is_duplicate(alert2)
    print(f"Alert 2 is duplicate of Alert 1: {is_duplicate}")
    assert is_duplicate, "Alert 2 should be detected as duplicate"
    
    # Create different alert (should not be duplicate)
    alert3 = manager.generate_alert(
        user_id="user_789",  # Different user
        trade_ids=["trade_20", "trade_21"],
        anomaly_score=80.0,
        risk_level=RiskLevel.HIGH,
        pattern_type=PatternType.PUMP_AND_DUMP,
        explanation="Detected pump and dump pattern",
        recommended_action="Investigate coordinated trading"
    )
    
    is_duplicate = manager._is_duplicate(alert3)
    print(f"Alert 3 is duplicate: {is_duplicate}")
    assert not is_duplicate, "Alert 3 should not be duplicate (different user)"
    
    print("✓ Alert deduplication test passed")


def test_alert_storage():
    """Test alert storage and retrieval"""
    print("\n=== Testing Alert Storage ===")
    
    # Create in-memory database
    db_path = "sqlite:///:memory:"
    storage = DatabaseStorage(db_path)
    storage.connect()
    
    # Create alert manager with storage
    manager = AlertManager(storage=storage)
    
    # Generate and save alerts
    alerts = []
    for i in range(5):
        alert = manager.generate_alert(
            user_id=f"user_{i % 3}",  # 3 different users
            trade_ids=[f"trade_{i*10}", f"trade_{i*10+1}"],
            anomaly_score=50.0 + i * 10,
            risk_level=RiskLevel.HIGH if i >= 3 else RiskLevel.MEDIUM,
            pattern_type=PatternType.WASH_TRADING if i % 2 == 0 else PatternType.HFT_MANIPULATION,
            explanation=f"Test alert {i}",
            recommended_action="Review and investigate"
        )
        alerts.append(alert)
    
    # Save alerts
    results = manager.save_alerts_batch(alerts, check_duplicates=False)
    print(f"Save results: {results}")
    
    assert results['saved'] == 5, f"Expected 5 saved, got {results['saved']}"
    assert results['duplicates'] == 0
    assert results['errors'] == 0
    
    # Retrieve all alerts
    retrieved_alerts = manager.get_alerts()
    print(f"Retrieved {len(retrieved_alerts)} alerts")
    assert len(retrieved_alerts) == 5
    
    # Filter by user
    user_alerts = manager.get_alerts(user_id="user_0")
    print(f"Alerts for user_0: {len(user_alerts)}")
    assert len(user_alerts) == 2  # user_0 and user_3 (3 % 3 = 0)
    
    # Filter by risk level
    high_risk_alerts = manager.get_alerts(risk_level=RiskLevel.HIGH)
    print(f"High risk alerts: {len(high_risk_alerts)}")
    assert len(high_risk_alerts) == 2  # i=3 and i=4
    
    # Filter by pattern type
    wash_trading_alerts = manager.get_alerts(pattern_type=PatternType.WASH_TRADING)
    print(f"Wash trading alerts: {len(wash_trading_alerts)}")
    assert len(wash_trading_alerts) == 3  # i=0, 2, 4
    
    print("✓ Alert storage test passed")


def test_alert_statistics():
    """Test alert statistics generation"""
    print("\n=== Testing Alert Statistics ===")
    
    # Create in-memory database
    db_path = "sqlite:///:memory:"
    storage = DatabaseStorage(db_path)
    storage.connect()
    
    manager = AlertManager(storage=storage)
    
    # Generate diverse alerts
    alerts = []
    
    # High risk wash trading
    for i in range(3):
        alert = manager.generate_alert(
            user_id=f"user_A",
            trade_ids=[f"trade_{i}"],
            anomaly_score=85.0,
            risk_level=RiskLevel.HIGH,
            pattern_type=PatternType.WASH_TRADING,
            explanation="High risk wash trading",
            recommended_action="Immediate review"
        )
        alerts.append(alert)
    
    # Medium risk pump and dump
    for i in range(2):
        alert = manager.generate_alert(
            user_id=f"user_B",
            trade_ids=[f"trade_{i+10}"],
            anomaly_score=65.0,
            risk_level=RiskLevel.MEDIUM,
            pattern_type=PatternType.PUMP_AND_DUMP,
            explanation="Medium risk pump and dump",
            recommended_action="Monitor activity"
        )
        alerts.append(alert)
    
    # Save alerts
    manager.save_alerts_batch(alerts, check_duplicates=False)
    
    # Get statistics
    stats = manager.get_alert_statistics()
    
    print(f"Total alerts: {stats['total_alerts']}")
    print(f"By risk level: {stats['by_risk_level']}")
    print(f"By pattern type: {stats['by_pattern_type']}")
    print(f"By user: {stats['by_user']}")
    print(f"Average anomaly score: {stats['average_anomaly_score']:.2f}")
    
    assert stats['total_alerts'] == 5
    assert stats['by_risk_level']['HIGH'] == 3
    assert stats['by_risk_level']['MEDIUM'] == 2
    assert stats['by_pattern_type']['WASH_TRADING'] == 3
    assert stats['by_pattern_type']['PUMP_AND_DUMP'] == 2
    assert stats['by_user']['user_A'] == 3
    assert stats['by_user']['user_B'] == 2
    assert 70.0 < stats['average_anomaly_score'] < 80.0
    
    print("✓ Alert statistics test passed")


def test_alert_review():
    """Test alert review functionality"""
    print("\n=== Testing Alert Review ===")
    
    # Create in-memory database
    db_path = "sqlite:///:memory:"
    storage = DatabaseStorage(db_path)
    storage.connect()
    
    manager = AlertManager(storage=storage)
    
    # Generate and save an alert
    alert = manager.generate_alert(
        user_id="user_review",
        trade_ids=["trade_r1", "trade_r2"],
        anomaly_score=90.0,
        risk_level=RiskLevel.HIGH,
        pattern_type=PatternType.SPOOFING,
        explanation="Detected spoofing behavior",
        recommended_action="Immediate investigation required"
    )
    
    manager.save_alert(alert, check_duplicate=False)
    
    # Verify initial state
    retrieved = manager.get_alerts(user_id="user_review")
    assert len(retrieved) == 1
    assert not retrieved[0].is_reviewed
    assert retrieved[0].is_true_positive is None
    
    # Update review status
    success = manager.update_alert_review(
        alert_id=alert.alert_id,
        is_true_positive=True,
        reviewer_notes="Confirmed spoofing pattern, user suspended"
    )
    
    assert success, "Alert review update should succeed"
    
    # Verify updated state
    retrieved = manager.get_alerts(user_id="user_review")
    assert len(retrieved) == 1
    assert retrieved[0].is_reviewed
    assert retrieved[0].is_true_positive is True
    assert "suspended" in retrieved[0].reviewer_notes.lower()
    
    print("✓ Alert review test passed")


def test_batch_save_with_deduplication():
    """Test batch save with deduplication"""
    print("\n=== Testing Batch Save with Deduplication ===")
    
    # Create in-memory database
    db_path = "sqlite:///:memory:"
    storage = DatabaseStorage(db_path)
    storage.connect()
    
    manager = AlertManager(storage=storage, deduplication_window_hours=24)
    
    # Create alerts with some duplicates
    alerts = []
    
    # Original alert
    alert1 = manager.generate_alert(
        user_id="user_dup",
        trade_ids=["trade_1", "trade_2"],
        anomaly_score=80.0,
        risk_level=RiskLevel.HIGH,
        pattern_type=PatternType.LAYERING,
        explanation="Layering detected",
        recommended_action="Investigate"
    )
    alerts.append(alert1)
    
    # Duplicate alert (same user, pattern, overlapping trades)
    alert2 = manager.generate_alert(
        user_id="user_dup",
        trade_ids=["trade_2", "trade_3"],  # Overlapping
        anomaly_score=82.0,
        risk_level=RiskLevel.HIGH,
        pattern_type=PatternType.LAYERING,
        explanation="Layering detected again",
        recommended_action="Investigate"
    )
    alerts.append(alert2)
    
    # Different alert (different pattern)
    alert3 = manager.generate_alert(
        user_id="user_dup",
        trade_ids=["trade_4", "trade_5"],
        anomaly_score=75.0,
        risk_level=RiskLevel.MEDIUM,
        pattern_type=PatternType.WASH_TRADING,  # Different pattern
        explanation="Wash trading detected",
        recommended_action="Monitor"
    )
    alerts.append(alert3)
    
    # Save with deduplication
    results = manager.save_alerts_batch(alerts, check_duplicates=True)
    
    print(f"Batch save results: {results}")
    print(f"  Saved: {results['saved']}")
    print(f"  Duplicates: {results['duplicates']}")
    print(f"  Errors: {results['errors']}")
    
    # Should save alert1 and alert3, skip alert2 as duplicate
    assert results['saved'] == 2, f"Expected 2 saved, got {results['saved']}"
    assert results['duplicates'] == 1, f"Expected 1 duplicate, got {results['duplicates']}"
    
    # Verify only 2 alerts in database
    all_alerts = manager.get_alerts()
    assert len(all_alerts) == 2
    
    print("✓ Batch save with deduplication test passed")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Alert Manager Test Suite")
    print("=" * 60)
    
    try:
        test_alert_generation()
        test_alert_deduplication()
        test_alert_storage()
        test_alert_statistics()
        test_alert_review()
        test_batch_save_with_deduplication()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {str(e)}")
        raise
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
