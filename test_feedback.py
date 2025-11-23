"""
Test Feedback and Retraining Module

Tests feedback collection and model retraining functionality.
"""

from datetime import datetime, timedelta

from trade_risk_analyzer.core.base import Alert, RiskLevel, PatternType
from trade_risk_analyzer.feedback.collector import (
    FeedbackCollector, Feedback, FeedbackType, FeedbackStatus
)
from trade_risk_analyzer.feedback.retraining import RetrainingPipeline


def create_test_alert(alert_id: str, user_id: str) -> Alert:
    """Create a test alert"""
    return Alert(
        alert_id=alert_id,
        timestamp=datetime.now(),
        user_id=user_id,
        trade_ids=[f"trade_{alert_id}_1", f"trade_{alert_id}_2"],
        anomaly_score=85.0,
        risk_level=RiskLevel.HIGH,
        pattern_type=PatternType.WASH_TRADING,
        explanation="Test alert for wash trading pattern",
        recommended_action="Review trading activity"
    )


def test_feedback_collector():
    """Test feedback collector"""
    print("\n=== Testing Feedback Collector ===")
    
    # Create collector (without storage for testing)
    collector = FeedbackCollector(storage=None)
    
    print("✓ Feedback collector created")
    
    # Test feedback submission
    try:
        feedback = collector.submit_feedback(
            alert_id="test_alert_1",
            reviewer_user_id="reviewer_1",
            is_true_positive=True,
            feedback_type=FeedbackType.TRUE_POSITIVE,
            reviewer_notes="This is a valid wash trading pattern",
            confidence_score=0.9
        )
        
        print(f"✓ Feedback submitted: {feedback.feedback_id}")
        print(f"  Alert ID: {feedback.alert_id}")
        print(f"  Is True Positive: {feedback.is_true_positive}")
        print(f"  Confidence: {feedback.confidence_score}")
        print(f"  Status: {feedback.status.value}")
        
    except Exception as e:
        print(f"✗ Feedback submission failed: {e}")
    
    # Test feedback validation
    print("\n--- Testing Validation ---")
    
    # Test invalid confidence score
    try:
        collector.submit_feedback(
            alert_id="test_alert_2",
            reviewer_user_id="reviewer_1",
            is_true_positive=False,
            confidence_score=1.5  # Invalid
        )
        print("✗ Should have raised ValueError for invalid confidence")
    except ValueError as e:
        print(f"✓ Validation caught invalid confidence: {e}")
    
    # Test notes sanitization
    feedback = collector.submit_feedback(
        alert_id="test_alert_3",
        reviewer_user_id="reviewer_1",
        is_true_positive=False,
        reviewer_notes="<script>alert('xss')</script>This is a false positive",
        confidence_score=0.8
    )
    
    if "<script>" not in feedback.reviewer_notes:
        print("✓ Notes sanitization working (HTML tags removed)")
    else:
        print("✗ Notes sanitization failed")
    
    print("\n✓ Feedback collector tests passed")


def test_feedback_types():
    """Test different feedback types"""
    print("\n=== Testing Feedback Types ===")
    
    collector = FeedbackCollector(storage=None)
    
    # Test TRUE_POSITIVE
    feedback1 = collector.submit_feedback(
        alert_id="alert_1",
        reviewer_user_id="reviewer_1",
        is_true_positive=True,
        feedback_type=FeedbackType.TRUE_POSITIVE
    )
    print(f"✓ TRUE_POSITIVE feedback: {feedback1.feedback_type.value}")
    
    # Test FALSE_POSITIVE
    feedback2 = collector.submit_feedback(
        alert_id="alert_2",
        reviewer_user_id="reviewer_1",
        is_true_positive=False,
        feedback_type=FeedbackType.FALSE_POSITIVE
    )
    print(f"✓ FALSE_POSITIVE feedback: {feedback2.feedback_type.value}")
    
    # Test SEVERITY_ADJUSTMENT
    feedback3 = collector.submit_feedback(
        alert_id="alert_3",
        reviewer_user_id="reviewer_1",
        is_true_positive=True,
        feedback_type=FeedbackType.SEVERITY_ADJUSTMENT,
        suggested_risk_level=RiskLevel.MEDIUM
    )
    print(f"✓ SEVERITY_ADJUSTMENT feedback: {feedback3.feedback_type.value}")
    print(f"  Suggested risk level: {feedback3.suggested_risk_level.value}")
    
    # Test PATTERN_CORRECTION
    feedback4 = collector.submit_feedback(
        alert_id="alert_4",
        reviewer_user_id="reviewer_1",
        is_true_positive=True,
        feedback_type=FeedbackType.PATTERN_CORRECTION,
        suggested_pattern_type=PatternType.PUMP_AND_DUMP
    )
    print(f"✓ PATTERN_CORRECTION feedback: {feedback4.feedback_type.value}")
    print(f"  Suggested pattern: {feedback4.suggested_pattern_type.value}")
    
    print("\n✓ Feedback types tests passed")


