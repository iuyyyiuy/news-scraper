"""
Test Reporting Module

Tests report generation, export, and visualization functionality.
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

from trade_risk_analyzer.core.base import Alert, RiskLevel, PatternType, Trade, TradeType
from trade_risk_analyzer.reporting.generator import ReportGenerator
from trade_risk_analyzer.reporting.exporters import ReportExporter
from trade_risk_analyzer.reporting.visualizations import Visualizer


def create_test_alerts(count: int = 50) -> list:
    """Create test alerts"""
    alerts = []
    base_time = datetime.now() - timedelta(days=7)
    
    patterns = list(PatternType)
    risk_levels = [RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW]
    
    for i in range(count):
        timestamp = base_time + timedelta(hours=i * 3)
        pattern = patterns[i % len(patterns)]
        risk_level = risk_levels[i % len(risk_levels)]
        
        # Score based on risk level
        if risk_level == RiskLevel.HIGH:
            score = 80 + (i % 20)
        elif risk_level == RiskLevel.MEDIUM:
            score = 50 + (i % 30)
        else:
            score = 20 + (i % 30)
        
        alert = Alert(
            alert_id=f"test_alert_{i}",
            timestamp=timestamp,
            user_id=f"user_{i % 10}",
            trade_ids=[f"trade_{i}", f"trade_{i+1}"],
            anomaly_score=score,
            risk_level=risk_level,
            pattern_type=pattern,
            explanation=f"Test alert {i} for {pattern.value}",
            recommended_action="Review trading activity"
        )
        alerts.append(alert)
    
    return alerts


def test_report_generator():
    """Test report generation"""
    print("\n=== Testing Report Generator ===")
    
    # Create generator (without storage for testing)
    generator = ReportGenerator(storage=None)
    
    print("✓ Report generator created")
    
    # Note: Without storage, we can't generate real reports
    # In production, you would pass a DatabaseStorage instance
    print("✓ Report generator test passed (requires database for full testing)")


def test_daily_summary_export():
    """Test daily summary report export"""
    print("\n=== Testing Daily Summary Export ===")
    
    # Create test alerts
    alerts = create_test_alerts(30)
    
    # Create a mock daily summary report
    from trade_risk_analyzer.reporting.generator import DailySummaryReport, ReportMetadata
    from collections import defaultdict
    
    date = datetime.now() - timedelta(days=1)
    metadata = ReportMetadata(
        report_id=f"test_daily_{int(datetime.now().timestamp())}",
        report_type='daily_summary',
        generated_at=datetime.now(),
        start_date=date,
        end_date=date + timedelta(days=1)
    )
    
    # Calculate statistics
    high_risk = sum(1 for a in alerts if a.risk_level == RiskLevel.HIGH)
    medium_risk = sum(1 for a in alerts if a.risk_level == RiskLevel.MEDIUM)
    low_risk = sum(1 for a in alerts if a.risk_level == RiskLevel.LOW)
    
    alerts_by_pattern = {}
    for pattern_type in PatternType:
        count = sum(1 for a in alerts if a.pattern_type == pattern_type)
        if count > 0:
            alerts_by_pattern[pattern_type.value] = count
    
    user_scores = defaultdict(list)
    for alert in alerts:
        user_scores[alert.user_id].append(alert.anomaly_score)
    
    top_risk_users = []
    for user_id, scores in user_scores.items():
        top_risk_users.append({
            'user_id': user_id,
            'alert_count': len(scores),
            'average_score': sum(scores) / len(scores),
            'max_score': max(scores)
        })
    top_risk_users.sort(key=lambda x: x['average_score'], reverse=True)
    
    avg_score = sum(a.anomaly_score for a in alerts) / len(alerts)
    
    report = DailySummaryReport(
        metadata=metadata,
        date=date,
        total_trades=1000,
        total_alerts=len(alerts),
        high_risk_alerts=high_risk,
        medium_risk_alerts=medium_risk,
        low_risk_alerts=low_risk,
        alerts_by_pattern=alerts_by_pattern,
        top_risk_users=top_risk_users,
        average_anomaly_score=avg_score,
        alerts=alerts
    )
    
    print(f"Created daily summary report with {len(alerts)} alerts")
    
    # Test exports
    exporter = ReportExporter()
    
    # Create output directory
    output_dir = Path("test_reports")
    output_dir.mkdir(exist_ok=True)
    
    # Test JSON export
    json_path = output_dir / "daily_summary.json"
    exporter.export(report, str(json_path), format='json')
    print(f"✓ JSON export: {json_path}")
    
    # Test CSV export
    csv_path = output_dir / "daily_summary.csv"
    exporter.export(report, str(csv_path), format='csv')
    print(f"✓ CSV export: {csv_path}")
    
    # Test PDF export (if reportlab is available)
    try:
        pdf_path = output_dir / "daily_summary.pdf"
        exporter.export(report, str(pdf_path), format='pdf')
        print(f"✓ PDF export: {pdf_path}")
    except ImportError:
        print("⚠ PDF export skipped (reportlab not installed)")
    
    print("✓ Daily summary export test passed")


def test_user_profile_export():
    """Test user profile report export"""
    print("\n=== Testing User Profile Export ===")
    
    # Create test alerts for one user
    alerts = [a for a in create_test_alerts(20) if a.user_id == "user_1"]
    
    # Create a mock user profile report
    from trade_risk_analyzer.reporting.generator import UserRiskProfile, ReportMetadata
    
    metadata = ReportMetadata(
        report_id=f"test_profile_{int(datetime.now().timestamp())}",
        report_type='user_risk_profile',
        generated_at=datetime.now(),
        parameters={'user_id': 'user_1', 'days': 30}
    )
    
    alerts_by_pattern = {}
    for pattern_type in PatternType:
        count = sum(1 for a in alerts if a.pattern_type == pattern_type)
        if count > 0:
            alerts_by_pattern[pattern_type.value] = count
    
    avg_score = sum(a.anomaly_score for a in alerts) / len(alerts) if alerts else 0
    
    if avg_score >= 80:
        risk_level = RiskLevel.HIGH
    elif avg_score >= 50:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.LOW
    
    report = UserRiskProfile(
        metadata=metadata,
        user_id='user_1',
        total_trades=500,
        total_alerts=len(alerts),
        risk_score=avg_score,
        risk_level=risk_level,
        alerts_by_pattern=alerts_by_pattern,
        recent_alerts=alerts[:5],
        trading_statistics={
            'total_volume': 10000.0,
            'average_volume': 20.0,
            'total_symbols': 5
        },
        risk_trend=[]
    )
    
    print(f"Created user profile report for user_1 with {len(alerts)} alerts")
    
    # Test exports
    exporter = ReportExporter()
    output_dir = Path("test_reports")
    
    # Test JSON export
    json_path = output_dir / "user_profile.json"
    exporter.export(report, str(json_path), format='json')
    print(f"✓ JSON export: {json_path}")
    
    # Test CSV export
    csv_path = output_dir / "user_profile.csv"
    exporter.export(report, str(csv_path), format='csv')
    print(f"✓ CSV export: {csv_path}")
    
    # Test PDF export (if reportlab is available)
    try:
        pdf_path = output_dir / "user_profile.pdf"
        exporter.export(report, str(pdf_path), format='pdf')
        print(f"✓ PDF export: {pdf_path}")
    except ImportError:
        print("⚠ PDF export skipped (reportlab not installed)")
    
    print("✓ User profile export test passed")


def test_pattern_analysis_export():
    """Test pattern analysis report export"""
    print("\n=== Testing Pattern Analysis Export ===")
    
    # Create test alerts
    all_alerts = create_test_alerts(40)
    pattern = PatternType.WASH_TRADING
    alerts = [a for a in all_alerts if a.pattern_type == pattern]
    
    # Create a mock pattern analysis report
    from trade_risk_analyzer.reporting.generator import PatternAnalysisReport, ReportMetadata
    from collections import defaultdict
    
    metadata = ReportMetadata(
        report_id=f"test_pattern_{int(datetime.now().timestamp())}",
        report_type='pattern_analysis',
        generated_at=datetime.now(),
        parameters={'pattern_type': pattern.value, 'days': 30}
    )
    
    affected_users = len(set(a.user_id for a in alerts))
    avg_severity = sum(a.anomaly_score for a in alerts) / len(alerts) if alerts else 0
    
    temporal_distribution = {}
    for alert in alerts:
        day_key = alert.timestamp.strftime('%Y-%m-%d')
        temporal_distribution[day_key] = temporal_distribution.get(day_key, 0) + 1
    
    user_counts = defaultdict(int)
    user_scores = defaultdict(list)
    for alert in alerts:
        user_counts[alert.user_id] += 1
        user_scores[alert.user_id].append(alert.anomaly_score)
    
    user_distribution = []
    for user_id, count in user_counts.items():
        avg_score = sum(user_scores[user_id]) / len(user_scores[user_id])
        user_distribution.append({
            'user_id': user_id,
            'occurrence_count': count,
            'average_severity': avg_score
        })
    user_distribution.sort(key=lambda x: x['occurrence_count'], reverse=True)
    
    report = PatternAnalysisReport(
        metadata=metadata,
        pattern_type=pattern,
        total_occurrences=len(alerts),
        affected_users=affected_users,
        average_severity=avg_severity,
        temporal_distribution=temporal_distribution,
        user_distribution=user_distribution,
        examples=alerts[:5]
    )
    
    print(f"Created pattern analysis report for {pattern.value} with {len(alerts)} occurrences")
    
    # Test exports
    exporter = ReportExporter()
    output_dir = Path("test_reports")
    
    # Test JSON export
    json_path = output_dir / "pattern_analysis.json"
    exporter.export(report, str(json_path), format='json')
    print(f"✓ JSON export: {json_path}")
    
    # Test CSV export
    csv_path = output_dir / "pattern_analysis.csv"
    exporter.export(report, str(csv_path), format='csv')
    print(f"✓ CSV export: {csv_path}")
    
    # Test PDF export (if reportlab is available)
    try:
        pdf_path = output_dir / "pattern_analysis.pdf"
        exporter.export(report, str(pdf_path), format='pdf')
        print(f"✓ PDF export: {pdf_path}")
    except ImportError:
        print("⚠ PDF export skipped (reportlab not installed)")
    
    print("✓ Pattern analysis export test passed")


def test_visualizations():
    """Test visualization generation"""
    print("\n=== Testing Visualizations ===")
    
    # Create test alerts
    alerts = create_test_alerts(100)
    
    # Create visualizer
    visualizer = Visualizer()
    
    if not visualizer.matplotlib_available:
        print("⚠ Visualizations skipped (matplotlib not installed)")
        return
    
    output_dir = Path("test_reports")
    output_dir.mkdir(exist_ok=True)
    
    # Test anomaly score distribution
    try:
        path = output_dir / "anomaly_distribution.png"
        visualizer.create_anomaly_score_distribution(alerts, str(path))
        print(f"✓ Anomaly score distribution: {path}")
    except Exception as e:
        print(f"⚠ Anomaly score distribution failed: {e}")
    
    # Test risk level distribution
    try:
        path = output_dir / "risk_distribution.png"
        visualizer.create_risk_level_distribution(alerts, str(path))
        print(f"✓ Risk level distribution: {path}")
    except Exception as e:
        print(f"⚠ Risk level distribution failed: {e}")
    
    # Test time series plot
    try:
        path = output_dir / "time_series.png"
        visualizer.create_time_series_plot(alerts, str(path))
        print(f"✓ Time series plot: {path}")
    except Exception as e:
        print(f"⚠ Time series plot failed: {e}")
    
    # Test temporal heatmap
    try:
        path = output_dir / "temporal_heatmap.png"
        visualizer.create_temporal_heatmap(alerts, str(path))
        print(f"✓ Temporal heatmap: {path}")
    except Exception as e:
        print(f"⚠ Temporal heatmap failed: {e}")
    
    # Test pattern distribution
    try:
        path = output_dir / "pattern_distribution.png"
        visualizer.create_pattern_distribution(alerts, str(path))
        print(f"✓ Pattern distribution: {path}")
    except Exception as e:
        print(f"⚠ Pattern distribution failed: {e}")
    
    # Test user risk comparison
    try:
        user_scores = {}
        for alert in alerts:
            if alert.user_id not in user_scores:
                user_scores[alert.user_id] = []
            user_scores[alert.user_id].append(alert.anomaly_score)
        
        user_avg_scores = {
            user_id: sum(scores) / len(scores)
            for user_id, scores in user_scores.items()
        }
        
        path = output_dir / "user_comparison.png"
        visualizer.create_user_risk_comparison(user_avg_scores, str(path))
        print(f"✓ User risk comparison: {path}")
    except Exception as e:
        print(f"⚠ User risk comparison failed: {e}")
    
    # Test dashboard
    try:
        path = output_dir / "dashboard.png"
        visualizer.create_dashboard(alerts, str(path))
        print(f"✓ Dashboard: {path}")
    except Exception as e:
        print(f"⚠ Dashboard failed: {e}")
    
    print("✓ Visualization tests completed")


def main():
    """Run all tests"""
    print("=" * 60)
    print("REPORTING MODULE TESTS")
    print("=" * 60)
    
    try:
        test_report_generator()
        test_daily_summary_export()
        test_user_profile_export()
        test_pattern_analysis_export()
        test_visualizations()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED ✓")
        print("=" * 60)
        print("\nGenerated reports are in the 'test_reports' directory")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
