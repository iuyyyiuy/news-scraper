"""
Example: Report Generation and Export

Demonstrates how to generate and export various types of reports.
"""

from datetime import datetime, timedelta
from pathlib import Path

from trade_risk_analyzer.core.base import Alert, RiskLevel, PatternType
from trade_risk_analyzer.reporting.generator import ReportGenerator
from trade_risk_analyzer.reporting.exporters import ReportExporter
from trade_risk_analyzer.reporting.visualizations import Visualizer


def create_sample_alerts(count: int = 50) -> list:
    """Create sample alerts for demonstration"""
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
            alert_id=f"alert_{i}",
            timestamp=timestamp,
            user_id=f"user_{i % 10}",
            trade_ids=[f"trade_{i}", f"trade_{i+1}"],
            anomaly_score=score,
            risk_level=risk_level,
            pattern_type=pattern,
            explanation=f"Detected {pattern.value} pattern with score {score:.1f}",
            recommended_action="Review trading activity and investigate further"
        )
        alerts.append(alert)
    
    return alerts


def example_daily_summary():
    """Example 1: Generate and export daily summary report"""
    print("=" * 60)
    print("Example 1: Daily Summary Report")
    print("=" * 60)
    
    # Create sample alerts
    alerts = create_sample_alerts(30)
    
    # Create a mock daily summary report
    from trade_risk_analyzer.reporting.generator import DailySummaryReport, ReportMetadata
    from collections import defaultdict
    
    date = datetime.now() - timedelta(days=1)
    metadata = ReportMetadata(
        report_id=f"daily_{date.strftime('%Y%m%d')}",
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
    
    print(f"\n📊 Daily Summary for {date.strftime('%Y-%m-%d')}")
    print(f"   Total Trades: {report.total_trades}")
    print(f"   Total Alerts: {report.total_alerts}")
    print(f"   High Risk: {report.high_risk_alerts}")
    print(f"   Medium Risk: {report.medium_risk_alerts}")
    print(f"   Low Risk: {report.low_risk_alerts}")
    print(f"   Average Score: {report.average_anomaly_score:.2f}")
    
    # Export to different formats
    output_dir = Path("example_reports")
    output_dir.mkdir(exist_ok=True)
    
    exporter = ReportExporter()
    
    # JSON export
    json_path = output_dir / "daily_summary.json"
    exporter.export(report, str(json_path), format='json')
    print(f"\n✓ Exported to JSON: {json_path}")
    
    # CSV export
    csv_path = output_dir / "daily_summary.csv"
    exporter.export(report, str(csv_path), format='csv')
    print(f"✓ Exported to CSV: {csv_path}")
    
    # PDF export (if available)
    try:
        pdf_path = output_dir / "daily_summary.pdf"
        exporter.export(report, str(pdf_path), format='pdf')
        print(f"✓ Exported to PDF: {pdf_path}")
    except ImportError:
        print("⚠ PDF export requires reportlab: pip install reportlab")


def example_user_profile():
    """Example 2: Generate and export user risk profile"""
    print("\n" + "=" * 60)
    print("Example 2: User Risk Profile")
    print("=" * 60)
    
    # Create sample alerts for one user
    all_alerts = create_sample_alerts(50)
    user_id = "user_5"
    alerts = [a for a in all_alerts if a.user_id == user_id]
    
    # Create a mock user profile report
    from trade_risk_analyzer.reporting.generator import UserRiskProfile, ReportMetadata
    
    metadata = ReportMetadata(
        report_id=f"profile_{user_id}_{int(datetime.now().timestamp())}",
        report_type='user_risk_profile',
        generated_at=datetime.now(),
        parameters={'user_id': user_id, 'days': 30}
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
        user_id=user_id,
        total_trades=500,
        total_alerts=len(alerts),
        risk_score=avg_score,
        risk_level=risk_level,
        alerts_by_pattern=alerts_by_pattern,
        recent_alerts=alerts[:5],
        trading_statistics={
            'total_volume': 10000.0,
            'average_volume': 20.0,
            'total_symbols': 5,
            'buy_count': 250,
            'sell_count': 250
        },
        risk_trend=[]
    )
    
    print(f"\n👤 User Profile: {user_id}")
    print(f"   Risk Score: {report.risk_score:.2f}")
    print(f"   Risk Level: {report.risk_level.value}")
    print(f"   Total Trades: {report.total_trades}")
    print(f"   Total Alerts: {report.total_alerts}")
    print(f"   Patterns Detected: {', '.join(report.alerts_by_pattern.keys())}")
    
    # Export to different formats
    output_dir = Path("example_reports")
    exporter = ReportExporter()
    
    # JSON export
    json_path = output_dir / f"user_profile_{user_id}.json"
    exporter.export(report, str(json_path), format='json')
    print(f"\n✓ Exported to JSON: {json_path}")
    
    # CSV export
    csv_path = output_dir / f"user_profile_{user_id}.csv"
    exporter.export(report, str(csv_path), format='csv')
    print(f"✓ Exported to CSV: {csv_path}")


def example_pattern_analysis():
    """Example 3: Generate and export pattern analysis"""
    print("\n" + "=" * 60)
    print("Example 3: Pattern Analysis")
    print("=" * 60)
    
    # Create sample alerts
    all_alerts = create_sample_alerts(60)
    pattern = PatternType.WASH_TRADING
    alerts = [a for a in all_alerts if a.pattern_type == pattern]
    
    # Create a mock pattern analysis report
    from trade_risk_analyzer.reporting.generator import PatternAnalysisReport, ReportMetadata
    from collections import defaultdict
    
    metadata = ReportMetadata(
        report_id=f"pattern_{pattern.value}_{int(datetime.now().timestamp())}",
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
    
    print(f"\n🔍 Pattern Analysis: {pattern.value}")
    print(f"   Total Occurrences: {report.total_occurrences}")
    print(f"   Affected Users: {report.affected_users}")
    print(f"   Average Severity: {report.average_severity:.2f}")
    print(f"   Peak Day: {max(temporal_distribution.items(), key=lambda x: x[1])[0]}")
    
    # Export to different formats
    output_dir = Path("example_reports")
    exporter = ReportExporter()
    
    # JSON export
    json_path = output_dir / f"pattern_{pattern.value}.json"
    exporter.export(report, str(json_path), format='json')
    print(f"\n✓ Exported to JSON: {json_path}")
    
    # CSV export
    csv_path = output_dir / f"pattern_{pattern.value}.csv"
    exporter.export(report, str(csv_path), format='csv')
    print(f"✓ Exported to CSV: {csv_path}")


def example_visualizations():
    """Example 4: Create visualizations"""
    print("\n" + "=" * 60)
    print("Example 4: Visualizations")
    print("=" * 60)
    
    # Create sample alerts
    alerts = create_sample_alerts(100)
    
    # Create visualizer
    visualizer = Visualizer()
    
    if not visualizer.matplotlib_available:
        print("\n⚠ Visualizations require matplotlib and seaborn")
        print("   Install with: pip install matplotlib seaborn")
        return
    
    output_dir = Path("example_reports")
    
    print("\n📈 Creating visualizations...")
    
    # Anomaly score distribution
    path = output_dir / "viz_anomaly_distribution.png"
    visualizer.create_anomaly_score_distribution(alerts, str(path))
    print(f"✓ Anomaly score distribution: {path}")
    
    # Risk level distribution
    path = output_dir / "viz_risk_distribution.png"
    visualizer.create_risk_level_distribution(alerts, str(path))
    print(f"✓ Risk level distribution: {path}")
    
    # Time series plot
    path = output_dir / "viz_time_series.png"
    visualizer.create_time_series_plot(alerts, str(path))
    print(f"✓ Time series plot: {path}")
    
    # Pattern distribution
    path = output_dir / "viz_pattern_distribution.png"
    visualizer.create_pattern_distribution(alerts, str(path))
    print(f"✓ Pattern distribution: {path}")
    
    # User risk comparison
    user_scores = {}
    for alert in alerts:
        if alert.user_id not in user_scores:
            user_scores[alert.user_id] = []
        user_scores[alert.user_id].append(alert.anomaly_score)
    
    user_avg_scores = {
        user_id: sum(scores) / len(scores)
        for user_id, scores in user_scores.items()
    }
    
    path = output_dir / "viz_user_comparison.png"
    visualizer.create_user_risk_comparison(user_avg_scores, str(path))
    print(f"✓ User risk comparison: {path}")
    
    # Comprehensive dashboard
    path = output_dir / "viz_dashboard.png"
    visualizer.create_dashboard(alerts, str(path))
    print(f"✓ Comprehensive dashboard: {path}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("REPORTING MODULE EXAMPLES")
    print("=" * 60)
    
    try:
        example_daily_summary()
        example_user_profile()
        example_pattern_analysis()
        example_visualizations()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        print("\nGenerated reports are in the 'example_reports' directory")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
