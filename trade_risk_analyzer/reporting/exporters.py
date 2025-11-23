"""
Report Export Module

Exports reports in various formats including PDF, CSV, and JSON.
"""

import pandas as pd
import json
import csv
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime
from io import StringIO, BytesIO

from trade_risk_analyzer.core.logger import get_logger
from trade_risk_analyzer.reporting.generator import (
    DailySummaryReport,
    UserRiskProfile,
    PatternAnalysisReport
)


logger = get_logger(__name__)


class JSONExporter:
    """Export reports to JSON format"""
    
    def __init__(self, indent: int = 2):
        """
        Initialize JSON exporter
        
        Args:
            indent: JSON indentation level
        """
        self.indent = indent
        self.logger = logger
    
    def export_daily_summary(
        self,
        report: DailySummaryReport,
        output_path: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Export daily summary report to JSON
        
        Args:
            report: DailySummaryReport to export
            output_path: Optional file path to save JSON
            
        Returns:
            JSON string or dict if no output_path
        """
        data = report.to_dict()
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=self.indent)
            self.logger.info(f"Daily summary exported to {output_path}")
            return output_path
        
        return data
    
    def export_user_profile(
        self,
        report: UserRiskProfile,
        output_path: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Export user risk profile to JSON
        
        Args:
            report: UserRiskProfile to export
            output_path: Optional file path to save JSON
            
        Returns:
            JSON string or dict if no output_path
        """
        data = report.to_dict()
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=self.indent)
            self.logger.info(f"User profile exported to {output_path}")
            return output_path
        
        return data
    
    def export_pattern_analysis(
        self,
        report: PatternAnalysisReport,
        output_path: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Export pattern analysis to JSON
        
        Args:
            report: PatternAnalysisReport to export
            output_path: Optional file path to save JSON
            
        Returns:
            JSON string or dict if no output_path
        """
        data = report.to_dict()
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=self.indent)
            self.logger.info(f"Pattern analysis exported to {output_path}")
            return output_path
        
        return data


class CSVExporter:
    """Export reports to CSV format"""
    
    def __init__(self):
        """Initialize CSV exporter"""
        self.logger = logger
    
    def export_daily_summary(
        self,
        report: DailySummaryReport,
        output_path: str
    ) -> str:
        """
        Export daily summary report to CSV
        
        Args:
            report: DailySummaryReport to export
            output_path: File path to save CSV
            
        Returns:
            Output path
        """
        # Create DataFrame from alerts
        if report.alerts:
            alerts_data = []
            for alert in report.alerts:
                alerts_data.append({
                    'Alert ID': alert.alert_id,
                    'User ID': alert.user_id,
                    'Timestamp': alert.timestamp.isoformat(),
                    'Anomaly Score': alert.anomaly_score,
                    'Risk Level': alert.risk_level.value,
                    'Pattern Type': alert.pattern_type.value,
                    'Explanation': alert.explanation,
                    'Trade IDs': ','.join(alert.trade_ids) if alert.trade_ids else ''
                })
            
            df = pd.DataFrame(alerts_data)
            df.to_csv(output_path, index=False)
            
            self.logger.info(f"Daily summary exported to {output_path}")
        else:
            # Create empty CSV with headers
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Alert ID', 'User ID', 'Timestamp', 'Anomaly Score',
                    'Risk Level', 'Pattern Type', 'Explanation', 'Trade IDs'
                ])
            
            self.logger.info(f"Empty daily summary exported to {output_path}")
        
        return output_path
    
    def export_user_profile(
        self,
        report: UserRiskProfile,
        output_path: str
    ) -> str:
        """
        Export user risk profile to CSV
        
        Args:
            report: UserRiskProfile to export
            output_path: File path to save CSV
            
        Returns:
            Output path
        """
        # Create DataFrame from recent alerts
        if report.recent_alerts:
            alerts_data = []
            for alert in report.recent_alerts:
                alerts_data.append({
                    'Alert ID': alert.alert_id,
                    'Timestamp': alert.timestamp.isoformat(),
                    'Anomaly Score': alert.anomaly_score,
                    'Risk Level': alert.risk_level.value,
                    'Pattern Type': alert.pattern_type.value,
                    'Explanation': alert.explanation
                })
            
            df = pd.DataFrame(alerts_data)
            
            # Add summary information as header rows
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['User Risk Profile'])
                writer.writerow(['User ID', report.user_id])
                writer.writerow(['Risk Score', report.risk_score])
                writer.writerow(['Risk Level', report.risk_level.value])
                writer.writerow(['Total Trades', report.total_trades])
                writer.writerow(['Total Alerts', report.total_alerts])
                writer.writerow([])
                writer.writerow(['Recent Alerts'])
            
            # Append alerts DataFrame
            df.to_csv(output_path, mode='a', index=False)
            
            self.logger.info(f"User profile exported to {output_path}")
        else:
            # Create CSV with summary only
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['User Risk Profile'])
                writer.writerow(['User ID', report.user_id])
                writer.writerow(['Risk Score', report.risk_score])
                writer.writerow(['Risk Level', report.risk_level.value])
                writer.writerow(['Total Trades', report.total_trades])
                writer.writerow(['Total Alerts', report.total_alerts])
            
            self.logger.info(f"User profile (no alerts) exported to {output_path}")
        
        return output_path
    
    def export_pattern_analysis(
        self,
        report: PatternAnalysisReport,
        output_path: str
    ) -> str:
        """
        Export pattern analysis to CSV
        
        Args:
            report: PatternAnalysisReport to export
            output_path: File path to save CSV
            
        Returns:
            Output path
        """
        # Create DataFrame from examples
        if report.examples:
            examples_data = []
            for alert in report.examples:
                examples_data.append({
                    'Alert ID': alert.alert_id,
                    'User ID': alert.user_id,
                    'Timestamp': alert.timestamp.isoformat(),
                    'Anomaly Score': alert.anomaly_score,
                    'Risk Level': alert.risk_level.value,
                    'Explanation': alert.explanation
                })
            
            df = pd.DataFrame(examples_data)
            
            # Add summary information as header rows
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Pattern Analysis Report'])
                writer.writerow(['Pattern Type', report.pattern_type.value])
                writer.writerow(['Total Occurrences', report.total_occurrences])
                writer.writerow(['Affected Users', report.affected_users])
                writer.writerow(['Average Severity', report.average_severity])
                writer.writerow([])
                writer.writerow(['Example Alerts'])
            
            # Append examples DataFrame
            df.to_csv(output_path, mode='a', index=False)
            
            self.logger.info(f"Pattern analysis exported to {output_path}")
        else:
            # Create CSV with summary only
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Pattern Analysis Report'])
                writer.writerow(['Pattern Type', report.pattern_type.value])
                writer.writerow(['Total Occurrences', report.total_occurrences])
                writer.writerow(['Affected Users', report.affected_users])
                writer.writerow(['Average Severity', report.average_severity])
            
            self.logger.info(f"Pattern analysis (no examples) exported to {output_path}")
        
        return output_path


class PDFExporter:
    """Export reports to PDF format using reportlab"""
    
    def __init__(self):
        """Initialize PDF exporter"""
        self.logger = logger
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if reportlab is available"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import (
                SimpleDocTemplate, Table, TableStyle, Paragraph,
                Spacer, PageBreak
            )
            self.reportlab_available = True
        except ImportError:
            self.logger.warning(
                "reportlab not installed. PDF export will not be available. "
                "Install with: pip install reportlab"
            )
            self.reportlab_available = False
    
    def export_daily_summary(
        self,
        report: DailySummaryReport,
        output_path: str
    ) -> str:
        """
        Export daily summary report to PDF
        
        Args:
            report: DailySummaryReport to export
            output_path: File path to save PDF
            
        Returns:
            Output path
        """
        if not self.reportlab_available:
            raise ImportError("reportlab is required for PDF export")
        
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        )
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(
            f"<b>Daily Summary Report - {report.date.strftime('%Y-%m-%d')}</b>",
            styles['Title']
        )
        story.append(title)
        story.append(Spacer(1, 0.3 * inch))
        
        # Summary statistics
        summary_data = [
            ['Metric', 'Value'],
            ['Total Trades', str(report.total_trades)],
            ['Total Alerts', str(report.total_alerts)],
            ['High Risk Alerts', str(report.high_risk_alerts)],
            ['Medium Risk Alerts', str(report.medium_risk_alerts)],
            ['Low Risk Alerts', str(report.low_risk_alerts)],
            ['Average Anomaly Score', f"{report.average_anomaly_score:.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Alerts by pattern
        if report.alerts_by_pattern:
            story.append(Paragraph("<b>Alerts by Pattern</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1 * inch))
            
            pattern_data = [['Pattern Type', 'Count']]
            for pattern, count in report.alerts_by_pattern.items():
                pattern_data.append([pattern, str(count)])
            
            pattern_table = Table(pattern_data, colWidths=[3 * inch, 2 * inch])
            pattern_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(pattern_table)
            story.append(Spacer(1, 0.3 * inch))
        
        # Top risk users
        if report.top_risk_users:
            story.append(Paragraph("<b>Top Risk Users</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1 * inch))
            
            users_data = [['User ID', 'Alert Count', 'Avg Score', 'Max Score']]
            for user in report.top_risk_users[:10]:
                users_data.append([
                    user['user_id'],
                    str(user['alert_count']),
                    f"{user['average_score']:.2f}",
                    f"{user['max_score']:.2f}"
                ])
            
            users_table = Table(users_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
            users_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(users_table)
        
        # Build PDF
        doc.build(story)
        
        self.logger.info(f"Daily summary PDF exported to {output_path}")
        return output_path
    
    def export_user_profile(
        self,
        report: UserRiskProfile,
        output_path: str
    ) -> str:
        """
        Export user risk profile to PDF
        
        Args:
            report: UserRiskProfile to export
            output_path: File path to save PDF
            
        Returns:
            Output path
        """
        if not self.reportlab_available:
            raise ImportError("reportlab is required for PDF export")
        
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        )
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(
            f"<b>User Risk Profile - {report.user_id}</b>",
            styles['Title']
        )
        story.append(title)
        story.append(Spacer(1, 0.3 * inch))
        
        # Profile summary
        profile_data = [
            ['Metric', 'Value'],
            ['User ID', report.user_id],
            ['Risk Score', f"{report.risk_score:.2f}"],
            ['Risk Level', report.risk_level.value],
            ['Total Trades', str(report.total_trades)],
            ['Total Alerts', str(report.total_alerts)]
        ]
        
        profile_table = Table(profile_data, colWidths=[3 * inch, 3 * inch])
        profile_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(profile_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Alerts by pattern
        if report.alerts_by_pattern:
            story.append(Paragraph("<b>Alerts by Pattern</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1 * inch))
            
            pattern_data = [['Pattern Type', 'Count']]
            for pattern, count in report.alerts_by_pattern.items():
                pattern_data.append([pattern, str(count)])
            
            pattern_table = Table(pattern_data, colWidths=[3 * inch, 2 * inch])
            pattern_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(pattern_table)
        
        # Build PDF
        doc.build(story)
        
        self.logger.info(f"User profile PDF exported to {output_path}")
        return output_path
    
    def export_pattern_analysis(
        self,
        report: PatternAnalysisReport,
        output_path: str
    ) -> str:
        """
        Export pattern analysis to PDF
        
        Args:
            report: PatternAnalysisReport to export
            output_path: File path to save PDF
            
        Returns:
            Output path
        """
        if not self.reportlab_available:
            raise ImportError("reportlab is required for PDF export")
        
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        )
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(
            f"<b>Pattern Analysis - {report.pattern_type.value}</b>",
            styles['Title']
        )
        story.append(title)
        story.append(Spacer(1, 0.3 * inch))
        
        # Analysis summary
        analysis_data = [
            ['Metric', 'Value'],
            ['Pattern Type', report.pattern_type.value],
            ['Total Occurrences', str(report.total_occurrences)],
            ['Affected Users', str(report.affected_users)],
            ['Average Severity', f"{report.average_severity:.2f}"]
        ]
        
        analysis_table = Table(analysis_data, colWidths=[3 * inch, 3 * inch])
        analysis_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(analysis_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Top users
        if report.user_distribution:
            story.append(Paragraph("<b>Top Affected Users</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1 * inch))
            
            users_data = [['User ID', 'Occurrences', 'Avg Severity']]
            for user in report.user_distribution[:10]:
                users_data.append([
                    user['user_id'],
                    str(user['occurrence_count']),
                    f"{user['average_severity']:.2f}"
                ])
            
            users_table = Table(users_data, colWidths=[2.5 * inch, 2 * inch, 2 * inch])
            users_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(users_table)
        
        # Build PDF
        doc.build(story)
        
        self.logger.info(f"Pattern analysis PDF exported to {output_path}")
        return output_path


class ReportExporter:
    """
    Main report exporter that handles all export formats
    """
    
    def __init__(self):
        """Initialize report exporter"""
        self.json_exporter = JSONExporter()
        self.csv_exporter = CSVExporter()
        self.pdf_exporter = PDFExporter()
        self.logger = logger
    
    def export(
        self,
        report: Union[DailySummaryReport, UserRiskProfile, PatternAnalysisReport],
        output_path: str,
        format: str = 'json'
    ) -> str:
        """
        Export report in specified format
        
        Args:
            report: Report to export
            output_path: Output file path
            format: Export format ('json', 'csv', 'pdf')
            
        Returns:
            Output path
        """
        format = format.lower()
        
        if format == 'json':
            if isinstance(report, DailySummaryReport):
                return self.json_exporter.export_daily_summary(report, output_path)
            elif isinstance(report, UserRiskProfile):
                return self.json_exporter.export_user_profile(report, output_path)
            elif isinstance(report, PatternAnalysisReport):
                return self.json_exporter.export_pattern_analysis(report, output_path)
        
        elif format == 'csv':
            if isinstance(report, DailySummaryReport):
                return self.csv_exporter.export_daily_summary(report, output_path)
            elif isinstance(report, UserRiskProfile):
                return self.csv_exporter.export_user_profile(report, output_path)
            elif isinstance(report, PatternAnalysisReport):
                return self.csv_exporter.export_pattern_analysis(report, output_path)
        
        elif format == 'pdf':
            if isinstance(report, DailySummaryReport):
                return self.pdf_exporter.export_daily_summary(report, output_path)
            elif isinstance(report, UserRiskProfile):
                return self.pdf_exporter.export_user_profile(report, output_path)
            elif isinstance(report, PatternAnalysisReport):
                return self.pdf_exporter.export_pattern_analysis(report, output_path)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        raise ValueError(f"Unsupported report type: {type(report)}")