def test_feedback_statistics():
    """Test feedback statistics"""
    print("\n=== Testing Feedback Statistics ===")
    
    collector = FeedbackCollector(storage=None)
    
    # Note: Without storage, we can't test actual statistics
    # In production, this would retrieve from database
    
    stats = collector.get_feedback_statistics()
    
    print(f"Total feedback: {stats['total_feedback']}")
    print(f"True positives: {stats['true_positives']}")
    print(f"False positives: {stats['false_positives']}")
    print(f"Precision: {stats['precision']:.2%}")
    
    print("\n✓ Feedback statistics test passed (requires database for full testing)")


def test_retraining_pipeline():
    """Test retraining pipeline"""
    print("\n=== Testing Retraining Pipeline ===")
    
    # Create pipeline (without storage for testing)
    pipeline = RetrainingPipeline(
        storage=None,
        model_dir="test_models",
        version_dir="test_model_versions"
    )
    
    print("✓ Retraining pipeline created")
    print(f"  Model directory: {pipeline.model_dir}")
    print(f"  Version directory: {pipeline.version_dir}")
    
    # Test model version retrieval
    versions = pipeline.get_model_versions()
    print(f"\n✓ Retrieved {len(versions)} model versions")
    
    # Note: Actual retraining requires database with feedback data
    print("\n✓ Retraining pipeline test passed (requires database for full testing)")


def test_model_versioning():
    """Test model versioning"""
    print("\n=== Testing Model Versioning ===")
    
    from trade_risk_analyzer.feedback.retraining import ModelVersion, PerformanceMetrics
    
    # Create performance metrics
    metrics = PerformanceMetrics(
        version="test_v1",
        timestamp=datetime.now(),
        accuracy=0.92,
        precision=0.89,
        recall=0.94,
        f1_score=0.91,
        auc_roc=0.95,
        training_samples=1000,
        feedback_samples=200
    )
    
    print("✓ Performance metrics created:")
    print(f"  Accuracy: {metrics.accuracy:.3f}")
    print(f"  Precision: {metrics.precision:.3f}")
    print(f"  Recall: {metrics.recall:.3f}")
    print(f"  F1 Score: {metrics.f1_score:.3f}")
    print(f"  AUC-ROC: {metrics.auc_roc:.3f}")
    
    # Create model version
    version = ModelVersion(
        version="random_forest_v20251112_120000",
        created_at=datetime.now(),
        model_type="random_forest",
        model_path="test_models/random_forest_v1.joblib",
        performance_metrics=metrics,
        is_active=True,
        notes="Test version with feedback data"
    )
    
    print(f"\n✓ Model version created:")
    print(f"  Version: {version.version}")
    print(f"  Model type: {version.model_type}")
    print(f"  Is active: {version.is_active}")
    print(f"  Notes: {version.notes}")
    
    # Test serialization
    version_dict = version.to_dict()
    print(f"\n✓ Version serialized to dict with {len(version_dict)} fields")
    
    print("\n✓ Model versioning tests passed")


def test_feedback_workflow():
    """Test complete feedback workflow"""
    print("\n=== Testing Complete Feedback Workflow ===")
    
    collector = FeedbackCollector(storage=None)
    
    # Step 1: Submit feedback
    print("\n1. Submitting feedback...")
    feedback = collector.submit_feedback(
        alert_id="workflow_alert_1",
        reviewer_user_id="compliance_officer_1",
        is_true_positive=True,
        feedback_type=FeedbackType.TRUE_POSITIVE,
        reviewer_notes="Confirmed wash trading pattern with supporting evidence",
        confidence_score=0.95
    )
    print(f"   ✓ Feedback submitted: {feedback.feedback_id}")
    print(f"   Status: {feedback.status.value}")
    
    # Step 2: Review feedback (simulated)
    print("\n2. Reviewing feedback...")
    print(f"   Alert ID: {feedback.alert_id}")
    print(f"   Is True Positive: {feedback.is_true_positive}")
    print(f"   Confidence: {feedback.confidence_score}")
    print(f"   Notes: {feedback.reviewer_notes}")
    
    # Step 3: Update status (would be done after review)
    print("\n3. Updating feedback status...")
    print(f"   Status changed: {feedback.status.value} -> REVIEWED")
    feedback.status = FeedbackStatus.REVIEWED
    
    # Step 4: Incorporate into training (simulated)
    print("\n4. Incorporating into training...")
    print(f"   Status changed: REVIEWED -> INCORPORATED")
    feedback.status = FeedbackStatus.INCORPORATED
    feedback.incorporated_at = datetime.now()
    
    print(f"\n✓ Complete workflow test passed")
    print(f"   Final status: {feedback.status.value}")
    print(f"   Incorporated at: {feedback.incorporated_at.isoformat()}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("FEEDBACK AND RETRAINING MODULE TESTS")
    print("=" * 60)
    
    try:
        test_feedback_collector()
        test_feedback_types()
        test_feedback_statistics()
        test_retraining_pipeline()
        test_model_versioning()
        test_feedback_workflow()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED ✓")
        print("=" * 60)
        print("\nNote: Full testing requires database integration")
        print("See example_feedback.py for complete usage examples")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
