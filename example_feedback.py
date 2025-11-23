"""
Example: Feedback and Continuous Learning

Demonstrates how to collect feedback and retrain models.
"""

from datetime import datetime, timedelta

from trade_risk_analyzer.core.base import Alert, RiskLevel, PatternType
from trade_risk_analyzer.feedback.collector import (
    FeedbackCollector, FeedbackType, FeedbackStatus
)
from trade_risk_analyzer.feedback.retraining import RetrainingPipeline


def example_feedback_submission():
    """Example 1: Submit feedback on alerts"""
    print("=" * 60)
    print("Example 1: Feedback Submission")
    print("=" * 60)
    
    # Create feedback collector
    collector = FeedbackCollector(storage=None)  # In production, pass DatabaseStorage
    
    print("\n📝 Submitting feedback on alerts...")
    
    # Example 1: True positive feedback
    feedback1 = collector.submit_feedback(
        alert_id="alert_12345",
        reviewer_user_id="compliance_officer_1",
        is_true_positive=True,
        feedback_type=FeedbackType.TRUE_POSITIVE,
        reviewer_notes="Confirmed wash trading pattern. User executed 15 matching buy/sell orders within 2 minutes.",
        confidence_score=0.95
    )
    
    print(f"\n✓ True Positive Feedback:")
    print(f"  Feedback ID: {feedback1.feedback_id}")
    print(f"  Alert ID: {feedback1.alert_id}")
    print(f"  Reviewer: {feedback1.user_id}")
    print(f"  Confidence: {feedback1.confidence_score}")
    print(f"  Status: {feedback1.status.value}")
    
    # Example 2: False positive feedback
    feedback2 = collector.submit_feedback(
        alert_id="alert_12346",
        reviewer_user_id="compliance_officer_1",
        is_true_positive=False,
        feedback_type=FeedbackType.FALSE_POSITIVE,
        reviewer_notes="Normal market making activity. User is a registered market maker.",
        confidence_score=0.90
    )
    
    print(f"\n✓ False Positive Feedback:")
    print(f"  Feedback ID: {feedback2.feedback_id}")
    print(f"  Is True Positive: {feedback2.is_true_positive}")
    print(f"  Notes: {feedback2.reviewer_notes}")
    
    # Example 3: Severity adjustment
    feedback3 = collector.submit_feedback(
        alert_id="alert_12347",
        reviewer_user_id="compliance_officer_2",
        is_true_positive=True,
        feedback_type=FeedbackType.SEVERITY_ADJUSTMENT,
        suggested_risk_level=RiskLevel.MEDIUM,
        reviewer_notes="Pattern detected but severity should be medium, not high.",
        confidence_score=0.85
    )
    
    print(f"\n✓ Severity Adjustment Feedback:")
    print(f"  Feedback ID: {feedback3.feedback_id}")
    print(f"  Suggested Risk Level: {feedback3.suggested_risk_level.value}")
    print(f"  Original would have been: HIGH")
    
    # Example 4: Pattern correction
    feedback4 = collector.submit_feedback(
        alert_id="alert_12348",
        reviewer_user_id="compliance_officer_2",
        is_true_positive=True,
        feedback_type=FeedbackType.PATTERN_CORRECTION,
        suggested_pattern_type=PatternType.PUMP_AND_DUMP,
        reviewer_notes="This is actually a pump-and-dump scheme, not wash trading.",
        confidence_score=0.80
    )
    
    print(f"\n✓ Pattern Correction Feedback:")
    print(f"  Feedback ID: {feedback4.feedback_id}")
    print(f"  Suggested Pattern: {feedback4.suggested_pattern_type.value}")


def example_feedback_statistics():
    """Example 2: Get feedback statistics"""
    print("\n" + "=" * 60)
    print("Example 2: Feedback Statistics")
    print("=" * 60)
    
    collector = FeedbackCollector(storage=None)
    
    # Get statistics
    stats = collector.get_feedback_statistics()
    
    print(f"\n📊 Feedback Statistics:")
    print(f"  Total Feedback: {stats['total_feedback']}")
    print(f"  True Positives: {stats['true_positives']}")
    print(f"  False Positives: {stats['false_positives']}")
    print(f"  Precision: {stats['precision']:.2%}")
    print(f"  Average Confidence: {stats['average_confidence']:.2f}")
    
    if stats['by_type']:
        print(f"\n  By Type:")
        for feedback_type, count in stats['by_type'].items():
            print(f"    {feedback_type}: {count}")
    
    if stats['by_status']:
        print(f"\n  By Status:")
        for status, count in stats['by_status'].items():
            print(f"    {status}: {count}")
    
    print("\n  Note: Requires database for actual statistics")


def example_model_retraining():
    """Example 3: Model retraining with feedback"""
    print("\n" + "=" * 60)
    print("Example 3: Model Retraining")
    print("=" * 60)
    
    # Create retraining pipeline
    pipeline = RetrainingPipeline(
        storage=None,  # In production, pass DatabaseStorage
        model_dir="models",
        version_dir="model_versions"
    )
    
    print("\n🔄 Model Retraining Pipeline:")
    print(f"  Model Directory: {pipeline.model_dir}")
    print(f"  Version Directory: {pipeline.version_dir}")
    
    # In production, you would retrain like this:
    print("\n  Retraining Random Forest (simulated):")
    print("  1. Collecting feedback data...")
    print("  2. Extracting features from labeled trades...")
    print("  3. Training model with feedback...")
    print("  4. Evaluating performance...")
    print("  5. Creating new model version...")
    print("  6. Saving model and metadata...")
    
    # Example of what the code would look like:
    print("\n  Code example:")
    print("  ```python")
    print("  version = pipeline.retrain_random_forest(")
    print("      min_feedback_samples=50,")
    print("      min_confidence=0.7,")
    print("      incremental=True")
    print("  )")
    print("  ```")
    
    print("\n  Note: Requires database with feedback data for actual retraining")


def example_model_versioning():
    """Example 4: Model version management"""
    print("\n" + "=" * 60)
    print("Example 4: Model Version Management")
    print("=" * 60)
    
    pipeline = RetrainingPipeline(
        storage=None,
        model_dir="models",
        version_dir="model_versions"
    )
    
    print("\n📦 Model Version Management:")
    
    # Get model versions
    versions = pipeline.get_model_versions(model_type="random_forest", limit=5)
    
    print(f"\n  Available Versions: {len(versions)}")
    
    if versions:
        for i, version in enumerate(versions, 1):
            print(f"\n  Version {i}:")
            print(f"    ID: {version.version}")
            print(f"    Created: {version.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    Active: {version.is_active}")
            print(f"    Accuracy: {version.performance_metrics.accuracy:.3f}")
            print(f"    Precision: {version.performance_metrics.precision:.3f}")
            print(f"    F1 Score: {version.performance_metrics.f1_score:.3f}")
    else:
        print("  No versions found (requires actual model training)")
    
    # Example of activating a version
    print("\n  Activating a version (example):")
    print("  ```python")
    print("  pipeline.activate_model_version('random_forest_v20251112_120000')")
    print("  ```")
    
    # Example of rollback
    print("\n  Rolling back to previous version (example):")
    print("  ```python")
    print("  pipeline.rollback_to_version('random_forest_v20251111_100000')")
    print("  ```")


def example_performance_tracking():
    """Example 5: Track performance over time"""
    print("\n" + "=" * 60)
    print("Example 5: Performance Tracking")
    print("=" * 60)
    
    pipeline = RetrainingPipeline(
        storage=None,
        model_dir="models",
        version_dir="model_versions"
    )
    
    print("\n📈 Performance History:")
    
    # Get performance history
    history = pipeline.get_performance_history(
        model_type="random_forest",
        limit=10
    )
    
    if history:
        print(f"\n  Tracking {len(history)} versions:")
        print(f"\n  {'Version':<30} {'Accuracy':<10} {'Precision':<10} {'F1 Score':<10}")
        print("  " + "-" * 60)
        
        for metrics in history:
            print(f"  {metrics.version:<30} {metrics.accuracy:<10.3f} "
                  f"{metrics.precision:<10.3f} {metrics.f1_score:<10.3f}")
        
        # Show improvement
        if len(history) >= 2:
            latest = history[0]
            previous = history[1]
            
            acc_improvement = (latest.accuracy - previous.accuracy) * 100
            prec_improvement = (latest.precision - previous.precision) * 100
            
            print(f"\n  Improvement from previous version:")
            print(f"    Accuracy: {acc_improvement:+.2f}%")
            print(f"    Precision: {prec_improvement:+.2f}%")
    else:
        print("  No performance history (requires actual model training)")


def example_complete_workflow():
    """Example 6: Complete feedback and retraining workflow"""
    print("\n" + "=" * 60)
    print("Example 6: Complete Workflow")
    print("=" * 60)
    
    print("\n🔄 Complete Feedback and Retraining Workflow:")
    
    print("\n  Step 1: Alert Generation")
    print("    - System detects suspicious trading pattern")
    print("    - Alert generated with anomaly score")
    
    print("\n  Step 2: Compliance Review")
    print("    - Compliance officer reviews alert")
    print("    - Investigates trading activity")
    print("    - Determines if true or false positive")
    
    print("\n  Step 3: Feedback Submission")
    print("    ```python")
    print("    collector = FeedbackCollector(storage=storage)")
    print("    feedback = collector.submit_feedback(")
    print("        alert_id='alert_12345',")
    print("        reviewer_user_id='officer_1',")
    print("        is_true_positive=True,")
    print("        confidence_score=0.95")
    print("    )")
    print("    ```")
    
    print("\n  Step 4: Feedback Accumulation")
    print("    - System collects feedback over time")
    print("    - Minimum threshold reached (e.g., 50 samples)")
    
    print("\n  Step 5: Model Retraining")
    print("    ```python")
    print("    pipeline = RetrainingPipeline(storage=storage)")
    print("    version = pipeline.retrain_random_forest(")
    print("        min_feedback_samples=50,")
    print("        incremental=True")
    print("    )")
    print("    ```")
    
    print("\n  Step 6: Performance Evaluation")
    print("    - New model evaluated on test set")
    print("    - Metrics compared to previous version")
    print("    - Decision to activate or rollback")
    
    print("\n  Step 7: Model Activation")
    print("    ```python")
    print("    if version.performance_metrics.f1_score > 0.85:")
    print("        pipeline.activate_model_version(version.version)")
    print("    ```")
    
    print("\n  Step 8: Continuous Monitoring")
    print("    - Track performance on new data")
    print("    - Collect more feedback")
    print("    - Repeat cycle")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("FEEDBACK AND CONTINUOUS LEARNING EXAMPLES")
    print("=" * 60)
    
    try:
        example_feedback_submission()
        example_feedback_statistics()
        example_model_retraining()
        example_model_versioning()
        example_performance_tracking()
        example_complete_workflow()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        print("\nNote: Full functionality requires database integration")
        print("See trade_risk_analyzer/feedback/README.md for details")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
